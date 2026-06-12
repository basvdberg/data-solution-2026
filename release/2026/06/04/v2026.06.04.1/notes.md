## Table of contents

<!-- markdown-toc:start -->
- [Metadata](#metadata)
- [Scope](#scope)
- [Changes](#changes)
- [Poller and Airflow impact](#poller-and-airflow-impact)
- [Deployment steps](#deployment-steps)
- [Validation](#validation)
- [Rollback plan](#rollback-plan)
- [Notes](#notes)
<!-- markdown-toc:end -->

## Table of contents


﻿# Release v2026.06.04.1

## Metadata

- Version: `v2026.06.04.1`
- Date: `2026-06-04`
- Branch: `main`
- Commit: `<fill-after-commit>`

## Scope

- Poller metadata in Postgres; runtime libraries under `code/`; Postgres infra for the local server.

## Changes

- Added:
  - Postgres stack (`infra/postgres/`), table `poller` schema (`code/postgres/schema.sql`), `connection/metadata-postgres.json`.
- Changed:
  - Poller persists state only to Postgres (removed CSV/file backend).
  - Moved `extractor_and_poller/` to `code/extractor_and_poller/`; Airflow `PYTHONPATH` includes `/opt/data-solution/code`.
  - `deploy-infra-on-nas.sh` starts Postgres before Airflow/Kafka.
- Fixed:
  - Poller no longer writes under `data/` for state (avoids read-only repo mount failures).

## Poller and Airflow impact

- Poller mapping: `source/openmeteo/daily-temperature` (unchanged).
- Airflow DAG (`code/airflow/dags/openmeteo_data_object_poller.py`): Postgres-only; removed `poller_state_backend` variable.
- Runtime variables: `POSTGRES_HOST`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `DATA_SOLUTION_DB` (default `data-solution-2026`).

## Deployment steps

- Auto deployment trigger: push to `main`
- NAS actions required after deploy:
  - [ ] Dependencies updated
  - [ ] Services restarted
  - [ ] Airflow DAGs available

## Validation

- [ ] Unit tests passed
- [ ] Integration checks passed
- [ ] Airflow poller manual run passed
- [ ] Kafka publish verified (or stdout in smoke mode)
- [ ] Postgres state persistence verified

## Rollback plan

- Previous stable tag: `v2026.06.03.3`
- Rollback command:

```bash
cd ~/apps/data-solution-2026
git fetch --all --tags
git checkout v2026.06.03.3
docker compose up -d
```

## Notes

- Additional operational notes.

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](../../../../../readme.md)
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
      - [Architecture](../../../../../doc/design/architecture.md)
      - [CI/CD workflow (main only + server pull deploy)](../../../../../doc/design/ci-cd.md)
      - [Event-based orchestration plan (single data object)](../../../../../doc/design/event-based-orchestration-plan.md)
      - [Kafka topic naming](../../../../../doc/design/kafka-topic-naming.md)
      - [Meta data design](../../../../../doc/design/meta-data-design.md)
    - Image
    - Implementation
      - [Implementation plan (Open-Meteo → event orchestration)](../../../../../doc/implementation/implementation-plan.md)
    - Linked In
      - [Linkedin Post Part3V2](../../../../../doc/linked-in/linkedin-post-part3v2.md)
    - Operation
      - Incident
        - [INC-001 — NAS non-interactive SSH environment](../../../../../doc/operation/incident/inc-001-nas-ssh-environment.md)
        - [INC-002 — Airflow standalone infra instability](../../../../../doc/operation/incident/inc-002-airflow-infra-stability.md)
        - [INC-003 — Agent rediscovery and false-done verification](../../../../../doc/operation/incident/inc-003-agent-process-gaps.md)
        - [INC-004 — Airflow PYTHONPATH drift (dag_run_guard import)](../../../../../doc/operation/incident/inc-004-airflow-pythonpath-drift.md)
        - [INC-<NNN> — <short title>](../../../../../doc/operation/incident/incident-template.md)
      - [Event orchestration monitoring](../../../../../doc/operation/event-orchestration-monitoring.md)
      - [Issue categories](../../../../../doc/operation/issue-category.md)
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
            - [Notes](../../02/v2026.06.02.1/notes.md)
          - V2026.06.02.2
            - [Release v2026.06.02.2](../../02/v2026.06.02.2/notes.md)
        - 03
          - V2026.06.03.1
            - [Release v2026.06.03.1](../../03/v2026.06.03.1/notes.md)
          - V2026.06.03.2
            - [Release v2026.06.03.2](../../03/v2026.06.03.2/notes.md)
          - V2026.06.03.3
            - [Release v2026.06.03.3](../../03/v2026.06.03.3/notes.md)
          - V2026.06.03.4
            - [Release v2026.06.03.4](../../03/v2026.06.03.4/notes.md)
            - [Retrospective](../../03/v2026.06.03.4/retrospective.md)
        - 04
          - V2026.06.04.1
            - [Notes](notes.md)
        - 05
          - V2026.06.05.6
            - [Notes](../../05/v2026.06.05.6/notes.md)
            - [Retrospective](../../05/v2026.06.05.6/retrospective.md)
        - 12
          - V2026.06.12.1
            - [Release v2026.06.12.1](../../12/v2026.06.12.1/notes.md)
    - [Release <version>](../../../../release-notes-template.md)
    - [Retrospective — <version>](../../../../retrospective-template.md)
  - [Getting started](../../../../../getting-started.md)
  - [Lessons learned](../../../../../lessons-learned-part1.md)
  - [Lessons learned (part 2)](../../../../../lessons-learned-part2.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
