# Code (generated runtime)

## Table of contents

<!-- markdown-toc:start -->
- [Purpose](#purpose)
- [Layout](#layout)
- [Relationship to metadata](#relationship-to-metadata)
- [Airflow](#airflow)
<!-- markdown-toc:end -->

## Purpose

This folder holds **generated and hand-maintained runtime code** that implements *how* the data solution runs on BasNAS: orchestration (Airflow), future event controllers, and similar artefacts.

It is separate from:

| Location | Role |
|----------|------|
| `data-object-mapping/`, `data-object/`, `connection/` | DSA metadata — *what* should happen |
| `extractor_and_poller/` | Shared Python libraries invoked by DAG tasks |
| `output/` | ADL-generated SQL |
| `infra/` | Docker Compose and deploy scripts (no application DAG source) |

## Layout

```text
code/
  readme.md
  airflow/
    readme.md
    dags/
      openmeteo_data_object_poller.py
```

Add new generated components under `code/` (for example `code/event-controller/` when the Kafka consumer is implemented).

## Relationship to metadata

Configuration stays in Git as JSON under `data-object-mapping/`. DAGs and services in `code/` call into `extractor_and_poller` using mapping and data-object ids from that metadata. See [Separate what and how](https://github.com/basvdberg/data-engineering-design-patterns/blob/main/design-patterns/generic/separate-what-and-how.md).

## Airflow

DAGs live in [airflow/dags/](airflow/dags/). The Airflow container mounts `${DATA_SOLUTION_ROOT}/code/airflow/dags` (see [infra/airflow/docker-compose.standalone.yaml](../infra/airflow/docker-compose.standalone.yaml)).

Rollout steps: [Implementation plan](../doc/implementation-plan.md).

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
      - V2026.06.03.3
    - Notes
      - [Release v2026.06.02.1](../release/notes/v2026.06.02.1.md)
      - [Release v2026.06.02.2](../release/notes/v2026.06.02.2.md)
      - [Release v2026.06.03.1](../release/notes/v2026.06.03.1.md)
      - [Release v2026.06.03.2](../release/notes/v2026.06.03.2.md)
      - [Release v2026.06.03.3](../release/notes/v2026.06.03.3.md)
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
