"""Poller event envelope and stdout publisher for local debugging."""

from __future__ import annotations

import json
import logging
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


def kafka_event_payload(result: PollResult) -> dict[str, str | None]:
    """Poll event envelope for Kafka consumers (matches Postgres marker column names)."""
    return {
        "data_object_id": result.data_object_id,
        "event_type": result.event_type,
        "event_time_utc": result.event_time_utc.isoformat(),
        "old_marker": result.previous_marker,
        "new_marker": result.current_marker,
        "event_id": result.event_id,
    }


def kafka_message_value(result: PollResult) -> str:
    """Serialize the poll event envelope as JSON for Kafka message values."""
    return json.dumps(kafka_event_payload(result), sort_keys=True)


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
