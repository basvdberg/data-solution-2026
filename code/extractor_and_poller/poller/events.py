"""Poller event envelope and publisher abstractions."""

from __future__ import annotations

import json
import logging
import os
from dataclasses import asdict
from typing import Protocol

from extractor_and_poller.poller.change_probe import PollResult
from extractor_and_poller.poller.kafka_topic import kafka_topic_for_event

log = logging.getLogger(__name__)


class EventPublisher(Protocol):
    def publish(self, result: PollResult) -> None: ...


def event_payload(result: PollResult) -> dict[str, str | None]:
    """Full poll result for stdout debugging."""
    payload = asdict(result)
    payload["event_time_utc"] = result.event_time_utc.isoformat()
    return payload


def kafka_message_value(result: PollResult) -> str:
    """Kafka message body: data object id only."""
    return result.data_object_id


class StdoutPublisher:
    """Publisher useful for local smoke runs and debugging."""

    def publish(self, result: PollResult) -> None:
        payload = event_payload(result)
        log.info(
            "event_published transport=stdout topic=%s event_type=%s key=%s idempotency_key=%s",
            kafka_topic_for_event(result.event_type),
            result.event_type,
            result.data_object_id,
            result.idempotency_key,
        )
        print("publish\t" + json.dumps(payload, sort_keys=True))


class KafkaPublisher:
    """Kafka producer backed by ``kafka-python`` when installed."""

    def __init__(self, bootstrap_servers: str) -> None:
        self._bootstrap_servers = bootstrap_servers
        self._producer = self._build_producer(bootstrap_servers)

    @staticmethod
    def _build_producer(bootstrap_servers: str):
        try:
            from kafka import KafkaProducer  # type: ignore
        except Exception as exc:  # pragma: no cover - depends on optional dependency
            raise RuntimeError(
                "Kafka publisher requested but 'kafka-python' is not installed. "
                "Install with: pip install kafka-python"
            ) from exc
        return KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            key_serializer=lambda value: value.encode("utf-8"),
            value_serializer=lambda value: value.encode("utf-8"),
        )

    def publish(self, result: PollResult) -> None:
        value = kafka_message_value(result)
        topic = kafka_topic_for_event(result.event_type)
        future = self._producer.send(
            topic,
            key=result.data_object_id,
            value=value,
        )
        future.get(timeout=10)
        log.info(
            "event_published transport=kafka bootstrap=%s topic=%s event_type=%s data_object_id=%s",
            self._bootstrap_servers,
            topic,
            result.event_type,
            value,
        )

    def close(self) -> None:
        self._producer.flush(timeout=10)
        self._producer.close()


def default_kafka_bootstrap() -> str:
    return os.getenv("KAFKA_HOST", "localhost:9092")
