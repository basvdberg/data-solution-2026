# Extractor and poller

## Table of contents

<!-- markdown-toc:start -->
- [Overview](#overview)
- [Poller metadata](#poller-metadata)
<!-- markdown-toc:end -->

## Overview

Open-Meteo extractor and poller driven by `data-object-mapping/` JSON. Lives under `code/extractor_and_poller/` (runtime *how* code).

Run from the solution root with `code/` on `PYTHONPATH`:

```powershell
cd "c:\Dev2\Data Engineering 2.0\data-solution-2026"
$env:PYTHONPATH = "code"
python -m extractor_and_poller.poller --list
python -m extractor_and_poller.poller --data-object source/openmeteo/daily-temperature
python -m extractor_and_poller.openmeteo.extractor --mapping daily-temperature
```

Event-oriented poller options:

```powershell
# Publish event envelopes to stdout or Kafka (state always in Postgres)
python -m extractor_and_poller.poller --data-object source/openmeteo/daily-temperature --publish stdout
python -m extractor_and_poller.poller --data-object source/openmeteo/daily-temperature --publish kafka
```

The `openmeteo/` subfolder holds `extractor/` and `poller/` probes. Shared helpers live under `common/`; the generic poller CLI is in `poller/`.

Airflow DAGs: [`code/airflow/`](../airflow/readme.md).

## Poller metadata

- No local files or directories are created by the poller.
- Each run appends one row to Postgres table `poller` (see [../postgres/schema.sql](../postgres/schema.sql)).
- Environment: `POSTGRES_HOST`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` (default `data_solution`), or `POSTGRES_DSN`.

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](../../readme.md)
  - Code
    - Airflow
      - Dags
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
      - [Architecture](../../doc/design/architecture.md)
      - [CI/CD workflow (main only + server pull deploy)](../../doc/design/ci-cd.md)
      - [Event-based orchestration plan (single data object)](../../doc/design/event-based-orchestration-plan.md)
      - [Meta data design](../../doc/design/meta-data-design.md)
    - [Implementation plan (Open-Meteo → event orchestration)](../../doc/implementation-plan.md)
  - Extractor_And_Poller
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
      - ﻿V2026.06.04.1
      - ﻿V2026.06.04.2
    - Notes
      - [Release v2026.06.02.1](../../release/notes/v2026.06.02.1.md)
      - [Release v2026.06.02.2](../../release/notes/v2026.06.02.2.md)
      - [Release v2026.06.03.1](../../release/notes/v2026.06.03.1.md)
      - [Release v2026.06.03.2](../../release/notes/v2026.06.03.2.md)
      - [Release v2026.06.03.3](../../release/notes/v2026.06.03.3.md)
      - [Release v2026.06.03.4](../../release/notes/v2026.06.03.4.md)
      - [V2026.06.04.1](../../release/notes/v2026.06.04.1.md)
      - [V2026.06.04.2](../../release/notes/v2026.06.04.2.md)
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
