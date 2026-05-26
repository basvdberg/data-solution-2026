"""Shared helpers for protocol poller probes."""

from __future__ import annotations

from extractor_and_poller.common.config import Config, Mapping


def merged_ext(mapping: Mapping, config: Config) -> dict[str, str]:
    return mapping.extensions_dict(config.defaults())


def primary_source(mapping: Mapping):
    sources = mapping.source_data_objects()
    if not sources:
        raise ValueError(f"Mapping '{mapping.id}' has no sourceDataObjects")
    return sources[0]
