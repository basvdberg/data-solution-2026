"""Standalone driver: extract one DWA mapping from its OData source to Parquet.

Proves the OData v4 paginator and the templated Parquet writer work end-to-end
against a real Dutch government feed, without any Kafka or Airflow involvement.

Run as a module from the ``data-solution-2026/`` directory::

    python -m Extractors.odata --list
    python -m Extractors.odata --config DataObjectMappings/odata-demo.json --mapping odata-demo-regions
    python -m Extractors.odata --mapping cbs-84583NED --limit 5000
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import date
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent               # Extractors/odata/
EXTRACTORS_ROOT = PACKAGE_DIR.parent                        # Extractors/
PROJECT_ROOT = EXTRACTORS_ROOT.parent                       # data-solution-2026/

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Extractors.common import config as cfg_module
from Extractors.odata import client as odata_module
from Extractors.common import parquet as parquet_module


def _make_defaults(config_defaults: dict[str, str]) -> dict[str, str]:
    """Promote ``default_<key>`` top-level entries to ``<key>`` for per-mapping merge."""
    out: dict[str, str] = {}
    for k, v in config_defaults.items():
        if k.startswith("default_"):
            out[k[len("default_"):]] = v
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        default=str(PROJECT_ROOT / "DataObjectMappings" / "000_Source" / "Northwind" / "regions.json"),
        help="path to the DWA-style configuration file (default: DataObjectMappings/000_Source/Northwind/regions.json)",
    )
    parser.add_argument(
        "--mapping",
        help="dataObjectMapping.id to extract (e.g. cbs-84583NED). Required unless --list.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        dest="list_mappings",
        help="list enabled mappings and exit",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=None,
        help="OData $top page size; overrides the per-mapping extension",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="cap total rows per source table (useful for smoke tests)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="enable DEBUG-level logging",
    )
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
        print(f"Mapping '{args.mapping}' not found in {args.config}.", file=sys.stderr)
        return 2
    if not mapping.enabled:
        print(f"Mapping '{args.mapping}' is disabled.", file=sys.stderr)
        return 2

    ext = mapping.extensions_dict(defaults=_make_defaults(config.defaults()))

    if "landing_path_template" not in ext:
        print(
            f"Mapping '{mapping.id}' is missing the 'landing_path_template' extension.",
            file=sys.stderr,
        )
        return 2

    page_size = args.page_size or int(ext.get("odata_page_size", "10000"))
    template = ext["landing_path_template"]
    today = date.today().isoformat()
    target_name = mapping.target_name() or mapping.id

    written: list[tuple[str, int]] = []
    for source in mapping.source_data_objects():
        base_url = source.connection_ext("base_url")
        full_url = f"{base_url.rstrip('/')}/{source.name}"
        logging.info(
            "Extracting %s (mapping=%s, page_size=%d, limit=%s)",
            full_url,
            mapping.id,
            page_size,
            args.limit,
        )
        rows = odata_module.fetch_all(
            full_url,
            page_size=page_size,
            max_rows=args.limit,
        )
        path = parquet_module.write(
            rows,
            template,
            {"dataset": target_name, "table": source.name, "date": today},
        )
        written.append((path, len(rows)))

    print(f"Extracted {len(written)} table(s) for mapping '{mapping.id}':")
    for path, n in written:
        print(f"  - {path} ({n} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
