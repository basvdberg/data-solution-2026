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

This folder holds **generated and hand-maintained runtime code** that implements *how* the data solution runs on the local server: orchestration (Airflow), extractor/poller libraries, Postgres schema, and Airflow Kafka handlers (`code/airflow/include/`).

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
      - Include
      - Plugins
    - Extractor_And_Poller
      - Common
      - Extract
      - Openmeteo
        - Extractor
        - Poller
      - Poller
      - Tests
    - Postgres
      - Migrations
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
    - Data Object Mapping
    - Design
      - [Architecture](../doc/design/architecture.md)
      - [CI/CD workflow (main only + server pull deploy)](../doc/design/ci-cd.md)
      - [Event-based orchestration plan (single data object)](../doc/design/event-based-orchestration-plan.md)
      - [Kafka topic naming](../doc/design/kafka-topic-naming.md)
      - [Meta data design](../doc/design/meta-data-design.md)
    - Image
    - Implementation
      - [Implementation plan (Open-Meteo → event orchestration)](../doc/implementation/implementation-plan.md)
    - Linked In
      - [Linkedin Post Part3V2](../doc/linked-in/linkedin-post-part3v2.md)
    - Operation
      - Incident
        - [INC-001 — NAS non-interactive SSH environment](../doc/operation/incident/inc-001-nas-ssh-environment.md)
        - [INC-002 — Airflow standalone infra instability](../doc/operation/incident/inc-002-airflow-infra-stability.md)
        - [INC-003 — Agent rediscovery and false-done verification](../doc/operation/incident/inc-003-agent-process-gaps.md)
        - [INC-004 — Airflow PYTHONPATH drift (dag_run_guard import)](../doc/operation/incident/inc-004-airflow-pythonpath-drift.md)
        - [INC-<NNN> — <short title>](../doc/operation/incident/incident-template.md)
      - [Event orchestration monitoring](../doc/operation/event-orchestration-monitoring.md)
      - [Issue categories](../doc/operation/issue-category.md)
  - Infra
    - Airflow
      - Dags
    - Kafka
    - Postgres
  - Release
    - 2026
      - 06
        - 02
          - V2026.06.02.1
            - [Notes](../release/2026/06/02/v2026.06.02.1/notes.md)
          - V2026.06.02.2
            - [Release v2026.06.02.2](../release/2026/06/02/v2026.06.02.2/notes.md)
        - 03
          - V2026.06.03.1
            - [Release v2026.06.03.1](../release/2026/06/03/v2026.06.03.1/notes.md)
          - V2026.06.03.2
            - [Release v2026.06.03.2](../release/2026/06/03/v2026.06.03.2/notes.md)
          - V2026.06.03.3
            - [Release v2026.06.03.3](../release/2026/06/03/v2026.06.03.3/notes.md)
          - V2026.06.03.4
            - [Release v2026.06.03.4](../release/2026/06/03/v2026.06.03.4/notes.md)
            - [Retrospective](../release/2026/06/03/v2026.06.03.4/retrospective.md)
        - 04
          - V2026.06.04.1
            - [Notes](../release/2026/06/04/v2026.06.04.1/notes.md)
        - 05
          - V2026.06.05.6
            - [Notes](../release/2026/06/05/v2026.06.05.6/notes.md)
            - [Retrospective](../release/2026/06/05/v2026.06.05.6/retrospective.md)
        - 12
          - V2026.06.12.1
            - [Release v2026.06.12.1](../release/2026/06/12/v2026.06.12.1/notes.md)
    - [Release <version>](../release/release-notes-template.md)
    - [Retrospective — <version>](../release/retrospective-template.md)
  - [Getting started](../getting-started.md)
  - [Lessons learned](../lessons-learned-part1.md)
  - [Lessons learned (part 2)](../lessons-learned-part2.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
