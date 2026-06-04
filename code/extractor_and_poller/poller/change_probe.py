"""Dispatch change-marker probes by ``interface_type`` classification."""

from __future__ import annotations

import logging
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from datetime import datetime, timezone
from importlib import import_module
from uuid import uuid4

from extractor_and_poller.common.config import Config, Mapping

log = logging.getLogger(__name__)

ProbeFn = Callable[[Mapping, Config], str]

_PROBE_MODULES: tuple[str, ...] = (
    "extractor_and_poller.openmeteo.poller.probe",
)


@dataclass(frozen=True)
class PollResult:
    event_id: str
    run_id: str
    data_object_id: str
    source_data_object_id: str
    target_data_object_id: str
    current_marker: str
    previous_marker: str | None
    event_time_utc: datetime
    event_type: str

    @property
    def changed(self) -> bool:
        return self.event_type == "data_object_change"

    @property
    def idempotency_key(self) -> str:
        return f"{self.data_object_id}:{self.current_marker}"


def _probe_registry() -> dict[str, ProbeFn]:
    registry: dict[str, ProbeFn] = {}
    for module_path in _PROBE_MODULES:
        mod = import_module(module_path)
        registry[mod.INTERFACE_TYPE] = mod.probe
    return registry


_REGISTRY: dict[str, ProbeFn] | None = None


def probe_registry() -> dict[str, ProbeFn]:
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = _probe_registry()
    return _REGISTRY


def interface_type_for(mapping: Mapping) -> str:
    value = mapping.get_classification_value("interface_type")
    if value:
        return value
    # Fallback for current metadata where protocol is defined on source connection.
    sources = mapping.source_data_objects()
    if sources:
        protocol = sources[0].connection_ext("protocol", "")
        if protocol:
            return protocol.lower()
    raise ValueError(f"Mapping '{mapping.id}' has no interface_type classification")


def probe_current_value(mapping: Mapping, config: Config) -> str:
    interface = interface_type_for(mapping)
    probe_fn = probe_registry().get(interface)
    if probe_fn is None:
        known = ", ".join(sorted(probe_registry()))
        raise ValueError(
            f"No poller probe for interface_type '{interface}' on mapping "
            f"'{mapping.id}' (known: {known})"
        )
    return probe_fn(mapping, config)


def poll_mapping(
    mapping: Mapping,
    config: Config,
    *,
    run_id: str,
    previous_marker: str | None = None,
) -> PollResult:
    current = probe_current_value(mapping, config)
    changed = previous_marker != current
    event_type = "data_object_change" if changed else "data_object_unchanged"
    source_id = mapping.primary_source_data_object_id()
    target_id = mapping.target_data_object_id() or mapping.id
    log.info(
        "%s data_object=%s marker=%s previous=%s",
        event_type,
        source_id,
        current,
        previous_marker,
    )
    return PollResult(
        event_id=str(uuid4()),
        run_id=run_id,
        data_object_id=source_id,
        source_data_object_id=source_id,
        target_data_object_id=target_id,
        current_marker=current,
        previous_marker=previous_marker,
        event_time_utc=datetime.now(timezone.utc),
        event_type=event_type,
    )


def iter_poll_results(
    config: Config,
    *,
    data_object_id: str | None = None,
    previous_markers: dict[str, str | None] | None = None,
) -> Iterator[PollResult]:
    run_id = str(uuid4())
    markers = previous_markers or {}
    mappings = config.enabled_mappings()
    if data_object_id:
        filtered = [
            mapping
            for mapping in mappings
            if mapping.primary_source_data_object_id() == data_object_id
        ]
        if not filtered:
            raise KeyError(f"Data object '{data_object_id}' not found in enabled mappings of {config.path}")
        mappings = filtered
    for mapping in mappings:
        data_object_id = mapping.primary_source_data_object_id()
        yield poll_mapping(
            mapping,
            config,
            run_id=run_id,
            previous_marker=markers.get(data_object_id),
        )
