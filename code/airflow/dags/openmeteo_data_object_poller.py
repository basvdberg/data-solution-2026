"""Open-Meteo data object poller — scheduled probe and Airflow Asset emit on change."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta
from typing import Any

from airflow.exceptions import AirflowException
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.standard.operators.python import BranchPythonOperator, PythonOperator
from airflow.sdk import DAG, Variable

from extractor_and_poller.common.paths import PROJECT_ROOT
from extractor_and_poller.poller.poll_events import EVENT_TYPE_CHANGE
from include.data_object_assets import change_asset

DAG_ID = "openmeteo_data_object_poller"
DEFAULT_DATA_OBJECT_ID = "source/openmeteo/daily-temperature"
DEFAULT_CONFIG = (
    PROJECT_ROOT
    / "data-object-mapping"
    / "staging"
    / "openmeteo"
    / "daily-temperature.json"
)

TASK_PROBE_API_AND_WRITE_POSTGRES = "probe_api_and_write_postgres"
TASK_CHECK_DATA_CHANGED = "check_data_changed"
TASK_EMIT_AIRFLOW_DATA_CHANGE_EVENT = "emit_airflow_data_change_event"
TASK_COMPLETE_UNCHANGED_RUN = "complete_unchanged_run"
TASK_POLL_RUN_SUMMARY = "poll_run_summary"

log = logging.getLogger(__name__)
source_change_asset = change_asset(DEFAULT_DATA_OBJECT_ID)


def run_probe_api_and_write_postgres() -> dict[str, Any]:
    """Probe source marker, persist to Postgres, return probe metadata for XCom."""
    from include.poll_run import probe_and_persist

    data_object_id = Variable.get("data_object_id", default=DEFAULT_DATA_OBJECT_ID)
    log.info(
        "Airflow task starting probe dag_id=%s run_id=%s data_object=%s",
        os.environ.get("AIRFLOW_CTX_DAG_ID"),
        os.environ.get("AIRFLOW_CTX_DAG_RUN_ID"),
        data_object_id,
    )
    try:
        return probe_and_persist(
            config_path=str(DEFAULT_CONFIG),
            data_object_id=data_object_id,
        )
    except ValueError as exc:
        raise AirflowException(f"poller configuration or validation error: {exc}") from exc
    except RuntimeError as exc:
        raise AirflowException(str(exc)) from exc


def check_data_changed(**context) -> str:
    """Branch to asset emit on change, or complete unchanged run."""
    ti = context["ti"]
    probe = ti.xcom_pull(task_ids=TASK_PROBE_API_AND_WRITE_POSTGRES) or {}
    if probe.get("event_type") == EVENT_TYPE_CHANGE:
        return TASK_EMIT_AIRFLOW_DATA_CHANGE_EVENT
    return TASK_COMPLETE_UNCHANGED_RUN


def _change_asset_extra(context: dict) -> dict[str, str]:
    ti = context["ti"]
    probe = ti.xcom_pull(task_ids=TASK_PROBE_API_AND_WRITE_POSTGRES) or {}
    extra: dict[str, str] = {
        "data_object_id": probe["data_object_id"],
        "event_type": probe["event_type"],
        "marker": probe["new_marker"],
        "event_id": probe["event_id"],
        "mapping_id": probe["mapping_id"],
    }
    change_scope = probe.get("change_scope")
    if change_scope is not None:
        extra["change_scope"] = str(change_scope)
    return extra


def emit_airflow_data_change_event(**context) -> dict[str, str]:
    """Build extract conf extra for the source change asset event."""
    extra = _change_asset_extra(context)
    log.info(
        "Emitting change asset uri=%s mapping=%s marker=%s event_id=%s",
        source_change_asset.uri,
        extra["mapping_id"],
        extra["marker"],
        extra["event_id"],
    )
    return extra


def _emit_change_post_execute(context: dict, result: dict[str, str]) -> None:
    context["outlet_events"][source_change_asset].extra = result


def _poll_summary_note(probe: dict[str, Any]) -> str:
    changed = probe.get("data_changed")
    event_type = probe.get("event_type", "unknown")
    api_ok = probe.get("api_reachable")
    return (
        f"{'changed' if changed else 'unchanged'} | "
        f"postgres:{event_type} | "
        f"api:{'ok' if api_ok else 'failed'}"
    )


def log_poll_run_summary(**context) -> None:
    """Log human-readable poll outcome and attach a short note to the DAG run."""
    probe = context["ti"].xcom_pull(task_ids=TASK_PROBE_API_AND_WRITE_POSTGRES) or {}
    log.info(
        "Poll run summary: event=%s changed=%s postgres_row_id=%s marker=%s api=%s",
        probe.get("event_type", "unknown"),
        "yes" if probe.get("data_changed") else "no",
        probe.get("postgres_row_id", "unknown"),
        probe.get("new_marker", "unknown"),
        "reachable" if probe.get("api_reachable") else "failed",
    )
    note = _poll_summary_note(probe)
    dag_run = context.get("dag_run")
    if dag_run is not None and hasattr(dag_run, "note"):
        dag_run.note = note


default_args = {
    "owner": "data-solution-2026",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id=DAG_ID,
    description=(
        "Probe Open-Meteo daily-temperature source marker; persist state in Postgres and "
        "emit an Airflow Asset on data_object_change."
    ),
    default_args=default_args,
    schedule="@hourly",
    start_date=datetime(2026, 6, 1),
    catchup=False,
    max_active_runs=1,
    is_paused_upon_creation=True,
    tags=["openmeteo", "poller", "data-object"],
) as dag:
    probe_task = PythonOperator(
        task_id=TASK_PROBE_API_AND_WRITE_POSTGRES,
        python_callable=run_probe_api_and_write_postgres,
    )

    check_data_changed_task = BranchPythonOperator(
        task_id=TASK_CHECK_DATA_CHANGED,
        python_callable=check_data_changed,
    )

    emit_task = PythonOperator(
        task_id=TASK_EMIT_AIRFLOW_DATA_CHANGE_EVENT,
        python_callable=emit_airflow_data_change_event,
        outlets=[source_change_asset],
        post_execute=_emit_change_post_execute,
    )

    complete_unchanged_task = EmptyOperator(task_id=TASK_COMPLETE_UNCHANGED_RUN)

    summary_task = PythonOperator(
        task_id=TASK_POLL_RUN_SUMMARY,
        python_callable=log_poll_run_summary,
        trigger_rule="none_failed_min_one_success",
    )

    probe_task >> check_data_changed_task >> [emit_task, complete_unchanged_task]
    [emit_task, complete_unchanged_task] >> summary_task
