"""CLI: extract Open-Meteo daily temperature to Parquet.

Run from ``data-solution-2026/``::

    python -m extractor.openmeteo --list
    python -m extractor.openmeteo --mapping openmeteo-daily-temperature
    python -m extractor.openmeteo --mapping openmeteo-daily-temperature --date 2026-05-20
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
EXTRACTORS_ROOT = PACKAGE_DIR.parent
PROJECT_ROOT = EXTRACTORS_ROOT.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from extractor.common import config as cfg_module
from extractor.common import parquet as parquet_module
from extractor.openmeteo import client as openmeteo_client


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        default=str(
            PROJECT_ROOT
            / "data-object-mapping"
            / "staging"
            / "openmeteo"
            / "openmeteo-daily-temperature.json"
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
        "--date",
        help="observation day YYYY-MM-DD (default: latest completed day from probe)",
    )
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

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

    ext = mapping.extensions_dict()
    template = ext.get("landing_path_template", "")
    if not template:
        print(f"Mapping '{mapping.id}' missing landing_path_template.", file=sys.stderr)
        return 2

    source = mapping.source_data_objects()[0]
    base_url = source.connection_ext("base_url", openmeteo_client.DEFAULT_BASE_URL)
    daily_variable = ext.get("openmeteo_daily_variable", "temperature_2m_mean")
    probe_lat = float(ext.get("openmeteo_probe_latitude", "52.10"))
    probe_lon = float(ext.get("openmeteo_probe_longitude", "5.18"))
    past_days = int(ext.get("openmeteo_past_days", "7"))
    tz = ext.get("openmeteo_timezone", "UTC")

    if args.date:
        observation_day = args.date
    else:
        observation_day = openmeteo_client.probe_change_marker(
            latitude=probe_lat,
            longitude=probe_lon,
            daily_variable=daily_variable,
            past_days=past_days,
            base_url=base_url,
            timezone=tz,
        )

    records = openmeteo_client.records_for_day(
        observation_day,
        daily_variable=daily_variable,
        base_url=base_url,
        timezone=tz,
    )

    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y-%m-%dT%H%M%S") + f"{now.microsecond // 1000:03d}Z"
    target_name = mapping.target_name() or mapping.id

    path = parquet_module.write(
        records,
        template,
        {"dataset": target_name, "table": source.name, "timestamp": timestamp},
    )
    print(f"Extracted mapping '{mapping.id}' from open-meteo {observation_day}:")
    print(f"  - {path} ({len(records):,} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
