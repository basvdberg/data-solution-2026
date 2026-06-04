"""Open-Meteo Forecast API — daily temperature, no authentication.

API: https://open-meteo.com/en/docs
Data licence: CC BY 4.0 (attribution required).
Models refresh frequently; ``past_days`` exposes the latest completed calendar days.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta, timezone
from typing import Any

import requests

from extractor_and_poller.openmeteo.extractor.stations import NL_REFERENCE_STATIONS, ReferenceStation

log = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://api.open-meteo.com/v1/forecast"


def _period_bounds(day: str) -> tuple[str, str]:
    begin = datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    end = begin + timedelta(days=1)
    return (
        begin.strftime("%Y-%m-%dT%H:%M:%SZ"),
        end.strftime("%Y-%m-%dT%H:%M:%SZ"),
    )


def fetch_daily(
    latitude: float,
    longitude: float,
    observation_day: str,
    *,
    daily_variable: str = "temperature_2m_mean",
    base_url: str = DEFAULT_BASE_URL,
    timezone: str = "UTC",
    timeout: float = 30.0,
) -> dict[str, Any]:
    """GET one calendar day of daily aggregates for a point."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": observation_day,
        "end_date": observation_day,
        "daily": daily_variable,
        "timezone": timezone,
    }
    log.debug("Open-Meteo %s %s %s", observation_day, latitude, longitude)
    r = requests.get(base_url, params=params, timeout=timeout)
    r.raise_for_status()
    return r.json()


def probe_change_marker(
    *,
    latitude: float = 52.10,
    longitude: float = 5.18,
    daily_variable: str = "temperature_2m_mean",
    past_days: int = 7,
    base_url: str = DEFAULT_BASE_URL,
    timezone: str = "UTC",
    timeout: float = 30.0,
) -> str:
    """Return the latest completed UTC calendar day with temperature data."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": daily_variable,
        "timezone": timezone,
        "past_days": past_days,
    }
    log.info(
        "Open-Meteo probe request %s lat=%s lon=%s past_days=%s timeout=%ss",
        base_url,
        latitude,
        longitude,
        past_days,
        timeout,
    )
    r = requests.get(base_url, params=params, timeout=timeout)
    r.raise_for_status()
    body = r.json()
    times = body.get("daily", {}).get("time") or []
    values = body.get("daily", {}).get(daily_variable) or []
    today = date.today().isoformat()
    candidates: list[str] = []
    for day, val in zip(times, values):
        if day >= today:
            continue
        if val is None:
            continue
        candidates.append(day)
    if not candidates:
        raise ValueError(
            f"No completed daily {daily_variable} in Open-Meteo probe "
            f"(past_days={past_days}, ref={latitude},{longitude})"
        )
    marker = max(candidates)
    log.info("Open-Meteo change marker: %s", marker)
    return marker


def records_for_day(
    observation_day: str,
    *,
    stations: tuple[ReferenceStation, ...] = NL_REFERENCE_STATIONS,
    daily_variable: str = "temperature_2m_mean",
    base_url: str = DEFAULT_BASE_URL,
    timezone: str = "UTC",
    timeout: float = 30.0,
) -> list[dict[str, Any]]:
    """One landing row per reference location for ``observation_day`` (YYYY-MM-DD)."""
    period_begin, period_end = _period_bounds(observation_day)
    records: list[dict[str, Any]] = []
    for station in stations:
        body = fetch_daily(
            station.latitude,
            station.longitude,
            observation_day,
            daily_variable=daily_variable,
            base_url=base_url,
            timezone=timezone,
            timeout=timeout,
        )
        daily = body.get("daily", {})
        times = daily.get("time") or []
        values = daily.get(daily_variable) or []
        if observation_day not in times:
            log.warning("No %s for station %s on %s", daily_variable, station.station_id, observation_day)
            continue
        idx = times.index(observation_day)
        value = values[idx]
        if value is None:
            continue
        records.append({
            "station_id": station.station_id,
            "observed_property": daily_variable,
            "latitude": station.latitude,
            "longitude": station.longitude,
            "period_begin": period_begin,
            "period_end": period_end,
            "timestamp": period_end,
            "value": float(value),
        })
    log.info("Open-Meteo %s: %d row(s)", observation_day, len(records))
    return records
