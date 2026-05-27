# Data Solution 2026

## Table of contents

<!-- markdown-toc:start -->
- [Purpose](#purpose)
- [Proof of concept](#proof-of-concept)
  - [Architecture](#architecture)
  - [Run the PoC](#run-the-poc)
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

This PoC implements a **staging layer** for daily mean temperature across the Netherlands. The source is [Open-Meteo](https://open-meteo.com/) — no API key, models refreshed continuously. [Agnostic Data Labs (ADL)](https://docs.agnosticdatalabs.com/docs/) visualizes transformations and lineage; the repository keeps a fixed folder layout so ADL can categorize DSA metadata consistently.

Python extraction code was generated with GenAI. Orchestration follows patterns from [data-engineering-design-patterns](https://github.com/basvdberg/data-engineering-design-patterns); AI-assisted tool selection led to Apache Airflow and Apache Kafka for this use case.

### Architecture

![Architecture](doc/architecture-staging.png)

The flow, left to right:

1. **Git holds the configuration.** `data-object-mapping/staging/openmeteo/` describes the source; staging targets and loads are defined in the same DSA metadata. Design patterns set the shape of the orchestration.
2. **Airflow + Kafka run ingestion.** A scheduled **poller** DAG probes the source and publishes only to the event bus: `data_object_change` when the marker moved, `data_object_progress` when it did not. The event controller reacts to **change** events and enqueues **extract** tasks; the extractor writes Parquet under `data/staging/`. The poller never runs the extractor. PostgreSQL stores baselines and the event log — configuration stays in Git.
3. **ADL generates staging artefacts.** Reading the same DSA metadata, ADL renders the Handlebars templates in `template/` into DDL and load SQL under `output/`, which load the Parquet landing files into the **100 Landing Area**.

This solution follows the [separate what and how](https://github.com/basvdberg/data-engineering-design-patterns/blob/main/design-patterns/separate-what-and-how.md) design pattern: DSA metadata files specify *what* must happen, while the Airflow DAGs, extractor, poller, and ADL-generated load procedures specify *how* it is executed.

### Run the PoC

```powershell
# Poller: detect + signal event bus (change or progress)
python -m extractor_and_poller.poller --mapping daily-temperature

# Extractor: run separately when orchestration handles a change event
python -m extractor_and_poller.openmeteo.extractor --mapping daily-temperature
```

Open-Meteo blends national models into a gridded daily mean at reference coordinates. Data is [CC BY 4.0](https://open-meteo.com/); attribute Open-Meteo in production use.

Details: [extractor_and_poller/openmeteo/](extractor_and_poller/openmeteo/).

### Lessons learned

#### Data extraction via API

**Before:** Extracting from a source with a well-defined API typically took one to two weeks — collecting and reading sometimes incomplete documentation, then iteratively building and testing the client.

**After:** With generative AI (Cursor in this project), the Open-Meteo extractor was produced in a handful of prompts. End-to-end validation, including a smoke test against the live service, fit within about an hour.

**Takeaway:** A large efficiency gain, and in this PoC the generated client code was stronger and faster to test than a typical hand-written first version.

#### Learning new tools

**Before:** Learning Airflow, Kafka, ADL, or a new protocol client is normal work, but it often costs weeks of courses and trial-and-error before you ship confidently.

**After:** AI explains how a tool fits a concrete use case in *your* architecture and generates starter code (DAGs, parsers, mapping JSON). You learn from working examples without mastering every aspect of the tool first. That shortens time-to-market for new tooling, makes it easier to compare or replace components, and supports a more technology-agnostic architecture.

#### Agnostic Data Labs

Although the look, feel, and offered functionalities of this tool are impressive, I hit some showstoppers:

1. A JSON file generated according to the published automation schema was not read correctly by the tool, with no easy way to find out what was going on.
2. The tool converts the JSON into elemental components. This alters the underlying JSON representation. It may make sense to represent elemental components in the first place instead of `DataObjectMappings`.

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
