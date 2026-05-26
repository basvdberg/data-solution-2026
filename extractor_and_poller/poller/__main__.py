"""CLI: probe data-object change markers and update local baseline state.

Run from ``data-solution-2026/``::

    python -m extractor_and_poller.poller --probe-only --mapping openmeteo-daily-temperature
    python -m extractor_and_poller.poller --mapping openmeteo-daily-temperature
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from extractor_and_poller.common.paths import PROJECT_ROOT, ensure_project_root_on_path

ensure_project_root_on_path()

from extractor_and_poller.common import config as cfg_module
from extractor_and_poller.poller import change_probe
from extractor_and_poller.poller.state import FileStateStore

DEFAULT_CONFIG = (
    PROJECT_ROOT
    / "data-object-mapping"
    / "staging"
    / "openmeteo"
    / "openmeteo-daily-temperature.json"
)
DEFAULT_STATE = PROJECT_ROOT / "data" / ".poller-state.json"


def _state_path(arg: str) -> Path:
    path = Path(arg)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


def _format_result(result: change_probe.PollResult) -> str:
    prev = result.previous_marker if result.previous_marker is not None else "(none)"
    return (
        f"{result.event_type}\t{result.mapping_id}\t"
        f"marker={result.current_marker}\tprevious={prev}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--mapping", help="single dataObjectMapping.id (default: all enabled)")
    parser.add_argument(
        "--probe-only",
        action="store_true",
        help="print current marker only; do not read or write baseline state",
    )
    parser.add_argument(
        "--state-file",
        default=str(DEFAULT_STATE.relative_to(PROJECT_ROOT)),
        help="JSON file for last-known markers (local runs)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        dest="list_mappings",
        help="list enabled mappings in the config and exit",
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
            iface = m.get_classification_value("interface_type") or "?"
            print(f"{m.id}\t{iface}\t{m.name}")
        return 0

    store: FileStateStore | None = None
    previous: dict[str, str | None] = {}
    if not args.probe_only:
        store = FileStateStore(_state_path(args.state_file))
        mappings = config.enabled_mappings()
        if args.mapping:
            m = config.get_mapping(args.mapping)
            mappings = [m] if m else []
        for m in mappings:
            if m and m.enabled:
                previous[m.id] = store.get(m.id)

    any_changed = False
    try:
        if args.probe_only:
            mappings = config.enabled_mappings()
            if args.mapping:
                m = config.get_mapping(args.mapping)
                if m is None:
                    raise KeyError(f"Mapping '{args.mapping}' not found in {config.path}")
                if not m.enabled:
                    raise ValueError(f"Mapping '{args.mapping}' is disabled")
                mappings = [m]
            for mapping in mappings:
                marker = change_probe.probe_current_value(mapping, config)
                print(f"probe\t{mapping.id}\tmarker={marker}")
        else:
            for result in change_probe.iter_poll_results(
                config,
                mapping_id=args.mapping,
                previous_markers=previous,
            ):
                print(_format_result(result))
                if result.changed:
                    any_changed = True
                    if store is not None:
                        store.set(result.mapping_id, result.current_marker)
    except (KeyError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if store is not None:
        store.save()

    return 1 if any_changed else 0


if __name__ == "__main__":
    raise SystemExit(main())
