# Kafka topic naming

## Table of contents

<!-- markdown-toc:start -->
- [Pattern](#pattern)
- [Formatting rules](#formatting-rules)
- [Poll events (implemented)](#poll-events-implemented)
- [Extract events (planned)](#extract-events-planned)
- [Load events (planned)](#load-events-planned)
- [Ops events (planned)](#ops-events-planned)
- [Invalid events (planned)](#invalid-events-planned)
- [Message conventions](#message-conventions)
- [Code reference](#code-reference)
<!-- markdown-toc:end -->

## Pattern

Topic names use three segments:

```text
{scope}.{category}.{event}
```

| Segment | Purpose | Example |
|---------|---------|---------|
| `scope` | Solution boundary on a shared broker | `ds` (data-solution-2026) |
| `category` | Orchestration stage or concern | `poll`, `extract`, `load` |
| `event` | Stable business signal; matches `event_type` in Postgres and stdout envelopes | `data_object_change` |

Do **not** embed source paths (`source/openmeteo/...`) in topic names. Use the message **key** (`data_object_id`) for per-object routing.

## Formatting rules

- Segments separated by `.` (Kafka-friendly grouping and ACL prefixes).
- Event tokens use **snake_case** to match `event_type`, Postgres columns, and Python constants.
- Category names are **singular nouns** (`poll`, not `polling`).
- Environment (`prod`, `dev`) is omitted on the dedicated NAS broker; use a separate cluster or scope prefix when environments share Kafka.

## Poll events (implemented)

Signals from the data object poller. See [event-based orchestration plan](event-based-orchestration-plan.md).

| Design pattern term | `event_type` | Kafka topic | Triggers downstream? |
|---------------------|--------------|-------------|----------------------|
| Data object change | `data_object_change` | `ds.poll.data_object_change` | Yes → extract |
| Data object progress | `data_object_progress` | `ds.poll.data_object_progress` | No (liveness / audit) |

`data_object_progress` replaces the earlier working name `data_object_unchanged` to align with the [event-based orchestration](https://github.com/basvdberg/data-engineering-design-patterns/blob/main/design-patterns/data-engineering/event-based-orchestration.md) pattern vocabulary.

## Extract events (planned)

Lifecycle events from the extract DAG after a change event.

| Signal | Kafka topic |
|--------|-------------|
| Extract started | `ds.extract.start` |
| Extract succeeded | `ds.extract.success` |
| Extract failed | `ds.extract.failed` |

Partition key: target staging `data_object_id` (for example `staging/openmeteo/daily-temperature`).

## Load events (planned)

When Parquet lands and ADL load runs into the 100 Landing Area.

| Signal | Kafka topic |
|--------|-------------|
| Load requested | `ds.load.request` |
| Load succeeded | `ds.load.success` |
| Load failed | `ds.load.failed` |

## Ops events (planned)

Cross-cutting control-plane signals.

| Signal | Kafka topic |
|--------|-------------|
| Controller enqueued task | `ds.ops.task_queued` |
| Idempotent skip (replay) | `ds.ops.task_skipped` |
| Health heartbeat | `ds.ops.heartbeat` |

## Invalid events (planned)

Schema violations and poison messages (quarantine and dead-letter).

| Signal | Kafka topic |
|--------|-------------|
| Contract violation | `ds.invalid.quarantine` |
| Exhausted retries | `ds.invalid.dead_letter` |

Route by `source_topic` and `event_id` in the payload rather than multiplying DLQ topic names per upstream category.

## Message conventions

| Concern | Convention |
|---------|------------|
| **Key** | `data_object_id` |
| **Value (poll)** | JSON envelope: `data_object_id`, `event_type`, `event_time_utc`, `old_marker`, `new_marker`; Postgres `poller` also stores `event_id` and `run_id` |
| **Retention** | Shorter for `ds.poll.data_object_progress`; longer for change and extract topics (replay) |
| **ACL / subscribe** | Consumers use category prefix (`ds.poll.*`, `ds.extract.*`) |

## Code reference

Poll topic mapping lives in [`code/extractor_and_poller/poller/kafka_topic.py`](../../code/extractor_and_poller/poller/kafka_topic.py) (poller CLI) and [`code/airflow/include/kafka_topics.py`](../../code/airflow/include/kafka_topics.py) (Airflow DAGs). The poller DAG `ProduceToTopicOperator` resolves `event_type` → topic via `kafka_topic_for_event()`.

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
      - [Architecture](architecture.md)
      - [CI/CD workflow (main only + server pull deploy)](ci-cd.md)
      - [Event-based orchestration plan (single data object)](event-based-orchestration-plan.md)
      - [Kafka topic naming](kafka-topic-naming.md)
      - [Meta data design](meta-data-design.md)
    - Image
    - Implementation
      - [Implementation plan (Open-Meteo → event orchestration)](../implementation/implementation-plan.md)
    - Linked In
      - [Linkedin Post Part3V2](../linked-in/linkedin-post-part3v2.md)
    - Operation
      - Incident
        - [INC-001 — NAS non-interactive SSH environment](../operation/incident/inc-001-nas-ssh-environment.md)
        - [INC-002 — Airflow standalone infra instability](../operation/incident/inc-002-airflow-infra-stability.md)
        - [INC-003 — Agent rediscovery and false-done verification](../operation/incident/inc-003-agent-process-gaps.md)
        - [INC-004 — Airflow PYTHONPATH drift (dag_run_guard import)](../operation/incident/inc-004-airflow-pythonpath-drift.md)
        - [INC-<NNN> — <short title>](../operation/incident/incident-template.md)
      - [Event orchestration monitoring](../operation/event-orchestration-monitoring.md)
      - [Issue categories](../operation/issue-category.md)
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
