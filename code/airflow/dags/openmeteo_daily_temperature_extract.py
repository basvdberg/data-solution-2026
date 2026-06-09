"""Open-Meteo extract — triggered by poll change events via the Kafka controller."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta

from airflow.exceptions import AirflowException
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG

DAG_ID = "openmeteo_daily_temperature_extract"
DEFAULT_MAPPING = "daily-temperature"

log = logging.getLogger(__name__)


def run_openmeteo_extract(**context) -> None:
    """Delegate to the extractor CLI ``main()``."""
    conf = (context.get("dag_run").conf or {}) if context.get("dag_run") else {}
    argv = ["--mapping", str(conf.get("mapping_id", DEFAULT_MAPPING))]
    if conf.get("marker"):
        argv.extend(["--marker", str(conf["marker"])])
    if conf.get("event_id"):
        argv.extend(["--event-id", str(conf["event_id"])])
    log.info(
        "Airflow task starting openmeteo extract dag_id=%s run_id=%s argv=%s",
        os.environ.get("AIRFLOW_CTX_DAG_ID"),
        os.environ.get("AIRFLOW_CTX_DAG_RUN_ID"),
        argv,
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
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id=DAG_ID,
    description=(
        "Extract Open-Meteo daily-temperature into Postgres staging "
        "(staging.openmeteo_daily_temperature). Triggered by Kafka data_object_change events."
    ),
    default_args=default_args,
    schedule=None,
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
