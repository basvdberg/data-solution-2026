"""Open-Meteo extractor and poller driven by data-object-mapping JSON.

Layout: ``openmeteo/extractor`` (lands Parquet) and ``openmeteo/poller`` (change
markers). Shared config and orchestration live under ``common/`` and ``poller/``.

CLI (from solution root, with ``code/`` on PYTHONPATH)::

    python -m extractor_and_poller.poller --data-object source/openmeteo/daily-temperature
    python -m extractor_and_poller.openmeteo.extractor --mapping daily-temperature
"""
