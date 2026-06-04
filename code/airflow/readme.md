# Airflow (generated)

## Table of contents

<!-- markdown-toc:start -->
- [DAGs](#dags)
- [Configuration](#configuration)
- [Poller DAG](#poller-dag)
<!-- markdown-toc:end -->

## DAGs

Python files under [dags/](dags/) are loaded by the Airflow scheduler from `/opt/airflow/dags` in the container.

## Configuration

Set Airflow Variables (Admin → Variables) to override defaults used by the poller DAG:

| Variable | Default | Purpose |
|----------|---------|---------|
| `poller_data_object_id` | `source/openmeteo/daily-temperature` | `--data-object` for the poller CLI |
| `poller_publish` | `none` | `none`, `stdout`, or `kafka` |

Poller state is always stored in Postgres (table `poller`). Postgres connection settings use container environment variables (`POSTGRES_HOST`, `POSTGRES_USER`, etc.). See [Implementation plan](../../doc/implementation-plan.md).

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
  --publish none
```

`PYTHONPATH` is set in the Airflow container (`/opt/data-solution/code:/opt/data-solution`).

The task runs as `PythonOperator` so it **inherits** container env vars (`POSTGRES_HOST`, `POSTGRES_USER`, etc.). Do not use a custom operator `env` dict that only sets `PYTHONPATH`—that replaces the whole environment and breaks Postgres (defaults to `localhost:5432`).

Confirm `~/apache-airflow/.env` on BasNAS includes `POSTGRES_HOST=postgres:5432` and `DATA_SOLUTION_DB=data-solution-2026` (see `infra/airflow/.env.example`). After changing `.env`, restart Airflow: `docker compose -f docker-compose.standalone.yaml up -d` in `~/apache-airflow`.

**DAG still shows BashOperator?** The bind-mounted DAG file comes from `~/apps/data-solution-2026`. If the NAS clone is behind `origin/main`, run `bash ~/apps/data-solution-2026/release/scripts/deploy-on-nas.sh`, then `docker exec airflow-standalone airflow dags reserialize`, and trigger a new run (old task attempts keep the operator they started with).

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](../../readme.md)
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
      - [Architecture](../../doc/design/architecture.md)
      - [CI/CD workflow (main only + server pull deploy)](../../doc/design/ci-cd.md)
      - [Event-based orchestration plan (single data object)](../../doc/design/event-based-orchestration-plan.md)
      - [Meta data design](../../doc/design/meta-data-design.md)
    - [Implementation plan (Open-Meteo → event orchestration)](../../doc/implementation-plan.md)
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
      - V2026.06.04.3
      - V2026.06.04.4
      - V2026.06.04.5
      - V2026.06.04.6
      - V2026.06.04.7
      - ﻿V2026.06.04.1
      - ﻿V2026.06.04.2
      - ﻿V2026.06.04.3
      - ﻿V2026.06.04.4
      - ﻿V2026.06.04.5
      - ﻿V2026.06.04.6
      - ﻿V2026.06.04.7
    - Notes
      - [Release v2026.06.02.1](../../release/notes/v2026.06.02.1.md)
      - [Release v2026.06.02.2](../../release/notes/v2026.06.02.2.md)
      - [Release v2026.06.03.1](../../release/notes/v2026.06.03.1.md)
      - [Release v2026.06.03.2](../../release/notes/v2026.06.03.2.md)
      - [Release v2026.06.03.3](../../release/notes/v2026.06.03.3.md)
      - [Release v2026.06.03.4](../../release/notes/v2026.06.03.4.md)
      - [V2026.06.04.1](../../release/notes/v2026.06.04.1.md)
      - [V2026.06.04.2](../../release/notes/v2026.06.04.2.md)
      - [V2026.06.04.3](../../release/notes/v2026.06.04.3.md)
      - [V2026.06.04.4](../../release/notes/v2026.06.04.4.md)
      - [V2026.06.04.5](../../release/notes/v2026.06.04.5.md)
      - [V2026.06.04.6](../../release/notes/v2026.06.04.6.md)
      - [V2026.06.04.7](../../release/notes/v2026.06.04.7.md)
    - [Release <version>](../../release/release-notes-template.md)
  - Setting
  - Template
  - [Getting started](../../getting-started.md)
  - [Lessons learned](../../lessons-learned-part1.md)
  - [Lessons learned (part 2)](../../lessons-learned-part2.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
