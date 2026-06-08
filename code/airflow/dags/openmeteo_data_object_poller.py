"""Open-Meteo data object poller — scheduled probe and optional event publish.

DAG source lives under ``code/airflow/dags/`` in the data-solution repo.
Mounted into Airflow at ``/opt/airflow/dags``; application code at ``/opt/data-solution/code``.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.exceptions import AirflowException
from airflow.providers.standard.operators.python import PythonOperator

try:
    from airflow.sdk import Variable
except ImportError:  # pragma: no cover - Airflow 2.x
    from airflow.models import Variable  # type: ignore[no-redef]

from dag_run_guard import assert_manual_trigger_allowed_from_context
from extractor_and_poller.common.heartbeat import log_early_progress

DAG_ID = "openmeteo_data_object_poller"
DEFAULT_DATA_OBJECT_ID = "source/openmeteo/daily-temperature"
DEFAULT_PUBLISH = "none"

log = logging.getLogger(__name__)


def _variable(name: str, default: str) -> str:
    try:
        return Variable.get(name, default=default)
    except TypeError:
        return Variable.get(name, default_var=default)
    except Exception:
        return default


def _log_postgres_env(task_log: logging.Logger | None = None) -> None:
    """Log non-secret Postgres settings (inherits Airflow container env)."""
    sink = task_log or log
    sink.info(
        "Postgres env for poller: POSTGRES_HOST=%s POSTGRES_USER=%s db=%s",
        os.getenv("POSTGRES_HOST") or "<unset>",
        os.getenv("POSTGRES_USER") or "<unset>",
        os.getenv("DATA_SOLUTION_DB") or os.getenv("POSTGRES_DB") or "<unset>",
    )


def _task_logger() -> logging.Logger:
    """Task-scoped logger so the first line appears in the Airflow UI immediately."""
    try:
        from airflow.sdk import get_current_context
    except ImportError:  # pragma: no cover - Airflow 2.x
        from airflow.operators.python import get_current_context  # type: ignore[no-redef]

    return get_current_context()["ti"].log


def run_openmeteo_poller() -> None:
    """Thin wrapper: delegate to the poller CLI ``main()`` (no duplicated logic)."""
    task_log = _task_logger()
    task_log.info("Open-Meteo poller task started (pid=%s)", os.getpid())

    assert_manual_trigger_allowed_from_context()

    from extractor_and_poller.poller.__main__ import main

    argv = [
        "--data-object",
        _variable("poller_data_object_id", DEFAULT_DATA_OBJECT_ID),
        "--publish",
        _variable("poller_publish", DEFAULT_PUBLISH),
    ]
    try:
        with log_early_progress(
            task_log,
            "Open-Meteo poller task invoked",
            pending_message="Open-Meteo poller task still running",
        ):
            _log_postgres_env(task_log)
            exit_code = main(argv)
    except RuntimeError as exc:
        raise AirflowException(str(exc)) from exc
    except Exception as exc:
        if exc.__class__.__name__ == "OperationalError":
            raise AirflowException(
                "Postgres connection failed. The Airflow container must have POSTGRES_HOST "
                "(e.g. postgres:5432 on the Docker network). Do not pass a custom operator "
                f"`env` that replaces the process environment. POSTGRES_HOST="
                f"{os.getenv('POSTGRES_HOST') or '<unset>'}"
            ) from exc
        raise

    if exit_code == 2:
        raise AirflowException("poller exited with code 2 (configuration or validation error)")
    if exit_code == 3:
        raise AirflowException(
            "poller exited with code 3 (probe ran but no rows were persisted to Postgres)"
        )
    if exit_code == 1:
        task_log.info("Poller finished: data object change detected")
    else:
        task_log.info("Poller finished: no change")


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
