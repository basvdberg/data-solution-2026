"""Open-Meteo extract — triggered by Kafka data_object_change via Airflow Asset Watcher."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta

from airflow.exceptions import AirflowException
from airflow.providers.common.messaging.triggers.msg_queue import MessageQueueTrigger
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import Asset, AssetWatcher, DAG

from include.kafka_topics import POLL_TOPIC_CHANGE

DAG_ID = "openmeteo_daily_temperature_extract"
DEFAULT_MAPPING = "daily-temperature"
KAFKA_HOST = os.getenv("KAFKA_HOST", "kafka:9092")
KAFKA_QUEUE = f"kafka://{KAFKA_HOST}/{POLL_TOPIC_CHANGE}"

log = logging.getLogger(__name__)

poll_change_asset = Asset(
    "ds_poll_data_object_change",
    watchers=[
        AssetWatcher(
            name="poll_change_watcher",
            trigger=MessageQueueTrigger(
                queue=KAFKA_QUEUE,
                apply_function="include.kafka_handlers.poll_change_apply_function",
            ),
        )
    ],
)


def _extract_conf_from_context(context: dict) -> dict:
    """Build extractor conf from manual trigger conf or asset watcher events."""
    dag_run = context.get("dag_run")
    conf: dict = dict((dag_run.conf or {}) if dag_run else {})

    triggering = context.get("triggering_asset_events") or {}
    asset_events = triggering.get(poll_change_asset) or []
    if asset_events:
        event_payload = asset_events[-1]
        if isinstance(event_payload, dict):
            conf = {**conf, **event_payload}
        else:
            log.warning("Unexpected asset event payload type: %s", type(event_payload))

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
        "(staging.openmeteo_daily_temperature). Triggered by Kafka data_object_change "
        "events via native Airflow Asset Watcher."
    ),
    default_args=default_args,
    schedule=[poll_change_asset],
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
