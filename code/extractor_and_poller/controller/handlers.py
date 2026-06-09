"""Event handlers for the Kafka controller."""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from typing import Protocol

from extractor_and_poller.common import config as cfg_module
from extractor_and_poller.common.paths import PROJECT_ROOT
from extractor_and_poller.controller.airflow_trigger import trigger_extract_dag
from extractor_and_poller.controller.events import DataObjectChangeEvent

log = logging.getLogger(__name__)

DEFAULT_CONFIG = (
    PROJECT_ROOT
    / "data-object-mapping"
    / "staging"
    / "openmeteo"
    / "daily-temperature.json"
)


class ExtractStarter(Protocol):
    def start_extract(
        self,
        *,
        mapping_id: str,
        marker: str,
        event_id: str | None,
    ) -> str: ...


class AirflowExtractStarter:
    def start_extract(
        self,
        *,
        mapping_id: str,
        marker: str,
        event_id: str | None,
    ) -> str:
        return trigger_extract_dag(
            mapping_id=mapping_id,
            marker=marker,
            event_id=event_id,
        )


class DirectExtractStarter:
    """Run the extractor CLI in-process (local smoke / tests)."""

    def start_extract(
        self,
        *,
        mapping_id: str,
        marker: str,
        event_id: str | None,
    ) -> str:
        argv = [
            sys.executable,
            "-m",
            "extractor_and_poller.openmeteo.extractor",
            "--mapping",
            mapping_id,
            "--marker",
            marker,
        ]
        if event_id:
            argv.extend(["--event-id", event_id])
        log.info("Starting extractor directly argv=%s", argv)
        completed = subprocess.run(argv, check=False)
        if completed.returncode != 0:
            raise RuntimeError(f"Extractor exited with code {completed.returncode}")
        return "direct"


def mapping_for_data_object(config_path: str, data_object_id: str) -> str | None:
    config = cfg_module.load(config_path)
    for mapping in config.enabled_mappings():
        if mapping.primary_source_data_object_id() == data_object_id:
            return mapping.id.split("/")[-1]
    return None


def on_data_object_change(
    event: DataObjectChangeEvent,
    *,
    config_path: str = str(DEFAULT_CONFIG),
    starter: ExtractStarter | None = None,
) -> str:
    """Handle a ``data_object_change`` poll event (onDataItemChange trigger).

    Resolves the mapping for ``event.data_object_id`` and starts extract for
    ``event.new_marker``.
    """
    mapping_id = mapping_for_data_object(config_path, event.data_object_id)
    if mapping_id is None:
        raise ValueError(
            f"No enabled mapping found for data_object_id={event.data_object_id!r}"
        )

    mode = os.getenv("CONTROLLER_EXTRACT_MODE", "airflow").lower()
    if starter is None:
        starter = DirectExtractStarter() if mode == "direct" else AirflowExtractStarter()

    log.info(
        "on_data_object_change data_object=%s mapping=%s marker=%s event_id=%s mode=%s",
        event.data_object_id,
        mapping_id,
        event.new_marker,
        event.event_id,
        mode,
    )
    return starter.start_extract(
        mapping_id=mapping_id,
        marker=event.new_marker,
        event_id=event.event_id,
    )
