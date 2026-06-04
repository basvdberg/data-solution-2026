# Getting started

## Table of contents

<!-- markdown-toc:start -->
- [Prerequisites](#prerequisites)
- [Quick start](#quick-start)
- [Infrastructure (Docker)](#infrastructure-docker)
- [Run key components](#run-key-components)
<!-- markdown-toc:end -->

## Prerequisites

- Python 3.11+
- Dependencies installed for `data-solution-2026` (including `psycopg[binary]` for poller metadata and optional `kafka-python` for event publish)
- Postgres running with database `data-solution-2026` (see [infra/postgres](infra/postgres/docker-compose.yml))
- Run commands from the `data-solution-2026/` root

## Quick start

```powershell
cd "c:\Dev2\Data Engineering 2.0\data-solution-2026"
```

## Infrastructure (Docker)

Airflow and Kafka Compose files for BasNAS: [infra/readme.md](infra/readme.md).

Airflow DAGs (generated orchestration): [code/airflow/readme.md](code/airflow/readme.md).

## Run key components

```powershell
$env:PYTHONPATH = "code"

# 1) List enabled data object poller entries
python -m extractor_and_poller.poller --list

# 2) Poll source/openmeteo/daily-temperature (requires Postgres; see infra/postgres)
python -m extractor_and_poller.poller --data-object source/openmeteo/daily-temperature

# 3) Run extractor for OpenMeteo data object
python -m extractor_and_poller.openmeteo.extractor --mapping daily-temperature
```

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](readme.md)
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
      - [Architecture](doc/design/architecture.md)
      - [CI/CD workflow (main only + server pull deploy)](doc/design/ci-cd.md)
      - [Event-based orchestration plan (single data object)](doc/design/event-based-orchestration-plan.md)
      - [Meta data design](doc/design/meta-data-design.md)
    - [Implementation plan (Open-Meteo → event orchestration)](doc/implementation-plan.md)
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
      - ﻿V2026.06.04.1
      - ﻿V2026.06.04.2
    - Notes
      - [Release v2026.06.02.1](release/notes/v2026.06.02.1.md)
      - [Release v2026.06.02.2](release/notes/v2026.06.02.2.md)
      - [Release v2026.06.03.1](release/notes/v2026.06.03.1.md)
      - [Release v2026.06.03.2](release/notes/v2026.06.03.2.md)
      - [Release v2026.06.03.3](release/notes/v2026.06.03.3.md)
      - [Release v2026.06.03.4](release/notes/v2026.06.03.4.md)
      - [V2026.06.04.1](release/notes/v2026.06.04.1.md)
      - [V2026.06.04.2](release/notes/v2026.06.04.2.md)
      - [V2026.06.04.3](release/notes/v2026.06.04.3.md)
    - [Release <version>](release/release-notes-template.md)
  - Setting
  - Template
  - [Getting started](getting-started.md)
  - [Lessons learned](lessons-learned-part1.md)
  - [Lessons learned (part 2)](lessons-learned-part2.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
