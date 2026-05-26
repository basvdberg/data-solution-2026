"""Probe any enabled data-object mapping for source changes.

Each mapping declares ``interface_type`` (via classifications) and
``change_detection_*`` extensions. Probes reuse extractor clients — no
duplicate HTTP or parsing logic.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable, Protocol

from extractor.common.config import Config, Mapping
from extractor.knmi import client as knmi_client
from extractor.odata import client as odata_client
from extractor.openmeteo import client as openmeteo_client
from extractor.wfs import client as wfs_client

log = logging.getLogger(__name__)

ProbeFn = Callable[[Mapping, Config], str]


class StateStore(Protocol):
    """Persist last-known change markers (PostgreSQL in Airflow; file for CLI)."""

    def get(self, mapping_id: str) -> str | None: ...

    def set(self, mapping_id: str, value: str) -> None: ...


@dataclass(frozen=True)
class ChangeDetectionResult:
    mapping_id: str
    object_name: str
    current: str
    previous: str | None
    changed: bool


def _merged_ext(mapping: Mapping, config: Config) -> dict[str, str]:
    return mapping.extensions_dict(config.defaults())


def _source(mapping: Mapping):
    sources = mapping.source_data_objects()
    if not sources:
        raise ValueError(f"Mapping '{mapping.id}' has no sourceDataObjects")
    return sources[0]


def _probe_odata(mapping: Mapping, config: Config) -> str:
    ext = _merged_ext(mapping, config)
    endpoint = ext.get("change_detection_endpoint")
    field = ext.get("change_detection_field")
    if not endpoint or not field:
        raise KeyError(
            f"Mapping '{mapping.id}' needs change_detection_endpoint and "
            "change_detection_field for OData"
        )
    base_url = _source(mapping).connection_ext("base_url").rstrip("/")
    url = f"{base_url}/{endpoint.lstrip('/')}"
    body = odata_client.fetch_singleton(url)
    if field not in body:
        raise KeyError(f"Field '{field}' not in OData probe response from {url}")
    return str(body[field])


def _probe_open_meteo(mapping: Mapping, config: Config) -> str:
    ext = _merged_ext(mapping, config)
    source = _source(mapping)
    base_url = source.connection_ext("base_url", openmeteo_client.DEFAULT_BASE_URL)
    return openmeteo_client.probe_change_marker(
        latitude=float(ext.get("openmeteo_probe_latitude", "52.10")),
        longitude=float(ext.get("openmeteo_probe_longitude", "5.18")),
        daily_variable=ext.get("openmeteo_daily_variable", "temperature_2m_mean"),
        past_days=int(ext.get("openmeteo_past_days", "7")),
        base_url=base_url,
        timezone=ext.get("openmeteo_timezone", "UTC"),
    )


def _probe_knmi_open_data(mapping: Mapping, config: Config) -> str:
    ext = _merged_ext(mapping, config)
    dataset = ext.get("kdp_dataset_name")
    version = ext.get("kdp_dataset_version")
    if not dataset or not version:
        raise KeyError(
            f"Mapping '{mapping.id}' needs kdp_dataset_name and kdp_dataset_version"
        )
    marker_field = ext.get("change_detection_field", "filename")
    order_by = ext.get("kdp_list_order_by", "created")
    sorting = ext.get("kdp_list_sorting", "desc")
    source = _source(mapping)
    base_url = source.connection_ext(
        "base_url", "https://api.dataplatform.knmi.nl/open-data/v1"
    )
    api_key_env = source.connection_ext("api_key_env", "KNMI_API_KEY")
    return knmi_client.probe_change_marker(
        dataset,
        version,
        marker_field=marker_field,
        base_url=base_url,
        api_key_env=api_key_env,
        order_by=order_by,
        sorting=sorting,
    )


def _probe_wfs(mapping: Mapping, config: Config) -> str:
    ext = _merged_ext(mapping, config)
    type_name = ext.get("wfs_type_name")
    if not type_name:
        raise KeyError(f"Mapping '{mapping.id}' needs wfs_type_name for WFS probe")
    probe_count = int(ext.get("change_detection_probe_count", "1"))
    base_url = _source(mapping).connection_ext("base_url")
    version = _source(mapping).connection_ext("version", "2.0.0")
    return wfs_client.probe_change_marker(
        base_url,
        type_name,
        probe_count=probe_count,
        version=version,
    )


_PROBE_BY_INTERFACE: dict[str, ProbeFn] = {
    "odata_v4": _probe_odata,
    "wfs_v2": _probe_wfs,
    "open_meteo": _probe_open_meteo,
    "knmi_open_data": _probe_knmi_open_data,
}


def probe_current_value(mapping: Mapping, config: Config) -> str:
    """Return the current change marker for one mapping (raises on unknown type)."""
    iface = mapping.get_classification_value("interface_type")
    if not iface:
        raise ValueError(
            f"Mapping '{mapping.id}' has no interface_type classification "
            "(e.g. interface_type:knmi_open_data, odata_v4, wfs_v2)"
        )
    probe = _PROBE_BY_INTERFACE.get(iface)
    if probe is None:
        supported = ", ".join(sorted(_PROBE_BY_INTERFACE))
        raise ValueError(
            f"Mapping '{mapping.id}' uses unsupported interface_type '{iface}'. "
            f"Supported: {supported}"
        )
    current = probe(mapping, config)
    log.debug("Probe %s -> %s", mapping.id, current)
    return current


def poll_mapping(
    mapping: Mapping,
    config: Config,
    state: StateStore,
) -> ChangeDetectionResult:
    """Probe one mapping and compare to stored baseline."""
    current = probe_current_value(mapping, config)
    previous = state.get(mapping.id)
    changed = previous is None or current != previous
    if changed:
        state.set(mapping.id, current)
    return ChangeDetectionResult(
        mapping_id=mapping.id,
        object_name=mapping.target_name() or mapping.id,
        current=current,
        previous=previous,
        changed=changed,
    )


def is_poll_trigger(mapping: Mapping) -> bool:
    """Mappings opted into scheduled polling / event-bus signaling."""
    return mapping.has_classification(
        "trigger:data_object_change"
    ) or mapping.has_classification("trigger:source_change")


def poll_registry(
    config: Config,
    state: StateStore,
    *,
    trigger_only: bool = True,
) -> list[ChangeDetectionResult]:
    """Poll all enabled mappings; optionally filter to poll triggers."""
    results: list[ChangeDetectionResult] = []
    for mapping in config.enabled_mappings():
        if trigger_only and not is_poll_trigger(mapping):
            log.debug("Skipping %s (no poll trigger classification)", mapping.id)
            continue
        results.append(poll_mapping(mapping, config, state))
    return results
