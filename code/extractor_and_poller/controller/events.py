"""Validate poll change events consumed from Kafka."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from extractor_and_poller.poller.kafka_topic import EVENT_TYPE_CHANGE


@dataclass(frozen=True)
class DataObjectChangeEvent:
    data_object_id: str
    event_type: str
    event_time_utc: str
    old_marker: str | None
    new_marker: str
    event_id: str | None = None


_REQUIRED_FIELDS = ("data_object_id", "event_type", "event_time_utc", "new_marker")


def parse_change_event(raw_value: bytes | str | None) -> DataObjectChangeEvent:
    if raw_value is None:
        raise ValueError("Kafka message value is empty")
    if isinstance(raw_value, bytes):
        raw_value = raw_value.decode("utf-8")
    try:
        payload: dict[str, Any] = json.loads(raw_value)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Kafka message value is not valid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("Kafka message value must be a JSON object")

    missing = [field for field in _REQUIRED_FIELDS if field not in payload]
    if missing:
        raise ValueError(f"Poll envelope missing required field(s): {', '.join(missing)}")

    event_type = str(payload["event_type"])
    if event_type != EVENT_TYPE_CHANGE:
        raise ValueError(f"Expected event_type {EVENT_TYPE_CHANGE!r}, got {event_type!r}")

    old_marker = payload.get("old_marker")
    if old_marker is not None:
        old_marker = str(old_marker)

    event_id = payload.get("event_id")
    if event_id is not None:
        event_id = str(event_id)

    return DataObjectChangeEvent(
        data_object_id=str(payload["data_object_id"]),
        event_type=event_type,
        event_time_utc=str(payload["event_time_utc"]),
        old_marker=old_marker,
        new_marker=str(payload["new_marker"]),
        event_id=event_id,
    )
