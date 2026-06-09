"""CLI: Kafka controller for poll change events.

Run from ``data-solution-2026/``::

    python -m extractor_and_poller.controller --once
    python -m extractor_and_poller.controller
"""

from __future__ import annotations

import argparse
import logging

from extractor_and_poller.common.logging_setup import configure_logging
from extractor_and_poller.common.paths import PROJECT_ROOT, ensure_project_root_on_path
from extractor_and_poller.controller import consumer
from extractor_and_poller.poller.events import default_kafka_bootstrap

ensure_project_root_on_path()

log = logging.getLogger(__name__)

DEFAULT_CONFIG = (
    PROJECT_ROOT
    / "data-object-mapping"
    / "staging"
    / "openmeteo"
    / "daily-temperature.json"
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument(
        "--once",
        action="store_true",
        help="process one message (or exit when topic is quiet) and stop",
    )
    parser.add_argument(
        "--kafka-bootstrap-servers",
        default=None,
        help="Kafka bootstrap servers, e.g. localhost:9092",
    )
    parser.add_argument(
        "--group-id",
        default=consumer.CONSUMER_GROUP,
        help="Kafka consumer group id",
    )
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args(argv)

    configure_logging(verbose=args.verbose)
    bootstrap = args.kafka_bootstrap_servers or default_kafka_bootstrap()

    if args.once:
        handled = consumer.consume_once(
            bootstrap_servers=bootstrap,
            group_id=args.group_id,
            config_path=args.config,
        )
        log.info("Controller processed %d change event(s)", handled)
        return 0

    consumer.consume_forever(
        bootstrap_servers=bootstrap,
        group_id=args.group_id,
        config_path=args.config,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
