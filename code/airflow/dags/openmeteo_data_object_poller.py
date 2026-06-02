"""Open-Meteo data object poller — scheduled probe and optional event publish.

DAG source lives under ``code/airflow/dags/`` in the data-solution repo.
Mounted into Airflow at ``/opt/airflow/dags``; application code at ``/opt/data-solution``.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.models import Variable
from airflow.operators.bash import BashOperator

DAG_ID = "openmeteo_data_object_poller"
REPO_ROOT = "/opt/data-solution"

DEFAULT_DATA_OBJECT_ID = "source/openmeteo/daily-temperature"
DEFAULT_STATE_BACKEND = "file"
DEFAULT_PUBLISH = "none"


def _variable(name: str, default: str) -> str:
    try:
        return Variable.get(name, default_var=default)
    except Exception:
        return default


def _poll_command() -> str:
    data_object_id = _variable("poller_data_object_id", DEFAULT_DATA_OBJECT_ID)
    state_backend = _variable("poller_state_backend", DEFAULT_STATE_BACKEND)
    publish = _variable("poller_publish", DEFAULT_PUBLISH)
    return (
        f"python -m extractor_and_poller.poller "
        f"--data-object {data_object_id} "
        f"--state-backend {state_backend} "
        f"--publish {publish}"
    )


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
    description="Probe Open-Meteo daily-temperature source marker; persist state and optionally publish events.",
    default_args=default_args,
    schedule="@hourly",
    start_date=datetime(2026, 6, 1),
    catchup=False,
    max_active_runs=1,
    is_paused_upon_creation=True,
    tags=["openmeteo", "poller", "data-object"],
) as dag:
    BashOperator(
        task_id="poll_openmeteo_daily_temperature",
        bash_command=_poll_command(),
        cwd=REPO_ROOT,
        env={"PYTHONPATH": REPO_ROOT},
    )
