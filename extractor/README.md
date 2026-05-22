# Extractor

## Table of contents

<!-- markdown-toc:start -->
- [Overview](#overview)
- [Structure](#structure)
- [Design principles](#design-principles)
- [Quickstart](#quickstart)
- [Output file naming](#output-file-naming)
- [Adding a new extractor](#adding-a-new-extractor)
- [Available extractors](#available-extractors)
<!-- markdown-toc:end -->

## Overview

This folder contains the runtime extraction logic for pulling data from
external source systems into the `data/000_Source/` landing zone. Each
sub-folder targets a specific protocol or API type, plus a `common/` folder
for shared utilities.

## Structure

```text
extractor/
├── __init__.py
├── README.md
├── requirements.txt
├── .gitignore
├── common/                Shared utilities
│   ├── __init__.py
│   ├── config.py          Load and query DWA-style metadata JSON files
│   └── parquet.py         Templated Parquet file writer
├── odata/                 OData v4 extractor
│   ├── __init__.py
│   ├── __main__.py        CLI driver (python -m extractor.odata)
│   └── client.py          HTTP client — pagination via @odata.nextLink
├── knmi/                  KNMI Data Platform Open Data API (active KNMI source)
│   ├── client.py          List files, probe latest filename for poller
│   └── README.md
└── wfs/                   OGC WFS 2.0 extractor (legacy; stale KNMI haleconnect feed)
    ├── __init__.py
    ├── __main__.py        CLI driver (python -m extractor.wfs)
    ├── client.py          HTTP client — GetCapabilities, GetFeature
    ├── gml_parser.py      GML parser
    └── README.md
```

Poller (change detection only) lives at project root as `poller/` — see [poller plan](../plan/data-object-poller/airflow-kafka.md).

The legacy **WFS** extractor remains for reference; KNMI ingestion uses **KDP Open Data** — see [knmi/README.md](knmi/README.md) and the [stale WFS note](../readme.md#stale-knmi-wfs-feed-superseded).

## Design principles

- **One sub-folder per protocol.** Each extractor is self-contained: a client
  module that handles the HTTP and protocol specifics, plus optional parser
  modules for response formats that need flattening.
- **Config-driven.** Extractors don't hardcode endpoints or table names. They
  read DWA-style JSON mappings from `data-object-mapping/` which specify the
  connection URL, feature type, output format, page size, and landing path.
- **Parquet output to `Data/`.** Every extractor produces `list[dict]`
  records written to Parquet under the `Data/` directory (gitignored).
- **Runnable as Python modules.** Each extractor has a `__main__.py` so it can
  be invoked with `python -m extractor.<protocol>` from the project root.

## Quickstart

From the project root (`data-solution-2026/`):

```powershell
pip install -r extractor/requirements.txt

# OData: smoke test against public Northwind v4 reference
python -m extractor.odata --config data-object-mapping/odata-demo.json --mapping odata-demo-regions

# WFS: extract KNMI daily temperature (2 stations, capped at 100 records)
python -m extractor.wfs --mapping knmi-daggegevens-temperature --page-size 2 --max-features 2 --limit 100

# KNMI KDP: extract latest daily NetCDF to Parquet (requires KNMI_API_KEY)
python -m extractor.knmi --mapping knmi-daggegevens-temperature

# Poller: probe for new daily file
python -m poller --probe-only --mapping knmi-daggegevens-temperature
```

Output lands under `Data/000_Source/...` as defined by the `landing_path_template`
extension in each mapping JSON.

## Output file naming

Each extraction run produces a Parquet file whose name is a UTC timestamp
captured at the moment the extractor starts. The format is ISO 8601 hybrid
with millisecond precision:

```text
2026-05-12T164832123Z.parquet
│          │││││││││└─ UTC indicator
│          │││││││└┘┘── milliseconds (000-999)
│          │││││└┘───── seconds (00-59)
│          │││└┘─────── minutes (00-59)
│          │└┘───────── hours (00-23)
│          └─────────── T separator (ISO 8601)
└───────────────────── date (YYYY-MM-DD, ISO 8601 extended)
```

Design choices:

- **Extended date with dashes** — keeps the date portion human-readable.
- **`T` separator** — the ISO 8601-defined boundary between date and time.
- **Compact time without colons** — colons are illegal in Windows filenames.
- **3-digit milliseconds** — ensures uniqueness across multiple runs on the
  same day without requiring directory scanning or UUIDs.
- **`Z` suffix** — makes it unambiguous that all timestamps are UTC,
  regardless of the machine's local timezone.
- **Captured once at extractor start** — all tables within a single
  extraction run share the same timestamp, so they can be correlated.

## Adding a new extractor

1. Create a new sub-folder (e.g. `rest/`, `sftp/`).
2. Add a `client.py` with the protocol-specific fetch logic.
3. Add parser modules if the raw response needs flattening.
4. Expose the public API from the sub-folder's `__init__.py`.
5. Add a `__main__.py` CLI driver.
6. Create a DWA-style mapping JSON in `data-object-mapping/`.

## Available extractors

| Sub-folder | Protocol | Status |
| --- | --- | --- |
| `odata/` | OData v4 | Implemented — CBS + Northwind demo |
| `knmi/` | KDP Open Data API | Poller + NetCDF → Parquet extractor |
| `wfs/` | OGC WFS 2.0 | Legacy — stale haleconnect KNMI feed (see [readme](../readme.md)) |

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](../readme.md)
  - Data
    - Staging
      - Knmi
        - Daggegevens_Temperature
  - Data Object Mapping
    - Staging
      - Knmi
  - Docs
  - Extractor
    - Common
    - Knmi
    - Odata
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
