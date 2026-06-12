"""Kafka produce helpers for the poller DAG."""

from __future__ import annotations

from collections.abc import Iterator


def produce_poll_event(
    *,
    data_object_id: str,
    envelope_json: str,
) -> Iterator[tuple[str, str]]:
    """Yield one key/value pair for ``ProduceToTopicOperator``."""
    yield data_object_id, envelope_json
