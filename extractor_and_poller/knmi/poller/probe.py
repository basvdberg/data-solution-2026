"""KNMI Open Data change-marker probe."""

from __future__ import annotations

from extractor_and_poller.common.config import Config, Mapping
from extractor_and_poller.common import probe_helpers as ph
from extractor_and_poller.knmi.extractor import client as knmi_client

INTERFACE_TYPE = "knmi_open_data"


def probe(mapping: Mapping, config: Config) -> str:
    ext = ph.merged_ext(mapping, config)
    dataset = ext.get("kdp_dataset_name")
    version = ext.get("kdp_dataset_version")
    if not dataset or not version:
        raise KeyError(
            f"Mapping '{mapping.id}' needs kdp_dataset_name and kdp_dataset_version"
        )
    marker_field = ext.get("change_detection_field", "filename")
    source = ph.primary_source(mapping)
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
        order_by=ext.get("kdp_list_order_by", "created"),
        sorting=ext.get("kdp_list_sorting", "desc"),
    )
