# Extractor and poller

## Table of contents

<!-- markdown-toc:start -->
- [Layout](#layout)
- [CLI](#cli)
<!-- markdown-toc:end -->

This folder implements the [data extractor](../../data-engineering-design-patterns/design-patterns/data-extractor.md) and [data object poller](../../data-engineering-design-patterns/design-patterns/data-object-poller.md) design patterns.

Together they support ingestion of any kind of **data object**: a logical unit of data at a source you want to land in staging. The same pattern applies regardless of where that object lives—for example:

- public data on a public HTTP API (Open-Meteo, OData, KNMI Open Data)
- a CSV file on a network share
- a table in a SQL Server database on the local network

Each source type is wired through **data-object-mapping** JSON (under `data-object-mapping/` in the project root). A **poller** probes a lightweight change marker and signals when the object changed; an **extractor** reads the full payload and writes landing files (Parquet under `data/staging/` in this PoC).

## Layout

Per protocol or interface, code is grouped as `{protocol}/extractor` (land data) and `{protocol}/poller` (change detection). Shared configuration and helpers live under `common/`.

Current reference implementations in this repo include Open-Meteo, OData, WFS, and KNMI Open Data. Additional protocols (file share, relational database, and others) follow the same split: protocol-specific probe + extract, driven by mapping metadata.

## CLI

From the `data-solution-2026` project root:

```powershell
python -m extractor_and_poller.poller --mapping openmeteo-daily-temperature
python -m extractor_and_poller.openmeteo.extractor --mapping openmeteo-daily-temperature
```

See the [project readme](../readme.md) for orchestration context (Airflow, Kafka, and event-based extraction).

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
  - Extractor_And_Poller
    - Common
    - Knmi
      - Extractor
      - Poller
    - Odata
      - Extractor
      - Poller
    - Openmeteo
      - Extractor
      - Poller
    - Poller
    - Tests
    - Wfs
      - Extractor
      - Poller
  - Plan
    - Data Object Poller
      - [Data object poller — Airflow + Kafka implementation](../plan/data-object-poller/airflow-kafka.md)
    - [Phase one: CBS OData extraction with event-based orchestration](../plan/plan1.md)
    - [Phase two: minimal Dutch government OData ingestion with event-based orchestration](../plan/plan2.md)
    - [Phase three: JSON-configured Dutch government OData ingestion](../plan/plan3.md)
  - Schema
    - [Schema follow-ups](../schema/data-objects-schema.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026)
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns)
<!-- markdown-project-structure:end -->
