# Implementation plan (Open-Meteo → event orchestration)

## Table of contents

<!-- markdown-toc:start -->
- [Goal](#goal)
- [Scope](#scope)
- [Related documentation](#related-documentation)
- [Prerequisites](#prerequisites)
  - [Local server setup (ordered)](#local-server-setup-ordered)
    - [1 — One-time host tooling](#1-one-time-host-tooling)
    - [2 — Clone the application repo](#2-clone-the-application-repo)
    - [3 — Postgres metadata stack](#3-postgres-metadata-stack)
    - [4 — Kafka stack (needed before Step 2; optional for Step 1)](#4-kafka-stack-needed-before-step-2-optional-for-step-1)
    - [5 — Airflow standalone stack](#5-airflow-standalone-stack)
    - [6 — Sync compose files and restart stacks](#6-sync-compose-files-and-restart-stacks)
    - [7 — Poller runtime config (automated)](#7-poller-runtime-config-automated)
    - [8 — Service readiness checklist](#8-service-readiness-checklist)
  - [Application and smoke checks](#application-and-smoke-checks)
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
  - [Step 5 — End-to-end validation on the local server](#step-5-end-to-end-validation-on-the-local-server)
  - [Step 6 — Production rollout and operations](#step-6-production-rollout-and-operations)
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
| Poller DAG id (target) | `openmeteo_data_object_poller` |

Out of scope for this plan: additional sources, multi-mapping routing, and advanced retry policies.

## Related documentation

| Topic | Document |
|-------|----------|
| Target architecture and event contract | [Event-based orchestration plan](design/event-based-orchestration-plan.md) |
| Airflow / Kafka Compose on NAS | [Infrastructure](../infra/readme.md) |
| Deploy to the local server (commit + push `main`) | [CI/CD workflow](design/ci-cd.md) · Cursor skill `.cursor/skills/deploy-basnas-via-cicd` (local server deploy) |
| Poller CLI and options | [Extractor and poller](../code/extractor_and_poller/readme.md) |
| Airflow DAGs and variables | [code/airflow](../code/airflow/readme.md) |
| Local commands | [Getting started](../getting-started.md) |

## Prerequisites

Complete everything below before [Step 1](#step-1-run-the-open-meteo-data-object-poller-in-airflow). Detailed stack behaviour: [Infrastructure](../infra/readme.md). Deploy automation: [CI/CD workflow](design/ci-cd.md).

### Local server setup (ordered)

Run on the local server over SSH unless noted. Connection settings: [infra/local-server.env.example](../infra/local-server.env.example). Check off each step in order.

#### 1 — One-time host tooling

- [ ] **Docker** available for SSH sessions. If `docker: command not found`, run once from the repo clone:

```bash
cd ~/apps/data-solution-2026
bash infra/scripts/setup-nas-ssh-env.sh
```

- [ ] **Git** works over non-interactive SSH. If `git` fails with `libcharset.so.1`, the same script fixes it; for bare `ssh … git`, also run `bash infra/scripts/enable-nas-ssh-user-env.sh` once (admin password). See [Infrastructure — SSH troubleshooting](../infra/readme.md#non-interactive-ssh-git-fails-with-libcharsetso1).

#### 2 — Clone the application repo

- [ ] Clone or update `data-solution-2026` at `~/apps/data-solution-2026` (or set `APP_ROOT` to your path). NAS must be able to `git pull` from the remote (HTTPS token or deploy key).

```bash
mkdir -p ~/apps
cd ~/apps
git clone <your-remote-url> data-solution-2026   # first time only
cd ~/apps/data-solution-2026
git checkout main
git pull origin main
```

#### 3 — Postgres metadata stack

**First-time tip:** Seed compose files and `.env` without starting containers, then edit secrets, then start stacks:

```bash
cd ~/apps/data-solution-2026
RUN_COMPOSE=0 bash infra/scripts/deploy-infra-on-nas.sh
# Edit ~/data-solution-postgres/.env and ~/apache-airflow/.env (steps 3 and 5), then run deploy again without RUN_COMPOSE=0
```

- [ ] **Create `.env`** at `~/data-solution-postgres/.env` (deploy script can seed this from [infra/postgres/.env.example](../infra/postgres/.env.example)). Edit secrets — do not commit `.env`:

| Variable | Set to | Notes |
|----------|--------|--------|
| `POSTGRES_USER` | `postgres` | Bootstrap superuser inside the container |
| `POSTGRES_PASSWORD` | Strong secret | Superuser password |
| `DATA_SOLUTION_DB` | `data-solution-2026` | Database name |
| `POSTGRES_CONTAINER` | `basnas_postgress` | Shared Postgres container on host port `5432` |
| `DATA_SOLUTION_APP_USER` | `data-solution-2026_app` | Poller / Airflow application role |
| `DATA_SOLUTION_APP_PASSWORD` | Strong secret | Must match Airflow `.env` after step 5 |
| `DATA_SOLUTION_ROOT` | Absolute path to clone | e.g. `/share/.../apps/data-solution-2026` |

- [ ] **Ensure shared Postgres** (`basnas_postgress`) is running on host port `5432` (no dedicated compose stack in this repo).

- [ ] **Create the application role** (reads `~/data-solution-postgres/.env`; prints password if generated):

```bash
cd ~/apps/data-solution-2026
bash infra/postgres/create-app-user.sh
```

- [ ] **Verify**: `create-app-user.sh` applied [code/postgres/schema.sql](../code/postgres/schema.sql) on database `data-solution-2026`.

#### 4 — Kafka stack (needed before Step 2; optional for Step 1)

- [ ] **Optional `.env`** at `~/kafka/.env` — only if you need a new cluster id ([infra/kafka/.env.example](../infra/kafka/.env.example)); changing `KAFKA_CLUSTER_ID` on an existing volume wipes data.

- [ ] **Start Kafka** (included in `deploy-infra-on-nas.sh` after Postgres). Confirm broker and UI: `${LOCAL_SERVER_URL_KAFKA}` (see [local-server.env.example](../infra/local-server.env.example)) or host port `8085`.

#### 5 — Airflow standalone stack

- [ ] **Create or update `.env`** at `~/apache-airflow/.env` from [infra/airflow/.env.example](../infra/airflow/.env.example). Required values:

| Variable | Set to | Notes |
|----------|--------|--------|
| `AIRFLOW_ADMIN_PASSWORD` | Strong secret | UI login user `admin` |
| `AIRFLOW_UID` | `id -u` on NAS | Writable `logs/` and `plugins/` on host |
| `DATA_SOLUTION_ROOT` | Same absolute path as Postgres | Mounts repo at `/opt/data-solution` |
| `AIRFLOW_HOST_PORT` | e.g. `8081` | Host → container `8080` |
| `POSTGRES_HOST` | `basnas_postgress:5432` | Shared Postgres on Docker network `immich_default` |
| `POSTGRES_USER` | `data-solution-2026_app` | From `create-app-user.sh` |
| `POSTGRES_PASSWORD` | Same as `DATA_SOLUTION_APP_PASSWORD` | Must match Postgres `.env` |
| `DATA_SOLUTION_DB` | `data-solution-2026` | |

- [ ] **`_PIP_ADDITIONAL_REQUIREMENTS`** — leave commented to use the compose default (`requests`, `pandas`, `pyarrow`, `jsonschema`, `psycopg[binary]`, optional `kafka-python`).

- [ ] **Start Airflow** (deploy script starts Postgres → Kafka → Airflow). First start can take **3–5 minutes** (`_PIP_ADDITIONAL_REQUIREMENTS` + DB init); `${LOCAL_SERVER_URL_AIRFLOW}` may return 502 until healthy (see [local-server.env.example](../infra/local-server.env.example)).

```bash
curl -s http://127.0.0.1:8081/api/v2/monitor/health
```

- [ ] **Verify mounts**: DAG folder `${DATA_SOLUTION_ROOT}/code/airflow/dags` → `/opt/airflow/dags`; app code at `/opt/data-solution`; `PYTHONPATH` includes `/opt/data-solution/code`.

- [ ] **Verify network**: Airflow container joins external network `immich_default` so tasks reach `basnas_postgress:5432`.

- [ ] **Step 2+**: Airflow compose joins external network `kafka_default` and sets `KAFKA_HOST=kafka:9092` when enabling Kafka publish (see [docker-compose.standalone.yaml](../infra/airflow/docker-compose.standalone.yaml)).

#### 6 — Sync compose files and restart stacks

After pushing `infra/` changes to `main`, run on the local server (app pull is already done by CI/CD):

```bash
RUN_INFRA_SYNC=1 bash ~/apps/data-solution-2026/release/scripts/deploy-on-nas.sh
```

That runs `infra/scripts/deploy-infra-on-nas.sh`: copies compose to `~/apache-airflow` and `~/kafka`, syncs Postgres setup scripts to `~/data-solution-postgres`, preserves `.env`, sets `DATA_SOLUTION_ROOT` when missing, ensures `data/staging/...` dirs exist, and runs `docker compose up -d` for Kafka and Airflow. Options: `RUN_COMPOSE=0` (sync only), `DRY_RUN=1` (print actions). See [infra/readme.md](../infra/readme.md).

#### 7 — Poller runtime config (automated)

`deploy-infra-on-nas.sh` appends missing keys to `~/apache-airflow/.env` from [`.env.example`](../infra/airflow/.env.example), including `KAFKA_HOST=kafka:9092`. The poller DAG always uses `--publish kafka`; no transport toggle variable.

| Setting | Source | Default |
|---------|--------|---------|
| Kafka bootstrap | `KAFKA_HOST` in `~/apache-airflow/.env` | `kafka:9092` |
| Postgres DSN pieces | `POSTGRES_HOST`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `DATA_SOLUTION_DB` in `.env` | see `.env.example` |
| Data object id | DAG code default; optional Airflow Variable `data_object_id` | `source/openmeteo/daily-temperature` |

Obsolete variables (`publish_transport`, `poller_publish`, `kafka_host`) are removed on infra deploy.

#### 8 — Service readiness checklist

- [ ] Postgres: `basnas_postgress` is up on host port `5432`; poller can connect as `data-solution-2026_app`.
- [ ] Airflow: UI loads at `${LOCAL_SERVER_URL_AIRFLOW}` (or `http://<local-server>:8081`; URLs in [local-server.env.example](../infra/local-server.env.example)); login `admin` + `AIRFLOW_ADMIN_PASSWORD`.
- [ ] DAG `openmeteo_data_object_poller` appears without import errors (paused by default).
- [ ] HTTPS reverse proxy: NGINX shares the Airflow Docker network with `airflow-standalone` (see local server deploy skill if 502 persists after health is green).

### Application and smoke checks

- [ ] **Mapping config** exists: `data-object-mapping/staging/openmeteo/daily-temperature.json`.

- [ ] **Optional — local poller smoke** (dev machine; confirms CLI before NAS DAG):

```powershell
cd "c:\Dev2\Data Engineering 2.0\data-solution-2026"
$env:PYTHONPATH = "code"
python -m extractor_and_poller.poller --list
python -m extractor_and_poller.poller --data-object source/openmeteo/daily-temperature --publish stdout
```

Expected: log line with `data_object_change` or `data_object_progress` and a JSON envelope on stdout. On NAS, the equivalent check is a manual DAG trigger in Step 1.5.

- [ ] **Optional — poller smoke on NAS** after Postgres is up:

```bash
docker exec airflow-standalone bash -lc '
  cd /opt/data-solution &&
  PYTHONPATH=/opt/data-solution/code:/opt/data-solution \
  python -m extractor_and_poller.poller \
    --data-object source/openmeteo/daily-temperature \
    --publish none
'
```

Expected: probe log and `Persisted poller rows to Postgres table poller`.

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

The repo DAG uses `PythonOperator` to call `extractor_and_poller.poller` CLI `main()` (wrapper only; no duplicated poller logic). Container `PYTHONPATH` is `/opt/data-solution/code:/opt/data-solution`. Tune behaviour via Airflow Variables (see [code/airflow/readme.md](../code/airflow/readme.md)).

**Smoke command** (Postgres state, optional stdout publish):

```bash
python -m extractor_and_poller.poller \
  --data-object source/openmeteo/daily-temperature \
  --publish stdout
```

Pass connection settings via Airflow Variables or environment (see 1.3).

#### 1.2 Deploy DAGs to the running Airflow container

**Routine deploy:** commit and push to `main`; [CI/CD](design/ci-cd.md) runs tests and the post-push hook runs `release/scripts/deploy-on-nas.sh` on the local server (resets the clone to `origin/main`, discarding local edits). DAGs are bind-mounted from `code/airflow/dags/`—no manual copy.

After deploy (or if compose under `infra/` changed), sync stacks when needed:

```bash
RUN_INFRA_SYNC=1 bash ~/apps/data-solution-2026/release/scripts/deploy-on-nas.sh
```

Manual fallback only (troubleshooting): `bash ~/apps/data-solution-2026/release/scripts/deploy-on-nas.sh` or restart Airflow in `~/apache-airflow`.

Confirm the DAG appears in the UI (`${LOCAL_SERVER_URL_AIRFLOW}` or host port `8081`; see [local-server.env.example](../infra/local-server.env.example)) without import errors.

#### 1.3 Configure Airflow for the poller task

Infra deploy sets `~/apache-airflow/.env` (Postgres + `KAFKA_HOST`) and restarts stacks. Airflow joins `kafka_default` via [docker-compose.standalone.yaml](../infra/airflow/docker-compose.standalone.yaml).

| Setting | Example | Purpose |
|---------|---------|---------|
| `KAFKA_HOST` | `kafka:9092` | Kafka bootstrap (poller publishes every run) |
| `POSTGRES_HOST` | `basnas_postgress:5432` | Poller metadata (`poller` table) |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `DATA_SOLUTION_DB` | `data-solution-2026` on NAS | DSN pieces for poller |
| `data_object_id` (optional Variable) | `source/openmeteo/daily-temperature` | Override probed data object |

`psycopg[binary]` is included in default `_PIP_ADDITIONAL_REQUIREMENTS`.

#### 1.4 Wire Postgres metadata (before schedule)

1. Run `bash infra/postgres/create-app-user.sh` on `basnas_postgress` (shared Postgres on host port `5432`).
2. Run one manual poller execution; the poller creates table `poller` if missing (see [code/postgres/schema.sql](../code/postgres/schema.sql)).
3. Re-run the poller; confirm second run emits `data_object_progress` when the Open-Meteo marker did not advance.

#### 1.5 Manual DAG run and acceptance

1. Leave the DAG **paused**.
2. Trigger **DAG → Trigger DAG** once.
3. Open task logs and verify:
   - [ ] Probe reached Open-Meteo API (no import / network errors).
   - [ ] Log shows `data_object_change` or `data_object_progress` with `new=` / `old=` markers.
   - [ ] State persisted (`Persisted poller rows to Postgres table poller`).
4. Trigger again without source change; expect `data_object_progress` only.
5. Confirm Kafka publish in task logs (`event_published transport=kafka`) and a topic in Kafka UI.
6. **Unpause** the DAG only after the checks above pass.

**Step 1 done when:** scheduled or manual Airflow runs execute the poller reliably and baseline state survives restarts (Postgres backend).

---

### Step 2 — Publish poll events to Kafka

**Objective:** Each poll run publishes to Kafka (topics per [Kafka topic naming](design/kafka-topic-naming.md); auto-created when the broker allows).

Automated by infra deploy: Kafka stack up, Airflow on `kafka_default`, `KAFKA_HOST` in `.env`, DAG uses `--publish kafka`.

**Validate after deploy:**

1. Trigger the poller DAG once.
2. Task logs show `event_published transport=kafka`.
3. Kafka UI lists the poll topic(s) with at least one message (key `data_object_id`).

**Done when:** every poller run produces exactly one message on the correct topic with key `data_object_id`.

---

### Step 3 — React to change events (event controller)

**Objective:** A small consumer service reads `ds.poll.data_object_change` and triggers downstream work (initially log-only, then Airflow API).

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

**Done when:** one `ds.poll.data_object_change` event → one extract run → file under `data/staging/openmeteo/daily-temperature/`.

---

### Step 5 — End-to-end validation on the local server

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

1. Commit and push DAG and controller code to `main`; release and NAS deploy run via [CI/CD](design/ci-cd.md) (post-push hook → `deploy-on-nas.sh`).
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
- [ ] **Step 5:** End-to-end smoke on the local server documented in a release note.
- [ ] Runbook pointers updated in [readme.md](../readme.md) documentation table if new operational steps were added.

For schema-level acceptance criteria, use [Definition of done](design/event-based-orchestration-plan.md#definition-of-done) in the event-based orchestration plan.

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](../readme.md)
  - Code
    - Airflow
      - Dags
      - Plugins
    - Extractor_And_Poller
      - Common
      - Controller
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
    - Data Solution
      - Data Object Mapping
    - Design
      - [Architecture](design/architecture.md)
      - [CI/CD workflow (main only + server pull deploy)](design/ci-cd.md)
      - [Event-based orchestration plan (single data object)](design/event-based-orchestration-plan.md)
      - [Kafka topic naming](design/kafka-topic-naming.md)
      - [Meta data design](design/meta-data-design.md)
    - Operation
      - Incident
        - [INC-001 — NAS non-interactive SSH environment](operation/incident/inc-001-nas-ssh-environment.md)
        - [INC-002 — Airflow standalone infra instability](operation/incident/inc-002-airflow-infra-stability.md)
        - [INC-003 — Agent rediscovery and false-done verification](operation/incident/inc-003-agent-process-gaps.md)
        - [INC-004 — Airflow PYTHONPATH drift (dag_run_guard import)](operation/incident/inc-004-airflow-pythonpath-drift.md)
        - [INC-<NNN> — <short title>](operation/incident/incident-template.md)
      - [Issue categories](operation/issue-category.md)
    - [Implementation plan (Open-Meteo → event orchestration)](implementation-plan.md)
  - Docs
    - [LinkedIn post (part 3)](../docs/linkedin-post-part3.md)
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
            - [Notes](../release/2026/06/02/v2026.06.02.1/notes.md)
          - V2026.06.02.2
            - [Release v2026.06.02.2](../release/2026/06/02/v2026.06.02.2/notes.md)
        - 03
          - V2026.06.03.1
            - [Release v2026.06.03.1](../release/2026/06/03/v2026.06.03.1/notes.md)
          - V2026.06.03.2
            - [Release v2026.06.03.2](../release/2026/06/03/v2026.06.03.2/notes.md)
          - V2026.06.03.3
            - [Release v2026.06.03.3](../release/2026/06/03/v2026.06.03.3/notes.md)
          - V2026.06.03.4
            - [Release v2026.06.03.4](../release/2026/06/03/v2026.06.03.4/notes.md)
            - [Retrospective](../release/2026/06/03/v2026.06.03.4/retrospective.md)
        - 04
          - V2026.06.04.1
            - [Notes](../release/2026/06/04/v2026.06.04.1/notes.md)
        - 05
          - V2026.06.05.6
            - [Notes](../release/2026/06/05/v2026.06.05.6/notes.md)
            - [Retrospective](../release/2026/06/05/v2026.06.05.6/retrospective.md)
        - 08
          - V2026.06.08.1
            - [Notes](../release/2026/06/08/v2026.06.08.1/notes.md)
            - [Retrospective](../release/2026/06/08/v2026.06.08.1/retrospective.md)
          - V2026.06.08.2
            - [Notes](../release/2026/06/08/v2026.06.08.2/notes.md)
            - [Retrospective](../release/2026/06/08/v2026.06.08.2/retrospective.md)
        - 09
          - V2026.06.09.1
            - [Notes](../release/2026/06/09/v2026.06.09.1/notes.md)
            - [Retrospective](../release/2026/06/09/v2026.06.09.1/retrospective.md)
          - V2026.06.09.10
            - [Notes](../release/2026/06/09/v2026.06.09.10/notes.md)
            - [Retrospective](../release/2026/06/09/v2026.06.09.10/retrospective.md)
          - V2026.06.09.11
            - [Notes](../release/2026/06/09/v2026.06.09.11/notes.md)
            - [Retrospective](../release/2026/06/09/v2026.06.09.11/retrospective.md)
          - V2026.06.09.12
            - [Notes](../release/2026/06/09/v2026.06.09.12/notes.md)
            - [Retrospective](../release/2026/06/09/v2026.06.09.12/retrospective.md)
          - V2026.06.09.13
            - [Notes](../release/2026/06/09/v2026.06.09.13/notes.md)
            - [Retrospective](../release/2026/06/09/v2026.06.09.13/retrospective.md)
          - V2026.06.09.14
            - [Notes](../release/2026/06/09/v2026.06.09.14/notes.md)
            - [Retrospective](../release/2026/06/09/v2026.06.09.14/retrospective.md)
          - V2026.06.09.15
            - [Notes](../release/2026/06/09/v2026.06.09.15/notes.md)
            - [Retrospective](../release/2026/06/09/v2026.06.09.15/retrospective.md)
          - V2026.06.09.16
            - [Notes](../release/2026/06/09/v2026.06.09.16/notes.md)
            - [Retrospective](../release/2026/06/09/v2026.06.09.16/retrospective.md)
          - V2026.06.09.17
            - [Notes](../release/2026/06/09/v2026.06.09.17/notes.md)
            - [Retrospective](../release/2026/06/09/v2026.06.09.17/retrospective.md)
          - V2026.06.09.2
            - [Notes](../release/2026/06/09/v2026.06.09.2/notes.md)
            - [Retrospective](../release/2026/06/09/v2026.06.09.2/retrospective.md)
          - V2026.06.09.3
            - [Notes](../release/2026/06/09/v2026.06.09.3/notes.md)
            - [Retrospective](../release/2026/06/09/v2026.06.09.3/retrospective.md)
          - V2026.06.09.4
            - [Notes](../release/2026/06/09/v2026.06.09.4/notes.md)
            - [Retrospective](../release/2026/06/09/v2026.06.09.4/retrospective.md)
          - V2026.06.09.5
            - [Notes](../release/2026/06/09/v2026.06.09.5/notes.md)
            - [Retrospective](../release/2026/06/09/v2026.06.09.5/retrospective.md)
          - V2026.06.09.6
            - [Notes](../release/2026/06/09/v2026.06.09.6/notes.md)
            - [Retrospective](../release/2026/06/09/v2026.06.09.6/retrospective.md)
          - V2026.06.09.7
            - [Notes](../release/2026/06/09/v2026.06.09.7/notes.md)
            - [Retrospective](../release/2026/06/09/v2026.06.09.7/retrospective.md)
          - V2026.06.09.8
            - [Notes](../release/2026/06/09/v2026.06.09.8/notes.md)
            - [Retrospective](../release/2026/06/09/v2026.06.09.8/retrospective.md)
          - V2026.06.09.9
            - [Notes](../release/2026/06/09/v2026.06.09.9/notes.md)
            - [Retrospective](../release/2026/06/09/v2026.06.09.9/retrospective.md)
        - 11
          - V2026.06.11.1
            - [Notes](../release/2026/06/11/v2026.06.11.1/notes.md)
            - [Retrospective](../release/2026/06/11/v2026.06.11.1/retrospective.md)
          - V2026.06.11.2
            - [Notes](../release/2026/06/11/v2026.06.11.2/notes.md)
            - [Retrospective](../release/2026/06/11/v2026.06.11.2/retrospective.md)
          - V2026.06.11.3
            - [Notes](../release/2026/06/11/v2026.06.11.3/notes.md)
            - [Retrospective](../release/2026/06/11/v2026.06.11.3/retrospective.md)
    - [Release <version>](../release/release-notes-template.md)
    - [Retrospective — <version>](../release/retrospective-template.md)
  - Setting
  - Template
  - [Getting started](../getting-started.md)
  - [Lessons learned](../lessons-learned-part1.md)
  - [Lessons learned (part 2)](../lessons-learned-part2.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
