# Extractor and poller

## Table of contents

<!-- markdown-toc:start -->
- [Overview](#overview)
- [Poller metadata](#poller-metadata)
<!-- markdown-toc:end -->

## Overview

Open-Meteo extractor and poller driven by `data-object-mapping/` JSON. Lives under `code/extractor_and_poller/` (runtime *how* code).

Run from the solution root with `code/` on `PYTHONPATH`:

```powershell
cd "c:\Dev2\Data Engineering 2.0\data-solution-2026"
$env:PYTHONPATH = "code"
python -m extractor_and_poller.poller --list
python -m extractor_and_poller.poller --data-object source/openmeteo/daily-temperature
python -m extractor_and_poller.openmeteo.extractor --mapping daily-temperature
```

Event-oriented poller options:

```powershell
# Publish events to stdout for local debugging (production uses Airflow Assets)
python -m extractor_and_poller.poller --data-object source/openmeteo/daily-temperature --publish stdout
```

Airflow asset URIs: [Airflow asset naming](../../doc/design/airflow-asset-naming.md) (`ds://source/openmeteo/daily-temperature/change`).

**Asset-scheduled extract** is handled by the extract DAG `schedule=[source_change_asset]` — see [Implementation plan — Step 3](../../doc/implementation/implementation-plan.md#step-3-react-to-change-assets-native-airflow-scheduling).

The `openmeteo/` subfolder holds `extractor/` and `poller/` probes. Shared helpers live under `common/`; the generic poller CLI is in `poller/`.

Airflow DAGs: [`code/airflow/`](../airflow/readme.md).

## Poller metadata

- No local files or directories are created by the poller.
- Each run appends one row to Postgres table `poller` (see [../postgres/schema.sql](../postgres/schema.sql)).
- Query `poller_latest_first` to browse newest probe events first.
- Schema upgrades on deploy: [../../infra/postgres/run-applicable-migrations.sh](../../infra/postgres/run-applicable-migrations.sh) (when `run_db_migrations` is set in deploy-config).
- Environment: `POSTGRES_HOST`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `DATA_SOLUTION_DB` (default `data-solution-2026`), or `POSTGRES_DSN`.

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
      - Cicd
        - [CI/CD workflow (main only + server pull deploy)](../../doc/design/cicd/ci-cd.md)
      - Monitoring
        - [Monitoring architecture](../../doc/design/monitoring/monitoring-architecture.md)
      - [Airflow asset naming](../../doc/design/airflow-asset-naming.md)
      - [Event-based orchestration plan](../../doc/design/event-based-orchestration-plan.md)
      - [Meta data design](../../doc/design/meta-data-design.md)
    - Image
    - Implementation
      - [Implementation plan (Open-Meteo → event orchestration)](../../doc/implementation/implementation-plan.md)
    - Linked In
      - [Linkedin Post Part3V2](../../doc/linked-in/linkedin-post-part3v2.md)
    - Operation
      - [Event orchestration monitoring](../../doc/operation/event-orchestration-monitoring.md)
    - Retrospective
      - Incident
        - [INC-001 — NAS non-interactive SSH environment](../../doc/retrospective/incident/inc-001-nas-ssh-environment.md)
        - [INC-002 — Airflow standalone infra instability](../../doc/retrospective/incident/inc-002-airflow-infra-stability.md)
        - [INC-003 — Agent rediscovery and false-done verification](../../doc/retrospective/incident/inc-003-agent-process-gaps.md)
        - [INC-004 — Airflow PYTHONPATH drift (dag_run_guard import)](../../doc/retrospective/incident/inc-004-airflow-pythonpath-drift.md)
        - [INC-<NNN> — <short title>](../../doc/retrospective/incident/incident-template.md)
      - [Issue categories](../../doc/retrospective/issue-category.md)
    - [Implementation plan](../../doc/implementation-plan.md)
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
