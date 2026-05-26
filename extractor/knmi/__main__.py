"""CLI: extract KNMI KDP daily NetCDF to Parquet.

Run from ``data-solution-2026/``::

    python -m extractor.knmi --list
    python -m extractor.knmi --mapping knmi-daggegevens-temperature
    python -m extractor.knmi --mapping knmi-daggegevens-temperature --filename daily-observations-20260521.nc
"""

from __future__ import annotations

import argparse
import logging
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
EXTRACTORS_ROOT = PACKAGE_DIR.parent
PROJECT_ROOT = EXTRACTORS_ROOT.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from extractor.common import config as cfg_module
from extractor.common import parquet as parquet_module
from extractor.knmi import client as knmi_client
from extractor.knmi import netcdf_parser


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        default=str(
            PROJECT_ROOT / "data-object-mapping" / "staging" / "knmi" / "knmi-daggegevens.json"
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
        "--filename",
        help="specific NetCDF file in the dataset (default: latest in catalog)",
    )
    parser.add_argument(
        "--local-file",
        help="skip download; parse this local .nc path (for offline dev)",
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
    base_url = source.connection_ext("base_url")

    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y-%m-%dT%H%M%S") + f"{now.microsecond // 1000:03d}Z"
    target_name = mapping.target_name() or mapping.id

    dataset_name = ext.get("kdp_dataset_name", "")
    dataset_version = ext.get("kdp_dataset_version", "1.0")
    variable = ext.get("netcdf_variable", "TG")
    if not dataset_name:
        print(f"Mapping '{mapping.id}' missing kdp_dataset_name.", file=sys.stderr)
        return 2

    api_key_env = source.connection_ext("api_key_env", "KNMI_API_KEY")
    order_by = ext.get("kdp_list_order_by", "created")
    sorting = ext.get("kdp_list_sorting", "desc")

    nc_path: Path
    catalog_filename: str
    cleanup: Path | None = None

    if args.local_file:
        nc_path = Path(args.local_file)
        catalog_filename = nc_path.name
        if not nc_path.is_file():
            print(f"Local file not found: {nc_path}", file=sys.stderr)
            return 2
    else:
        cleanup = Path(tempfile.mkdtemp(prefix="knmi-extract-"))
        if args.filename:
            catalog_filename = args.filename
            nc_path = cleanup / catalog_filename
            knmi_client.download_file(
                dataset_name,
                dataset_version,
                catalog_filename,
                str(nc_path),
                base_url=base_url,
                api_key_env=api_key_env,
            )
        else:
            catalog_filename, downloaded = knmi_client.download_latest(
                dataset_name,
                dataset_version,
                str(cleanup / "latest.nc"),
                base_url=base_url,
                api_key_env=api_key_env,
                order_by=order_by,
                sorting=sorting,
            )
            nc_path = Path(downloaded)
            catalog_filename = catalog_filename

    try:
        records = netcdf_parser.parse_daily_temperature(
            nc_path,
            variable=variable,
            source_filename=catalog_filename,
        )
        path = parquet_module.write(
            records,
            template,
            {"dataset": target_name, "table": source.name, "timestamp": timestamp},
        )
    finally:
        if cleanup is not None:
            for f in cleanup.iterdir():
                f.unlink(missing_ok=True)
            cleanup.rmdir()

    print(f"Extracted mapping '{mapping.id}' from {catalog_filename}:")
    print(f"  - {path} ({len(records):,} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
