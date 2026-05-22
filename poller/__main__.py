"""CLI: probe enabled mappings for source changes.

Run from ``data-solution-2026/``::

    python -m poller --config data-object-mapping/staging/knmi/knmi-daggegevens.json
    python -m poller --mapping knmi-daggegevens-temperature --probe-only
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_DIR.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from extractor.common import config as cfg_module
from poller import change_probe
from poller.state import FileStateStore

_DEFAULT_CONFIG = (
    PROJECT_ROOT / "data-object-mapping" / "staging" / "knmi" / "knmi-daggegevens.json"
)
_DEFAULT_STATE = PROJECT_ROOT / "data" / ".poller-state.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(_DEFAULT_CONFIG))
    parser.add_argument("--mapping", help="poll a single mapping id")
    parser.add_argument(
        "--state-file",
        default=str(_DEFAULT_STATE),
        help="JSON file for last-known markers (local stand-in for PostgreSQL)",
    )
    parser.add_argument(
        "--probe-only",
        action="store_true",
        help="fetch current marker only; do not read or update baseline",
    )
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    config = cfg_module.load(args.config)
    state = FileStateStore(args.state_file)

    mappings = config.enabled_mappings()
    if args.mapping:
        m = config.get_mapping(args.mapping)
        if m is None:
            print(f"Mapping '{args.mapping}' not found.", file=sys.stderr)
            return 2
        mappings = [m]

    exit_code = 0
    for mapping in mappings:
        if args.probe_only:
            current = change_probe.probe_current_value(mapping, config)
            print(f"{mapping.id}\tcurrent={current}")
            continue

        result = change_probe.poll_mapping(mapping, config, state)
        status = "CHANGED" if result.changed else "unchanged"
        print(
            f"{result.mapping_id}\t{status}\t"
            f"current={result.current}\tprevious={result.previous}"
        )
        if result.changed:
            exit_code = 1

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
