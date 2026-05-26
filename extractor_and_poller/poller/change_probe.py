"""Dispatch change-marker probes by ``interface_type`` classification."""

from __future__ import annotations

import logging
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from datetime import datetime, timezone
from importlib import import_module

from extractor_and_poller.common.config import Config, Mapping

log = logging.getLogger(__name__)

ProbeFn = Callable[[Mapping, Config], str]

_PROBE_MODULES: tuple[str, ...] = (
    "extractor_and_poller.openmeteo.poller.probe",
    "extractor_and_poller.knmi.poller.probe",
    "extractor_and_poller.odata.poller.probe",
    "extractor_and_poller.wfs.poller.probe",
)


@dataclass(frozen=True)
class PollResult:
    mapping_id: str
    data_object_name: str
    current_marker: str
    previous_marker: str | None
    changed: bool
    polled_at_utc: datetime
    event_type: str

    @property
    def unchanged(self) -> bool:
        return not self.changed


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
    if not value:
        raise ValueError(
            f"Mapping '{mapping.id}' has no interface_type classification"
        )
    return value


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
    previous_marker: str | None = None,
) -> PollResult:
    current = probe_current_value(mapping, config)
    changed = previous_marker != current
    event_type = "data_object_change" if changed else "data_object_progress"
    target = mapping.target_name() or mapping.id
    log.info(
        "%s mapping=%s marker=%s previous=%s",
        event_type,
        mapping.id,
        current,
        previous_marker,
    )
    return PollResult(
        mapping_id=mapping.id,
        data_object_name=target,
        current_marker=current,
        previous_marker=previous_marker,
        changed=changed,
        polled_at_utc=datetime.now(timezone.utc),
        event_type=event_type,
    )


def iter_poll_results(
    config: Config,
    *,
    mapping_id: str | None = None,
    previous_markers: dict[str, str | None] | None = None,
) -> Iterator[PollResult]:
    markers = previous_markers or {}
    mappings = config.enabled_mappings()
    if mapping_id:
        mapping = config.get_mapping(mapping_id)
        if mapping is None:
            raise KeyError(f"Mapping '{mapping_id}' not found in {config.path}")
        if not mapping.enabled:
            raise ValueError(f"Mapping '{mapping_id}' is disabled")
        mappings = [mapping]
    for mapping in mappings:
        yield poll_mapping(
            mapping,
            config,
            previous_marker=markers.get(mapping.id),
        )
