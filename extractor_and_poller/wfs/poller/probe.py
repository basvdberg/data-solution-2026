"""WFS 2.0 change-marker probe."""

from __future__ import annotations

from extractor_and_poller.common.config import Config, Mapping
from extractor_and_poller.common import probe_helpers as ph
from extractor_and_poller.wfs.extractor import client as wfs_client

INTERFACE_TYPE = "wfs_v2"


def probe(mapping: Mapping, config: Config) -> str:
    ext = ph.merged_ext(mapping, config)
    type_name = ext.get("wfs_type_name")
    if not type_name:
        raise KeyError(f"Mapping '{mapping.id}' needs wfs_type_name for WFS probe")
    source = ph.primary_source(mapping)
    return wfs_client.probe_change_marker(
        source.connection_ext("base_url"),
        type_name,
        probe_count=int(ext.get("change_detection_probe_count", "1")),
        version=source.connection_ext("version", "2.0.0"),
    )
