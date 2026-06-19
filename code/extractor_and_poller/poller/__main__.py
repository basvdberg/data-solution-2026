"""CLI: poll data-object change markers and persist state in Postgres.

Run from ``data-solution-2026/`` (with ``code/`` on PYTHONPATH)::

    python -m extractor_and_poller.poller --list
    python -m extractor_and_poller.poller --data-object source/openmeteo/daily-temperature
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import argparse
import logging
import os
import sys

from extractor_and_poller.common.paths import PROJECT_ROOT, ensure_project_root_on_path

ensure_project_root_on_path()

from extractor_and_poller.common.heartbeat import log_early_progress
from extractor_and_poller.common.logging_setup import configure_logging

DEFAULT_CONFIG = (
    PROJECT_ROOT
    / "data-object-mapping"
    / "staging"
    / "openmeteo"
    / "daily-temperature.json"
)
log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from extractor_and_poller.poller.change_probe import PollResult


def _format_result(result: PollResult) -> str:
    prev = result.previous_marker if result.previous_marker is not None else "(none)"
    return (
        f"{result.event_type}\t{result.data_object_id}\t"
        f"new={result.current_marker}\told={prev}\trun_id={result.run_id}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument(
        "--data-object",
        help="single source data object id (default: all enabled in config)",
    )
    parser.add_argument(
        "--mapping",
        help="deprecated: mapping selector kept for backwards compatibility",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        dest="list_mappings",
        help="list enabled data object poller entries and exit",
    )
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument(
        "--postgres-dsn",
        default=None,
        help="Postgres DSN for poller metadata table",
    )
    parser.add_argument(
        "--publish",
        choices=("none", "stdout"),
        default="none",
        help="publish poll events to stdout for local debugging (production uses Airflow Assets)",
    )
    args = parser.parse_args(argv)

    configure_logging(verbose=args.verbose)
    log.info(
        "Poller CLI started pid=%s data_object=%s publish=%s config=%s",
        os.getpid(),
        args.data_object or "(all enabled)",
        args.publish,
        args.config,
    )

    from extractor_and_poller.common import config as cfg_module
    from extractor_and_poller.poller import change_probe
    from extractor_and_poller.poller.events import EventPublisher, StdoutPublisher
    from extractor_and_poller.poller.state import PostgresStateStore, default_postgres_dsn

    if args.postgres_dsn is None:
        args.postgres_dsn = default_postgres_dsn()

    log.info("Loading poller config from %s", args.config)
    config = cfg_module.load(args.config)
    selected_data_object_id: str | None = args.data_object
    if selected_data_object_id is None and args.mapping:
        mapping_for_arg = config.get_mapping(args.mapping)
        if mapping_for_arg is None:
            print(f"Mapping '{args.mapping}' not found in {config.path}", file=sys.stderr)
            return 2
        selected_data_object_id = mapping_for_arg.primary_source_data_object_id()

    if args.list_mappings:
        for m in config.enabled_mappings():
            iface = m.get_classification_value("interface_type") or "?"
            print(f"{m.id}\t{iface}\t{m.name}")
        return 0

    with log_early_progress(
        log,
        None,
        pending_message="Poller run still in progress",
    ):
        store = PostgresStateStore(args.postgres_dsn)
        publisher: EventPublisher | None = None
        previous: dict[str, str | None] = {}

        if args.publish == "stdout":
            publisher = StdoutPublisher()

        mappings = config.enabled_mappings()
        if args.mapping:
            m = config.get_mapping(args.mapping)
            mappings = [m] if m else []
        if selected_data_object_id:
            mappings = [
                m
                for m in mappings
                if m and m.primary_source_data_object_id() == selected_data_object_id
            ]
        for m in mappings:
            if m and m.enabled:
                data_object_id = m.primary_source_data_object_id()
                log.info("Loading previous marker for %s", data_object_id)
                previous[data_object_id] = store.last_marker(data_object_id)
                log.info(
                    "Previous marker for %s: %s",
                    data_object_id,
                    previous[data_object_id] if previous[data_object_id] is not None else "(none)",
                )

        any_changed = False
        rows_persisted = 0
        probes_expected = sum(1 for m in mappings if m and m.enabled)
        try:
            if selected_data_object_id and not mappings:
                raise KeyError(f"Data object '{selected_data_object_id}' not found in {config.path}")
            if args.mapping:
                m = config.get_mapping(args.mapping)
                if m is None:
                    raise KeyError(f"Mapping '{args.mapping}' not found in {config.path}")
                if not m.enabled:
                    raise ValueError(f"Mapping '{args.mapping}' is disabled")

            log.info("Starting change probe run")
            for result in change_probe.iter_poll_results(
                config,
                data_object_id=selected_data_object_id,
                previous_markers=previous,
            ):
                log.info(_format_result(result))
                if result.changed:
                    any_changed = True
                row_id = store.append(result)
                rows_persisted += 1
                log.info(
                    "Persisted poller row id=%s for data_object=%s",
                    row_id,
                    result.data_object_id,
                )
                if publisher is not None:
                    publisher.publish(result)
        except (KeyError, ValueError) as exc:
            print(str(exc), file=sys.stderr)
            return 2

        if probes_expected > 0 and rows_persisted == 0:
            print(
                "Poller probe completed but no rows were persisted to Postgres",
                file=sys.stderr,
            )
            return 3
        if rows_persisted > 0:
            log.info(
                "Persisted %d poller row(s) to Postgres table public.poller",
                rows_persisted,
            )
        return 1 if any_changed else 0


if __name__ == "__main__":
    configure_logging()
    log.info("Poller process bootstrapping")
    raise SystemExit(main())
