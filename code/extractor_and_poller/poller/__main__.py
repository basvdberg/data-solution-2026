"""CLI: poll data-object change markers and persist state in Postgres.

Run from ``data-solution-2026/`` (with ``code/`` on PYTHONPATH)::

    python -m extractor_and_poller.poller --list
    python -m extractor_and_poller.poller --data-object source/openmeteo/daily-temperature
"""

from __future__ import annotations

import argparse
import logging
import sys

from extractor_and_poller.common.paths import PROJECT_ROOT, ensure_project_root_on_path

ensure_project_root_on_path()

from extractor_and_poller.common import config as cfg_module
from extractor_and_poller.common.logging_setup import configure_logging
from extractor_and_poller.poller import change_probe
from extractor_and_poller.poller.events import (
    EventPublisher,
    KafkaPublisher,
    StdoutPublisher,
    default_kafka_bootstrap,
)
from extractor_and_poller.poller.state import PostgresStateStore, default_postgres_dsn

DEFAULT_CONFIG = (
    PROJECT_ROOT
    / "data-object-mapping"
    / "staging"
    / "openmeteo"
    / "daily-temperature.json"
)
log = logging.getLogger(__name__)


def _format_result(result: change_probe.PollResult) -> str:
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
        default=default_postgres_dsn(),
        help="Postgres DSN for poller metadata table",
    )
    parser.add_argument(
        "--publish",
        choices=("none", "stdout", "kafka"),
        default="none",
        help="publish poll events to selected transport",
    )
    parser.add_argument(
        "--kafka-bootstrap-servers",
        default=default_kafka_bootstrap(),
        help="Kafka bootstrap servers, e.g. localhost:9092",
    )
    args = parser.parse_args(argv)

    configure_logging(verbose=args.verbose)

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

    store = PostgresStateStore(args.postgres_dsn)
    publisher: EventPublisher | None = None
    previous: dict[str, str | None] = {}

    if args.publish == "stdout":
        publisher = StdoutPublisher()
    elif args.publish == "kafka":
        publisher = KafkaPublisher(args.kafka_bootstrap_servers)

    mappings = config.enabled_mappings()
    if args.mapping:
        m = config.get_mapping(args.mapping)
        mappings = [m] if m else []
    if selected_data_object_id:
        mappings = [
            m for m in mappings if m and m.primary_source_data_object_id() == selected_data_object_id
        ]
    for m in mappings:
        if m and m.enabled:
            data_object_id = m.primary_source_data_object_id()
            previous[data_object_id] = store.last_marker(data_object_id)

    any_changed = False
    try:
        if selected_data_object_id and not mappings:
            raise KeyError(f"Data object '{selected_data_object_id}' not found in {config.path}")
        if args.mapping:
            m = config.get_mapping(args.mapping)
            if m is None:
                raise KeyError(f"Mapping '{args.mapping}' not found in {config.path}")
            if not m.enabled:
                raise ValueError(f"Mapping '{args.mapping}' is disabled")

        for result in change_probe.iter_poll_results(
            config,
            data_object_id=selected_data_object_id,
            previous_markers=previous,
        ):
            log.info(_format_result(result))
            if result.changed:
                any_changed = True
            store.append(result)
            if publisher is not None:
                publisher.publish(result)
    except (KeyError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    log.info("Persisted poller rows to Postgres table poller")
    if isinstance(publisher, KafkaPublisher):
        publisher.close()
        log.info("Closed Kafka publisher")

    return 1 if any_changed else 0


if __name__ == "__main__":
    raise SystemExit(main())
