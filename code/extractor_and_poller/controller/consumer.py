"""Kafka consumer for ``ds.poll.data_object_change``."""

from __future__ import annotations

import logging

from extractor_and_poller.controller.events import parse_change_event
from extractor_and_poller.controller.handlers import on_data_object_change
from extractor_and_poller.poller.events import default_kafka_bootstrap
from extractor_and_poller.poller.kafka_topic import POLL_TOPIC_CHANGE

log = logging.getLogger(__name__)

CONSUMER_GROUP = "data-solution-2026-controller"


def _build_consumer(
    bootstrap_servers: str,
    group_id: str,
    *,
    consumer_timeout_ms: int,
):
    try:
        from kafka import KafkaConsumer  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "Kafka consumer requires 'kafka-python'. "
            "Install with: pip install kafka-python"
        ) from exc
    return KafkaConsumer(
        POLL_TOPIC_CHANGE,
        bootstrap_servers=bootstrap_servers,
        group_id=group_id,
        enable_auto_commit=True,
        auto_offset_reset="latest",
        consumer_timeout_ms=consumer_timeout_ms,
        value_deserializer=lambda value: value,
    )


def consume_once(
    *,
    bootstrap_servers: str | None = None,
    group_id: str = CONSUMER_GROUP,
    config_path: str | None = None,
) -> int:
    """Process at most one change event; returns number of extracts started."""
    bootstrap_servers = bootstrap_servers or default_kafka_bootstrap()
    consumer = _build_consumer(bootstrap_servers, group_id, consumer_timeout_ms=1000)
    handled = 0
    try:
        for message in consumer:
            try:
                event = parse_change_event(message.value)
            except ValueError as exc:
                log.warning("Rejected Kafka message on %s: %s", message.topic, exc)
                continue
            kwargs = {}
            if config_path is not None:
                kwargs["config_path"] = config_path
            on_data_object_change(event, **kwargs)
            handled += 1
            return handled
    finally:
        consumer.close()
    return handled


def consume_forever(
    *,
    bootstrap_servers: str | None = None,
    group_id: str = CONSUMER_GROUP,
    config_path: str | None = None,
) -> None:
    """Block and react to every valid change event."""
    bootstrap_servers = bootstrap_servers or default_kafka_bootstrap()
    consumer = _build_consumer(bootstrap_servers, group_id, consumer_timeout_ms=-1)
    log.info(
        "Controller listening topic=%s bootstrap=%s group=%s",
        POLL_TOPIC_CHANGE,
        bootstrap_servers,
        group_id,
    )
    try:
        for message in consumer:
            try:
                event = parse_change_event(message.value)
            except ValueError as exc:
                log.warning("Rejected Kafka message on %s: %s", message.topic, exc)
                continue
            kwargs = {}
            if config_path is not None:
                kwargs["config_path"] = config_path
            on_data_object_change(event, **kwargs)
    finally:
        consumer.close()
