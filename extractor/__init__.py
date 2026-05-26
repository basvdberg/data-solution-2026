"""Extractors: download and flatten source data to Parquet.

One sub-package per protocol. Change detection is **not** here — use the
project-root ``poller`` package (``python -m poller``).

Sub-packages:
    common      Config loader and Parquet writer.
    openmeteo   Open-Meteo Forecast API (default PoC).
    knmi        KNMI Data Platform Open Data (NetCDF).
    odata       OData v4 HTTP client.
    wfs         OGC WFS 2.0 client + GML parser (legacy).
"""
