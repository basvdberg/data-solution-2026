# KNMI Data Platform extractor (sketch)

## Table of contents

<!-- markdown-toc:start -->
- [Overview](#overview)
- [Why not WFS](#why-not-wfs)
- [Open Data API](#open-data-api)
- [Mapping extensions](#mapping-extensions)
- [Poller rule](#poller-rule)
- [Extractor CLI](#extractor-cli)
- [Setup](#setup)
<!-- markdown-toc:end -->

## Overview

Replaces the legacy [INSPIRE WFS on haleconnect.com](../wfs/README.md) for KNMI daily in-situ observations. The [KNMI Data Platform](https://dataplatform.knmi.nl/) publishes **current** NetCDF files via the [Open Data API](https://developer.dataplatform.knmi.nl/open-data-api) (nightly updates for unvalidated daily data).

Mapping: `data-object-mapping/staging/knmi/knmi-daggegevens.json`.

## Why not WFS

The haleconnect WFS feed for *Gecontroleerde klimatologische daggegevens* stopped advancing around **2023-09-01** (all 33 stations capped at that date). Catalog metadata can still look “active” while feature payloads are frozen. See the **Stale KNMI WFS feed** note in the [project readme](../../readme.md).

## Open Data API

| Item | Value |
|------|--------|
| Base URL | `https://api.dataplatform.knmi.nl/open-data/v1` |
| Dataset | `daily-in-situ-meteorological-observations` |
| Version | `1.0` |
| File pattern | `daily-observations-YYYYMMDD.nc` |
| Auth | `Authorization: <API_KEY>` header |

List newest file (poller probe):

```http
GET /datasets/daily-in-situ-meteorological-observations/versions/1.0/files
    ?maxKeys=1&orderBy=created&sorting=desc
```

Download (extractor, planned):

```http
GET /datasets/{dataset}/versions/{version}/files/{filename}/url
```

## Mapping extensions

| Extension | Purpose |
|-----------|---------|
| `kdp_dataset_name` | e.g. `daily-in-situ-meteorological-observations` |
| `kdp_dataset_version` | e.g. `1.0` |
| `kdp_list_order_by` | `created` or `lastModified` (poller list sort) |
| `kdp_list_sorting` | `desc` |
| `change_detection_rule` | `knmi_latest_file` |
| `change_detection_field` | `filename`, `created`, or `lastModified` |
| `landing_path_template` | Parquet landing path |
| `netcdf_variable` | (planned) temperature variable in NetCDF |

Connection extensions: `base_url`, `api_key_env` (default `KNMI_API_KEY`).

## Poller rule

`interface_type:knmi_open_data` → `extractor.knmi.client.probe_change_marker`.

Baseline is the latest catalog file’s `filename` (or `created`). When KNMI lands a new `daily-observations-*.nc`, the marker changes and `poller` emits `CHANGED`.

```powershell
$env:KNMI_API_KEY = "<your-key>"
python -m poller --probe-only --mapping knmi-daggegevens-temperature
```

Prefer a **registered** API key (see KDP developer portal); the shared anonymous key has a low shared rate limit.

## Extractor CLI

```powershell
$env:KNMI_API_KEY = "<your-key>"
python -m extractor.knmi --mapping knmi-daggegevens-temperature
python -m extractor.knmi --mapping knmi-daggegevens-temperature --filename daily-observations-20260521.nc
```

Downloads the latest (or named) `daily-observations-*.nc`, parses variable `TG` (daily mean temperature in °C, one row per station), and writes Parquet under `data/staging/knmi/daggegevens-temperature/`.

Offline dev without catalog API:

```powershell
python -m extractor.knmi --mapping knmi-daggegevens-temperature --local-file path\to\daily-observations-20260521.nc
```

## Setup

1. Register at [developer.dataplatform.knmi.nl](https://developer.dataplatform.knmi.nl/open-data-api) and request an Open Data API key.
2. Set `KNMI_API_KEY` in the environment (do not commit keys).
3. Point `data-object-mapping/staging/knmi/knmi-daggegevens.json` at the KDP dataset (already configured in-repo).

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](../../readme.md)
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
      - [Data object poller — Airflow + Kafka implementation](../../plan/data-object-poller/airflow-kafka.md)
    - [Phase one: CBS OData extraction with event-based orchestration](../../plan/plan1.md)
    - [Phase two: minimal Dutch government OData ingestion with event-based orchestration](../../plan/plan2.md)
    - [Phase three: JSON-configured Dutch government OData ingestion](../../plan/plan3.md)
  - Poller
  - Schema
    - [Schema follow-ups](../../schema/data-objects-schema.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026)
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns)
<!-- markdown-project-structure:end -->
