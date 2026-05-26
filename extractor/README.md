# Extractor

## Table of contents

<!-- markdown-toc:start -->
- [Overview](#overview)
- [Where is the poller?](#where-is-the-poller)
- [Structure](#structure)
- [Design principles](#design-principles)
- [Quickstart](#quickstart)
- [Output file naming](#output-file-naming)
- [Adding a new extractor](#adding-a-new-extractor)
- [Available extractors](#available-extractors)
<!-- markdown-toc:end -->

## Overview

Python packages that **download and flatten** source data into Parquet under `data/staging/`, driven by DWA-style JSON in `data-object-mapping/`.

Each subfolder is one **protocol or API** (OData, WFS, Open-Meteo, KNMI KDP). Shared helpers live in `common/`.

## Where is the poller?

There is **no** `extractor/poller/` folder.

| Location | Purpose |
|----------|---------|
| [`poller/`](../poller/) (project root) | Detect marker changes and publish `data_object_change` / `data_object_progress` to the event bus — **never** runs extractors |
| `extractor/<protocol>/client.py` | HTTP clients; some expose `probe_*` helpers reused by the poller |

Orchestration connects the two: **change** events enqueue extract tasks; **progress** events record that polling ran. See [poller/README.md](../poller/README.md).

## Structure

```text
extractor/
├── __init__.py
├── README.md
├── requirements.txt
├── .gitignore
├── common/
│   ├── config.py          # Load DWA-style mapping JSON
│   └── parquet.py         # Templated Parquet writer
├── openmeteo/             # Open-Meteo Forecast API (default PoC source)
│   ├── __main__.py        # python -m extractor.openmeteo
│   ├── client.py
│   └── stations.py        # NL reference coordinates
├── knmi/                  # KNMI Data Platform Open Data (NetCDF; needs API key)
│   ├── __main__.py        # python -m extractor.knmi
│   ├── client.py          # Catalog list + download (also used by poller)
│   ├── netcdf_parser.py
│   └── README.md
├── odata/                 # OData v4
│   ├── __main__.py        # python -m extractor.odata
│   └── client.py
└── wfs/                   # OGC WFS 2.0 (legacy; stale KNMI haleconnect feed)
    ├── __main__.py        # python -m extractor.wfs
    ├── client.py
    ├── gml_parser.py
    └── README.md
```

## Design principles

- **One subfolder per protocol** — client + optional parsers + `__main__.py` CLI.
- **Config-driven** — endpoints and landing paths come from `data-object-mapping/`, not hardcoded in extractors.
- **Parquet to `data/staging/`** — paths from `landing_path_template` in each mapping.
- **`python -m extractor.<protocol>`** — run from the `data-solution-2026/` project root.

## Quickstart

```powershell
pip install -r extractor/requirements.txt

# Default PoC: Open-Meteo (no API key)
python -m poller --probe-only --mapping openmeteo-daily-temperature
python -m extractor.openmeteo --mapping openmeteo-daily-temperature

# KNMI KDP in-situ (requires KNMI_API_KEY; mapping disabled by default)
$env:KNMI_API_KEY = "<your-key>"
python -m extractor.knmi --config data-object-mapping/staging/knmi/knmi-daggegevens.json --mapping knmi-daggegevens-temperature

# OData / WFS: pass --config to a mapping JSON that defines the source
python -m extractor.odata --config <path-to-mapping.json> --mapping <mapping-id>
python -m extractor.wfs --config data-object-mapping/staging/knmi/knmi-daggegevens.json --mapping knmi-daggegevens-temperature --limit 100
```

## Output file naming

Each run writes one Parquet file named with a UTC timestamp at extractor start:

```text
2026-05-22T142402322Z.parquet
```

- Extended date (`YYYY-MM-DD`), `T` separator, compact time (no `:` for Windows), milliseconds, `Z` = UTC.

## Adding a new extractor

1. Add `extractor/<protocol>/` with `client.py` and `__main__.py`.
2. If the poller should detect changes, add a probe in `client.py` and register `interface_type` in `poller/change_probe.py`.
3. Add mapping JSON under `data-object-mapping/staging/<source>/`.

## Available extractors

| Sub-folder | Protocol | Status |
| --- | --- | --- |
| `openmeteo/` | Open-Meteo Forecast API | **Default** — daily temperature, no API key |
| `knmi/` | KDP Open Data API | Optional — nightly NetCDF, `KNMI_API_KEY` |
| `odata/` | OData v4 | Implemented — bring your own mapping JSON |
| `wfs/` | OGC WFS 2.0 | Legacy reference — stale haleconnect KNMI feed |

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](../readme.md)
  - Data
    - Staging
      - Openmeteo
        - Daily_Temperature
  - Data Object Mapping
    - Staging
      - Knmi
      - Openmeteo
  - Docs
  - Extractor
    - Common
    - Knmi
    - Odata
    - Openmeteo
    - Poller
    - Wfs
  - Plan
    - Data Object Poller
      - [Data object poller — Airflow + Kafka implementation](../plan/data-object-poller/airflow-kafka.md)
    - [Phase one: CBS OData extraction with event-based orchestration](../plan/plan1.md)
    - [Phase two: minimal Dutch government OData ingestion with event-based orchestration](../plan/plan2.md)
    - [Phase three: JSON-configured Dutch government OData ingestion](../plan/plan3.md)
  - Poller
  - Schema
    - [Schema follow-ups](../schema/data-objects-schema.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026)
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns)
<!-- markdown-project-structure:end -->
