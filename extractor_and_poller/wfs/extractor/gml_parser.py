"""Parse WFS GML 3.2 responses into flat dicts suitable for Parquet.

Currently supports:

- **INSPIRE ``omso:PointTimeSeriesObservation``** — flattens each station's
  embedded ``wml2:MeasurementTimeseries`` into one dict per ``(station, date,
  value)`` triple.  This is the shape exposed by the KNMI *Gecontroleerde
  klimatologische daggegevens* WFS service.

Adding support for new feature types means writing one more ``parse_*``
function that takes ``root`` (an ``ElementTree`` element) and yields dicts.
"""

from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from typing import Any

log = logging.getLogger(__name__)

_NS = {
    "wfs": "http://www.opengis.net/wfs/2.0",
    "gml": "http://www.opengis.net/gml/3.2",
    "om": "http://www.opengis.net/om/2.0",
    "omso": "http://inspire.ec.europa.eu/schemas/omso/3.0",
    "sams": "http://www.opengis.net/samplingSpatial/2.0",
    "wml2": "http://www.opengis.net/waterml/2.0",
    "xlink": "http://www.w3.org/1999/xlink",
}


def parse_timeseries_observations(
    gml_bytes: bytes,
    *,
    max_rows: int | None = None,
) -> list[dict[str, Any]]:
    """Parse ``omso:PointTimeSeriesObservation`` GML into flat records.

    Each output dict has the keys::

        station_id, observed_property, latitude, longitude,
        period_begin, period_end, timestamp, value

    ``value`` is the measurement in tenths of a degree Celsius (as published
    by KNMI); conversion to real-world units is left to downstream transforms.
    """
    root = ET.fromstring(gml_bytes)
    records: list[dict[str, Any]] = []
    total_tvp = 0

    for member in root.findall(".//wfs:member", _NS):
        obs = member.find("omso:PointTimeSeriesObservation", _NS)
        if obs is None:
            continue

        station_id = obs.findtext("gml:identifier", "", _NS).strip()
        observed_prop_el = obs.find("om:observedProperty", _NS)
        observed_prop = (
            observed_prop_el.attrib.get(f"{{{_NS['xlink']}}}href", "")
            if observed_prop_el is not None
            else ""
        )
        period_begin = obs.findtext(
            ".//om:phenomenonTime/gml:TimePeriod/gml:beginPosition", "", _NS
        )
        period_end = obs.findtext(
            ".//om:phenomenonTime/gml:TimePeriod/gml:endPosition", "", _NS
        )
        pos_text = obs.findtext(".//sams:shape/gml:Point/gml:pos", "", _NS).split()
        lat = float(pos_text[0]) if len(pos_text) >= 2 else None
        lon = float(pos_text[1]) if len(pos_text) >= 2 else None

        tvps = obs.findall(
            ".//wml2:MeasurementTimeseries/wml2:point/wml2:MeasurementTVP", _NS
        )
        log.debug("  station %s: %d time-value pairs", station_id, len(tvps))

        for tvp in tvps:
            timestamp = tvp.findtext("wml2:time", "", _NS)
            raw_value = tvp.findtext("wml2:value", "", _NS)
            value = float(raw_value) if raw_value else None

            records.append({
                "station_id": station_id,
                "observed_property": observed_prop,
                "latitude": lat,
                "longitude": lon,
                "period_begin": period_begin,
                "period_end": period_end,
                "timestamp": timestamp,
                "value": value,
            })
            total_tvp += 1
            if max_rows is not None and total_tvp >= max_rows:
                log.info("Hit max_rows=%d, stopping parse early.", max_rows)
                return records

    log.info(
        "Parsed %d observations -> %d records",
        len(root.findall(".//wfs:member", _NS)),
        len(records),
    )
    return records


def extract_max_period_end(gml_bytes: bytes) -> str | None:
    """Return the latest ``gml:endPosition`` from observation phenomenon times.

    Used by the data object poller as a lightweight change marker for INSPIRE
    ``PointTimeSeriesObservation`` features. Does not flatten measurement
    time-value pairs — only reads each member's phenomenon time period.
    """
    root = ET.fromstring(gml_bytes)
    ends: list[str] = []
    for member in root.findall(".//wfs:member", _NS):
        obs = member.find("omso:PointTimeSeriesObservation", _NS)
        if obs is None:
            continue
        period_end = obs.findtext(
            ".//om:phenomenonTime/gml:TimePeriod/gml:endPosition", "", _NS
        ).strip()
        if period_end:
            ends.append(period_end)
    return max(ends) if ends else None
