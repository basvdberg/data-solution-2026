"""Open-Meteo data object poller — scheduled probe and optional event publish.

DAG source lives under ``code/airflow/dags/`` in the data-solution repo.
Mounted into Airflow at ``/opt/airflow/dags``; application code at ``/opt/data-solution/code``.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

from airflow import DAG
from airflow.exceptions import AirflowException
from airflow.models import Variable
from airflow.providers.standard.operators.python import PythonOperator

DAG_ID = "openmeteo_data_object_poller"
DEFAULT_DATA_OBJECT_ID = "source/openmeteo/daily-temperature"
DEFAULT_PUBLISH = "none"

log = logging.getLogger(__name__)


def _variable(name: str, default: str) -> str:
    try:
        return Variable.get(name, default_var=default)
    except Exception:
        return default


def run_openmeteo_poller() -> None:
    """Thin wrapper: delegate to the poller CLI ``main()`` (no duplicated logic)."""
    log.info("Starting Open-Meteo data object poller task")

    from extractor_and_poller.poller.__main__ import main

    argv = [
        "--data-object",
        _variable("poller_data_object_id", DEFAULT_DATA_OBJECT_ID),
        "--publish",
        _variable("poller_publish", DEFAULT_PUBLISH),
    ]
    exit_code = main(argv)

    if exit_code == 2:
        raise AirflowException("poller exited with code 2 (configuration or validation error)")
    if exit_code == 1:
        log.info("Poller finished: data object change detected")
    else:
        log.info("Poller finished: no change")


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
    description="Probe Open-Meteo daily-temperature source marker; persist state in Postgres and optionally publish events.",
    default_args=default_args,
    schedule="@hourly",
    start_date=datetime(2026, 6, 1),
    catchup=False,
    max_active_runs=1,
    is_paused_upon_creation=True,
    tags=["openmeteo", "poller", "data-object"],
) as dag:
    PythonOperator(
        task_id="poll_openmeteo_daily_temperature",
        python_callable=run_openmeteo_poller,
    )
