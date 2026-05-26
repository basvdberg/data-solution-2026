"""Per-protocol extractors and pollers driven by data-object-mapping JSON.

Layout: ``{protocol}/extractor`` (land Parquet) and ``{protocol}/poller`` (change
markers). Shared config and orchestration live under ``common/`` and ``poller/``.

CLI (from project root)::

    python -m extractor_and_poller.poller --mapping openmeteo-daily-temperature
    python -m extractor_and_poller.openmeteo.extractor --mapping openmeteo-daily-temperature
"""
