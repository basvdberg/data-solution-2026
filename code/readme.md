# Code (generated runtime)

## Table of contents

<!-- markdown-toc:start -->
- [Purpose](#purpose)
- [Layout](#layout)
- [Relationship to metadata](#relationship-to-metadata)
- [Airflow](#airflow)
- [Postgres metadata](#postgres-metadata)
<!-- markdown-toc:end -->

## Purpose

This folder holds **generated and hand-maintained runtime code** that implements *how* the data solution runs on BasNAS: orchestration (Airflow), extractor/poller libraries, Postgres schema, and future event controllers.

It is separate from:

| Location | Role |
|----------|------|
| `data-object-mapping/`, `data-object/`, `connection/` | DSA metadata — *what* should happen |
| `data/` | Landing files (Parquet); gitignored |
| `output/` | ADL-generated SQL |
| `infra/` | Docker Compose and deploy scripts |

## Layout

```text
code/
  readme.md
  postgres/
    schema.sql              # table poller (+ future audit tables)
  extractor_and_poller/     # Open-Meteo extractor and generic poller CLI
  airflow/
    readme.md
    dags/
      openmeteo_data_object_poller.py
```

## Relationship to metadata

Configuration stays in Git as JSON under `data-object-mapping/`. DAGs and libraries in `code/` read those ids. Runtime state (poller history, markers) is stored in Postgres (`connection/metadata-postgres.json`), not in the repo.

## Airflow

DAGs live in [airflow/dags/](airflow/dags/). The Airflow container mounts `${DATA_SOLUTION_ROOT}/code/airflow/dags` and sets `PYTHONPATH=/opt/data-solution/code:/opt/data-solution`.

## Postgres metadata

- Schema reference: [postgres/schema.sql](postgres/schema.sql)
- Compose stack: [infra/postgres](../infra/postgres/docker-compose.yml)
- Poller rows: table `poller` with `data_object_id`, `polled_at_utc`, `old_marker`, `new_marker`, and event envelope fields

Rollout: [Implementation plan](../doc/implementation-plan.md).

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](../readme.md)
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
      - [Architecture](../doc/design/architecture.md)
      - [CI/CD workflow (main only + server pull deploy)](../doc/design/ci-cd.md)
      - [Event-based orchestration plan (single data object)](../doc/design/event-based-orchestration-plan.md)
      - [Meta data design](../doc/design/meta-data-design.md)
    - [Implementation plan (Open-Meteo → event orchestration)](../doc/implementation-plan.md)
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
      - [Release v2026.06.02.1](../release/notes/v2026.06.02.1.md)
      - [Release v2026.06.02.2](../release/notes/v2026.06.02.2.md)
      - [Release v2026.06.03.1](../release/notes/v2026.06.03.1.md)
      - [Release v2026.06.03.2](../release/notes/v2026.06.03.2.md)
      - [Release v2026.06.03.3](../release/notes/v2026.06.03.3.md)
      - [Release v2026.06.03.4](../release/notes/v2026.06.03.4.md)
      - [V2026.06.04.1](../release/notes/v2026.06.04.1.md)
      - [V2026.06.04.2](../release/notes/v2026.06.04.2.md)
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
