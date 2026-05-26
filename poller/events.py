"""Poller outcomes as event-bus messages (local CLI and Kafka producers)."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone

from poller.change_probe import ChangeDetectionResult

EVENT_DATA_OBJECT_CHANGE = "data_object_change"
EVENT_DATA_OBJECT_PROGRESS = "data_object_progress"


@dataclass(frozen=True)
class PollerEvent:
    """One poll outcome for orchestration.events."""

    event_type: str
    mapping_id: str
    data_object_name: str
    current_marker: str
    previous_marker: str | None
    polled_at_utc: str

    @property
    def changed(self) -> bool:
        return self.event_type == EVENT_DATA_OBJECT_CHANGE


def from_poll_result(result: ChangeDetectionResult) -> PollerEvent:
    event_type = (
        EVENT_DATA_OBJECT_CHANGE if result.changed else EVENT_DATA_OBJECT_PROGRESS
    )
    return PollerEvent(
        event_type=event_type,
        mapping_id=result.mapping_id,
        data_object_name=result.object_name,
        current_marker=result.current,
        previous_marker=result.previous,
        polled_at_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )


def format_cli_line(event: PollerEvent) -> str:
    prev = event.previous_marker if event.previous_marker is not None else ""
    return (
        f"{event.event_type}\t{event.mapping_id}\t"
        f"current={event.current_marker}\tprevious={prev}"
    )


def to_bus_payload(event: PollerEvent) -> dict[str, str | None]:
    """Kafka-ready dict (orchestration.events envelope fields)."""
    return asdict(event)
