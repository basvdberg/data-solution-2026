"""Open-Meteo extract — triggered by source change Airflow Asset."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta
from typing import Any

from airflow.exceptions import AirflowException
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG

from extractor_and_poller.common.paths import PROJECT_ROOT
from extractor_and_poller.poller.poll_events import EVENT_TYPE_CHANGE
from include.asset_conf import extract_conf_from_asset_extra
from include.data_object_assets import change_asset

DAG_ID = "openmeteo_daily_temperature_extract"
DEFAULT_MAPPING = "daily-temperature"
DEFAULT_SOURCE_DATA_OBJECT_ID = "source/openmeteo/daily-temperature"
DEFAULT_STAGING_DATA_OBJECT_ID = "staging/openmeteo/daily-temperature"
DEFAULT_CONFIG = (
    PROJECT_ROOT
    / "data-object-mapping"
    / "staging"
    / "openmeteo"
    / "daily-temperature.json"
)

TASK_EXTRACT = "extract_openmeteo_daily_temperature"
TASK_EMIT_STAGING_CHANGE = "emit_staging_data_change_event"

log = logging.getLogger(__name__)
source_change_asset = change_asset(DEFAULT_SOURCE_DATA_OBJECT_ID)
staging_change_asset = change_asset(DEFAULT_STAGING_DATA_OBJECT_ID)


def _extract_conf_from_context(context: dict) -> dict:
    """Build extractor conf from manual trigger conf or asset event extra."""
    dag_run = context.get("dag_run")
    conf: dict = dict((dag_run.conf or {}) if dag_run else {})

    triggering = context.get("triggering_asset_events") or {}
    asset_events = triggering.get(source_change_asset) or []
    if asset_events:
        latest = asset_events[-1]
        extra = getattr(latest, "extra", None)
        if extra is None and isinstance(latest, dict):
            extra = latest.get("extra")
        asset_conf = extract_conf_from_asset_extra(extra)
        if asset_conf:
            conf = {**conf, **asset_conf}
        else:
            log.warning("Asset-triggered run but extra did not yield extract conf: %s", extra)

    return conf


def run_openmeteo_extract(**context) -> dict[str, Any]:
    """Run extractor and return orchestration outcome metadata for XCom."""
    from extractor_and_poller.extract.run import run_extract
    from extractor_and_poller.poller.state import default_postgres_dsn

    conf = _extract_conf_from_context(context)
    mapping_id = str(conf.get("mapping_id", DEFAULT_MAPPING))
    argv_marker = conf.get("marker")
    argv_event_id = conf.get("event_id")
    log.info(
        "Airflow task starting openmeteo extract dag_id=%s run_id=%s mapping=%s conf=%s",
        os.environ.get("AIRFLOW_CTX_DAG_ID"),
        os.environ.get("AIRFLOW_CTX_DAG_RUN_ID"),
        mapping_id,
        conf,
    )

    try:
        outcome = run_extract(
            config_path=str(DEFAULT_CONFIG),
            mapping_id=mapping_id,
            marker=str(argv_marker) if argv_marker else None,
            event_id=str(argv_event_id) if argv_event_id else None,
            postgres_dsn=default_postgres_dsn(),
        )
    except ValueError as exc:
        raise AirflowException(f"extractor configuration or validation error: {exc}") from exc

    if outcome is None:
        return {"skipped": "true", "event_id": str(argv_event_id or "")}

    return outcome.as_dict()


def emit_staging_data_change_event(**context) -> dict[str, str]:
    """Build staging change asset extra after a successful extract."""
    ti = context["ti"]
    outcome = ti.xcom_pull(task_ids=TASK_EXTRACT) or {}
    if outcome.get("skipped") == "true":
        log.info("Extract skipped (duplicate event_id=%s); no staging asset emit", outcome.get("event_id"))
        return {}

    event_type = str(outcome.get("event_type", EVENT_TYPE_CHANGE))
    if event_type != EVENT_TYPE_CHANGE:
        log.warning("Extract outcome event_type=%s; skipping staging asset emit", event_type)
        return {}

    extra = {key: str(value) for key, value in outcome.items() if value is not None}
    log.info(
        "Emitting change asset uri=%s data_object=%s marker=%s event_id=%s",
        staging_change_asset.uri,
        extra.get("data_object_id"),
        extra.get("marker"),
        extra.get("event_id"),
    )
    return extra


def _emit_staging_post_execute(context: dict, result: dict[str, str]) -> None:
    if result:
        context["outlet_events"][staging_change_asset].extra = result


default_args = {
    "owner": "data-solution-2026",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 5,
    "retry_delay": timedelta(minutes=2),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=30),
}

with DAG(
    dag_id=DAG_ID,
    description=(
        "Extract Open-Meteo daily-temperature into Postgres staging "
        "(staging.openmeteo_daily_temperature). Triggered by source change Airflow Asset."
    ),
    default_args=default_args,
    schedule=[source_change_asset],
    start_date=datetime(2026, 6, 1),
    catchup=False,
    max_active_runs=3,
    is_paused_upon_creation=False,
    tags=["openmeteo", "extract", "data-object"],
) as dag:
    extract_task = PythonOperator(
        task_id=TASK_EXTRACT,
        python_callable=run_openmeteo_extract,
    )

    emit_task = PythonOperator(
        task_id=TASK_EMIT_STAGING_CHANGE,
        python_callable=emit_staging_data_change_event,
        outlets=[staging_change_asset],
        post_execute=_emit_staging_post_execute,
    )

    extract_task >> emit_task
