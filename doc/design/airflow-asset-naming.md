# Airflow asset naming

## Table of contents

<!-- markdown-toc:start -->
- [Purpose](#purpose)
- [URI scheme](#uri-scheme)
- [Change assets in this PoC](#change-assets-in-this-poc)
- [Event extra fields](#event-extra-fields)
<!-- markdown-toc:end -->

## Purpose

Airflow **Assets** carry orchestration change signals between DAGs. URIs are stable identifiers derived from data object paths so producers and consumers stay aligned with DSA metadata.

## URI scheme

```text
ds://<data_object_id>/change
```

| Part | Meaning |
|------|---------|
| `ds` | Data-solution asset scheme (constant) |
| `data_object_id` | DSA path, for example `source/openmeteo/daily-temperature` |
| `change` | Signal that the object’s change marker moved |

Implementation: [`code/airflow/include/data_object_asset_uris.py`](../../code/airflow/include/data_object_asset_uris.py).

## Change assets in this PoC

| Data object | Asset URI | Producer | Consumer |
|-------------|-----------|----------|----------|
| `source/openmeteo/daily-temperature` | `ds://source/openmeteo/daily-temperature/change` | Poller DAG `emit_airflow_data_change_event` | Extract DAG schedule |
| `staging/openmeteo/daily-temperature` | `ds://staging/openmeteo/daily-temperature/change` | Extract DAG `emit_staging_data_change_event` | (future downstream DAGs) |

## Event extra fields

Asset event `extra` metadata uses orchestration glossary event types (`data_object_change`, `data_object_unchanged`, `processing_error`).

Minimum fields for extract conf from a source change asset:

| Field | Required | Meaning |
|-------|----------|---------|
| `data_object_id` | yes | Source data object path |
| `marker` | yes | Current change marker (observation day) |
| `event_type` | no | Defaults to `data_object_change` |
| `event_id` | no | Poll event id for idempotency |
| `mapping_id` | no | Short mapping slug when omitted |
| `change_scope` | no | Glossary scope (`incremental_update`, `full_rewrite`, …) |

Validation: [`code/airflow/include/asset_conf.py`](../../code/airflow/include/asset_conf.py).

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
        - [CI/CD workflow (main only + server pull deploy)](cicd/ci-cd.md)
      - Monitoring
        - [Monitoring architecture](monitoring/monitoring-architecture.md)
      - [Airflow asset naming](airflow-asset-naming.md)
      - [Event-based orchestration plan](event-based-orchestration-plan.md)
      - [Meta data design](meta-data-design.md)
    - Image
    - Implementation
      - [Implementation plan (Open-Meteo → event orchestration)](../implementation/implementation-plan.md)
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
