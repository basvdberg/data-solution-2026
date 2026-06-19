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
from extractor_and_poller.extract.run import run_extract
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

    try:
        outcome = run_extract(
            config_path=args.config,
            mapping_id=args.mapping,
            marker=args.marker,
            event_id=args.event_id or str(uuid4()),
            postgres_dsn=args.postgres_dsn,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if outcome is None:
        return 0

    log.info(
        "Extracted mapping '%s' marker=%s into %s (%s rows)",
        outcome.mapping_id,
        outcome.marker,
        outcome.output_table,
        f"{outcome.row_count:,}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
