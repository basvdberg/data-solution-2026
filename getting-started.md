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
- Dependencies installed for `data-solution-2026` (including `psycopg[binary]` for poller metadata)
- Postgres database `data-solution-2026` on shared `basnas_postgress` (host port **5432**; see [infra/postgres](infra/postgres/create-app-user.sh))
- Run commands from the `data-solution-2026/` root

## Quick start

```powershell
cd "c:\Dev2\Data Engineering 2.0\data-solution-2026"
```

## Infrastructure (Docker)

Airflow Compose files for the local server: [infra/readme.md](infra/readme.md). Connection settings: [infra/local-server.env.example](infra/local-server.env.example).

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
        - [CI/CD workflow (main only + server pull deploy)](doc/design/cicd/ci-cd.md)
      - Monitoring
        - [Monitoring architecture](doc/design/monitoring/monitoring-architecture.md)
      - [Airflow asset naming](doc/design/airflow-asset-naming.md)
      - [Event-based orchestration plan](doc/design/event-based-orchestration-plan.md)
      - [Meta data design](doc/design/meta-data-design.md)
    - Image
    - Implementation
      - [Implementation plan (Open-Meteo → event orchestration)](doc/implementation/implementation-plan.md)
    - Linked In
      - [Data object quality of service](doc/linked-in/data-object-quality-of-service.md)
      - [Linkedin Post Part3V2](doc/linked-in/linkedin-post-part3v2.md)
    - Operation
      - [Event orchestration monitoring](doc/operation/event-orchestration-monitoring.md)
    - Retrospective
      - Incident
        - [INC-001 — NAS non-interactive SSH environment](doc/retrospective/incident/inc-001-nas-ssh-environment.md)
        - [INC-002 — Airflow standalone infra instability](doc/retrospective/incident/inc-002-airflow-infra-stability.md)
        - [INC-003 — Agent rediscovery and false-done verification](doc/retrospective/incident/inc-003-agent-process-gaps.md)
        - [INC-004 — Airflow PYTHONPATH drift (dag_run_guard import)](doc/retrospective/incident/inc-004-airflow-pythonpath-drift.md)
        - [INC-<NNN> — <short title>](doc/retrospective/incident/incident-template.md)
      - [Issue categories](doc/retrospective/issue-category.md)
    - [Implementation plan](doc/implementation-plan.md)
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
        - 12
          - V2026.06.12.1
            - [Release v2026.06.12.1](release/2026/06/12/v2026.06.12.1/notes.md)
    - [Release <version>](release/release-notes-template.md)
    - [Retrospective — <version>](release/retrospective-template.md)
  - Schema
  - [Getting started](getting-started.md)
  - [Lessons learned](lessons-learned-part1.md)
  - [Lessons learned (part 2)](lessons-learned-part2.md)
  - [Lessons learned (part 3)](lessons-learned-part3.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
