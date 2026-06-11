# Infrastructure (Docker)

## Table of contents

<!-- markdown-toc:start -->
- [Purpose](#purpose)
- [Layout](#layout)
- [Local server deployment](#local-server-deployment)
  - [Sync script (recommended)](#sync-script-recommended)
  - [Manual compose (from repo paths)](#manual-compose-from-repo-paths)
- [Airflow](#airflow)
- [Postgres](#postgres)
  - [UI shows Bad Gateway or Missing Meta Database / Scheduler / Triggerer](#ui-shows-bad-gateway-or-missing-meta-database-scheduler-triggerer)
  - [Non-interactive SSH: git fails with libcharset.so.1](#non-interactive-ssh-git-fails-with-libcharsetso1)
  - [SSH: docker: command not found](#ssh-docker-command-not-found)
  - [Task logs show http://:8793/... No host supplied](#task-logs-show-http8793-no-host-supplied)
- [Kafka](#kafka)
- [Related docs](#related-docs)
<!-- markdown-toc:end -->

## Purpose

Version-controlled Docker Compose for the PoC runtime on the local server: **Apache Airflow** (orchestration), **Apache Kafka** (change events), and **PostgreSQL** (runtime metadata). Application libraries live under `code/extractor_and_poller/`; these stacks host the services. SSH and service URLs: [local-server.env.example](local-server.env.example).

Source of truth on NAS today:

| Service | NAS path (historical) | Compose file in this repo |
|---------|----------------------|---------------------------|
| Airflow | `~/apache-airflow/` | [airflow/docker-compose.standalone.yaml](airflow/docker-compose.standalone.yaml) |
| Kafka | `~/kafka/` | [kafka/docker-compose.yml](kafka/docker-compose.yml) |
| Postgres (shared) | `basnas_postgress` on host **5432** | [postgres/](postgres/) (setup scripts only) |

## Layout

```text
infra/
  readme.md
  scripts/
    deploy-infra-on-nas.sh           # sync to ~/apache-airflow, ~/kafka, ~/data-solution-postgres
  airflow/
    docker-compose.standalone.yaml   # active Airflow stack (standalone)
    .env.example
  kafka/
    docker-compose.yml               # Kafka + Kafka UI
  postgres/
    create-app-user.sh               # schema + app role on basnas_postgress

code/                                # generated runtime (not under infra/)
  airflow/dags/                      # DAG files → /opt/airflow/dags
  extractor_and_poller/              # poller + extractor CLIs
  postgres/schema.sql                # DDL reference
```

The large upstream multi-service Airflow template (`docker-compose.yaml` with Celery/Redis/Postgres) is **not** vendored here; this PoC uses **standalone** mode only. See [Apache Airflow Docker docs](https://airflow.apache.org/docs/docker-stack/index.html) if you need that layout.

## Local server deployment

### Sync script (recommended)

Copies compose files from `infra/` into legacy NAS folders (`~/apache-airflow`, `~/kafka`), keeps existing `.env` / `logs` / Kafka data, sets `DATA_SOLUTION_ROOT`, and restarts stacks.

Routine pushes to `main` run infra sync automatically when [release/deploy-config.json](../release/deploy-config.json) has `sync_infra: true` (pre-commit sets this when stack files under `infra/airflow`, `infra/kafka`, or `infra/postgres` change since the last release tag). Only the listed `infra_components` are copied and restarted — a Kafka-only change does not recreate Airflow. Force a full sync manually:

```bash
RUN_INFRA_SYNC=1 bash ~/apps/data-solution-2026/release/scripts/deploy-on-nas.sh
```

Options:

| Variable | Default | Meaning |
|----------|---------|---------|
| `APP_ROOT` | `~/apps/data-solution-2026` | Repo clone |
| `AIRFLOW_DEST` | `~/apache-airflow` | Airflow compose target |
| `KAFKA_DEST` | `~/kafka` | Kafka compose target |
| `POSTGRES_DEST` | `~/data-solution-postgres` | Postgres config + setup scripts (no compose) |
| `INFRA_COMPONENTS` | from `deploy-config.json` | Comma-separated subset: `airflow`, `kafka`, `postgres` |
| `RUN_COMPOSE` | `1` | Run `docker compose up -d` after sync |
| `DRY_RUN` | `0` | Print actions only |

Combined app + infra deploy:

```bash
RUN_INFRA_SYNC=1 bash release/scripts/deploy-on-nas.sh
```

### Manual compose (from repo paths)

```bash
cd ~/apps/data-solution-2026/infra/postgres
cp -n .env.example ~/data-solution-postgres/.env
# Edit .env: POSTGRES_PASSWORD = basnas_postgress admin password
bash create-app-user.sh

cd ~/apps/data-solution-2026/infra/kafka
cp -n .env.example .env 2>/dev/null || true
docker compose up -d

cd ~/apps/data-solution-2026/infra/airflow
cp -n .env.example .env
# Set DATA_SOLUTION_ROOT to the clone root on NAS
docker compose -f docker-compose.standalone.yaml up -d
```

HTTPS UI: `${LOCAL_SERVER_URL_AIRFLOW}` and `${LOCAL_SERVER_URL_KAFKA}` (values in [local-server.env.example](local-server.env.example); NGINX setup in [local server deploy skill](https://github.com/basvdberg/cursor-config/tree/main/skills/deploy-basnas-container)).

## Airflow

- Image: `apache/airflow:3.2.0`, command `standalone`, container name `airflow-standalone`.
- Host port default: `8081` → container `8080`.
- Mounts application repo at `/opt/data-solution` (read-only) and `${DATA_SOLUTION_ROOT}/data` (read-write for Parquet).
- `PYTHONPATH=/opt/data-solution/code:/opt/data-solution` so DAG tasks run `python -m extractor_and_poller...`.
- Mounts `${DATA_SOLUTION_ROOT}/code/airflow/dags` at `/opt/airflow/dags` (see [code/airflow](../code/airflow/readme.md)).
- Joins external network `immich_default` so tasks reach `basnas_postgress:5432` (table `poller`).
- Install runtime deps via `_PIP_ADDITIONAL_REQUIREMENTS` in `.env` (includes `psycopg[binary]`).
- `PYTHONUNBUFFERED=1` and `AIRFLOW__LOGGING__TASK_LOG_TO_STDOUT=true` in compose so task subprocess logs reach the UI without buffering delay.

Optional: uncomment the `kafka` external network in [docker-compose.standalone.yaml](airflow/docker-compose.standalone.yaml) after Kafka is up so tasks can reach `kafka:9092`.

## Postgres

- **Shared instance:** existing container `basnas_postgress` on host port **5432** (Docker network `immich_default`). Airflow connects as `basnas_postgress:5432`; SQL clients use `basnas:5432`.
- Database: `data-solution-2026` (see [postgres/.env.example](postgres/.env.example)).
- Schema DDL: [code/postgres/schema.sql](../code/postgres/schema.sql), applied by [postgres/create-app-user.sh](postgres/create-app-user.sh).
- Incremental migrations: [code/postgres/migrations/](../code/postgres/migrations/) with applicability checks; [postgres/run-applicable-migrations.sh](postgres/run-applicable-migrations.sh) runs from [release/scripts/deploy-on-nas.sh](../release/scripts/deploy-on-nas.sh) when `release/deploy-config.json` has `run_db_migrations=true` (set by pre-commit when migration files change). Force with `RUN_DB_MIGRATIONS=1`; skip with `RUN_DB_MIGRATIONS=0`.
- Application role: `data-solution-2026_app` (login, `SELECT`/`INSERT` on `poller` only). Create or rotate with `create-app-user.sh`; set `POSTGRES_USER` / `POSTGRES_PASSWORD` in Airflow `.env` to that role (see [airflow/.env.example](airflow/.env.example)).
- Upgrading from `data_solution`: run [postgres/migrate-database-name.sh](postgres/migrate-database-name.sh) once, update `.env`, then `create-app-user.sh`.
- Poller appends one row per probe to table `poller` (`data_object_id`, `polled_at_utc`, markers, `event_type`, `event_id`, `run_id`).

**Migrating from the legacy dedicated Postgres (`data-solution-postgres` on port 5433):**

```bash
bash infra/postgres/migrate-poller-from-dedicated-postgres.sh
bash infra/postgres/remove-dedicated-postgres.sh
```

Then redeploy Airflow so it joins `immich_default` instead of `data-solution-postgres_default`.

### UI shows Bad Gateway or Missing Meta Database / Scheduler / Triggerer

Common causes on the local server:

1. **Still starting** — On each `up` or recreate, the image may run `_PIP_ADDITIONAL_REQUIREMENTS` and `airflow standalone` DB init (often 3–5 minutes). NGINX returns **502 Bad Gateway** until the API listens on port 8080. Wait, then check: `curl -s http://127.0.0.1:8081/api/v2/monitor/health`.
2. **Logs volume permissions** — `logs/` and `plugins/` on the host must be writable by the container user. Set `AIRFLOW_UID=$(id -u)` in `.env` and use the `user:` line in [docker-compose.standalone.yaml](airflow/docker-compose.standalone.yaml). Symptom in logs: `PermissionError: ... '/opt/airflow/logs/dag_processor'`.
3. **HTTPS proxy** — `${LOCAL_SERVER_URL_AIRFLOW}` proxies to `http://airflow-standalone:8080`. NGINX must share the `apache-airflow_default` network with the Airflow container (see local server deploy skill `patch-bridge-upstreams.sh` after recreates).

**Admin login:** user `admin`, password from `AIRFLOW_ADMIN_PASSWORD` in [airflow/.env](airflow/.env) (see [.env.example](airflow/.env.example)). The compose file writes that value into the Simple Auth Manager passwords file on each container start, so recreating the stack does not change the password. After upgrading an existing NAS `.env`, add `AIRFLOW_ADMIN_PASSWORD=...` (or re-sync from `.env.example` on a new install).

### Non-interactive SSH: `git` fails with `libcharset.so.1`

QNAP `/usr/bin/git` needs `libcharset.so.1` from an optional QPKG (NGinX on this NAS). Non-interactive SSH (`ssh $LOCAL_SERVER_SSH 'git …'`; see [local-server.env.example](local-server.env.example)) uses `PATH=/usr/bin:/bin` only and does not load `~/.profile`.

Fix (run once on NAS after pull):

```bash
bash infra/scripts/setup-nas-ssh-env.sh
```

That installs `~/.local/bin/git` (sets `LD_LIBRARY_PATH` only for git) and writes `~/.ssh/environment`. For bare `ssh … git` without `bash -lc`, enable user environment once (admin password):

```bash
bash infra/scripts/enable-nas-ssh-user-env.sh
```

Deploy scripts source [nas-remote-env.sh](scripts/nas-remote-env.sh) automatically. Do **not** set global `LD_LIBRARY_PATH` in `~/.profile` — it breaks QNAP `/bin/bash` and Cursor Remote SSH.

### SSH: `docker: command not found`

Container Station installs `docker` under `/share/CACHEDEV*_DATA/.qpkg/container-station/bin`, which QNAP does not put on `PATH` for SSH sessions.

Fix (run once on NAS after pull):

```bash
bash infra/scripts/setup-nas-ssh-env.sh
```

That installs `~/.local/bin/nas-path.sh`, `~/.local/bin/docker` (symlink), and `~/.local/bin/nas-login-sh`. Interactive `ssh $LOCAL_SERVER_SSH` loads `nas-path.sh` from `~/.profile`.

For bare `ssh $LOCAL_SERVER_SSH 'docker …'` (agents and CI hooks), set the login shell once (survives QNAP reboot):

```bash
ssh $LOCAL_SERVER_SSH
sudo cp -p /etc/passwd /etc/passwd.bak.nas-path
sudo sed -i 's#:/bin/sh$#:/share/homes/bas/.local/bin/nas-login-sh#' /etc/passwd
```

`sudo` uses the **QTS administrator password**, not the SSH user password. QNAP Control Panel has no custom-shell field. Manual `PermitUserEnvironment` in `/etc/config/ssh/sshd_config` is **wiped on reboot** — do not rely on it. See Cursor skill **basnas-ssh** (`cursor-config/skills/basnas-ssh`).

Verify (after `source local-server.env.example` or your `local-server.env`):

```bash
ssh $LOCAL_SERVER_SSH 'docker --version'
ssh $LOCAL_SERVER_SSH 'command -v docker'
```

### Task logs show `http://:8793/... No host supplied`

Airflow 3 stores a worker hostname on each task run and builds log URLs like `http://<hostname>:8793/log/...`. In Docker on QNAP, the default hostname detector (`getfqdn`) often returns an empty string, so the UI shows **Could not read served logs: Invalid URL 'http://:8793/...': No host supplied**.

Fix (already in [docker-compose.standalone.yaml](airflow/docker-compose.standalone.yaml)):

- Set container `hostname: airflow-standalone`
- Set `AIRFLOW__CORE__HOSTNAME_CALLABLE=airflow.utils.net.get_host_ip_address`

Redeploy on the local server:

```bash
cd ~/apache-airflow   # or ~/apps/data-solution-2026/infra/airflow
docker compose -f docker-compose.standalone.yaml up -d
```

**Existing runs** keep the old empty hostname in the DB; trigger a new DAG run to verify. To read logs for a failed run immediately:

```bash
docker exec airflow-standalone ls /opt/airflow/logs/dag_id=openmeteo_data_object_poller/
docker exec airflow-standalone cat '/opt/airflow/logs/dag_id=openmeteo_data_object_poller/run_id=.../task_id=poll_openmeteo_daily_temperature/attempt=2.log'
```

## Kafka

- Broker: `apache/kafka:3.8.0` on ports `9092` / `9093`.
- UI: `provectuslabs/kafka-ui` on host port `8085`.

## Related docs

- [Generated runtime code](../code/readme.md)
- [CI/CD workflow](../doc/design/ci-cd.md)
- [Event-based orchestration plan](../doc/design/event-based-orchestration-plan.md)
- [Getting started](../getting-started.md)

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
      - [Architecture](../doc/design/architecture.md)
      - [CI/CD workflow (main only + server pull deploy)](../doc/design/ci-cd.md)
      - [Event-based orchestration plan (single data object)](../doc/design/event-based-orchestration-plan.md)
      - [Kafka topic naming](../doc/design/kafka-topic-naming.md)
      - [Meta data design](../doc/design/meta-data-design.md)
    - Operation
      - Incident
        - [INC-001 — NAS non-interactive SSH environment](../doc/operation/incident/inc-001-nas-ssh-environment.md)
        - [INC-002 — Airflow standalone infra instability](../doc/operation/incident/inc-002-airflow-infra-stability.md)
        - [INC-003 — Agent rediscovery and false-done verification](../doc/operation/incident/inc-003-agent-process-gaps.md)
        - [INC-004 — Airflow PYTHONPATH drift (dag_run_guard import)](../doc/operation/incident/inc-004-airflow-pythonpath-drift.md)
        - [INC-<NNN> — <short title>](../doc/operation/incident/incident-template.md)
      - [Issue categories](../doc/operation/issue-category.md)
    - [Implementation plan (Open-Meteo → event orchestration)](../doc/implementation-plan.md)
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
          - V2026.06.11.4
            - [Notes](../release/2026/06/11/v2026.06.11.4/notes.md)
            - [Retrospective](../release/2026/06/11/v2026.06.11.4/retrospective.md)
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
