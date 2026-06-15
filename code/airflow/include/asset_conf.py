"""Extract DAG conf from Airflow asset event extra metadata."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from extractor_and_poller.common.paths import PROJECT_ROOT
from extractor_and_poller.poller.poll_events import EVENT_TYPE_CHANGE

log = logging.getLogger(__name__)

DEFAULT_CONFIG = (
    PROJECT_ROOT
    / "data-object-mapping"
    / "staging"
    / "openmeteo"
    / "daily-temperature.json"
)

_REQUIRED_EXTRA_FIELDS = ("data_object_id", "marker")


def mapping_for_data_object(config_path: str | Path, data_object_id: str) -> str | None:
    from extractor_and_poller.common import config as cfg_module

    config = cfg_module.load(str(config_path))
    for mapping in config.enabled_mappings():
        if mapping.primary_source_data_object_id() == data_object_id:
            return mapping.id.split("/")[-1]
    return None


def extract_conf_from_asset_extra(
    extra: dict[str, Any] | None,
    *,
    config_path: str | None = None,
) -> dict[str, str] | None:
    """Return extract conf when asset extra is a valid change signal; else None."""
    config_path = config_path or str(DEFAULT_CONFIG)
    if not extra:
        log.warning("Rejected asset event: extra is empty")
        return None

    missing = [field for field in _REQUIRED_EXTRA_FIELDS if field not in extra]
    if missing:
        log.warning(
            "Rejected asset event: extra missing required field(s): %s",
            ", ".join(missing),
        )
        return None

    event_type = str(extra.get("event_type", EVENT_TYPE_CHANGE))
    if event_type != EVENT_TYPE_CHANGE:
        return None

    data_object_id = str(extra["data_object_id"])
    mapping_id = extra.get("mapping_id")
    if mapping_id is None:
        mapping_id = mapping_for_data_object(config_path, data_object_id)
    if mapping_id is None:
        log.warning(
            "Rejected asset event: no enabled mapping for data_object_id=%r",
            data_object_id,
        )
        return None

    result: dict[str, str] = {
        "mapping_id": str(mapping_id),
        "marker": str(extra["marker"]),
        "data_object_id": data_object_id,
    }
    event_id = extra.get("event_id")
    if event_id is not None:
        result["event_id"] = str(event_id)
    log.info(
        "Accepted data_object_change mapping=%s marker=%s event_id=%s",
        result["mapping_id"],
        result["marker"],
        result.get("event_id"),
    )
    return result
