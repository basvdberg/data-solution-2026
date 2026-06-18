# Implementation plan (Open-Meteo → event orchestration)

## Table of contents

<!-- markdown-toc:start -->
- [Goal](#goal)
- [Scope](#scope)
- [Related documentation](#related-documentation)
- [Prerequisites](#prerequisites)
- [Implementation steps](#implementation-steps)
  - [Step 1 — Poller in Airflow (verify)](#step-1-poller-in-airflow-verify)
  - [Step 2 — Airflow Asset emit (verify)](#step-2-airflow-asset-emit-verify)
  - [Step 3 — React to change assets (native Airflow scheduling)](#step-3-react-to-change-assets-native-airflow-scheduling)
    - [3.1 What consumes the change asset](#31-what-consumes-the-change-asset)
    - [3.2 Local smoke (dev machine)](#32-local-smoke-dev-machine)
    - [3.3 Runtime config (local server)](#33-runtime-config-local-server)
    - [3.4 Acceptance](#34-acceptance)
    - [3.5 Recovery and monitoring](#35-recovery-and-monitoring)
  - [After Step 3](#after-step-3)
- [Definition of done](#definition-of-done)
<!-- markdown-toc:end -->

## Goal

Move from a **locally runnable** Open-Meteo poller and extractor to **scheduled, event-driven orchestration** on the local server: Airflow runs the poller, **Airflow Assets** carry change signals, and Airflow runs extract only when the source marker advances.

This document is the **action checklist** for implementation. Technical detail for contracts, Postgres tables, and phases lives in [Event-based orchestration plan](design/event-based-orchestration-plan.md).

## Scope

Single data object for the PoC:

| Item | Value |
|------|--------|
| Mapping | `data-object-mapping/staging/openmeteo/daily-temperature` |
| Mapping CLI alias | `daily-temperature` |
| Source data object | `source/openmeteo/daily-temperature` |
| Staging target | `staging/openmeteo/daily-temperature` |
| Change asset URI | `ds://source/openmeteo/daily-temperature/change` |
| Poller DAG id | `openmeteo_data_object_poller` |
| Extract DAG id | `openmeteo_daily_temperature_extract` |

Out of scope: additional sources, multi-mapping routing, and a dedicated controller Docker service.

## Related documentation

| Topic | Document |
|-------|----------|
| Target architecture and event contract | [Event-based orchestration plan](design/event-based-orchestration-plan.md) |
| Airflow / Postgres on the local server | [Infrastructure](../infra/readme.md) |
| Deploy to the local server (commit + push `main`) | [CI/CD workflow](design/ci-cd.md) |
| Poller CLI and options | [Extractor and poller](../code/extractor_and_poller/readme.md) |
| Airflow DAGs and variables | [code/airflow](../code/airflow/readme.md) |
| Local commands | [Getting started](../getting-started.md) |

## Prerequisites

Complete local-server setup before Step 1: Postgres metadata and Airflow standalone stack running with `.env` secrets configured. Follow [Infrastructure](../infra/readme.md) for ordered setup, SSH troubleshooting, and `deploy-infra-on-nas.sh`. For dev-machine commands, see [Getting started](../getting-started.md).

---

## Implementation steps

### Step 1 — Poller in Airflow (verify)

**Status:** implemented — verify on the local server.

- [ ] DAG `openmeteo_data_object_poller` appears in the Airflow UI without import errors.
- [ ] Manual trigger reaches Open-Meteo and persists rows to Postgres table `poller`.
- [ ] Second run with unchanged marker logs `data_object_progress` only.

Troubleshooting (PYTHONPATH, infra sync, Postgres env): [code/airflow/readme.md](../code/airflow/readme.md).

---

### Step 2 — Airflow Asset emit (verify)

**Status:** implemented — verify after deploy.

- [ ] Poller DAG task `emit_change_asset` succeeds when marker changes.
- [ ] Airflow UI shows asset event for `ds://source/openmeteo/daily-temperature/change`.
- [ ] Unchanged marker run skips `emit_change_asset` (branch to `record_progress`).

Asset naming: [Airflow asset naming](design/airflow-asset-naming.md).

---

### Step 3 — React to change assets (native Airflow scheduling)

**Status:** implemented — deploy and validate on the local server.

**Objective:** Schedule extract DAG on `ds://source/openmeteo/daily-temperature/change` and run extract when asset extra contains a valid change signal.

#### 3.1 What consumes the change asset

- **Extract DAG** [`openmeteo_daily_temperature_extract.py`](../code/airflow/dags/openmeteo_daily_temperature_extract.py) uses `schedule=[source_change_asset]`.
- **Asset URI:** `ds://source/openmeteo/daily-temperature/change`
- **Conf resolver:** [`code/airflow/include/asset_conf.py`](../code/airflow/include/asset_conf.py) — `extract_conf_from_asset_extra()` reads `{mapping_id, marker, event_id}` from `triggering_asset_events`.
- **No separate process** — scheduler triggers extract DAG on asset update.

Poller emit uses `emit_change_asset` with `outlets=[source_change_asset]` in [`openmeteo_data_object_poller.py`](../code/airflow/dags/openmeteo_data_object_poller.py).

#### 3.2 Local smoke (dev machine)

```powershell
cd "c:\Dev2\Data Engineering 2.0\data-solution-2026"
python -m unittest code.extractor_and_poller.tests.test_asset_conf code.extractor_and_poller.tests.test_poller_events
```

#### 3.3 Runtime config (local server)

Set in `~/apache-airflow/.env` (see [infra/airflow/.env.example](../infra/airflow/.env.example)):

| Variable | Example | Purpose |
|----------|---------|---------|
| `POSTGRES_HOST` | `basnas_postgress:5432` | Poller and extract metadata |
| `DATA_SOLUTION_ROOT` | clone path on NAS | DAG and code mounts |

Prerequisite: both DAGs load without import errors (`airflow dags list-import-errors` empty).

#### 3.4 Acceptance

1. Poller emits change asset on marker change (Step 2 green).
2. Extract DAG shows runs **triggered by asset** `ds://source/openmeteo/daily-temperature/change`.
3. On marker change, one `openmeteo_daily_temperature_extract` run starts with conf `{mapping_id, marker, event_id}`.
4. Progress polls do not trigger extract.
5. Extract task retries up to **5 times** on transient failure.

**Step 3 done when:** one real change poll creates exactly one extract DAG run.

#### 3.5 Recovery and monitoring

- **Retries:** extract DAG `retries=5` with exponential backoff.
- **Idempotency:** `extract_run_audit` skips only successful `event_id`; failed rows are reset to `running` on retry.
- **Manual replay:** re-trigger extract DAG with conf from a failed audit row.
- **Monitoring:** [Event orchestration monitoring](../operation/event-orchestration-monitoring.md).

---

### After Step 3

Remaining work after asset-triggered extract runs reliably:

- **Extract + idempotency** — extract DAG calls `python -m extractor_and_poller.openmeteo.extractor --mapping daily-temperature`; write `extract_run_audit` rows and skip duplicate successful `event_id`. See [Phase 5 — Extract DAG and idempotency](design/event-based-orchestration-plan.md#phase-5---extract-dag-and-idempotency).
- **End-to-end smoke** — poller → asset → extract → Postgres staging. Document failures in [lessons-learned.md](../lessons-learned-part1.md).
- **Rollout** — commit and push to `main`; CI/CD and NAS deploy via [CI/CD workflow](design/ci-cd.md) (post-push hook → `deploy-on-nas.sh`). Record DAG ids in [release notes](../release/release-notes-template.md).

---

## Definition of done

The PoC orchestration path is complete when all of the following are true:

- [ ] **Step 1:** Poller runs in Airflow with Postgres state.
- [ ] **Step 2:** Poll results emit change assets with stable extra schema.
- [ ] **Step 3:** Change assets trigger extract orchestration (no manual extract for routine loads).
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
      - [Airflow asset naming](../design/airflow-asset-naming.md)
      - [Architecture](../design/architecture.md)
      - [CI/CD workflow (main only + server pull deploy)](../design/ci-cd.md)
      - [Event-based orchestration plan (single data object)](../design/event-based-orchestration-plan.md)
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
  - Schema
  - [Getting started](../../getting-started.md)
  - [Lessons learned](../../lessons-learned-part1.md)
  - [Lessons learned (part 2)](../../lessons-learned-part2.md)
  - [Lessons learned (part 3)](../../lessons-learned-part3.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
