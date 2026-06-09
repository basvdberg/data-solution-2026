# Airflow (generated)

## Table of contents

<!-- markdown-toc:start -->
- [DAGs](#dags)
- [Configuration](#configuration)
- [Poller DAG](#poller-dag)
<!-- markdown-toc:end -->

**Target runtime:** Apache Airflow **3.2.0** (`apache/airflow:3.2.0` in [`infra/airflow/docker-compose.standalone.yaml`](../../infra/airflow/docker-compose.standalone.yaml)). DAGs import from `airflow.sdk`; operators from `airflow.providers.standard.*`.

## DAGs

Python files under [dags/](dags/) are loaded by the Airflow scheduler from `/opt/airflow/dags` in the container.

## Configuration

The poller DAG always runs with `--publish kafka`. Kafka bootstrap servers come from container env `KAFKA_HOST` (set automatically by [deploy-infra-on-nas.sh](../../infra/scripts/deploy-infra-on-nas.sh) from [`.env.example`](../../infra/airflow/.env.example)).

Optional Airflow Variable (override only):

| Variable | Default | Value semantics |
|----------|---------|-----------------|
| `data_object_id` | `source/openmeteo/daily-temperature` | Source data object id probed by the poller |

Poller state is stored in Postgres (table `poller`). Postgres connection uses `POSTGRES_HOST`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `DATA_SOLUTION_DB` from `~/apache-airflow/.env` (also applied by deploy-infra). See [Implementation plan](../../doc/implementation-plan.md).

Local CLI debugging may still use `--publish none` or `--publish stdout`; production Airflow does not use a transport toggle variable.

## Poller DAG

| Property | Value |
|----------|--------|
| File | `dags/openmeteo_data_object_poller.py` |
| `dag_id` | `openmeteo_data_object_poller` |
| Schedule | `@hourly` (paused on creation until smoke passes) |

The DAG task is a `PythonOperator` that calls `extractor_and_poller.poller.__main__.main()` with the same arguments as the CLI (no duplicated poller logic).

Equivalent manual run inside the Airflow container:

```bash
python -m extractor_and_poller.poller \
  --data-object source/openmeteo/daily-temperature \
  --publish kafka
```

`PYTHONPATH` is set in the Airflow container (`/opt/data-solution/code:/opt/data-solution`).

The task runs as `PythonOperator` so it **inherits** container env vars (`POSTGRES_HOST`, `POSTGRES_USER`, etc.). Do not use a custom operator `env` dict that only sets `PYTHONPATH`—that replaces the whole environment and breaks Postgres (defaults to `localhost:5432`).

**Manual trigger while a run is active:** the DAG has `max_active_runs=1`, so Airflow **queues** a new manual run until the current run finishes. That is expected. While queued, the DAG run shows state **queued** in the UI and there are **no task logs** yet — logs appear only when the run moves to **running**. To cancel, clear or fail the queued DAG run from the UI.

**Task logs:** the DAG has no custom logging; output comes from the poller CLI. When run under Airflow, `configure_logging()` does **not** replace Airflow's task log handlers (see `extractor_and_poller.common.logging_setup.running_in_airflow_task`).

Confirm `~/apache-airflow/.env` on the local server includes `POSTGRES_HOST=postgres:5432` and `DATA_SOLUTION_DB=data-solution-2026` (see `infra/airflow/.env.example`). After changing `.env`, restart Airflow: `docker compose -f docker-compose.standalone.yaml up -d` in `~/apache-airflow`.

**DAG still shows BashOperator?** The bind-mounted DAG file comes from `~/apps/data-solution-2026`. If the NAS clone is behind `origin/main`, run `bash ~/apps/data-solution-2026/release/scripts/deploy-on-nas.sh`, then `docker exec airflow-standalone airflow dags reserialize`, and trigger a new run (old task attempts keep the operator they started with).

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](../../readme.md)
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
      - [Architecture](../../doc/design/architecture.md)
      - [CI/CD workflow (main only + server pull deploy)](../../doc/design/ci-cd.md)
      - [Event-based orchestration plan (single data object)](../../doc/design/event-based-orchestration-plan.md)
      - [Kafka topic naming](../../doc/design/kafka-topic-naming.md)
      - [Meta data design](../../doc/design/meta-data-design.md)
    - Operation
      - Incident
        - [INC-001 — NAS non-interactive SSH environment](../../doc/operation/incident/inc-001-nas-ssh-environment.md)
        - [INC-002 — Airflow standalone infra instability](../../doc/operation/incident/inc-002-airflow-infra-stability.md)
        - [INC-003 — Agent rediscovery and false-done verification](../../doc/operation/incident/inc-003-agent-process-gaps.md)
        - [INC-004 — Airflow PYTHONPATH drift (dag_run_guard import)](../../doc/operation/incident/inc-004-airflow-pythonpath-drift.md)
        - [INC-<NNN> — <short title>](../../doc/operation/incident/incident-template.md)
      - [Issue categories](../../doc/operation/issue-category.md)
    - [Implementation plan (Open-Meteo → event orchestration)](../../doc/implementation-plan.md)
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
        - 08
          - V2026.06.08.1
            - [Notes](../../release/2026/06/08/v2026.06.08.1/notes.md)
            - [Retrospective](../../release/2026/06/08/v2026.06.08.1/retrospective.md)
          - V2026.06.08.2
            - [Notes](../../release/2026/06/08/v2026.06.08.2/notes.md)
            - [Retrospective](../../release/2026/06/08/v2026.06.08.2/retrospective.md)
        - 09
          - V2026.06.09.1
            - [Notes](../../release/2026/06/09/v2026.06.09.1/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.1/retrospective.md)
          - V2026.06.09.10
            - [Notes](../../release/2026/06/09/v2026.06.09.10/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.10/retrospective.md)
          - V2026.06.09.11
            - [Notes](../../release/2026/06/09/v2026.06.09.11/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.11/retrospective.md)
          - V2026.06.09.12
            - [Notes](../../release/2026/06/09/v2026.06.09.12/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.12/retrospective.md)
          - V2026.06.09.13
            - [Notes](../../release/2026/06/09/v2026.06.09.13/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.13/retrospective.md)
          - V2026.06.09.2
            - [Notes](../../release/2026/06/09/v2026.06.09.2/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.2/retrospective.md)
          - V2026.06.09.3
            - [Notes](../../release/2026/06/09/v2026.06.09.3/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.3/retrospective.md)
          - V2026.06.09.4
            - [Notes](../../release/2026/06/09/v2026.06.09.4/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.4/retrospective.md)
          - V2026.06.09.5
            - [Notes](../../release/2026/06/09/v2026.06.09.5/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.5/retrospective.md)
          - V2026.06.09.6
            - [Notes](../../release/2026/06/09/v2026.06.09.6/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.6/retrospective.md)
          - V2026.06.09.7
            - [Notes](../../release/2026/06/09/v2026.06.09.7/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.7/retrospective.md)
          - V2026.06.09.8
            - [Notes](../../release/2026/06/09/v2026.06.09.8/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.8/retrospective.md)
          - V2026.06.09.9
            - [Notes](../../release/2026/06/09/v2026.06.09.9/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.9/retrospective.md)
    - [Release <version>](../../release/release-notes-template.md)
    - [Retrospective — <version>](../../release/retrospective-template.md)
  - Setting
  - Template
  - [Getting started](../../getting-started.md)
  - [Lessons learned](../../lessons-learned-part1.md)
  - [Lessons learned (part 2)](../../lessons-learned-part2.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
