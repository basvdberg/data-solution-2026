"""CLI: extract Open-Meteo daily temperature into Postgres staging.

Run from ``data-solution-2026/``::

    python -m extractor_and_poller.openmeteo.extractor --list
    python -m extractor_and_poller.openmeteo.extractor --mapping daily-temperature
"""

from __future__ import annotations

import argparse
import logging
import sys
from uuid import uuid4

from extractor_and_poller.common.paths import PROJECT_ROOT, ensure_project_root_on_path

ensure_project_root_on_path()

from extractor_and_poller.common import config as cfg_module
from extractor_and_poller.common.logging_setup import configure_logging
from extractor_and_poller.common.postgres_load import columns_from_data_object, reload_staging_table
from extractor_and_poller.extract.audit import ExtractRunAudit
from extractor_and_poller.openmeteo.extractor import client as openmeteo_client
from extractor_and_poller.poller.state import default_postgres_dsn

log = logging.getLogger(__name__)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        default=str(
            PROJECT_ROOT
            / "data-object-mapping"
            / "staging"
            / "openmeteo"
            / "daily-temperature.json"
        ),
    )
    parser.add_argument("--mapping", help="dataObjectMapping.id to extract")
    parser.add_argument(
        "--list",
        action="store_true",
        dest="list_mappings",
        help="list enabled mappings and exit",
    )
    parser.add_argument(
        "--marker",
        help="observation day (YYYY-MM-DD); default: probe current change marker",
    )
    parser.add_argument(
        "--event-id",
        help="poll event id for idempotency (skip if already processed)",
    )
    parser.add_argument(
        "--postgres-dsn",
        default=None,
        help="Postgres DSN for staging load and extract audit",
    )
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args(argv)

    configure_logging(verbose=args.verbose)

    if args.postgres_dsn is None:
        args.postgres_dsn = default_postgres_dsn()

    config = cfg_module.load(args.config)

    if args.list_mappings:
        for m in config.enabled_mappings():
            print(f"{m.id}\t{m.name}")
        return 0

    if not args.mapping:
        parser.error("--mapping is required (or use --list)")

    mapping = config.get_mapping(args.mapping)
    if mapping is None:
        print(f"Mapping '{args.mapping}' not found.", file=sys.stderr)
        return 2
    if not mapping.enabled:
        print(f"Mapping '{args.mapping}' is disabled.", file=sys.stderr)
        return 2

    source_data_object_id = mapping.primary_source_data_object_id()
    target_object = mapping.raw.get("targetDataObject")
    if not isinstance(target_object, dict):
        print(f"Mapping '{mapping.id}' has no resolved targetDataObject.", file=sys.stderr)
        return 2

    event_id = args.event_id or str(uuid4())
    audit = ExtractRunAudit(args.postgres_dsn)
    if audit.already_processed(event_id):
        log.info("Skipping duplicate extract for event_id=%s", event_id)
        return 0

    ext = mapping.extensions_dict()
    source = mapping.source_data_objects()[0]
    base_url = source.connection_ext("base_url", openmeteo_client.DEFAULT_BASE_URL)
    daily_variable = ext.get("openmeteo_daily_variable", "temperature_2m_mean")
    probe_lat = float(ext.get("openmeteo_probe_latitude", "52.10"))
    probe_lon = float(ext.get("openmeteo_probe_longitude", "5.18"))
    past_days = int(ext.get("openmeteo_past_days", "7"))
    tz = ext.get("openmeteo_timezone", "UTC")

    observation_day = args.marker or openmeteo_client.probe_change_marker(
        latitude=probe_lat,
        longitude=probe_lon,
        daily_variable=daily_variable,
        past_days=past_days,
        base_url=base_url,
        timezone=tz,
    )

    run_id = audit.start(
        event_id=event_id,
        mapping_id=mapping.id,
        marker=observation_day,
    )

    try:
        records = openmeteo_client.records_for_day(
            observation_day,
            daily_variable=daily_variable,
            base_url=base_url,
            timezone=tz,
        )
        log.info("Fetched %d record(s) for %s", len(records), observation_day)

        columns = columns_from_data_object(target_object)
        try:
            import psycopg  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(
                "Postgres staging load requires 'psycopg'. "
                "Install with: pip install psycopg[binary]"
            ) from exc
        with psycopg.connect(args.postgres_dsn) as conn:
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
        )
        log.info(
            "Extracted mapping '%s' from open-meteo %s into %s (%s rows)",
            mapping.id,
            observation_day,
            output_table,
            f"{row_count:,}",
        )
        return 0
    except Exception:
        audit.finish(
            run_id,
            status="failed",
            output_table="",
            row_count=0,
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
