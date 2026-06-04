# Implementation plan (Open-Meteo → event orchestration)

## Table of contents

<!-- markdown-toc:start -->
- [Goal](#goal)
- [Scope](#scope)
- [Related documentation](#related-documentation)
- [Prerequisites](#prerequisites)
- [Implementation steps](#implementation-steps)
  - [Step 1 — Run the Open-Meteo data object poller in Airflow](#step-1-run-the-open-meteo-data-object-poller-in-airflow)
    - [1.1 Create the DAG folder and file](#11-create-the-dag-folder-and-file)
    - [1.2 Deploy DAGs to the running Airflow container](#12-deploy-dags-to-the-running-airflow-container)
    - [1.3 Configure Airflow for the poller task](#13-configure-airflow-for-the-poller-task)
    - [1.4 Wire Postgres metadata (before schedule)](#14-wire-postgres-metadata-before-schedule)
    - [1.5 Manual DAG run and acceptance](#15-manual-dag-run-and-acceptance)
  - [Step 2 — Publish poll events to Kafka](#step-2-publish-poll-events-to-kafka)
  - [Step 3 — React to change events (event controller)](#step-3-react-to-change-events-event-controller)
  - [Step 4 — Run extract on change in Airflow](#step-4-run-extract-on-change-in-airflow)
  - [Step 5 — End-to-end validation on BasNAS](#step-5-end-to-end-validation-on-basnas)
  - [Step 6 — Production rollout and operations](#step-6-production-rollout-and-operations)
- [Definition of done](#definition-of-done)
<!-- markdown-toc:end -->

## Goal

Move from a **locally runnable** Open-Meteo poller and extractor to **scheduled, event-driven orchestration** on BasNAS: Airflow runs the poller, Kafka carries change signals, and Airflow runs extract only when the source marker advances.

This document is the **action checklist** for implementation. Technical detail for contracts, Postgres tables, and phases lives in [Event-based orchestration plan](design/event-based-orchestration-plan.md).

## Scope

Single data object for the PoC:

| Item | Value |
|------|--------|
| Mapping | `data-object-mapping/staging/openmeteo/daily-temperature` |
| Mapping CLI alias | `daily-temperature` |
| Source data object | `source/openmeteo/daily-temperature` |
| Staging target | `staging/openmeteo/daily-temperature` |
| Poller DAG id (target) | `openmeteo_data_object_poller` |

Out of scope for this plan: additional sources, multi-mapping routing, and advanced retry policies.

## Related documentation

| Topic | Document |
|-------|----------|
| Target architecture and event contract | [Event-based orchestration plan](design/event-based-orchestration-plan.md) |
| Airflow / Kafka Compose on NAS | [Infrastructure](../infra/readme.md) |
| Deploy and poller rollout sequence | [CI/CD workflow](design/ci-cd.md) |
| Poller CLI and options | [Extractor and poller](../code/extractor_and_poller/readme.md) |
| Airflow DAGs and variables | [code/airflow](../code/airflow/readme.md) |
| Local commands | [Getting started](../getting-started.md) |

## Prerequisites

Complete before Step 1:

- [ ] `data-solution-2026` clone on BasNAS at `~/apps/data-solution-2026` (or your `APP_ROOT`).
- [ ] Airflow standalone stack running; repo mounted at `/opt/data-solution` via `DATA_SOLUTION_ROOT` in [infra/airflow/.env.example](../infra/airflow/.env.example).
- [ ] Postgres metadata stack running (`infra/postgres`); Airflow on network `data-solution-postgres_default`.
- [ ] Container has poller dependencies (`requests`, `pandas`, `pyarrow`, `jsonschema`, `psycopg[binary]`).
- [ ] Mapping config exists: `data-object-mapping/staging/openmeteo/daily-temperature.json`.
- [ ] Local poller smoke passes from repo root:

```powershell
cd "c:\Dev2\Data Engineering 2.0\data-solution-2026"
$env:PYTHONPATH = "code"
python -m extractor_and_poller.poller --list
python -m extractor_and_poller.poller --data-object source/openmeteo/daily-temperature --publish stdout
```

Expected: log line with `data_object_change` or `data_object_unchanged` and a JSON envelope on stdout.

---

## Implementation steps

### Step 1 — Run the Open-Meteo data object poller in Airflow

**Objective:** Airflow executes the existing poller CLI on a schedule (or manual trigger) and you can verify marker comparison and state persistence from the UI.

#### 1.1 Create the DAG folder and file

DAG source lives under [`code/airflow/dags/`](../code/airflow/dags/). The compose stack mounts that folder into the container (`/opt/airflow/dags`).

1. Confirm `code/airflow/dags/openmeteo_data_object_poller.py` is present (generated orchestration).
2. Review DAG settings:

| Setting | Value |
|---------|--------|
| `dag_id` | `openmeteo_data_object_poller` |
| `schedule` | `@hourly` (or `None` until smoke is green) |
| `catchup` | `false` |
| `max_active_runs` | `1` |
| `is_paused_upon_creation` | `true` |

The repo DAG uses `BashOperator` with working directory `/opt/data-solution` and `PYTHONPATH=/opt/data-solution/code:/opt/data-solution`. Tune behaviour via Airflow Variables (see [code/airflow/readme.md](../code/airflow/readme.md)).

**Smoke command** (Postgres state, optional stdout publish):

```bash
python -m extractor_and_poller.poller \
  --data-object source/openmeteo/daily-temperature \
  --publish stdout
```

Pass connection settings via Airflow Variables or environment (see 1.3).

#### 1.2 Deploy DAGs to the running Airflow container

On BasNAS:

```bash
cd ~/apps/data-solution-2026
git pull origin main
bash infra/scripts/deploy-infra-on-nas.sh
# Or restart only Airflow:
cd ~/apache-airflow   # or infra/airflow on host
docker compose -f docker-compose.standalone.yaml up -d
```

Confirm the DAG appears in the UI (`https://airflow.basnas/` or host port `8081`) without import errors.

#### 1.3 Configure Airflow for the poller task

Set **Airflow Variables** (Admin → Variables) or export env vars in compose for the task:

| Variable / env | Example | Purpose |
|----------------|---------|---------|
| `poller_data_object_id` | `source/openmeteo/daily-temperature` | Selects mapping via source id |
| `poller_publish` | `none` → `stdout` → `kafka` | Event transport (ramp gradually) |
| `POSTGRES_HOST` | `postgres:5432` on Docker network | Poller metadata (`poller` table) |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | `data-solution-2026` on NAS | DSN pieces for poller |
| `KAFKA_HOST` | `kafka:9092` on shared Docker network | When `poller_publish=kafka` |

Optional: uncomment the `kafka` external network in [docker-compose.standalone.yaml](../infra/airflow/docker-compose.standalone.yaml) so the Airflow container can reach the broker.

`psycopg[binary]` is included in default `_PIP_ADDITIONAL_REQUIREMENTS`.

#### 1.4 Wire Postgres metadata (before schedule)

1. Start Postgres: `bash infra/scripts/deploy-infra-on-nas.sh` (starts `~/data-solution-postgres` before Airflow).
2. Run one manual poller execution; the poller creates table `poller` if missing (see [code/postgres/schema.sql](../code/postgres/schema.sql)).
3. Re-run the poller; confirm second run emits `data_object_unchanged` when the Open-Meteo marker did not advance.

#### 1.5 Manual DAG run and acceptance

1. Leave the DAG **paused**.
2. Trigger **DAG → Trigger DAG** once.
3. Open task logs and verify:
   - [ ] Probe reached Open-Meteo API (no import / network errors).
   - [ ] Log shows `data_object_change` or `data_object_unchanged` with `new=` / `old=` markers.
   - [ ] State persisted (`Persisted poller rows to Postgres table poller`).
4. Trigger again without source change; expect `data_object_unchanged` only.
5. When stable, set `poller_publish=stdout` and confirm JSON envelope in logs.
6. **Unpause** the DAG only after the checks above pass.

**Step 1 done when:** scheduled or manual Airflow runs execute the poller reliably and baseline state survives restarts (Postgres backend).

---

### Step 2 — Publish poll events to Kafka

**Objective:** Each poll run publishes `data_object_change` or `data_object_unchanged` to Kafka with the envelope defined in the orchestration plan.

1. Confirm Kafka stack is up ([infra/kafka](../infra/kafka/)).
2. Create topics (if not auto-created): `data_object_change`, `data_object_unchanged`.
3. Connect Airflow to the `kafka_default` network (compose change in Step 1.3).
4. Set `poller_publish=kafka` and `KAFKA_HOST` (e.g. `kafka:9092`).
5. Update the DAG command to:

```bash
python -m extractor_and_poller.poller \
  --data-object source/openmeteo/daily-temperature \
  --publish kafka
```

6. Trigger the poller DAG; consume one message in Kafka UI and validate fields: `event_id`, `event_type`, `data_object_id`, `current_marker`, `previous_marker`, `run_id`.

**Done when:** every poller run produces exactly one message on the correct topic with key `data_object_id`.

---

### Step 3 — React to change events (event controller)

**Objective:** A small consumer service reads `data_object_change` and triggers downstream work (initially log-only, then Airflow API).

Follow [Phase 4 — Event controller](design/event-based-orchestration-plan.md#phase-4---event-controller):

1. Implement consumer with schema validation for the poll envelope.
2. Deploy in **passive mode**: log valid events, do not trigger extract yet.
3. Enable **active mode**: call Airflow REST API to trigger the extract DAG with `mapping_id`, `current_marker`, and `event_id` in conf.

**Done when:** a synthetic or real change event creates exactly one queued extract DAG run.

---

### Step 4 — Run extract on change in Airflow

**Objective:** Extract DAG lands Parquet only when the marker changed; replays do not duplicate work.

Follow [Phase 5 — Extract DAG and idempotency](design/event-based-orchestration-plan.md#phase-5---extract-dag-and-idempotency):

1. Add `code/airflow/dags/openmeteo_daily_temperature_extract.py` (name as you prefer; keep stable in release notes).
2. Task command:

```bash
python -m extractor_and_poller.openmeteo.extractor --mapping daily-temperature
```

3. Write `extract_run_audit` rows (Postgres) with `event_id`, marker, output path, row count, status.
4. Enforce idempotency: skip if `event_id` already processed.

**Done when:** one `data_object_change` event → one extract run → file under `data/staging/openmeteo/daily-temperature/`.

---

### Step 5 — End-to-end validation on BasNAS

Run the smoke sequence from the orchestration plan:

1. Trigger poller DAG manually (or wait for schedule).
2. Verify Kafka message and Postgres `poller` / `event_log` rows.
3. On marker change, verify extract DAG triggered and Parquet landed.
4. Re-trigger with unchanged marker; verify no duplicate extract.
5. Replay same `event_id`; verify idempotent skip.

Document any failures in [lessons-learned.md](../lessons-learned.md).

---

### Step 6 — Production rollout and operations

Align with [Poller rollout merged into CI/CD](design/ci-cd.md#poller-rollout-merged-into-cicd) and release process:

1. Merge DAG and controller code to `main`; tag release; NAS `git pull` via deploy script.
2. Roll out in order: poller DAG (paused) → Kafka publish → passive controller → active triggers → idempotency tests.
3. Record DAG ids and rollback tag in [release notes](../release/release-notes-template.md).
4. Keep poller DAG paused on failed deploy until smoke passes.

---

## Definition of done

The PoC orchestration path is complete when all of the following are true:

- [ ] **Step 1:** Open-Meteo data object poller runs in Airflow on schedule with Postgres state.
- [ ] **Step 2:** Poll results publish to Kafka with a stable envelope.
- [ ] **Step 3:** Change events trigger extract orchestration (no manual extract for routine loads).
- [ ] **Step 4:** Extract is idempotent per `event_id` and lands staging Parquet.
- [ ] **Step 5:** End-to-end smoke on BasNAS documented in a release note.
- [ ] Runbook pointers updated in [readme.md](../readme.md) documentation table if new operational steps were added.

For schema-level acceptance criteria, use [Definition of done](design/event-based-orchestration-plan.md#definition-of-done) in the event-based orchestration plan.

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](../readme.md)
  - Code
    - Airflow
      - Dags
    - Extractor_And_Poller
      - Common
      - Openmeteo
        - Extractor
        - Poller
      - Poller
      - Tests
    - Postgres
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
    - Data Solution
      - Data Object Mapping
    - Design
      - [Architecture](design/architecture.md)
      - [CI/CD workflow (main only + server pull deploy)](design/ci-cd.md)
      - [Event-based orchestration plan (single data object)](design/event-based-orchestration-plan.md)
      - [Meta data design](design/meta-data-design.md)
    - [Implementation plan (Open-Meteo → event orchestration)](implementation-plan.md)
  - Extractor_And_Poller
  - Infra
    - Airflow
      - Dags
    - Kafka
    - Postgres
  - Release
    - Details
      - V2026.06.02.1
      - V2026.06.02.2
      - V2026.06.03.1
      - V2026.06.03.2
      - V2026.06.03.3
      - V2026.06.03.4
      - V2026.06.04.1
      - V2026.06.04.2
      - ﻿V2026.06.04.1
      - ﻿V2026.06.04.2
    - Notes
      - [Release v2026.06.02.1](../release/notes/v2026.06.02.1.md)
      - [Release v2026.06.02.2](../release/notes/v2026.06.02.2.md)
      - [Release v2026.06.03.1](../release/notes/v2026.06.03.1.md)
      - [Release v2026.06.03.2](../release/notes/v2026.06.03.2.md)
      - [Release v2026.06.03.3](../release/notes/v2026.06.03.3.md)
      - [Release v2026.06.03.4](../release/notes/v2026.06.03.4.md)
      - [V2026.06.04.1](../release/notes/v2026.06.04.1.md)
      - [V2026.06.04.2](../release/notes/v2026.06.04.2.md)
    - [Release <version>](../release/release-notes-template.md)
  - Setting
  - Template
  - [Getting started](../getting-started.md)
  - [Lessons learned](../lessons-learned-part1.md)
  - [Lessons learned (part 2)](../lessons-learned-part2.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
