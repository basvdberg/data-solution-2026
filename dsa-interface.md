# DSA interface

## Table of contents

<!-- markdown-toc:start -->
- [Overview](#overview)
- [IDs](#ids)
- [Artifact types](#artifact-types)
  - [Data connection](#data-connection)
  - [Data object](#data-object)
  - [Data object mapping](#data-object-mapping)
- [Folder layout](#folder-layout)
- [References vs embedded copies](#references-vs-embedded-copies)
- [Deploy bundle (optional)](#deploy-bundle-optional)
<!-- markdown-toc:end -->

Data Solution Automation (DSA) describes data transformations as JSON metadata in Git. Each artifact type lives in its own file. Files reference each other by path, not by UUID.

## Overview

A **data transformation** connects sources to a target:

- **Data connections** — where data lives (API, file path, database).
- **Data objects** — logical datasets (tables, files, APIs) with optional **data items** (columns or fields).
- **Data object mappings** — how sources become a target (poll rules, field logic, extensions).

Use **multiple JSON files** linked by path. Do not maintain one large JSON for the whole solution.

## IDs

The **ID of an artifact is its path** relative to the solution root (the folder that contains `connection/`, `data-object/`, and `data-object-mapping/`).

Rules:

| Rule | Example |
|------|---------|
| Forward slashes only | `staging/openmeteo/daily-temperature` |
| Repo-relative, never absolute | Not `c:\Dev2\...` |
| Lowercase kebab-case paths | `connection/staging` |
| No `.json` in the ID | File on disk: `data-object/staging/openmeteo/daily-temperature.json`; ID: `staging/openmeteo/daily-temperature` |
| No `data-object/` in the ID | Folder `data-object/` is storage only; the ID is the path inside it |

The `id` field inside a JSON file, if present, **must equal** the logical ID (not the full file path). Tools may omit `id` and derive it from the file location under `data-object/`.

**Data item IDs** extend the data object ID with the item name:

```text
{data-object-id}/{item-name}
```

Example: `staging/openmeteo/daily-temperature/station_id`

Renaming or moving a file changes its ID. Update every reference, or add a short-lived redirect file at the old path during migration.

## Artifact types

### Data connection

One file per connection. Holds connectivity only (URL, path, protocol, credentials reference).

```json
{
  "id": "connection/open-meteo-forecast",
  "name": "open-meteo-forecast",
  "extensions": [
    { "key": "base_url", "value": "https://api.open-meteo.com/v1/forecast" },
    { "key": "protocol", "value": "OPEN_METEO" }
  ]
}
```

### Data object

One file per dataset. References a connection by path. Lists **data items** when the schema is known.

```json
{
  "id": "staging/openmeteo/daily-temperature",
  "name": "daily_temperature",
  "notes": "One row per (station, day) with daily mean 2 m temperature in °C.",
  "dataConnectionId": "connection/staging",
  "dataItems": [
    {
      "id": "staging/openmeteo/daily-temperature/station_id",
      "name": "station_id",
      "ordinalPosition": 1,
      "dataType": "string"
    },
    {
      "id": "staging/openmeteo/daily-temperature/value",
      "name": "value",
      "ordinalPosition": 2,
      "dataType": "double"
    }
  ],
  "classifications": [
    { "group": "Solution Layer", "classification": "Staging Layer" }
  ]
}
```

Use `dataConnectionId` when the connection is shared. Inline `dataConnection` is allowed only when it is truly private to that object.

### Data object mapping

One file per transformation (source → target). References other artifacts by path. Put integration-specific settings here (`enabled`, poller rules, landing templates), not in the data object.

```json
{
  "id": "data-object-mapping/staging/openmeteo/daily-temperature",
  "name": "Open-Meteo daily temperature to staging landing",
  "enabled": true,
  "sourceDataObjectIds": ["source/openmeteo/daily-temperature"],
  "targetDataObjectId": "staging/openmeteo/daily-temperature",
  "extensions": [
    { "key": "change_detection_rule", "value": "openmeteo_latest_day" },
    { "key": "landing_path_template", "value": "./data/staging/openmeteo/{dataset}/{timestamp}.parquet" }
  ]
}
```

Field-level transform rules (rename, cast, expression) belong in this file when you add them, for example under `fieldMappings`.

## Folder layout

```text
data-solution-2026/
  connection/              # shared connections
  data-object/             # datasets (source/, staging/, …)
  data-object-mapping/     # transformations (staging/openmeteo/…)
  extractor_and_poller/    # Python extractors and pollers
```

JSON Schema files under `schema/` describe each artifact type. One artifact per file.

## References vs embedded copies

**Authoring (preferred):** mappings list `sourceDataObjectIds` and `targetDataObjectId` only. Load the full object from the referenced file.

**Deploy bundle (optional):** a build step may produce one self-contained JSON with embedded connections and objects for a runtime engine. That bundle is generated output, not the source of truth in Git.

## Deploy bundle (optional)

When a tool needs a single document:

1. Read all referenced paths.
2. Resolve `dataConnectionId` and `dataObjectId` into full objects.
3. Emit one JSON (or keep the historical embedded shape for compatibility).

The path IDs in the repo remain the stable names humans use in reviews and logs.

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](readme.md)
  - Classification
  - Configuration
  - Connection
  - Convention
  - Data
    - Staging
      - Openmeteo
        - Daily_Temperature
  - Data Object
    - Source
      - Openmeteo
    - Staging
      - Openmeteo
  - Data Object Mapping
    - Staging
      - Openmeteo
  - Doc
    - Data Object Mapping
    - [Remote SSH development workflow](doc/remote-ssh.md)
  - Extractor_And_Poller
    - Common
    - Openmeteo
      - Extractor
      - Poller
    - Poller
    - Tests
  - Output
  - Perspective
  - Schema
    - [Schema follow-ups](schema/data-objects-schema.md)
  - Setting
  - Template
  - [DSA interface](dsa-interface.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026)
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns)
<!-- markdown-project-structure:end -->
