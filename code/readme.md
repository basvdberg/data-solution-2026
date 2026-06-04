# Code (generated runtime)

## Table of contents

<!-- markdown-toc:start -->
- [Purpose](#purpose)
- [Layout](#layout)
- [Relationship to metadata](#relationship-to-metadata)
- [Airflow](#airflow)
- [Postgres metadata](#postgres-metadata)
<!-- markdown-toc:end -->

## Purpose

This folder holds **generated and hand-maintained runtime code** that implements *how* the data solution runs on BasNAS: orchestration (Airflow), extractor/poller libraries, Postgres schema, and future event controllers.

It is separate from:

| Location | Role |
|----------|------|
| `data-object-mapping/`, `data-object/`, `connection/` | DSA metadata — *what* should happen |
| `data/` | Landing files (Parquet); gitignored |
| `output/` | ADL-generated SQL |
| `infra/` | Docker Compose and deploy scripts |

## Layout

```text
code/
  readme.md
  postgres/
    schema.sql              # table poller (+ future audit tables)
  extractor_and_poller/     # Open-Meteo extractor and generic poller CLI
  airflow/
    readme.md
    dags/
      openmeteo_data_object_poller.py
```

## Relationship to metadata

Configuration stays in Git as JSON under `data-object-mapping/`. DAGs and libraries in `code/` read those ids. Runtime state (poller history, markers) is stored in Postgres (`connection/metadata-postgres.json`), not in the repo.

## Airflow

DAGs live in [airflow/dags/](airflow/dags/). The Airflow container mounts `${DATA_SOLUTION_ROOT}/code/airflow/dags` and sets `PYTHONPATH=/opt/data-solution/code:/opt/data-solution`.

## Postgres metadata

- Schema reference: [postgres/schema.sql](postgres/schema.sql)
- Compose stack: [infra/postgres](../infra/postgres/docker-compose.yml)
- Poller rows: table `poller` with `data_object_id`, `polled_at_utc`, `old_marker`, `new_marker`, and event envelope fields

Rollout: [Implementation plan](../doc/implementation-plan.md).
