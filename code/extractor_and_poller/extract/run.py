"""Extract execution with audit and orchestration outcome metadata."""

from __future__ import annotations

import logging
import sys
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from extractor_and_poller.common import config as cfg_module
from extractor_and_poller.common.postgres_load import columns_from_data_object, reload_staging_table
from extractor_and_poller.extract.audit import ExtractRunAudit
from extractor_and_poller.openmeteo.extractor import client as openmeteo_client
from extractor_and_poller.poller.poll_events import (
    CHANGE_SCOPE_FULL_REWRITE,
    EVENT_TYPE_CHANGE,
    EVENT_TYPE_PROCESSING_ERROR,
)

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class ExtractOutcome:
    event_type: str
    data_object_id: str
    marker: str
    event_id: str
    mapping_id: str
    change_scope: str | None
    output_table: str
    row_count: int

    def as_dict(self) -> dict[str, str]:
        payload: dict[str, str] = {
            "event_type": self.event_type,
            "data_object_id": self.data_object_id,
            "marker": self.marker,
            "event_id": self.event_id,
            "mapping_id": self.mapping_id,
            "output_table": self.output_table,
            "row_count": str(self.row_count),
        }
        if self.change_scope is not None:
            payload["change_scope"] = self.change_scope
        return payload


def _mapping_slug(mapping_id: str) -> str:
    return mapping_id.split("/")[-1]


def run_extract(
    *,
    config_path: str,
    mapping_id: str,
    marker: str | None = None,
    event_id: str | None = None,
    postgres_dsn: str,
) -> ExtractOutcome | None:
    """Run one extract for *mapping_id* and return orchestration outcome metadata."""
    config = cfg_module.load(config_path)
    mapping = config.get_mapping(mapping_id)
    if mapping is None:
        raise ValueError(f"Mapping '{mapping_id}' not found.")
    if not mapping.enabled:
        raise ValueError(f"Mapping '{mapping_id}' is disabled.")

    target_object = mapping.raw.get("targetDataObject")
    if not isinstance(target_object, dict):
        raise ValueError(f"Mapping '{mapping.id}' has no resolved targetDataObject.")

    source_data_object_id = mapping.primary_source_data_object_id()
    target_data_object_id = mapping.target_data_object_id()
    resolved_event_id = event_id or str(uuid4())
    audit = ExtractRunAudit(postgres_dsn)
    if audit.already_processed(resolved_event_id):
        log.info(
            "Skipping duplicate extract for event_id=%s mapping=%s",
            resolved_event_id,
            _mapping_slug(mapping.id),
        )
        return None

    ext = mapping.extensions_dict()
    source = mapping.source_data_objects()[0]
    base_url = source.connection_ext("base_url", openmeteo_client.DEFAULT_BASE_URL)
    daily_variable = ext.get("openmeteo_daily_variable", "temperature_2m_mean")
    probe_lat = float(ext.get("openmeteo_probe_latitude", "52.10"))
    probe_lon = float(ext.get("openmeteo_probe_longitude", "5.18"))
    past_days = int(ext.get("openmeteo_past_days", "7"))
    tz = ext.get("openmeteo_timezone", "UTC")

    observation_day = marker or openmeteo_client.probe_change_marker(
        latitude=probe_lat,
        longitude=probe_lon,
        daily_variable=daily_variable,
        past_days=past_days,
        base_url=base_url,
        timezone=tz,
    )

    run_id = audit.start(
        event_id=resolved_event_id,
        mapping_id=mapping.id,
        data_object_id=target_data_object_id,
        marker=observation_day,
        change_scope=CHANGE_SCOPE_FULL_REWRITE,
    )

    try:
        records = openmeteo_client.records_for_day(
            observation_day,
            daily_variable=daily_variable,
            base_url=base_url,
            timezone=tz,
        )
        log.info("Fetched %d record(s) for marker=%s", len(records), observation_day)

        columns = columns_from_data_object(target_object)
        try:
            import psycopg  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(
                "Postgres staging load requires 'psycopg'. "
                "Install with: pip install psycopg[binary]"
            ) from exc
        with psycopg.connect(postgres_dsn) as conn:
            output_table, row_count = reload_staging_table(
                conn,
                source_data_object_id=source_data_object_id,
                columns=columns,
                records=records,
            )

        audit.finish(
            run_id,
            status="success",
            output_table=output_table,
            row_count=row_count,
            event_type=EVENT_TYPE_CHANGE,
        )
        outcome = ExtractOutcome(
            event_type=EVENT_TYPE_CHANGE,
            data_object_id=target_data_object_id,
            marker=observation_day,
            event_id=resolved_event_id,
            mapping_id=_mapping_slug(mapping.id),
            change_scope=CHANGE_SCOPE_FULL_REWRITE,
            output_table=output_table,
            row_count=row_count,
        )
        log.info(
            "Event: %s data_object=%s marker=%s event_id=%s rows=%d table=%s",
            outcome.event_type,
            outcome.data_object_id,
            outcome.marker,
            outcome.event_id,
            outcome.row_count,
            outcome.output_table,
        )
        return outcome
    except Exception:
        audit.finish(
            run_id,
            status="failed",
            output_table="",
            row_count=0,
            event_type=EVENT_TYPE_PROCESSING_ERROR,
        )
        log.error(
            "Event: %s data_object=%s marker=%s event_id=%s mapping=%s",
            EVENT_TYPE_PROCESSING_ERROR,
            target_data_object_id,
            observation_day,
            resolved_event_id,
            _mapping_slug(mapping.id),
            exc_info=True,
        )
        raise


def run_extract_argv(argv: list[str]) -> dict[str, Any]:
    """Parse CLI-style *argv* and return outcome dict for orchestration consumers."""
    from extractor_and_poller.common.paths import PROJECT_ROOT
    from extractor_and_poller.poller.state import default_postgres_dsn

    import argparse

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--config", default=str(
        PROJECT_ROOT / "data-object-mapping" / "staging" / "openmeteo" / "daily-temperature.json"
    ))
    parser.add_argument("--mapping", required=True)
    parser.add_argument("--marker")
    parser.add_argument("--event-id")
    parser.add_argument("--postgres-dsn", default=None)
    args = parser.parse_args(argv)

    postgres_dsn = args.postgres_dsn or default_postgres_dsn()
    try:
        outcome = run_extract(
            config_path=args.config,
            mapping_id=args.mapping,
            marker=args.marker,
            event_id=args.event_id,
            postgres_dsn=postgres_dsn,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2) from exc
    if outcome is None:
        return {"skipped": "true", "event_id": args.event_id or ""}
    return outcome.as_dict()
