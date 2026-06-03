# Infrastructure (Docker)

## Table of contents

<!-- markdown-toc:start -->
- [Purpose](#purpose)
- [Layout](#layout)
- [BasNAS deployment](#basnas-deployment)
  - [Sync script (recommended)](#sync-script-recommended)
  - [Manual compose (from repo paths)](#manual-compose-from-repo-paths)
- [Airflow](#airflow)
  - [UI shows Bad Gateway or Missing Meta Database / Scheduler / Triggerer](#ui-shows-bad-gateway-or-missing-meta-database-scheduler-triggerer)
  - [Task logs show http://:8793/... No host supplied](#task-logs-show-http8793-no-host-supplied)
- [Kafka](#kafka)
- [Related docs](#related-docs)
<!-- markdown-toc:end -->

## Purpose

Version-controlled Docker Compose for the PoC runtime on BasNAS: **Apache Airflow** (orchestration) and **Apache Kafka** (change events). Application code stays in the repo root (`extractor_and_poller/`); these stacks only host the services.

Source of truth on NAS today:

| Service | NAS path (historical) | Compose file in this repo |
|---------|----------------------|---------------------------|
| Airflow | `~/apache-airflow/` | [airflow/docker-compose.standalone.yaml](airflow/docker-compose.standalone.yaml) |
| Kafka | `~/kafka/` | [kafka/docker-compose.yml](kafka/docker-compose.yml) |

## Layout

```text
infra/
  readme.md
  scripts/
    deploy-infra-on-nas.sh           # sync to ~/apache-airflow and ~/kafka
  airflow/
    docker-compose.standalone.yaml   # active Airflow stack (standalone)
    .env.example
  kafka/
    docker-compose.yml               # Kafka + Kafka UI

code/                                # generated runtime (not under infra/)
  airflow/dags/                      # DAG files → /opt/airflow/dags
```

The large upstream multi-service Airflow template (`docker-compose.yaml` with Celery/Redis/Postgres) is **not** vendored here; this PoC uses **standalone** mode only. See [Apache Airflow Docker docs](https://airflow.apache.org/docs/docker-stack/index.html) if you need that layout.

## BasNAS deployment

### Sync script (recommended)

Copies compose files from `infra/` into legacy NAS folders (`~/apache-airflow`, `~/kafka`), keeps existing `.env` / `logs` / Kafka data, sets `DATA_SOLUTION_ROOT`, and restarts stacks:

```bash
cd ~/apps/data-solution-2026
git pull origin main
bash infra/scripts/deploy-infra-on-nas.sh
```

Options:

| Variable | Default | Meaning |
|----------|---------|---------|
| `APP_ROOT` | `~/apps/data-solution-2026` | Repo clone |
| `AIRFLOW_DEST` | `~/apache-airflow` | Airflow compose target |
| `KAFKA_DEST` | `~/kafka` | Kafka compose target |
| `RUN_COMPOSE` | `1` | Run `docker compose up -d` after sync |
| `DRY_RUN` | `0` | Print actions only |

Combined app + infra deploy:

```bash
RUN_INFRA_SYNC=1 bash release/scripts/deploy-on-nas.sh
```

### Manual compose (from repo paths)

```bash
cd ~/apps/data-solution-2026/infra/kafka
cp -n .env.example .env 2>/dev/null || true
docker compose up -d

cd ~/apps/data-solution-2026/infra/airflow
cp -n .env.example .env
# Set DATA_SOLUTION_ROOT to the clone root on NAS
docker compose -f docker-compose.standalone.yaml up -d
```

HTTPS UI: `https://airflow.basnas/` and `https://kafka.basnas/` (see [BasNAS deploy skill](https://github.com/basvdberg/data-engineering-2026/tree/main/cursor-config/skills/deploy-basnas-container) in the parent monorepo).

## Airflow

- Image: `apache/airflow:3.2.0`, command `standalone`, container name `airflow-standalone`.
- Host port default: `8081` → container `8080`.
- Mounts application repo at `/opt/data-solution` so DAG tasks can run `python -m extractor_and_poller...`.
- Mounts `${DATA_SOLUTION_ROOT}/code/airflow/dags` at `/opt/airflow/dags` (see [code/airflow](../code/airflow/readme.md)).
- Install runtime deps via `_PIP_ADDITIONAL_REQUIREMENTS` in `.env` (PoC shortcut) or a custom image for production.

Optional: uncomment the `kafka` external network in [docker-compose.standalone.yaml](airflow/docker-compose.standalone.yaml) after Kafka is up so tasks can reach `kafka:9092`.

### UI shows Bad Gateway or Missing Meta Database / Scheduler / Triggerer

Common causes on BasNAS:

1. **Still starting** — On each `up` or recreate, the image may run `_PIP_ADDITIONAL_REQUIREMENTS` and `airflow standalone` DB init (often 3–5 minutes). NGINX returns **502 Bad Gateway** until the API listens on port 8080. Wait, then check: `curl -s http://127.0.0.1:8081/api/v2/monitor/health`.
2. **Logs volume permissions** — `logs/` and `plugins/` on the host must be writable by the container user. Set `AIRFLOW_UID=$(id -u)` in `.env` and use the `user:` line in [docker-compose.standalone.yaml](airflow/docker-compose.standalone.yaml). Symptom in logs: `PermissionError: ... '/opt/airflow/logs/dag_processor'`.
3. **HTTPS proxy** — `https://airflow.basnas/` proxies to `http://airflow-standalone:8080`. NGINX must share the `apache-airflow_default` network with the Airflow container (see BasNAS deploy skill `patch-bridge-upstreams.sh` after recreates).

Admin password after a fresh standalone init: `docker logs airflow-standalone 2>&1 | grep "Password for user"`.

### Task logs show `http://:8793/... No host supplied`

Airflow 3 stores a worker hostname on each task run and builds log URLs like `http://<hostname>:8793/log/...`. In Docker on QNAP, the default hostname detector (`getfqdn`) often returns an empty string, so the UI shows **Could not read served logs: Invalid URL 'http://:8793/...': No host supplied**.

Fix (already in [docker-compose.standalone.yaml](airflow/docker-compose.standalone.yaml)):

- Set container `hostname: airflow-standalone`
- Set `AIRFLOW__CORE__HOSTNAME_CALLABLE=airflow.utils.net.get_host_ip_address`

Redeploy on BasNAS:

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
      - [Meta data design](../doc/design/meta-data-design.md)
    - [Implementation plan (Open-Meteo → event orchestration)](../doc/implementation-plan.md)
  - Extractor_And_Poller
    - Common
    - Openmeteo
      - Extractor
      - Poller
    - Poller
    - Tests
  - Infra
    - Airflow
      - Dags
    - Kafka
  - Release
    - Details
      - V2026.06.02.1
      - V2026.06.02.2
    - Notes
      - [Release v2026.06.02.1](../release/notes/v2026.06.02.1.md)
      - [Release v2026.06.02.2](../release/notes/v2026.06.02.2.md)
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
