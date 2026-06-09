# Getting started

## Table of contents

<!-- markdown-toc:start -->
- [Prerequisites](#prerequisites)
- [Quick start](#quick-start)
- [Infrastructure (Docker)](#infrastructure-docker)
- [Run key components](#run-key-components)
<!-- markdown-toc:end -->

## Prerequisites

- Python 3.11+
- Dependencies installed for `data-solution-2026` (including `psycopg[binary]` for poller metadata and optional `kafka-python` for event publish)
- Postgres database `data-solution-2026` on shared `basnas_postgress` (host port **5432**; see [infra/postgres](infra/postgres/create-app-user.sh))
- Run commands from the `data-solution-2026/` root

## Quick start

```powershell
cd "c:\Dev2\Data Engineering 2.0\data-solution-2026"
```

## Infrastructure (Docker)

Airflow and Kafka Compose files for the local server: [infra/readme.md](infra/readme.md). Connection settings: [infra/local-server.env.example](infra/local-server.env.example).

Airflow DAGs (generated orchestration): [code/airflow/readme.md](code/airflow/readme.md).

## Run key components

```powershell
$env:PYTHONPATH = "code"

# 1) List enabled data object poller entries
python -m extractor_and_poller.poller --list

# 2) Poll source/openmeteo/daily-temperature (requires Postgres; see infra/postgres)
python -m extractor_and_poller.poller --data-object source/openmeteo/daily-temperature

# 3) Run extractor for OpenMeteo data object
python -m extractor_and_poller.openmeteo.extractor --mapping daily-temperature
```

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](readme.md)
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
      - [Architecture](doc/design/architecture.md)
      - [CI/CD workflow (main only + server pull deploy)](doc/design/ci-cd.md)
      - [Event-based orchestration plan (single data object)](doc/design/event-based-orchestration-plan.md)
      - [Kafka topic naming](doc/design/kafka-topic-naming.md)
      - [Meta data design](doc/design/meta-data-design.md)
    - Operation
      - Incident
        - [INC-001 — NAS non-interactive SSH environment](doc/operation/incident/inc-001-nas-ssh-environment.md)
        - [INC-002 — Airflow standalone infra instability](doc/operation/incident/inc-002-airflow-infra-stability.md)
        - [INC-003 — Agent rediscovery and false-done verification](doc/operation/incident/inc-003-agent-process-gaps.md)
        - [INC-004 — Airflow PYTHONPATH drift (dag_run_guard import)](doc/operation/incident/inc-004-airflow-pythonpath-drift.md)
        - [INC-<NNN> — <short title>](doc/operation/incident/incident-template.md)
      - [Issue categories](doc/operation/issue-category.md)
    - [Implementation plan (Open-Meteo → event orchestration)](doc/implementation-plan.md)
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
            - [Notes](release/2026/06/02/v2026.06.02.1/notes.md)
          - V2026.06.02.2
            - [Release v2026.06.02.2](release/2026/06/02/v2026.06.02.2/notes.md)
        - 03
          - V2026.06.03.1
            - [Release v2026.06.03.1](release/2026/06/03/v2026.06.03.1/notes.md)
          - V2026.06.03.2
            - [Release v2026.06.03.2](release/2026/06/03/v2026.06.03.2/notes.md)
          - V2026.06.03.3
            - [Release v2026.06.03.3](release/2026/06/03/v2026.06.03.3/notes.md)
          - V2026.06.03.4
            - [Release v2026.06.03.4](release/2026/06/03/v2026.06.03.4/notes.md)
            - [Retrospective](release/2026/06/03/v2026.06.03.4/retrospective.md)
        - 04
          - V2026.06.04.1
            - [Notes](release/2026/06/04/v2026.06.04.1/notes.md)
        - 05
          - V2026.06.05.6
            - [Notes](release/2026/06/05/v2026.06.05.6/notes.md)
            - [Retrospective](release/2026/06/05/v2026.06.05.6/retrospective.md)
        - 08
          - V2026.06.08.1
            - [Notes](release/2026/06/08/v2026.06.08.1/notes.md)
            - [Retrospective](release/2026/06/08/v2026.06.08.1/retrospective.md)
          - V2026.06.08.2
            - [Notes](release/2026/06/08/v2026.06.08.2/notes.md)
            - [Retrospective](release/2026/06/08/v2026.06.08.2/retrospective.md)
        - 09
          - V2026.06.09.1
            - [Notes](release/2026/06/09/v2026.06.09.1/notes.md)
            - [Retrospective](release/2026/06/09/v2026.06.09.1/retrospective.md)
          - V2026.06.09.10
            - [Notes](release/2026/06/09/v2026.06.09.10/notes.md)
            - [Retrospective](release/2026/06/09/v2026.06.09.10/retrospective.md)
          - V2026.06.09.11
            - [Notes](release/2026/06/09/v2026.06.09.11/notes.md)
            - [Retrospective](release/2026/06/09/v2026.06.09.11/retrospective.md)
          - V2026.06.09.12
            - [Notes](release/2026/06/09/v2026.06.09.12/notes.md)
            - [Retrospective](release/2026/06/09/v2026.06.09.12/retrospective.md)
          - V2026.06.09.13
            - [Notes](release/2026/06/09/v2026.06.09.13/notes.md)
            - [Retrospective](release/2026/06/09/v2026.06.09.13/retrospective.md)
          - V2026.06.09.14
            - [Notes](release/2026/06/09/v2026.06.09.14/notes.md)
            - [Retrospective](release/2026/06/09/v2026.06.09.14/retrospective.md)
          - V2026.06.09.2
            - [Notes](release/2026/06/09/v2026.06.09.2/notes.md)
            - [Retrospective](release/2026/06/09/v2026.06.09.2/retrospective.md)
          - V2026.06.09.3
            - [Notes](release/2026/06/09/v2026.06.09.3/notes.md)
            - [Retrospective](release/2026/06/09/v2026.06.09.3/retrospective.md)
          - V2026.06.09.4
            - [Notes](release/2026/06/09/v2026.06.09.4/notes.md)
            - [Retrospective](release/2026/06/09/v2026.06.09.4/retrospective.md)
          - V2026.06.09.5
            - [Notes](release/2026/06/09/v2026.06.09.5/notes.md)
            - [Retrospective](release/2026/06/09/v2026.06.09.5/retrospective.md)
          - V2026.06.09.6
            - [Notes](release/2026/06/09/v2026.06.09.6/notes.md)
            - [Retrospective](release/2026/06/09/v2026.06.09.6/retrospective.md)
          - V2026.06.09.7
            - [Notes](release/2026/06/09/v2026.06.09.7/notes.md)
            - [Retrospective](release/2026/06/09/v2026.06.09.7/retrospective.md)
          - V2026.06.09.8
            - [Notes](release/2026/06/09/v2026.06.09.8/notes.md)
            - [Retrospective](release/2026/06/09/v2026.06.09.8/retrospective.md)
          - V2026.06.09.9
            - [Notes](release/2026/06/09/v2026.06.09.9/notes.md)
            - [Retrospective](release/2026/06/09/v2026.06.09.9/retrospective.md)
    - [Release <version>](release/release-notes-template.md)
    - [Retrospective — <version>](release/retrospective-template.md)
  - Setting
  - Template
  - [Getting started](getting-started.md)
  - [Lessons learned](lessons-learned-part1.md)
  - [Lessons learned (part 2)](lessons-learned-part2.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
