"""Open-Meteo extract — triggered by source change Airflow Asset."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta

from airflow.exceptions import AirflowException
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG

from include.asset_conf import extract_conf_from_asset_extra
from include.data_object_assets import change_asset

DAG_ID = "openmeteo_daily_temperature_extract"
DEFAULT_MAPPING = "daily-temperature"
DEFAULT_DATA_OBJECT_ID = "source/openmeteo/daily-temperature"

log = logging.getLogger(__name__)
source_change_asset = change_asset(DEFAULT_DATA_OBJECT_ID)


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


def run_openmeteo_extract(**context) -> None:
    """Delegate to the extractor CLI ``main()``."""
    conf = _extract_conf_from_context(context)
    argv = ["--mapping", str(conf.get("mapping_id", DEFAULT_MAPPING))]
    if conf.get("marker"):
        argv.extend(["--marker", str(conf["marker"])])
    if conf.get("event_id"):
        argv.extend(["--event-id", str(conf["event_id"])])
    log.info(
        "Airflow task starting openmeteo extract dag_id=%s run_id=%s argv=%s conf=%s",
        os.environ.get("AIRFLOW_CTX_DAG_ID"),
        os.environ.get("AIRFLOW_CTX_DAG_RUN_ID"),
        argv,
        conf,
    )

    from extractor_and_poller.openmeteo.extractor.__main__ import main

    exit_code = main(argv)
    if exit_code == 2:
        raise AirflowException("extractor exited with code 2 (configuration or validation error)")
    if exit_code != 0:
        raise AirflowException(f"extractor exited with unexpected code {exit_code}")


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
    PythonOperator(
        task_id="extract_openmeteo_daily_temperature",
        python_callable=run_openmeteo_extract,
    )
