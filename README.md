# Data Solution 2026

## Table of contents

<!-- markdown-toc:start -->
- [Purpose](#purpose)
- [Proof of concept](#proof-of-concept)
  - [Architecture](#architecture)
  - [Stale KNMI WFS feed (superseded)](#stale-knmi-wfs-feed-superseded)
  - [Lessons learned](#lessons-learned)
    - [Data extraction via API](#data-extraction-via-api)
    - [Learning new tools](#learning-new-tools)
    - [Agnostic Data Labs](#agnostic-data-labs)
<!-- markdown-toc:end -->

> [!WARNING]
> **This project is under construction.** Please check back later, or [watch the repository](https://github.com/basvdberg/data-solution-2026/watchers) on GitHub for updates.

## Purpose

Proof of concept for the GenAI way of working described in [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026). Design intent for orchestration and metadata shape is captured in [data-engineering-design-patterns](https://github.com/basvdberg/data-engineering-design-patterns).

## Proof of concept

This PoC implements a staging layer for Dutch weather data (KNMI) from the [KNMI Data Platform Open Data API](https://developer.dataplatform.knmi.nl/open-data-api). [Agnostic Data Labs (ADL)](https://docs.agnosticdatalabs.com/docs/) visualizes transformations and lineage; the repository keeps a fixed folder layout so ADL can categorize DSA metadata consistently.

Python extraction code was generated with GenAI. Orchestration follows patterns from [data-engineering-design-patterns](https://github.com/basvdberg/data-engineering-design-patterns); AI-assisted tool selection led to Apache Airflow and Apache Kafka for this use case.

### Architecture

![Architecture](docs/architecture-staging.png)

The flow, left to right:

1. **Git holds the configuration.** `data-object-mapping/staging/knmi/` describes the KNMI source (Open Data API); staging targets and loads are defined in the same DSA metadata. Design patterns set the shape of the orchestration.
2. **Airflow + Kafka run the ingestion.** The change-detector DAG polls the KDP file catalog on schedule and emits a `source_change` event when a new daily NetCDF appears. The event controller turns matching events into `extract` commands. The KNMI extractor (`python -m extractor.knmi`) downloads and flattens NetCDF to Parquet under `data/staging/knmi/`. PostgreSQL stores checkpoints and the event log only—no configuration.
3. **ADL generates staging artefacts.** Reading the same DSA metadata, ADL renders the Handlebars templates in `Templates/` into DDL and load SQL under `Output/`, which load the Parquet landing files into the **100 Landing Area**.

This solution follows the [separate what and how](https://github.com/basvdberg/data-engineering-design-patterns/blob/main/design-patterns/separate-what-and-how.md) design pattern: the DSA metadata files specify *what* must happen for each source and target, while the Airflow DAGs, extractors, poller, and ADL-generated load procedures are the implementation that specifies *how* it is executed.

### Stale KNMI WFS feed (superseded)

The original PoC used the INSPIRE **WFS 2.0** endpoint on `haleconnect.com` (*Gecontroleerde klimatologische daggegevens*). That service still responds, but embedded observation data **stopped updating around 2023-09-01** across all stations—the poller correctly reported that date, not a bug.

| Source | Freshness | Status in this repo |
|--------|-----------|---------------------|
| haleconnect INSPIRE WFS | Frozen ~2023-09 | **Replaced** — `extractor/wfs/` kept for reference only |
| [KDP Open Data API](https://dataplatform.knmi.nl/dataset/daily-in-situ-meteorological-observations-1-0) | Nightly `daily-observations-*.nc` | **Active** — mapping `knmi-daggegevens.json`, poller `interface_type:knmi_open_data` |

Set `KNMI_API_KEY` (register at [developer.dataplatform.knmi.nl](https://developer.dataplatform.knmi.nl/open-data-api)) and run:

```powershell
python -m poller --probe-only --mapping knmi-daggegevens-temperature
python -m extractor.knmi --mapping knmi-daggegevens-temperature
```

Details: [extractor/knmi/README.md](extractor/knmi/README.md), [data object poller plan](plan/data-object-poller/airflow-kafka.md).

### Lessons learned

#### Data extraction via API

**Before:** Extracting from a source with a well-defined API typically took one to two weeks—collecting and reading sometimes incomplete documentation, then iteratively building and testing the client.

**After:** With generative AI (Cursor in this project), extraction code for OData, WFS, and KNMI Open Data was produced in a handful of prompts. End-to-end validation, including a smoke test against the live service, fit within about an hour.

**Takeaway:** A large efficiency gain, and in this PoC the generated client code was stronger and faster to test than a typical hand-written first version.

#### Learning new tools

**Before:** Learning Airflow, Kafka, ADL, or a new protocol client is normal work, but it often costs weeks of courses and trial-and-error before you ship confidently.

**After:** AI explains how a tool fits a concrete use case in *your* architecture and generates starter code (DAGs, parsers, mapping JSON). You learn from working examples without mastering every aspect of the tool first. That shortens time-to-market for new tooling, makes it easier to compare or replace components, and supports a more technology-agnostic architecture.

#### Agnostic Data Labs
Although I'm Impressed. By the look and feel Plus the offered functionalities of this tool. I hit some Showstoppers. Like 
1. I generated a JSON file According to the Published Automation schema But this wasn't read correctly by the tool. And there was no easy way to find out what was going on. 
2. the tool converts the json into elemental components. This alters the underlying json representation. Maybe it makes sense to represent elemental components in the first place instead of DataObjectMappings.

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](readme.md)
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
      - [Data object poller — Airflow + Kafka implementation](plan/data-object-poller/airflow-kafka.md)
    - [Phase one: CBS OData extraction with event-based orchestration](plan/plan1.md)
    - [Phase two: minimal Dutch government OData ingestion with event-based orchestration](plan/plan2.md)
    - [Phase three: JSON-configured Dutch government OData ingestion](plan/plan3.md)
  - Poller
  - Schema
    - [Schema follow-ups](schema/data-objects-schema.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026)
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns)
<!-- markdown-project-structure:end -->
