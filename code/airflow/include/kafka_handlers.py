"""Kafka message handlers for native Airflow event-driven scheduling."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from include.kafka_topics import EVENT_TYPE_CHANGE

log = logging.getLogger(__name__)

DEFAULT_CONFIG = (
    Path(__file__).resolve().parents[3]
    / "data-object-mapping"
    / "staging"
    / "openmeteo"
    / "daily-temperature.json"
)

_REQUIRED_FIELDS = ("data_object_id", "event_type", "event_time_utc", "new_marker")


def _parse_envelope(raw_value: bytes | str | None) -> dict[str, Any]:
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
    return payload


def mapping_for_data_object(config_path: str | Path, data_object_id: str) -> str | None:
    from extractor_and_poller.common import config as cfg_module

    config = cfg_module.load(str(config_path))
    for mapping in config.enabled_mappings():
        if mapping.primary_source_data_object_id() == data_object_id:
            return mapping.id.split("/")[-1]
    return None


def poll_change_apply_function(message, *, config_path: str | None = None) -> dict[str, str] | None:
    """Return extract conf when message is a valid ``data_object_change`` event; else None."""
    config_path = config_path or str(DEFAULT_CONFIG)
    try:
        raw_value = message.value() if callable(getattr(message, "value", None)) else message.value
        payload = _parse_envelope(raw_value)
    except (ValueError, AttributeError) as exc:
        log.warning("Rejected Kafka message: %s", exc)
        return None

    event_type = str(payload["event_type"])
    if event_type != EVENT_TYPE_CHANGE:
        return None

    data_object_id = str(payload["data_object_id"])
    mapping_id = mapping_for_data_object(config_path, data_object_id)
    if mapping_id is None:
        log.warning(
            "Rejected Kafka message: no enabled mapping for data_object_id=%r",
            data_object_id,
        )
        return None

    event_id = payload.get("event_id")
    result = {
        "mapping_id": mapping_id,
        "marker": str(payload["new_marker"]),
        "data_object_id": data_object_id,
    }
    if event_id is not None:
        result["event_id"] = str(event_id)
    log.info(
        "Accepted data_object_change mapping=%s marker=%s event_id=%s",
        mapping_id,
        result["marker"],
        result.get("event_id"),
    )
    return result
