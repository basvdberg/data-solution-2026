# Event orchestration monitoring

## Table of contents

<!-- markdown-toc:start -->
- [Purpose](#purpose)
- [Poll events](#poll-events)
- [Extract events](#extract-events)
- [Airflow](#airflow)
- [Healthy signals](#healthy-signals)
<!-- markdown-toc:end -->

## Purpose

Operators troubleshoot event-based orchestration by correlating Postgres audit rows, structured logs, and Airflow DAG runs. Event names follow the [Event-based orchestration](https://github.com/basvdberg/data-engineering-design-patterns/blob/main/design-patterns/data-engineering/event-based-orchestration.md) glossary.

## Poll events

Table `public.poller` — one row per probe.

```sql
select polled_at_utc, data_object_id, event_type, change_scope, old_marker, new_marker, event_id
from poller_latest_first
limit 20;
```

| `event_type` | Meaning |
|--------------|---------|
| `data_object_unchanged` | Poll succeeded; marker unchanged (audit only) |
| `data_object_change` | Marker moved; source change asset emitted |

Structured log (poller DAG task `poll_run_summary`):

```text
Poll run summary: event=data_object_change changed=yes postgres_row_id=… marker=… api=reachable
```

## Extract events

Table `public.extract_run_audit` — one row per extract attempt.

```sql
select started_at_utc, finished_at_utc, data_object_id, event_type, status, marker, row_count, output_table
from extract_run_audit
order by started_at_utc desc
limit 20;
```

| `event_type` | `status` | Meaning |
|--------------|----------|---------|
| `data_object_change` | `success` | Staging updated; staging change asset emitted |
| `processing_error` | `failed` | Extract failed; no staging asset emit |
| (null) | `running` | In progress |

Structured log on success:

```text
Event: data_object_change data_object=staging/openmeteo/daily-temperature marker=… event_id=… rows=…
```

Structured log on failure:

```text
Event: processing_error data_object=staging/openmeteo/daily-temperature marker=… event_id=… mapping=…
```

## Airflow

| DAG | Schedule | Outcome |
|-----|----------|---------|
| `openmeteo_data_object_poller` | `@hourly` | Probe + Postgres; source asset on change |
| `openmeteo_daily_temperature_extract` | Source change asset | Extract + Postgres; staging asset on success |

DAG run notes on poller runs summarise `changed | postgres:<event_type> | api:ok`.

## Healthy signals

- Hourly poller runs with mostly `data_object_unchanged` and occasional `data_object_change` when Open-Meteo publishes a new observation day.
- Each source `data_object_change` eventually produces a matching extract row with `event_type=data_object_change` and a downstream staging asset update.
- Repeated `processing_error` rows for the same `event_id` after retries indicate a persistent extract failure worth investigation.

See also [Monitoring architecture](../design/monitoring/monitoring-architecture.md), [Event-based orchestration plan](../design/event-based-orchestration-plan.md), and [Airflow readme](../../code/airflow/readme.md).

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
      - [Implementation plan (Open-Meteo → event orchestration)](../implementation/implementation-plan.md)
    - Linked In
      - [Data Object Contract](../linked-in/data-object-contract.md)
      - [Linkedin Post Part3V2](../linked-in/linkedin-post-part3v2.md)
    - Operation
      - [Event orchestration monitoring](event-orchestration-monitoring.md)
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
