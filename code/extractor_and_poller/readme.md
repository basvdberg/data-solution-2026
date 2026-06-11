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
# Publish events: stdout = full JSON envelope; Kafka = data_object_id on ds.poll.* topics
python -m extractor_and_poller.poller --data-object source/openmeteo/daily-temperature --publish stdout
python -m extractor_and_poller.poller --data-object source/openmeteo/daily-temperature --publish kafka
```

Kafka topic names: [Kafka topic naming](../../doc/design/kafka-topic-naming.md) (`ds.poll.data_object_change`, `ds.poll.data_object_progress`).

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
  - Docs
    - [LinkedIn post (part 3)](../../docs/linkedin-post-part3.md)
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
          - V2026.06.09.14
            - [Notes](../../release/2026/06/09/v2026.06.09.14/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.14/retrospective.md)
          - V2026.06.09.15
            - [Notes](../../release/2026/06/09/v2026.06.09.15/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.15/retrospective.md)
          - V2026.06.09.16
            - [Notes](../../release/2026/06/09/v2026.06.09.16/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.16/retrospective.md)
          - V2026.06.09.17
            - [Notes](../../release/2026/06/09/v2026.06.09.17/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.17/retrospective.md)
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
        - 11
          - V2026.06.11.1
            - [Notes](../../release/2026/06/11/v2026.06.11.1/notes.md)
            - [Retrospective](../../release/2026/06/11/v2026.06.11.1/retrospective.md)
          - V2026.06.11.2
            - [Notes](../../release/2026/06/11/v2026.06.11.2/notes.md)
            - [Retrospective](../../release/2026/06/11/v2026.06.11.2/retrospective.md)
          - V2026.06.11.3
            - [Notes](../../release/2026/06/11/v2026.06.11.3/notes.md)
            - [Retrospective](../../release/2026/06/11/v2026.06.11.3/retrospective.md)
          - V2026.06.11.4
            - [Notes](../../release/2026/06/11/v2026.06.11.4/notes.md)
            - [Retrospective](../../release/2026/06/11/v2026.06.11.4/retrospective.md)
          - V2026.06.11.5
            - [Notes](../../release/2026/06/11/v2026.06.11.5/notes.md)
            - [Retrospective](../../release/2026/06/11/v2026.06.11.5/retrospective.md)
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
