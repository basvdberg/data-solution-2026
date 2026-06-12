# Airflow (generated)

## Table of contents

<!-- markdown-toc:start -->
- [DAGs](#dags)
- [Configuration](#configuration)
- [Poller DAG](#poller-dag)
- [Extract DAG](#extract-dag)
- [Kafka handlers](#kafka-handlers)
<!-- markdown-toc:end -->

**Target runtime:** Apache Airflow **3.2.0** (`apache/airflow:3.2.0` in [`infra/airflow/docker-compose.standalone.yaml`](../../infra/airflow/docker-compose.standalone.yaml)). DAGs import from `airflow.sdk`; Kafka via `apache-airflow-providers-apache-kafka` and `apache-airflow-providers-common-messaging`.

## DAGs

Python files under [dags/](dags/) are loaded by the Airflow scheduler from `/opt/airflow/dags` in the container.

| DAG id | Schedule | Role |
|--------|----------|------|
| `openmeteo_data_object_poller` | `@hourly` | Probe marker, persist Postgres, publish Kafka |
| `openmeteo_daily_temperature_extract` | Asset `ds_poll_data_object_change` | Extract on `data_object_change` events |

## Configuration

Kafka bootstrap from container env `KAFKA_HOST` (see [`.env.example`](../../infra/airflow/.env.example)). Airflow Connection `kafka_default` is set via `AIRFLOW_CONN_KAFKA_DEFAULT` in compose.

Optional Airflow Variable:

| Variable | Default | Value semantics |
|----------|---------|-----------------|
| `data_object_id` | `source/openmeteo/daily-temperature` | Source data object id probed by the poller |

`PYTHONPATH` in the Airflow container: `/opt/data-solution/code:/opt/data-solution/code/airflow:/opt/data-solution`.

## Poller DAG

| Property | Value |
|----------|--------|
| File | `dags/openmeteo_data_object_poller.py` |
| Tasks | `probe_and_persist` → `publish_poll_event` |
| Publish | `ProduceToTopicOperator` (`kafka_config_id=kafka_default`) |

Task `probe_and_persist` calls [`include/poll_run.py`](include/poll_run.py) (probe + Postgres, no Kafka in poller CLI). Task `publish_poll_event` publishes the JSON envelope to `ds.poll.data_object_change` or `ds.poll.data_object_progress`.

## Extract DAG

| Property | Value |
|----------|--------|
| File | `dags/openmeteo_daily_temperature_extract.py` |
| Trigger | `AssetWatcher` + `MessageQueueTrigger` on `ds.poll.data_object_change` |
| Retries | 5 with exponential backoff (2–30 min) |

The extract task reads `triggering_asset_events` for `{mapping_id, marker, event_id}` and calls the extractor CLI. Manual triggers with DAG conf still work for replay.

## Kafka handlers

Importable modules under [`include/`](include/):

| Module | Purpose |
|--------|---------|
| `kafka_handlers.py` | `poll_change_apply_function` — validate change events for Asset Watcher |
| `kafka_topics.py` | Topic name constants |
| `poller_kafka.py` | Producer function for `ProduceToTopicOperator` |
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
      - [Architecture](../../doc/design/architecture.md)
      - [CI/CD workflow (main only + server pull deploy)](../../doc/design/ci-cd.md)
      - [Event-based orchestration plan (single data object)](../../doc/design/event-based-orchestration-plan.md)
      - [Kafka topic naming](../../doc/design/kafka-topic-naming.md)
      - [Meta data design](../../doc/design/meta-data-design.md)
    - Image
    - Implementation
      - [Implementation plan (Open-Meteo → event orchestration)](../../doc/implementation/implementation-plan.md)
    - Linked In
      - [Linkedin Post Part3V2](../../doc/linked-in/linkedin-post-part3v2.md)
    - Operation
      - Incident
        - [INC-001 — NAS non-interactive SSH environment](../../doc/operation/incident/inc-001-nas-ssh-environment.md)
        - [INC-002 — Airflow standalone infra instability](../../doc/operation/incident/inc-002-airflow-infra-stability.md)
        - [INC-003 — Agent rediscovery and false-done verification](../../doc/operation/incident/inc-003-agent-process-gaps.md)
        - [INC-004 — Airflow PYTHONPATH drift (dag_run_guard import)](../../doc/operation/incident/inc-004-airflow-pythonpath-drift.md)
        - [INC-<NNN> — <short title>](../../doc/operation/incident/incident-template.md)
      - [Event orchestration monitoring](../../doc/operation/event-orchestration-monitoring.md)
      - [Issue categories](../../doc/operation/issue-category.md)
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
  - [Getting started](../../getting-started.md)
  - [Lessons learned](../../lessons-learned-part1.md)
  - [Lessons learned (part 2)](../../lessons-learned-part2.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
