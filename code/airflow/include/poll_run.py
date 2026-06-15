"""Single poll run for Airflow poller DAG tasks."""

from __future__ import annotations

import logging

from extractor_and_poller.common import config as cfg_module
from extractor_and_poller.poller import change_probe
from extractor_and_poller.poller.state import PostgresStateStore, default_postgres_dsn
from include.asset_conf import mapping_for_data_object

log = logging.getLogger(__name__)


def probe_and_persist(
    *,
    config_path: str,
    data_object_id: str,
    postgres_dsn: str | None = None,
) -> dict[str, str]:
    """Probe one data object, persist to Postgres, return probe metadata for downstream tasks."""
    postgres_dsn = postgres_dsn or default_postgres_dsn()
    config = cfg_module.load(config_path)
    mappings = [
        m
        for m in config.enabled_mappings()
        if m.enabled and m.primary_source_data_object_id() == data_object_id
    ]
    if not mappings:
        raise ValueError(f"Data object '{data_object_id}' not found in {config.path}")

    store = PostgresStateStore(postgres_dsn)
    previous = {data_object_id: store.last_marker(data_object_id)}
    log.info(
        "Probe starting data_object=%s previous_marker=%s",
        data_object_id,
        previous[data_object_id] if previous[data_object_id] is not None else "(none)",
    )

    result = None
    for poll_result in change_probe.iter_poll_results(
        config,
        data_object_id=data_object_id,
        previous_markers=previous,
    ):
        row_id = store.append(poll_result)
        log.info(
            "Persisted poller row id=%s event_type=%s marker=%s",
            row_id,
            poll_result.event_type,
            poll_result.current_marker,
        )
        result = poll_result
        break

    if result is None:
        raise RuntimeError("Poller probe completed but no rows were persisted to Postgres")

    mapping_id = mapping_for_data_object(config_path, data_object_id) or ""
    return {
        "data_object_id": result.data_object_id,
        "event_type": result.event_type,
        "event_id": result.event_id,
        "new_marker": result.current_marker,
        "mapping_id": mapping_id,
    }
