"""Parse KNMI KDP daily NetCDF into flat records for Parquet landing."""

from __future__ import annotations

import logging
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import numpy as np
import xarray as xr

log = logging.getLogger(__name__)

_FILENAME_RE = re.compile(r"daily-observations-(\d{8})\.nc", re.I)


def _observation_day_from_filename(filename: str) -> tuple[str, str]:
    """Return ``(period_begin, period_end)`` ISO timestamps for a daily file name."""
    m = _FILENAME_RE.search(filename)
    if not m:
        raise ValueError(f"Cannot parse observation day from filename: {filename!r}")
    ymd = m.group(1)
    begin = datetime.strptime(ymd, "%Y%m%d").replace(tzinfo=timezone.utc)
    end = begin + timedelta(days=1)
    return (
        begin.strftime("%Y-%m-%dT%H:%M:%SZ"),
        end.strftime("%Y-%m-%dT%H:%M:%SZ"),
    )


def _time_end_iso(ds: xr.Dataset) -> str:
    if "time" not in ds.coords and "time" not in ds.dims:
        raise KeyError("NetCDF has no time coordinate")
    t = np.asarray(ds["time"].values).ravel()[0]
    if hasattr(t, "isoformat"):
        text = t.isoformat().replace("+00:00", "Z")
        if not text.endswith("Z"):
            text += "Z"
        return text
    return str(t)


def parse_daily_temperature(
    nc_path: str | Path,
    *,
    variable: str = "TG",
    source_filename: str | None = None,
) -> list[dict[str, Any]]:
    """Flatten one daily NetCDF file to one row per station with ``variable`` set.

    Output columns align with ``knmi-daggegevens.json`` dataItems:
    ``station_id``, ``observed_property``, ``latitude``, ``longitude``,
    ``period_begin``, ``period_end``, ``timestamp``, ``value``.
    """
    path = Path(nc_path)
    filename = source_filename or path.name

    records: list[dict[str, Any]] = []
    with xr.open_dataset(path) as ds:
        if _FILENAME_RE.search(filename):
            period_begin, period_end = _observation_day_from_filename(filename)
        else:
            period_end = _time_end_iso(ds)
            end_dt = datetime.fromisoformat(period_end.replace("Z", "+00:00"))
            begin_dt = end_dt - timedelta(days=1)
            period_begin = begin_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            period_end = end_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        if variable not in ds:
            raise KeyError(
                f"Variable '{variable}' not in {filename}. "
                f"Available: {sorted(ds.data_vars)}"
            )
        var = ds[variable]
        timestamp = period_end
        observed_property = str(
            var.attrs.get("standard_name")
            or var.attrs.get("long_name")
            or variable
        )

        station_dim = "station" if "station" in var.dims else var.dims[0]
        stations = ds[station_dim].values
        lats = ds["lat"].values if "lat" in ds else ds["latitude"].values
        lons = ds["lon"].values if "lon" in ds else ds["longitude"].values

        values = np.asarray(var.values)
        if "time" in var.dims:
            time_axis = var.dims.index("time")
            if time_axis == 1:
                values = values[:, 0]
            else:
                values = values[0, :]

        for i, station_id in enumerate(stations):
            raw = values[i]
            if raw is None or (isinstance(raw, float) and np.isnan(raw)):
                continue
            records.append({
                "station_id": str(station_id),
                "observed_property": observed_property,
                "latitude": float(lats[i]),
                "longitude": float(lons[i]),
                "period_begin": period_begin,
                "period_end": period_end,
                "timestamp": timestamp,
                "value": float(raw),
            })

    log.info(
        "Parsed %s: %d station(s) with %s",
        filename,
        len(records),
        variable,
    )
    return records
