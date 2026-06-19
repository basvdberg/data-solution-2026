# Airflow (generated)

## Table of contents

<!-- markdown-toc:start -->
- [DAGs](#dags)
- [Configuration](#configuration)
- [Poller DAG](#poller-dag)
- [Extract DAG](#extract-dag)
- [Asset helpers](#asset-helpers)
<!-- markdown-toc:end -->

**Target runtime:** Apache Airflow **3.2.0** (`apache/airflow:3.2.0` in [`infra/airflow/docker-compose.standalone.yaml`](../../infra/airflow/docker-compose.standalone.yaml)). DAGs import from `airflow.sdk`.

## DAGs

Python files under [dags/](dags/) are loaded by the Airflow scheduler from `/opt/airflow/dags` in the container.

| DAG id | Schedule | Role |
|--------|----------|------|
| `openmeteo_data_object_poller` | `@hourly` | Probe marker, persist Postgres, emit change asset |
| `openmeteo_daily_temperature_extract` | Asset `ds://source/openmeteo/daily-temperature/change` | Extract on `data_object_change`; emit staging asset on success |

## Configuration

Optional Airflow Variable:

| Variable | Default | Value semantics |
|----------|---------|-----------------|
| `data_object_id` | `source/openmeteo/daily-temperature` | Source data object id probed by the poller |

`PYTHONPATH` in the Airflow container: `/opt/data-solution/code:/opt/data-solution/code/airflow:/opt/data-solution`.

## Poller DAG

| Property | Value |
|----------|--------|
| File | `dags/openmeteo_data_object_poller.py` |
| Tasks | `probe_api_and_write_postgres` → `check_data_changed` → `emit_airflow_data_change_event` or `complete_unchanged_run` → `poll_run_summary` |
| Asset emit | `emit_airflow_data_change_event` with `outlets=[source_change_asset]` |

Task `probe_api_and_write_postgres` calls [`include/poll_run.py`](include/poll_run.py) (Open-Meteo API probe + Postgres). On `data_object_change`, `emit_airflow_data_change_event` updates the source change asset with extract conf in event extra. Task `poll_run_summary` logs a human-readable outcome and sets a short DAG run note.

## Extract DAG

| Property | Value |
|----------|--------|
| File | `dags/openmeteo_daily_temperature_extract.py` |
| Trigger | `schedule=[source_change_asset]` |
| Tasks | `extract_openmeteo_daily_temperature` → `emit_staging_data_change_event` |
| Staging asset | `ds://staging/openmeteo/daily-temperature/change` on successful extract |
| Retries | 5 with exponential backoff (2–30 min) |

The extract task reads `triggering_asset_events` for `{mapping_id, marker, event_id}` and runs the extractor. On success, `emit_staging_data_change_event` updates the staging change asset. On failure, Postgres records `processing_error` and the extract task fails (no staging asset emit). Manual triggers with DAG conf still work for replay.

## Asset helpers

Importable modules under [`include/`](include/):

| Module | Purpose |
|--------|---------|
| `asset_conf.py` | `extract_conf_from_asset_extra` — build extract conf from asset event extra |
| `data_object_asset_uris.py` | `change_asset_uri()` — URI without Airflow import |
| `data_object_assets.py` | `change_asset()` — Airflow `Asset` builder |
| `poll_run.py` | Single probe + Postgres persist for poller DAG |

Monitoring: [Event orchestration monitoring](../../doc/operation/event-orchestration-monitoring.md).

Implementation checklist: [Implementation plan](../../doc/implementation/implementation-plan.md).

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
        - [CI/CD workflow (main only + server pull deploy)](../../doc/design/cicd/ci-cd.md)
      - Monitoring
        - [Monitoring architecture](../../doc/design/monitoring/monitoring-architecture.md)
      - [Airflow asset naming](../../doc/design/airflow-asset-naming.md)
      - [Event-based orchestration plan](../../doc/design/event-based-orchestration-plan.md)
      - [Meta data design](../../doc/design/meta-data-design.md)
    - Image
    - Implementation
      - [Implementation plan (Open-Meteo → event orchestration)](../../doc/implementation/implementation-plan.md)
    - Linked In
      - [Linkedin Post Part3V2](../../doc/linked-in/linkedin-post-part3v2.md)
    - Operation
      - [Event orchestration monitoring](../../doc/operation/event-orchestration-monitoring.md)
    - Retrospective
      - Incident
        - [INC-001 — NAS non-interactive SSH environment](../../doc/retrospective/incident/inc-001-nas-ssh-environment.md)
        - [INC-002 — Airflow standalone infra instability](../../doc/retrospective/incident/inc-002-airflow-infra-stability.md)
        - [INC-003 — Agent rediscovery and false-done verification](../../doc/retrospective/incident/inc-003-agent-process-gaps.md)
        - [INC-004 — Airflow PYTHONPATH drift (dag_run_guard import)](../../doc/retrospective/incident/inc-004-airflow-pythonpath-drift.md)
        - [INC-<NNN> — <short title>](../../doc/retrospective/incident/incident-template.md)
      - [Issue categories](../../doc/retrospective/issue-category.md)
    - [Implementation plan](../../doc/implementation-plan.md)
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
