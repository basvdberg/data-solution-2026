# Incident register

## Table of contents

<!-- markdown-toc:start -->
- [Index](#index)
- [Naming](#naming)
- [New incident](#new-incident)
<!-- markdown-toc:end -->

Blameless postmortems for significant failures. Format follows common SRE practice: summary, impact, timeline, root cause, detection gap, action items.

Tactical session errors stay in [`.cursor/troubleshooting-errors.md`](../../../.cursor/troubleshooting-errors.md) as `ERR-NNN`; promote here when impact warrants a durable record.

## Index

| ID | Title | Category | Severity | Release(s) | Status |
|----|-------|----------|----------|------------|--------|
| [INC-001](inc-001-nas-ssh-environment.md) | NAS non-interactive SSH environment | infra-environment | degraded | pre-release | resolved |
| [INC-002](inc-002-airflow-infra-stability.md) | Airflow standalone infra instability | orchestration | blocker | pre-release | resolved |
| [INC-003](inc-003-agent-process-gaps.md) | Agent rediscovery and false-done verification | agent-efficiency, process-verification | degraded | pre-release | codified |
| [INC-004](inc-004-airflow-pythonpath-drift.md) | Airflow PYTHONPATH drift (dag_run_guard import) | orchestration | blocker | v2026.06.05.6 | resolved |

## Naming

- File: `inc-<NNN>-<kebab-title>.md`
- ID: `INC-001`, monotonic in this register

## New incident

Copy [incident-template.md](incident-template.md). Link from:

- Affected `release/notes/<version>.md` → **Related artifacts**
- `release/details/<version>/README.md` → **Linked files**
- `release/retrospective/<version>.md` → **Incidents**

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](../../../readme.md)
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
        - [CI/CD workflow (main only + server pull deploy)](../../design/cicd/ci-cd.md)
      - Monitoring
        - [Monitoring architecture](../../design/monitoring/monitoring-architecture.md)
      - [Airflow asset naming](../../design/airflow-asset-naming.md)
      - [Event-based orchestration plan](../../design/event-based-orchestration-plan.md)
      - [Meta data design](../../design/meta-data-design.md)
    - Image
    - Implementation
      - [Implementation plan (Open-Meteo → event orchestration)](../../implementation/implementation-plan.md)
    - Linked In
      - [Data Object Contract](../../linked-in/data-object-contract.md)
      - [Linkedin Post Part3V2](../../linked-in/linkedin-post-part3v2.md)
    - Operation
      - [Event orchestration monitoring](../../operation/event-orchestration-monitoring.md)
    - Retrospective
      - Incident
        - [INC-001 — NAS non-interactive SSH environment](inc-001-nas-ssh-environment.md)
        - [INC-002 — Airflow standalone infra instability](inc-002-airflow-infra-stability.md)
        - [INC-003 — Agent rediscovery and false-done verification](inc-003-agent-process-gaps.md)
        - [INC-004 — Airflow PYTHONPATH drift (dag_run_guard import)](inc-004-airflow-pythonpath-drift.md)
        - [INC-<NNN> — <short title>](incident-template.md)
      - [Issue categories](../issue-category.md)
    - [Implementation plan](../../implementation-plan.md)
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
            - [Notes](../../../release/2026/06/02/v2026.06.02.1/notes.md)
          - V2026.06.02.2
            - [Release v2026.06.02.2](../../../release/2026/06/02/v2026.06.02.2/notes.md)
        - 03
          - V2026.06.03.1
            - [Release v2026.06.03.1](../../../release/2026/06/03/v2026.06.03.1/notes.md)
          - V2026.06.03.2
            - [Release v2026.06.03.2](../../../release/2026/06/03/v2026.06.03.2/notes.md)
          - V2026.06.03.3
            - [Release v2026.06.03.3](../../../release/2026/06/03/v2026.06.03.3/notes.md)
          - V2026.06.03.4
            - [Release v2026.06.03.4](../../../release/2026/06/03/v2026.06.03.4/notes.md)
            - [Retrospective](../../../release/2026/06/03/v2026.06.03.4/retrospective.md)
        - 04
          - V2026.06.04.1
            - [Notes](../../../release/2026/06/04/v2026.06.04.1/notes.md)
        - 05
          - V2026.06.05.6
            - [Notes](../../../release/2026/06/05/v2026.06.05.6/notes.md)
            - [Retrospective](../../../release/2026/06/05/v2026.06.05.6/retrospective.md)
        - 12
          - V2026.06.12.1
            - [Release v2026.06.12.1](../../../release/2026/06/12/v2026.06.12.1/notes.md)
    - [Release <version>](../../../release/release-notes-template.md)
    - [Retrospective — <version>](../../../release/retrospective-template.md)
  - Schema
  - [Getting started](../../../getting-started.md)
  - [Lessons learned](../../../lessons-learned-part1.md)
  - [Lessons learned (part 2)](../../../lessons-learned-part2.md)
  - [Lessons learned (part 3)](../../../lessons-learned-part3.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
