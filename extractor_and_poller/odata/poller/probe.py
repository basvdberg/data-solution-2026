"""OData v4 change-marker probe."""

from __future__ import annotations

from extractor_and_poller.common.config import Config, Mapping
from extractor_and_poller.common import probe_helpers as ph
from extractor_and_poller.odata.extractor import client as odata_client

INTERFACE_TYPE = "odata_v4"


def probe(mapping: Mapping, config: Config) -> str:
    ext = ph.merged_ext(mapping, config)
    endpoint = ext.get("change_detection_endpoint")
    field = ext.get("change_detection_field")
    if not endpoint or not field:
        raise KeyError(
            f"Mapping '{mapping.id}' needs change_detection_endpoint and "
            "change_detection_field for OData"
        )
    base_url = ph.primary_source(mapping).connection_ext("base_url").rstrip("/")
    url = f"{base_url}/{endpoint.lstrip('/')}"
    body = odata_client.fetch_singleton(url)
    if field not in body:
        raise KeyError(f"Field '{field}' not in OData probe response from {url}")
    return str(body[field])
