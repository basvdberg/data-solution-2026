"""Open-Meteo data object poller — scheduled probe and Kafka publish via Airflow provider."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta
from pathlib import Path

from airflow.exceptions import AirflowException
from airflow.providers.apache.kafka.operators.produce import ProduceToTopicOperator
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG, Variable

DAG_ID = "openmeteo_data_object_poller"
DEFAULT_DATA_OBJECT_ID = "source/openmeteo/daily-temperature"
DEFAULT_CONFIG = (
    Path(__file__).resolve().parents[3]
    / "data-object-mapping"
    / "staging"
    / "openmeteo"
    / "daily-temperature.json"
)

log = logging.getLogger(__name__)


def run_probe_and_persist() -> dict[str, str]:
    """Probe source marker, persist to Postgres, return Kafka publish metadata for XCom."""
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
        "publish events to Kafka via ProduceToTopicOperator."
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

    publish_task = ProduceToTopicOperator(
        task_id="publish_poll_event",
        kafka_config_id="kafka_default",
        topic="{{ ti.xcom_pull(task_ids='probe_and_persist')['topic'] }}",
        producer_function="include.poller_kafka.produce_poll_event",
        producer_function_kwargs={
            "data_object_id": "{{ ti.xcom_pull(task_ids='probe_and_persist')['data_object_id'] }}",
            "envelope_json": "{{ ti.xcom_pull(task_ids='probe_and_persist')['envelope_json'] }}",
        },
    )

    probe_task >> publish_task
