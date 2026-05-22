"""Generic OGC WFS 2.0 HTTP client.

Entry points:

- :func:`get_capabilities` — parse a GetCapabilities response into a summary.
- :func:`get_feature_gml` — fetch a single page of features as raw GML bytes.
- :func:`get_feature_geojson` — fetch a single page as parsed GeoJSON.
- :func:`fetch_all_gml` — paginate through the full dataset via ``startIndex``
  and return the concatenated GML bytes per page for the caller to parse.
"""

from __future__ import annotations

import json
import logging
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Any, Iterator

import requests

log = logging.getLogger(__name__)

_NS = {
    "wfs": "http://www.opengis.net/wfs/2.0",
    "ows": "http://www.opengis.net/ows/1.1",
    "fes": "http://www.opengis.net/fes/2.0",
    "xlink": "http://www.w3.org/1999/xlink",
}


def _local(tag: str) -> str:
    """Strip namespace URI from an ElementTree tag, returning the local name."""
    return tag.rpartition("}")[2] if "}" in tag else tag


def _find_local(parent: ET.Element, local_name: str) -> ET.Element | None:
    for c in parent:
        if _local(c.tag) == local_name:
            return c
    return None


def _findall_local(parent: ET.Element, local_name: str) -> list[ET.Element]:
    return [c for c in parent if _local(c.tag) == local_name]


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class FeatureTypeInfo:
    name: str
    title: str
    default_crs: str
    other_crs: list[str] = field(default_factory=list)
    formats: list[str] = field(default_factory=list)
    bbox_lower: tuple[float, float] | None = None
    bbox_upper: tuple[float, float] | None = None


@dataclass(frozen=True)
class WfsCapabilities:
    title: str
    abstract: str
    provider: str
    version: str
    feature_types: list[FeatureTypeInfo]
    count_default: int | None = None
    supports_paging: bool = False


# ---------------------------------------------------------------------------
# GetCapabilities
# ---------------------------------------------------------------------------

def get_capabilities(
    base_url: str,
    *,
    version: str = "2.0.0",
    timeout: float = 30.0,
) -> WfsCapabilities:
    """GET ``?SERVICE=WFS&REQUEST=GetCapabilities`` and parse the response."""

    r = requests.get(
        base_url,
        params={"SERVICE": "WFS", "VERSION": version, "REQUEST": "GetCapabilities"},
        timeout=timeout,
    )
    r.raise_for_status()
    root = ET.fromstring(r.content)

    svc = root.find("ows:ServiceIdentification", _NS) or ET.Element("_")
    provider_el = root.find("ows:ServiceProvider/ows:ProviderName", _NS)
    ops = root.find("ows:OperationsMetadata", _NS) or ET.Element("_")

    count_el = ops.find(".//ows:Constraint[@name='CountDefault']/ows:DefaultValue", _NS)
    paging_el = ops.find(".//ows:Constraint[@name='ImplementsResultPaging']/ows:DefaultValue", _NS)

    feature_types: list[FeatureTypeInfo] = []
    for ftl in root.iter():
        if _local(ftl.tag) != "FeatureTypeList":
            continue
        for ft in ftl:
            if _local(ft.tag) != "FeatureType":
                continue

            name_el = _find_local(ft, "Name")
            title_el = _find_local(ft, "Title")
            crs_el = _find_local(ft, "DefaultCRS")
            other = [e.text or "" for e in _findall_local(ft, "OtherCRS")]
            of_el = _find_local(ft, "OutputFormats")
            fmts = [e.text or "" for e in _findall_local(of_el, "Format")] if of_el is not None else []

            bbox_el = ft.find("ows:WGS84BoundingBox", _NS)
            lower = upper = None
            if bbox_el is not None:
                lc = bbox_el.findtext("ows:LowerCorner", "", _NS).split()
                uc = bbox_el.findtext("ows:UpperCorner", "", _NS).split()
                if len(lc) == 2 and len(uc) == 2:
                    lower = (float(lc[0]), float(lc[1]))
                    upper = (float(uc[0]), float(uc[1]))

            feature_types.append(FeatureTypeInfo(
                name=(name_el.text or "") if name_el is not None else "",
                title=(title_el.text or "") if title_el is not None else "",
                default_crs=(crs_el.text or "") if crs_el is not None else "",
                other_crs=other,
                formats=fmts,
                bbox_lower=lower,
                bbox_upper=upper,
            ))

    return WfsCapabilities(
        title=svc.findtext("ows:Title", "", _NS),
        abstract=svc.findtext("ows:Abstract", "", _NS),
        provider=(provider_el.text or "") if provider_el is not None else "",
        version=root.attrib.get("version", version),
        feature_types=feature_types,
        count_default=int(count_el.text) if count_el is not None and count_el.text else None,
        supports_paging=(paging_el is not None and (paging_el.text or "").upper() == "TRUE"),
    )


# ---------------------------------------------------------------------------
# GetFeature — single page
# ---------------------------------------------------------------------------

def get_feature_gml(
    base_url: str,
    type_name: str,
    *,
    version: str = "2.0.0",
    count: int | None = None,
    start_index: int | None = None,
    bbox: tuple[float, float, float, float] | None = None,
    timeout: float = 300.0,
) -> bytes:
    """Fetch one page of features as raw GML 3.2 bytes."""
    params: dict[str, str] = {
        "SERVICE": "WFS",
        "VERSION": version,
        "REQUEST": "GetFeature",
        "TYPENAMES": type_name,
        "outputFormat": "application/gml+xml; version=3.2",
    }
    if count is not None:
        params["count"] = str(count)
    if start_index is not None:
        params["startIndex"] = str(start_index)
    if bbox is not None:
        params["BBOX"] = ",".join(str(c) for c in bbox)

    log.info("WFS GetFeature GML: %s (count=%s, startIndex=%s)", type_name, count, start_index)
    r = requests.get(base_url, params=params, timeout=timeout, stream=True)
    r.raise_for_status()
    content = r.content
    log.info("  -> %d bytes", len(content))
    return content


def _count_members(gml_bytes: bytes) -> int:
    """Count ``<wfs:member>`` elements in a GML response without a full parse."""
    root = ET.fromstring(gml_bytes)
    return len(root.findall("wfs:member", _NS))


# ---------------------------------------------------------------------------
# GetFeature — paginated
# ---------------------------------------------------------------------------

def iter_gml_pages(
    base_url: str,
    type_name: str,
    *,
    page_size: int = 10,
    max_features: int | None = None,
    version: str = "2.0.0",
    timeout: float = 300.0,
) -> Iterator[bytes]:
    """Paginate through a WFS feature type using ``startIndex`` / ``count``.

    Yields one GML response (bytes) per page. Stops when a page returns fewer
    members than ``page_size`` (dataset exhausted) or when ``max_features``
    total features have been fetched.

    WFS 2.0 defines ``startIndex`` (0-based) and ``count`` for result paging.
    Even servers that advertise ``ImplementsResultPaging=FALSE`` in their
    capabilities often honour these parameters (confirmed for haleconnect.com).
    """
    fetched = 0
    start_index = 0

    while True:
        effective_count = page_size
        if max_features is not None:
            remaining = max_features - fetched
            if remaining <= 0:
                break
            effective_count = min(page_size, remaining)

        gml = get_feature_gml(
            base_url, type_name,
            version=version,
            count=effective_count,
            start_index=start_index,
            timeout=timeout,
        )
        n = _count_members(gml)
        log.info("  page at startIndex=%d: %d member(s)", start_index, n)

        if n == 0:
            break

        yield gml
        fetched += n
        start_index += n

        if n < effective_count:
            break

    log.info("Pagination complete: %d feature(s) across pages.", fetched)


def fetch_all_gml(
    base_url: str,
    type_name: str,
    *,
    page_size: int = 10,
    max_features: int | None = None,
    version: str = "2.0.0",
    timeout: float = 300.0,
) -> list[bytes]:
    """Convenience wrapper: collect every page from :func:`iter_gml_pages`."""
    return list(iter_gml_pages(
        base_url, type_name,
        page_size=page_size,
        max_features=max_features,
        version=version,
        timeout=timeout,
    ))


# ---------------------------------------------------------------------------
# GetFeature — GeoJSON (single page, simple types only)
# ---------------------------------------------------------------------------

def probe_change_marker(
    base_url: str,
    type_name: str,
    *,
    probe_count: int = 1,
    version: str = "2.0.0",
    timeout: float = 60.0,
) -> str:
    """Lightweight WFS probe for change detection (no bulk extract).

    Issues ``GetFeature`` with a small ``count``, then derives a single
    baseline string from the GML (max ``period_end`` across returned members).
    Reuses :func:`get_feature_gml`; parsing is delegated to
    :func:`extractor.wfs.gml_parser.extract_max_period_end`.
    """
    from extractor.wfs import gml_parser

    gml = get_feature_gml(
        base_url,
        type_name,
        version=version,
        count=max(1, probe_count),
        timeout=timeout,
    )
    marker = gml_parser.extract_max_period_end(gml)
    if not marker:
        raise ValueError(
            f"No change marker (period_end) in WFS probe for {type_name!r} at {base_url}"
        )
    log.info("WFS change marker for %s: %s", type_name, marker)
    return marker


def get_feature_geojson(
    base_url: str,
    type_name: str,
    *,
    version: str = "2.0.0",
    count: int | None = None,
    timeout: float = 120.0,
) -> dict[str, Any]:
    """Fetch features as parsed GeoJSON (single page).

    Works for simple feature types. Complex INSPIRE types may break GeoJSON on
    some servers; use :func:`fetch_all_gml` with a GML parser instead.
    """
    params: dict[str, str] = {
        "SERVICE": "WFS",
        "VERSION": version,
        "REQUEST": "GetFeature",
        "TYPENAMES": type_name,
        "outputFormat": "application/geo+json",
    }
    if count is not None:
        params["count"] = str(count)

    log.info("WFS GetFeature GeoJSON: %s (count=%s)", type_name, count)
    r = requests.get(base_url, params=params, timeout=timeout)
    r.raise_for_status()
    data = json.loads(r.content.decode("utf-8-sig"))
    n = len(data.get("features", []))
    log.info("  -> %d features", n)
    return data
