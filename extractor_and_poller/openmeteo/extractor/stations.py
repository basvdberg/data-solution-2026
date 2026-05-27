"""Reference locations across the Netherlands (public station ids and coordinates)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReferenceStation:
    station_id: str
    name: str
    latitude: float
    longitude: float


# Major automatic weather station coordinates across the Netherlands.
NL_REFERENCE_STATIONS: tuple[ReferenceStation, ...] = (
    ReferenceStation("260", "De Bilt", 52.100, 5.180),
    ReferenceStation("235", "De Kooy", 52.928, 4.781),
    ReferenceStation("280", "Eelde", 53.125, 6.586),
    ReferenceStation("240", "Schiphol", 52.308, 4.764),
    ReferenceStation("344", "Rotterdam", 51.957, 4.437),
    ReferenceStation("330", "Vlissingen", 51.442, 3.596),
    ReferenceStation("310", "Volkel", 51.656, 5.708),
    ReferenceStation("370", "Eindhoven", 51.456, 5.390),
    ReferenceStation("375", "Maastricht", 50.906, 5.763),
    ReferenceStation("269", "Lelystad", 52.458, 5.527),
    ReferenceStation("290", "Hoorn", 52.653, 5.406),
    ReferenceStation("215", "Voorschoten", 52.166, 4.417),
)
