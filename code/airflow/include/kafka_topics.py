"""Kafka topic names for orchestration events."""

from __future__ import annotations

SCOPE = "ds"

POLL_TOPIC_CHANGE = f"{SCOPE}.poll.data_object_change"
POLL_TOPIC_PROGRESS = f"{SCOPE}.poll.data_object_progress"

EVENT_TYPE_CHANGE = "data_object_change"
EVENT_TYPE_PROGRESS = "data_object_progress"

_EVENT_TYPE_TO_TOPIC: dict[str, str] = {
    EVENT_TYPE_CHANGE: POLL_TOPIC_CHANGE,
    EVENT_TYPE_PROGRESS: POLL_TOPIC_PROGRESS,
}


def kafka_topic_for_event(event_type: str) -> str:
    """Map a poll ``event_type`` to its Kafka topic name."""
    try:
        return _EVENT_TYPE_TO_TOPIC[event_type]
    except KeyError as exc:
        raise ValueError(f"Unknown event_type for Kafka topic: {event_type!r}") from exc
