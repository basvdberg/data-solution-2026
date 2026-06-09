"""Open-Meteo data object poller — scheduled probe and optional event publish."""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow.exceptions import AirflowException
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG, Variable

DAG_ID = "openmeteo_data_object_poller"
DEFAULT_DATA_OBJECT_ID = "source/openmeteo/daily-temperature"
DEFAULT_PUBLISH = "none"


def run_openmeteo_poller() -> None:
    """Delegate to the poller CLI ``main()`` (same args as manual ``python -m``)."""
    from extractor_and_poller.poller.__main__ import main

    exit_code = main(
        [
            "--data-object",
            Variable.get("poller_data_object_id", default=DEFAULT_DATA_OBJECT_ID),
            "--publish",
            Variable.get("poller_publish", default=DEFAULT_PUBLISH),
        ]
    )

    if exit_code == 2:
        raise AirflowException("poller exited with code 2 (configuration or validation error)")
    if exit_code == 3:
        raise AirflowException(
            "poller exited with code 3 (probe ran but no rows were persisted to Postgres)"
        )
    if exit_code not in (0, 1):
        raise AirflowException(f"poller exited with unexpected code {exit_code}")


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
        "optionally publish events. Manual triggers while a run is active are queued "
        "(max_active_runs=1); task logs appear when the run starts."
    ),
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
