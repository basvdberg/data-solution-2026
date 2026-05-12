"""Extractor sub-packages, one per source protocol.

Each sub-package exposes a client and optional parsers that take a URL and
return records suitable for downstream Parquet writing.

Sub-packages:
    common  Shared utilities (config loader, Parquet writer).
    odata   OData v4 HTTP client.
    wfs     OGC WFS 2.0 client + GML parser.
"""
