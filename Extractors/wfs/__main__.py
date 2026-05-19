"""Standalone driver: extract a WFS mapping to Parquet.

Fetches features via OGC WFS 2.0, parses the GML response into flat records,
and writes Parquet files using the shared Parquet writer.

Run as a module from the ``data-solution-2026/`` directory::

    python -m Extractors.wfs --list
    python -m Extractors.wfs --mapping knmi-daggegevens-temperature --info
    python -m Extractors.wfs --mapping knmi-daggegevens-temperature --page-size 2 --max-features 4 --limit 500
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PACKAGE_DIR = Path(__file__).resolve().parent               # Extractors/wfs/
EXTRACTORS_ROOT = PACKAGE_DIR.parent                        # Extractors/
PROJECT_ROOT = EXTRACTORS_ROOT.parent                       # data-solution-2026/

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Extractors.common import config as cfg_module
from Extractors.common import parquet as parquet_module
from Extractors.wfs import client as wfs_client
from Extractors.wfs import gml_parser


_PARSERS = {
    "timeseries_observations": gml_parser.parse_timeseries_observations,
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        default=str(PROJECT_ROOT / "DataObjectMappings" / "000_Source" / "KNMI" / "knmi-daggegevens.json"),
        help="path to the DWA-style configuration file",
    )
    parser.add_argument("--mapping", help="dataObjectMapping.id to extract")
    parser.add_argument("--list", action="store_true", dest="list_mappings",
                        help="list enabled mappings and exit")
    parser.add_argument("--info", action="store_true",
                        help="print WFS GetCapabilities summary and exit")
    parser.add_argument("--page-size", type=int, default=None,
                        help="features per WFS page (startIndex pagination); "
                             "overrides the wfs_page_size extension")
    parser.add_argument("--max-features", type=int, default=None,
                        help="cap total WFS features (stations) to fetch across all pages")
    parser.add_argument("--limit", type=int, default=None,
                        help="cap total parsed records (time-value pairs) per source table")
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
        print(f"Mapping '{args.mapping}' not found in {args.config}.", file=sys.stderr)
        return 2
    if not mapping.enabled:
        print(f"Mapping '{args.mapping}' is disabled.", file=sys.stderr)
        return 2

    ext = mapping.extensions_dict()

    if args.info:
        source = mapping.source_data_objects()[0]
        base_url = source.connection_ext("base_url")
        caps = wfs_client.get_capabilities(base_url)
        print(f"Title:    {caps.title}")
        print(f"Provider: {caps.provider}")
        print(f"Version:  {caps.version}")
        print(f"Paging:   {caps.supports_paging}")
        print(f"CountDefault: {caps.count_default}")
        print(f"Feature types ({len(caps.feature_types)}):")
        for ft in caps.feature_types:
            print(f"  - {ft.name} ({ft.title})")
            print(f"    CRS: {ft.default_crs}")
            if ft.bbox_lower and ft.bbox_upper:
                print(f"    BBOX: {ft.bbox_lower} -> {ft.bbox_upper}")
            print(f"    Formats: {', '.join(ft.formats)}")
        return 0

    parser_key = ext.get("gml_parser", "")
    parse_fn = _PARSERS.get(parser_key)
    if parse_fn is None:
        print(
            f"Unknown gml_parser '{parser_key}'. Available: {list(_PARSERS.keys())}",
            file=sys.stderr,
        )
        return 2

    template = ext.get("landing_path_template", "")
    if not template:
        print(f"Mapping '{mapping.id}' missing 'landing_path_template'.", file=sys.stderr)
        return 2

    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y-%m-%dT%H%M%S") + f"{now.microsecond // 1000:03d}Z"
    target_name = mapping.target_name() or mapping.id
    page_size = args.page_size or int(ext.get("wfs_page_size", ext.get("wfs_count", "10")))
    max_features = args.max_features

    written: list[tuple[str, int]] = []
    for source in mapping.source_data_objects():
        base_url = source.connection_ext("base_url")
        type_name = ext.get("wfs_type_name", source.name)

        logging.info(
            "Fetching %s from %s (page_size=%d, max_features=%s)",
            type_name, base_url, page_size, max_features,
        )

        records: list[dict[str, Any]] = []
        for gml_bytes in wfs_client.iter_gml_pages(
            base_url,
            type_name,
            page_size=page_size,
            max_features=max_features,
        ):
            rows_left = None
            if args.limit is not None:
                rows_left = args.limit - len(records)
                if rows_left <= 0:
                    break
            logging.info("Parsing GML page (%d bytes) with %s ...", len(gml_bytes), parser_key)
            records.extend(parse_fn(gml_bytes, max_rows=rows_left))

        if args.limit is not None:
            records = records[: args.limit]

        path = parquet_module.write(
            records,
            template,
            {"dataset": target_name, "table": source.name, "timestamp": timestamp},
        )
        written.append((path, len(records)))

    print(f"Extracted {len(written)} table(s) for mapping '{mapping.id}':")
    for path, n in written:
        print(f"  - {path} ({n:,} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
