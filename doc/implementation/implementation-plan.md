# Implementation plan (Open-Meteo → event orchestration)

## Table of contents

<!-- markdown-toc:start -->
- [Purpose](#purpose)
- [Step 1 — Poller probe and Postgres audit](#step-1-poller-probe-and-postgres-audit)
- [Step 2 — Source change asset emit](#step-2-source-change-asset-emit)
- [Step 3 — Asset-scheduled extract](#step-3-asset-scheduled-extract)
- [Step 4 — Staging outcome events](#step-4-staging-outcome-events)
- [Verification](#verification)
<!-- markdown-toc:end -->

## Purpose

Checklist for implementing [Event-based orchestration plan](design/event-based-orchestration-plan.md) for `data-object-mapping/staging/openmeteo/daily-temperature`.

## Step 1 — Poller probe and Postgres audit

- [x] Open-Meteo probe returns observation-day marker
- [x] Compare marker to previous row in `public.poller`
- [x] Persist `data_object_change` or `data_object_unchanged` per probe
- [x] Poller DAG `@hourly` aligned with source `refreshContract`

Code: `code/extractor_and_poller/poller/`, `code/airflow/include/poll_run.py`.

## Step 2 — Source change asset emit

- [x] Branch on `event_type == data_object_change`
- [x] Emit Airflow Asset `ds://source/openmeteo/daily-temperature/change` with extract conf extra
- [x] Unchanged runs complete without asset emit

Code: `code/airflow/dags/openmeteo_data_object_poller.py`.

## Step 3 — Asset-scheduled extract

- [x] Extract DAG `schedule=[source_change_asset]`
- [x] Build extract conf from asset extra (`mapping_id`, `marker`, `event_id`)
- [x] Idempotency via `extract_run_audit` on `event_id`

Code: `code/airflow/dags/openmeteo_daily_temperature_extract.py`, `code/extractor_and_poller/openmeteo/extractor/`.

## Step 4 — Staging outcome events

- [x] On success: `extract_run_audit.event_type = data_object_change`, emit staging asset `ds://staging/openmeteo/daily-temperature/change`
- [x] On failure: `extract_run_audit.event_type = processing_error`, structured error log, Airflow task failure

Code: `code/extractor_and_poller/extract/run.py`, extract DAG `emit_staging_data_change_event`.

## Verification

- Unit tests: `python -m pytest code/extractor_and_poller/tests/ -q`
- Postgres: query `poller_latest_first` and `extract_run_audit` (see [Event orchestration monitoring](operation/event-orchestration-monitoring.md))
- Airflow: trigger poller DAG manually or wait for hourly run; confirm extract DAG runs on change asset

Related: [Airflow asset naming](design/airflow-asset-naming.md), [Meta data design](design/meta-data-design.md).

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](../../readme.md)
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
      - Cicd
        - [CI/CD workflow (main only + server pull deploy)](../design/cicd/ci-cd.md)
      - Monitoring
        - [Monitoring architecture](../design/monitoring/monitoring-architecture.md)
      - [Airflow asset naming](../design/airflow-asset-naming.md)
      - [Event-based orchestration plan](../design/event-based-orchestration-plan.md)
      - [Meta data design](../design/meta-data-design.md)
    - Image
    - Implementation
      - [Implementation plan (Open-Meteo → event orchestration)](implementation-plan.md)
    - Linked In
      - [Linkedin Post Part3V2](../linked-in/linkedin-post-part3v2.md)
    - Operation
      - [Event orchestration monitoring](../operation/event-orchestration-monitoring.md)
    - Retrospective
      - Incident
        - [INC-001 — NAS non-interactive SSH environment](../retrospective/incident/inc-001-nas-ssh-environment.md)
        - [INC-002 — Airflow standalone infra instability](../retrospective/incident/inc-002-airflow-infra-stability.md)
        - [INC-003 — Agent rediscovery and false-done verification](../retrospective/incident/inc-003-agent-process-gaps.md)
        - [INC-004 — Airflow PYTHONPATH drift (dag_run_guard import)](../retrospective/incident/inc-004-airflow-pythonpath-drift.md)
        - [INC-<NNN> — <short title>](../retrospective/incident/incident-template.md)
      - [Issue categories](../retrospective/issue-category.md)
    - [Implementation plan](../implementation-plan.md)
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
            - [Notes](../../release/2026/06/02/v2026.06.02.1/notes.md)
          - V2026.06.02.2
            - [Release v2026.06.02.2](../../release/2026/06/02/v2026.06.02.2/notes.md)
        - 03
          - V2026.06.03.1
            - [Release v2026.06.03.1](../../release/2026/06/03/v2026.06.03.1/notes.md)
          - V2026.06.03.2
            - [Release v2026.06.03.2](../../release/2026/06/03/v2026.06.03.2/notes.md)
          - V2026.06.03.3
            - [Release v2026.06.03.3](../../release/2026/06/03/v2026.06.03.3/notes.md)
          - V2026.06.03.4
            - [Release v2026.06.03.4](../../release/2026/06/03/v2026.06.03.4/notes.md)
            - [Retrospective](../../release/2026/06/03/v2026.06.03.4/retrospective.md)
        - 04
          - V2026.06.04.1
            - [Notes](../../release/2026/06/04/v2026.06.04.1/notes.md)
        - 05
          - V2026.06.05.6
            - [Notes](../../release/2026/06/05/v2026.06.05.6/notes.md)
            - [Retrospective](../../release/2026/06/05/v2026.06.05.6/retrospective.md)
        - 12
          - V2026.06.12.1
            - [Release v2026.06.12.1](../../release/2026/06/12/v2026.06.12.1/notes.md)
    - [Release <version>](../../release/release-notes-template.md)
    - [Retrospective — <version>](../../release/retrospective-template.md)
  - Schema
  - [Getting started](../../getting-started.md)
  - [Lessons learned](../../lessons-learned-part1.md)
  - [Lessons learned (part 2)](../../lessons-learned-part2.md)
  - [Lessons learned (part 3)](../../lessons-learned-part3.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
