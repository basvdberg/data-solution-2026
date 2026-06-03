# Extractor and poller

## Table of contents

<!-- markdown-toc:start -->
- [Overview](#overview)
<!-- markdown-toc:end -->

## Overview

Open-Meteo extractor and poller driven by `data-object-mapping/` JSON.

Run from the solution root (`data-solution-2026/`):

```powershell
# List Enabled data object poller
python -m extractor_and_poller.poller --list

# Poll source/openmeteo/daily-temperature
python -m extractor_and_poller.poller --mapping daily-temperature

# Run extractor for OpenMeteo data object
python -m extractor_and_poller.openmeteo.extractor --mapping daily-temperature
```

Event-oriented poller options:

```powershell
# Persist state in Postgres and publish envelopes to Kafka
python -m extractor_and_poller.poller --mapping daily-temperature --state-backend postgres --publish kafka

# Local smoke run: publish event payloads to stdout
python -m extractor_and_poller.poller --mapping daily-temperature --publish stdout
```

The `openmeteo/` subfolder holds the `extractor/` and `poller/` packages. Shared helpers live under `common/`; the generic poller CLI is in `poller/`.

Airflow DAGs that call these modules live under [`code/airflow/`](../code/airflow/readme.md).

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](../readme.md)
  - Code
    - Airflow
      - Dags
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
      - [Architecture](../doc/design/architecture.md)
      - [CI/CD workflow (main only + server pull deploy)](../doc/design/ci-cd.md)
      - [Event-based orchestration plan (single data object)](../doc/design/event-based-orchestration-plan.md)
      - [Meta data design](../doc/design/meta-data-design.md)
    - [Implementation plan (Open-Meteo → event orchestration)](../doc/implementation-plan.md)
  - Extractor_And_Poller
    - Common
    - Openmeteo
      - Extractor
      - Poller
    - Poller
    - Tests
  - Infra
    - Airflow
      - Dags
    - Kafka
  - Release
    - Details
      - V2026.06.02.1
      - V2026.06.02.2
      - V2026.06.03.1
      - V2026.06.03.2
    - Notes
      - [Release v2026.06.02.1](../release/notes/v2026.06.02.1.md)
      - [Release v2026.06.02.2](../release/notes/v2026.06.02.2.md)
      - [Release v2026.06.03.1](../release/notes/v2026.06.03.1.md)
      - [Release v2026.06.03.2](../release/notes/v2026.06.03.2.md)
    - [Release <version>](../release/release-notes-template.md)
  - Setting
  - Template
  - [Getting started](../getting-started.md)
  - [Lessons learned](../lessons-learned-part1.md)
  - [Lessons learned (part 2)](../lessons-learned-part2.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
