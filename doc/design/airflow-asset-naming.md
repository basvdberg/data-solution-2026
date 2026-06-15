# Airflow asset naming

## Table of contents

<!-- markdown-toc:start -->
- [Pattern](#pattern)
- [Formatting rules](#formatting-rules)
- [Poll signals (implemented)](#poll-signals-implemented)
- [Extract signals (planned)](#extract-signals-planned)
- [Load signals (planned)](#load-signals-planned)
- [Event extra conventions](#event-extra-conventions)
- [Code reference](#code-reference)
<!-- markdown-toc:end -->

## Pattern

Asset URIs use the solution scheme and the data object id:

```text
ds://{data-object-id}/{signal}
```

| Segment | Purpose | Example |
|---------|---------|---------|
| `ds` | Solution boundary (data-solution-2026) | `ds` |
| `data-object-id` | Repo-relative data object id | `source/openmeteo/daily-temperature` |
| `signal` | Stable orchestration signal | `change` |

This applies the [Simplicity](https://github.com/basvdberg/data-engineering-design-patterns/blob/main/design-patterns/generic/simplicity.md) pattern: one orchestration runtime (Airflow) instead of a separate message broker.

## Formatting rules

- Scheme is always `ds://` for this PoC.
- Data object ids use forward slashes and match DSA metadata paths (no `data-object/` prefix).
- Signal tokens use **lowercase** nouns (`change`, not `data_object_change` in the URI).
- `event_type` in Postgres and poll envelopes remains **snake_case** (`data_object_change`, `data_object_progress`).

## Poll signals (implemented)

Signals from the data object poller. See [event-based orchestration plan](event-based-orchestration-plan.md).

| Design pattern term | `event_type` | Airflow Asset URI | Triggers downstream? |
|---------------------|--------------|-------------------|----------------------|
| Data object change | `data_object_change` | `ds://source/openmeteo/daily-temperature/change` | Yes → extract DAG |
| Data object progress | `data_object_progress` | *(none — Postgres audit only)* | No (liveness / audit) |

On `data_object_change`, the poller DAG task `emit_change_asset` updates the asset with **extra** metadata for the extract DAG. On `data_object_progress`, only a `poller` table row is written.

## Extract signals (planned)

When staging publish completes, emit a **publish success** asset for downstream dependency triggers:

| Signal | Asset URI (example) |
|--------|---------------------|
| Staging publish success | `ds://staging/openmeteo/daily-temperature/publish` |

## Load signals (planned)

When Parquet lands and ADL load runs into the 100 Landing Area:

| Signal | Asset URI (example) |
|--------|---------------------|
| Load succeeded | `ds://staging/openmeteo/daily-temperature/load` |

## Event extra conventions

Asset event **extra** carries per-run orchestration conf (JSON-serializable):

| Field | Purpose |
|-------|---------|
| `data_object_id` | Source object that changed |
| `event_type` | `data_object_change` |
| `marker` | New change marker (`new_marker` in Postgres) |
| `event_id` | Idempotency key for extract |
| `mapping_id` | Mapping CLI slug (for example `daily-temperature`) |

Postgres table `poller` stores the same markers plus `event_id` and `run_id`; query `poller_latest_first` for newest rows first.

## Code reference

| Module | Purpose |
|--------|---------|
| [`code/airflow/include/data_object_asset_uris.py`](../../code/airflow/include/data_object_asset_uris.py) | `change_asset_uri()` — URI without Airflow import |
| [`code/airflow/include/data_object_assets.py`](../../code/airflow/include/data_object_assets.py) | `change_asset()` — Airflow `Asset` builder |
| [`code/airflow/include/asset_conf.py`](../../code/airflow/include/asset_conf.py) | `extract_conf_from_asset_extra()` — consumer conf |
| [`code/extractor_and_poller/poller/poll_events.py`](../../code/extractor_and_poller/poller/poll_events.py) | `event_type` constants |

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
      - [Airflow asset naming](airflow-asset-naming.md)
      - [Architecture](architecture.md)
      - [CI/CD workflow (main only + server pull deploy)](ci-cd.md)
      - [Event-based orchestration plan (single data object)](event-based-orchestration-plan.md)
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
  - [Lessons learned (part 3)](../../lessons-learned-part3.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
