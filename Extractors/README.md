# Extractors

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
external source systems into the `Data/000_Source/` landing zone. Each
sub-folder targets a specific protocol or API type, plus a `common/` folder
for shared utilities.

## Structure

```text
Extractors/
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
│   ├── __main__.py        CLI driver (python -m Extractors.odata)
│   └── client.py          HTTP client — pagination via @odata.nextLink
└── wfs/                   OGC WFS 2.0 extractor
    ├── __init__.py
    ├── __main__.py        CLI driver (python -m Extractors.wfs)
    ├── client.py          HTTP client — GetCapabilities, GetFeature, startIndex pagination
    ├── gml_parser.py      GML 3.2 response parser — flattens XML into tabular records
    └── README.md
```

## Design principles

- **One sub-folder per protocol.** Each extractor is self-contained: a client
  module that handles the HTTP and protocol specifics, plus optional parser
  modules for response formats that need flattening.
- **Config-driven.** Extractors don't hardcode endpoints or table names. They
  read DWA-style JSON mappings from `DataObjectMappings/` which specify the
  connection URL, feature type, output format, page size, and landing path.
- **Parquet output to `Data/`.** Every extractor produces `list[dict]`
  records written to Parquet under the `Data/` directory (gitignored).
- **Runnable as Python modules.** Each extractor has a `__main__.py` so it can
  be invoked with `python -m Extractors.<protocol>` from the project root.

## Quickstart

From the project root (`data-solution-2026/`):

```powershell
pip install -r Extractors/requirements.txt

# OData: smoke test against public Northwind v4 reference
python -m Extractors.odata --config DataObjectMappings/odata-demo.json --mapping odata-demo-regions

# WFS: extract KNMI daily temperature (2 stations, capped at 100 records)
python -m Extractors.wfs --mapping knmi-daggegevens-temperature --page-size 2 --max-features 2 --limit 100
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
6. Create a DWA-style mapping JSON in `DataObjectMappings/`.

## Available extractors

| Sub-folder | Protocol | Status |
| --- | --- | --- |
| `odata/` | OData v4 | Implemented — CBS + Northwind demo |
| `wfs/` | OGC WFS 2.0 | Implemented — KNMI INSPIRE daily climate data |

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](../readme.md)
  - Classifications
  - Configurations
  - Connections
    - Sources
  - Conventions
  - Dataobjectmappings
    - 000_Source
      - Knmi
        - Roelant
    - Persistentstaging
    - Staging
  - Dataobjects
    - 000_Source
      - Dbo
    - 100_Landing_Area
      - Dbo
    - 150_Persistent_Staging_Area
      - Dbo
  - Docs
    - [Markdown automation](../docs/markdown-automation.md)
  - Extractors
    - Common
    - Odata
    - Wfs
  - Perspectives
  - Schemas
    - [Schema follow-ups](../Schemas/follow-ups.md)
  - Settings
  - Templates
    - Dataobjectmappinglists
      - [Landing Area Stored Procedure Delta](../Templates/DataObjectMappingLists/LandingSqlServerStoredProcedureDelta.handlebars.md)
      - [Landing Area Stored Procedure Landing](../Templates/DataObjectMappingLists/LandingSqlServerStoredProcedureLanding.handlebars.md)
      - [Persistent Staging Area Stored Procedure Delta](../Templates/DataObjectMappingLists/PersistentStagingSqlServerStoredProcedureDelta.handlebars.md)
      - [Persistent Staging Area Stored Procedure Full Outer Join](../Templates/DataObjectMappingLists/PersistentStagingSqlServerStoredProcedureFullOuterJoin.handlebars.md)
    - Dataobjects
      - [Source Area Generate Table](../Templates/DataObjects/CreatePhysicalDataObject.handlebars.md)
      - [Landing Area Generate Table](../Templates/DataObjects/LandingSqlServerGenerateTable.handlebars.md)
      - [Persistent Staging Area Generate Table](../Templates/DataObjects/PersistentStagingSqlServerGenerateTable.handlebars.md)
      - [Source Area Generate Table](../Templates/DataObjects/SourceSqlServerGenerateTable.handlebars.md)
    - Other
      - [Deployment](../Templates/Other/Container.handlebars.md)
      - [Control Framework Registration](../Templates/Other/ControlFrameworkRegistration.handlebars.md)
      - [Databases](../Templates/Other/Databases.handlebars.md)
      - [Deployment](../Templates/Other/Deployment.handlebars.md)
      - [Documentation](../Templates/Other/Documentation.handlebars.md)
      - [Readme](../Templates/Other/Readme.handlebars.md)
      - [Sample Data - SaveMore Source System](../Templates/Other/SampleDataSqlServer.handlebars.md)
  - [Phase one: CBS OData extraction with event-based orchestration](../plan1.md)
  - [Phase two: minimal Dutch government OData ingestion with event-based orchestration](../plan2.md)
  - [Phase three: JSON-configured Dutch government OData ingestion](../plan3.md)
- Related repositories
  - [cursor-config](https://github.com/basvdberg/cursor-config)
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026)
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns)
<!-- markdown-project-structure:end -->
