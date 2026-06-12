# Implementation plan (Open-Meteo → event orchestration)

## Table of contents

<!-- markdown-toc:start -->
- [Goal](#goal)
- [Scope](#scope)
- [Related documentation](#related-documentation)
- [Prerequisites](#prerequisites)
- [Implementation steps](#implementation-steps)
  - [Step 1 — Poller in Airflow (verify)](#step-1-poller-in-airflow-verify)
  - [Step 2 — Kafka publish (verify)](#step-2-kafka-publish-verify)
  - [Step 3 — React to change events (native Airflow Kafka)](#step-3-react-to-change-events-native-airflow-kafka)
    - [3.1 What subscribes to Kafka](#31-what-subscribes-to-kafka)
    - [3.2 Local smoke (dev machine)](#32-local-smoke-dev-machine)
    - [3.3 Runtime config (local server)](#33-runtime-config-local-server)
    - [3.4 Acceptance](#34-acceptance)
    - [3.5 Recovery and monitoring](#35-recovery-and-monitoring)
  - [After Step 3](#after-step-3)
- [Definition of done](#definition-of-done)
<!-- markdown-toc:end -->

## Goal

Move from a **locally runnable** Open-Meteo poller and extractor to **scheduled, event-driven orchestration** on the local server: Airflow runs the poller, Kafka carries change signals, and Airflow runs extract only when the source marker advances.

This document is the **action checklist** for implementation. Technical detail for contracts, Postgres tables, and phases lives in [Event-based orchestration plan](design/event-based-orchestration-plan.md).

## Scope

Single data object for the PoC:

| Item | Value |
|------|--------|
| Mapping | `data-object-mapping/staging/openmeteo/daily-temperature` |
| Mapping CLI alias | `daily-temperature` |
| Source data object | `source/openmeteo/daily-temperature` |
| Staging target | `staging/openmeteo/daily-temperature` |
| Poller DAG id | `openmeteo_data_object_poller` |
| Extract DAG id | `openmeteo_daily_temperature_extract` |

Out of scope: additional sources, multi-mapping routing, and a dedicated controller Docker service (PoC uses native Airflow Kafka providers inside the Airflow container).

## Related documentation

| Topic | Document |
|-------|----------|
| Target architecture and event contract | [Event-based orchestration plan](design/event-based-orchestration-plan.md) |
| Airflow / Kafka / Postgres on the local server | [Infrastructure](../infra/readme.md) |
| Deploy to the local server (commit + push `main`) | [CI/CD workflow](design/ci-cd.md) |
| Poller CLI and options | [Extractor and poller](../code/extractor_and_poller/readme.md) |
| Airflow DAGs and variables | [code/airflow](../code/airflow/readme.md) |
| Local commands | [Getting started](../getting-started.md) |

## Prerequisites

Complete local-server setup before Step 1: Postgres metadata, Kafka, and Airflow standalone stacks running with `.env` secrets configured. Follow [Infrastructure](../infra/readme.md) for ordered setup, SSH troubleshooting, and `deploy-infra-on-nas.sh`. For dev-machine commands, see [Getting started](../getting-started.md).

---

## Implementation steps

### Step 1 — Poller in Airflow (verify)

**Status:** implemented — verify on the local server.

- [ ] DAG `openmeteo_data_object_poller` appears in the Airflow UI without import errors.
- [ ] Manual trigger reaches Open-Meteo and persists rows to Postgres table `poller`.
- [ ] Second run with unchanged marker logs `data_object_progress` only.

Troubleshooting (PYTHONPATH, infra sync, Postgres env): [code/airflow/readme.md](../code/airflow/readme.md).

---

### Step 2 — Kafka publish (verify)

**Status:** implemented — verify after infra deploy (`KAFKA_HOST`, `kafka_default` network).

- [ ] Poller DAG task `publish_poll_event` succeeds (`ProduceToTopicOperator`).
- [ ] Kafka UI lists `ds.poll.data_object_change` and/or `ds.poll.data_object_progress` with key `data_object_id`.

Topic naming: [Kafka topic naming](design/kafka-topic-naming.md).

---

### Step 3 — React to change events (native Airflow Kafka)

**Status:** implemented — deploy and validate on the local server.

**Objective:** Subscribe to `ds.poll.data_object_change` with native Airflow Kafka providers and run the extract DAG when a valid change event arrives.

#### 3.1 What subscribes to Kafka

- **Extract DAG** [`openmeteo_daily_temperature_extract.py`](../code/airflow/dags/openmeteo_daily_temperature_extract.py) uses `schedule=[poll_change_asset]` with an `AssetWatcher` + `MessageQueueTrigger`.
- **Topic:** `ds.poll.data_object_change`
- **Handler:** [`code/airflow/include/kafka_handlers.py`](../code/airflow/include/kafka_handlers.py) — `poll_change_apply_function` validates JSON, rejects progress events, resolves `mapping_id`, returns extract conf.
- **No separate process** — the Airflow triggerer watches Kafka; no `extractor_and_poller.controller` CLI.

Poller publish uses `ProduceToTopicOperator` in [`openmeteo_data_object_poller.py`](../code/airflow/dags/openmeteo_data_object_poller.py).

#### 3.2 Local smoke (dev machine)

```powershell
cd "c:\Dev2\Data Engineering 2.0\data-solution-2026"
python -m unittest code.extractor_and_poller.tests.test_kafka_handlers
```

#### 3.3 Runtime config (local server)

Set in `~/apache-airflow/.env` (see [infra/airflow/.env.example](../infra/airflow/.env.example)):

| Variable | Example | Purpose |
|----------|---------|---------|
| `KAFKA_HOST` | `kafka:9092` | Kafka bootstrap for Asset Watcher queue URL |

Airflow Connection `kafka_default` is created via `AIRFLOW_CONN_KAFKA_DEFAULT` in compose (bootstrap `kafka:9092`).

Providers installed at container start: `apache-airflow-providers-apache-kafka`, `apache-airflow-providers-common-messaging`.

Prerequisite: both DAGs load without import errors (`airflow dags list-import-errors` empty). Triggerer must be healthy (part of standalone mode).

#### 3.4 Acceptance

1. Poller publishes to `ds.poll.data_object_change` (Step 2 green).
2. Extract DAG shows runs **triggered by asset** `ds_poll_data_object_change`.
3. On marker change, one `openmeteo_daily_temperature_extract` run starts with conf `{mapping_id, marker, event_id}`.
4. Invalid payloads log `Rejected Kafka message` in triggerer/worker logs — no extract run.
5. Extract task retries up to **5 times** on transient failure.

**Step 3 done when:** one real or synthetic change event creates exactly one extract DAG run.

#### 3.5 Recovery and monitoring

- **Retries:** extract DAG `retries=5` with exponential backoff.
- **Idempotency:** `extract_run_audit` skips only successful `event_id`; failed rows are reset to `running` on retry.
- **Manual replay:** re-trigger extract DAG with conf from a failed audit row.
- **Monitoring:** [Event orchestration monitoring](../operation/event-orchestration-monitoring.md).

---

### After Step 3

Remaining work after asset-triggered extract runs reliably:

- **Extract + idempotency** — extract DAG calls `python -m extractor_and_poller.openmeteo.extractor --mapping daily-temperature`; write `extract_run_audit` rows and skip duplicate successful `event_id`. See [Phase 5 — Extract DAG and idempotency](design/event-based-orchestration-plan.md#phase-5---extract-dag-and-idempotency).
- **End-to-end smoke** — poller → Kafka → asset watcher → extract → Postgres staging. Document failures in [lessons-learned.md](../lessons-learned-part1.md).
- **Rollout** — commit and push to `main`; CI/CD and NAS deploy via [CI/CD workflow](design/ci-cd.md) (post-push hook → `deploy-on-nas.sh`). Record DAG ids in [release notes](../release/release-notes-template.md).

---

## Definition of done

The PoC orchestration path is complete when all of the following are true:

- [ ] **Step 1:** Poller runs in Airflow with Postgres state.
- [ ] **Step 2:** Poll results publish to Kafka with a stable envelope.
- [ ] **Step 3:** Change events trigger extract orchestration (no manual extract for routine loads).
- [ ] **After Step 3:** Extract is idempotent per `event_id` and lands staging Parquet; end-to-end smoke documented in a release note.

For schema-level acceptance criteria, use [Definition of done](design/event-based-orchestration-plan.md#definition-of-done) in the event-based orchestration plan.

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
      - [Architecture](../design/architecture.md)
      - [CI/CD workflow (main only + server pull deploy)](../design/ci-cd.md)
      - [Event-based orchestration plan (single data object)](../design/event-based-orchestration-plan.md)
      - [Kafka topic naming](../design/kafka-topic-naming.md)
      - [Meta data design](../design/meta-data-design.md)
    - Image
    - Implementation
      - [Implementation plan (Open-Meteo → event orchestration)](implementation-plan.md)
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
