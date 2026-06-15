"""Open-Meteo data object poller — scheduled probe and Airflow Asset emit on change."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta

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

log = logging.getLogger(__name__)
source_change_asset = change_asset(DEFAULT_DATA_OBJECT_ID)


def run_probe_and_persist() -> dict[str, str]:
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


def choose_after_probe(**context) -> str:
    """Branch to asset emit on change, or progress audit only."""
    ti = context["ti"]
    probe = ti.xcom_pull(task_ids="probe_and_persist") or {}
    if probe.get("event_type") == EVENT_TYPE_CHANGE:
        return "emit_change_asset"
    return "record_progress"


def _change_asset_extra(context: dict) -> dict[str, str]:
    ti = context["ti"]
    probe = ti.xcom_pull(task_ids="probe_and_persist") or {}
    return {
        "data_object_id": probe["data_object_id"],
        "event_type": probe["event_type"],
        "marker": probe["new_marker"],
        "event_id": probe["event_id"],
        "mapping_id": probe["mapping_id"],
    }


def emit_change_asset(**context) -> dict[str, str]:
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
        task_id="probe_and_persist",
        python_callable=run_probe_and_persist,
    )

    branch_task = BranchPythonOperator(
        task_id="branch_on_event_type",
        python_callable=choose_after_probe,
    )

    emit_task = PythonOperator(
        task_id="emit_change_asset",
        python_callable=emit_change_asset,
        outlets=[source_change_asset],
        post_execute=_emit_change_post_execute,
    )

    progress_task = EmptyOperator(task_id="record_progress")

    probe_task >> branch_task >> [emit_task, progress_task]
