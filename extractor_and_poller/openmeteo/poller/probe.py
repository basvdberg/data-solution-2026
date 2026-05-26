"""Open-Meteo change-marker probe."""

from __future__ import annotations

from extractor_and_poller.common.config import Config, Mapping
from extractor_and_poller.common import probe_helpers as ph
from extractor_and_poller.openmeteo.extractor import client as openmeteo_client

INTERFACE_TYPE = "open_meteo"


def probe(mapping: Mapping, config: Config) -> str:
    ext = ph.merged_ext(mapping, config)
    source = ph.primary_source(mapping)
    base_url = source.connection_ext("base_url", openmeteo_client.DEFAULT_BASE_URL)
    return openmeteo_client.probe_change_marker(
        latitude=float(ext.get("openmeteo_probe_latitude", "52.10")),
        longitude=float(ext.get("openmeteo_probe_longitude", "5.18")),
        daily_variable=ext.get("openmeteo_daily_variable", "temperature_2m_mean"),
        past_days=int(ext.get("openmeteo_past_days", "7")),
        base_url=base_url,
        timezone=ext.get("openmeteo_timezone", "UTC"),
    )
