# Meta data design

## Table of contents

<!-- markdown-toc:start -->
- [Design patterns](#design-patterns)
- [Purpose](#purpose)
- [Artifact IDs](#artifact-ids)
- [Artifact types](#artifact-types)
  - [Data connection](#data-connection)
  - [Data object](#data-object)
  - [Data object mapping](#data-object-mapping)
- [Folder layout](#folder-layout)
- [References vs embedded copies](#references-vs-embedded-copies)
- [Deploy bundle (optional)](#deploy-bundle-optional)
<!-- markdown-toc:end -->

## Design patterns

This documentation is founded on design patterns that are documented here [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns/blob/main/readme.md#purpose). The following patterns are used:

- [Data solution](https://github.com/basvdberg/data-engineering-design-patterns/blob/main/design-patterns/data-engineering/data-solution.md) — `connection/`, `data-object/`, and `data-object-mapping/` layout under the solution root.
- [Separate what and how](https://github.com/basvdberg/data-engineering-design-patterns/blob/main/design-patterns/generic/separate-what-and-how.md) — path-based JSON in Git specifies *what*; extractors, pollers, and ADL specify *how*.
- [Data object](https://github.com/basvdberg/data-engineering-design-patterns/blob/main/design-patterns/data-engineering/data-object.md) — connections, data objects, and data items as separate artifacts.
- [Data object tree](https://github.com/basvdberg/data-engineering-design-patterns/blob/main/design-patterns/data-engineering/data-object-tree.md) — data item IDs as `{data-object-id}/{item-name}`.

## Purpose

Data solution meta data describes what the data solution should do. It can be seen as the configuration of the data solution. The meta data consists of different artifacts that are stored using JSON storage format. 

## Artifact IDs

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

Because the name of an artifact is encoded in its ID we do not store the name as an additional property. 

## Artifact types

### Data connection

One file per connection. Holds connectivity only (URL, path, protocol, credentials reference).

```json
{
  "id": "connection/open-meteo-forecast",
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
  "notes": "One row per (station, day) with daily mean 2 m temperature in °C.",
  "dataConnectionId": "connection/staging",
  "dataItems": [
    {
      "id": "staging/openmeteo/daily-temperature/station_id",
      "ordinalPosition": 1,
      "dataType": "string"
    },
    {
      "id": "staging/openmeteo/daily-temperature/value",
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
  code/                    # generated runtime (Airflow DAGs, event services)
  extractor_and_poller/    # Python libraries used by code/ and local CLI
  output/                  # ADL-generated SQL
```

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
- [Data Solution 2026](../../readme.md)
  - Code
    - Airflow
      - Dags
      - Plugins
    - Extractor_And_Poller
      - Common
      - Openmeteo
        - Extractor
        - Poller
      - Poller
      - Tests
    - Postgres
  - Connection
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
    - Data Solution
      - Data Object Mapping
    - Design
      - [Architecture](architecture.md)
      - [CI/CD workflow (main only + server pull deploy)](ci-cd.md)
      - [Event-based orchestration plan (single data object)](event-based-orchestration-plan.md)
      - [Meta data design](meta-data-design.md)
    - [Implementation plan (Open-Meteo → event orchestration)](../implementation-plan.md)
  - Infra
    - Airflow
      - Dags
    - Kafka
    - Postgres
  - Release
    - Details
      - V2026.06.02.1
      - V2026.06.02.2
      - V2026.06.03.1
      - V2026.06.03.2
      - V2026.06.03.3
      - V2026.06.03.4
      - V2026.06.04.1
      - V2026.06.04.2
      - V2026.06.04.3
      - V2026.06.04.4
      - V2026.06.04.5
      - V2026.06.04.6
      - V2026.06.04.7
      - V2026.06.04.8
      - V2026.06.04.9
      - V2026.06.05.1
      - V2026.06.05.2
      - V2026.06.05.3
      - V2026.06.05.4
      - ﻿V2026.06.04.1
      - ﻿V2026.06.04.2
      - ﻿V2026.06.04.3
      - ﻿V2026.06.04.4
      - ﻿V2026.06.04.5
      - ﻿V2026.06.04.6
      - ﻿V2026.06.04.7
      - ﻿V2026.06.04.8
      - ﻿V2026.06.04.9
      - ﻿V2026.06.05.1
      - ﻿V2026.06.05.2
      - ﻿V2026.06.05.3
      - ﻿V2026.06.05.4
    - Notes
      - [Release v2026.06.02.1](../../release/notes/v2026.06.02.1.md)
      - [Release v2026.06.02.2](../../release/notes/v2026.06.02.2.md)
      - [Release v2026.06.03.1](../../release/notes/v2026.06.03.1.md)
      - [Release v2026.06.03.2](../../release/notes/v2026.06.03.2.md)
      - [Release v2026.06.03.3](../../release/notes/v2026.06.03.3.md)
      - [Release v2026.06.03.4](../../release/notes/v2026.06.03.4.md)
      - [V2026.06.04.1](../../release/notes/v2026.06.04.1.md)
      - [V2026.06.04.2](../../release/notes/v2026.06.04.2.md)
      - [V2026.06.04.3](../../release/notes/v2026.06.04.3.md)
      - [V2026.06.04.4](../../release/notes/v2026.06.04.4.md)
      - [V2026.06.04.5](../../release/notes/v2026.06.04.5.md)
      - [V2026.06.04.6](../../release/notes/v2026.06.04.6.md)
      - [V2026.06.04.7](../../release/notes/v2026.06.04.7.md)
      - [V2026.06.04.8](../../release/notes/v2026.06.04.8.md)
      - [V2026.06.04.9](../../release/notes/v2026.06.04.9.md)
      - [V2026.06.05.1](../../release/notes/v2026.06.05.1.md)
      - [V2026.06.05.2](../../release/notes/v2026.06.05.2.md)
      - [V2026.06.05.3](../../release/notes/v2026.06.05.3.md)
      - [V2026.06.05.4](../../release/notes/v2026.06.05.4.md)
    - [Release <version>](../../release/release-notes-template.md)
  - Setting
  - Template
  - [Getting started](../../getting-started.md)
  - [Lessons learned](../../lessons-learned-part1.md)
  - [Lessons learned (part 2)](../../lessons-learned-part2.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
