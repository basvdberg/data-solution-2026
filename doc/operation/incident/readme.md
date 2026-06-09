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
      - [Architecture](../../design/architecture.md)
      - [CI/CD workflow (main only + server pull deploy)](../../design/ci-cd.md)
      - [Event-based orchestration plan (single data object)](../../design/event-based-orchestration-plan.md)
      - [Kafka topic naming](../../design/kafka-topic-naming.md)
      - [Meta data design](../../design/meta-data-design.md)
    - Operation
      - Incident
        - [INC-001 — NAS non-interactive SSH environment](inc-001-nas-ssh-environment.md)
        - [INC-002 — Airflow standalone infra instability](inc-002-airflow-infra-stability.md)
        - [INC-003 — Agent rediscovery and false-done verification](inc-003-agent-process-gaps.md)
        - [INC-004 — Airflow PYTHONPATH drift (dag_run_guard import)](inc-004-airflow-pythonpath-drift.md)
        - [INC-<NNN> — <short title>](incident-template.md)
      - [Issue categories](../issue-category.md)
    - [Implementation plan (Open-Meteo → event orchestration)](../../implementation-plan.md)
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
        - 08
          - V2026.06.08.1
            - [Notes](../../../release/2026/06/08/v2026.06.08.1/notes.md)
            - [Retrospective](../../../release/2026/06/08/v2026.06.08.1/retrospective.md)
          - V2026.06.08.2
            - [Notes](../../../release/2026/06/08/v2026.06.08.2/notes.md)
            - [Retrospective](../../../release/2026/06/08/v2026.06.08.2/retrospective.md)
        - 09
          - V2026.06.09.1
            - [Notes](../../../release/2026/06/09/v2026.06.09.1/notes.md)
            - [Retrospective](../../../release/2026/06/09/v2026.06.09.1/retrospective.md)
          - V2026.06.09.10
            - [Notes](../../../release/2026/06/09/v2026.06.09.10/notes.md)
            - [Retrospective](../../../release/2026/06/09/v2026.06.09.10/retrospective.md)
          - V2026.06.09.11
            - [Notes](../../../release/2026/06/09/v2026.06.09.11/notes.md)
            - [Retrospective](../../../release/2026/06/09/v2026.06.09.11/retrospective.md)
          - V2026.06.09.12
            - [Notes](../../../release/2026/06/09/v2026.06.09.12/notes.md)
            - [Retrospective](../../../release/2026/06/09/v2026.06.09.12/retrospective.md)
          - V2026.06.09.13
            - [Notes](../../../release/2026/06/09/v2026.06.09.13/notes.md)
            - [Retrospective](../../../release/2026/06/09/v2026.06.09.13/retrospective.md)
          - V2026.06.09.14
            - [Notes](../../../release/2026/06/09/v2026.06.09.14/notes.md)
            - [Retrospective](../../../release/2026/06/09/v2026.06.09.14/retrospective.md)
          - V2026.06.09.15
            - [Notes](../../../release/2026/06/09/v2026.06.09.15/notes.md)
            - [Retrospective](../../../release/2026/06/09/v2026.06.09.15/retrospective.md)
          - V2026.06.09.16
            - [Notes](../../../release/2026/06/09/v2026.06.09.16/notes.md)
            - [Retrospective](../../../release/2026/06/09/v2026.06.09.16/retrospective.md)
          - V2026.06.09.17
            - [Notes](../../../release/2026/06/09/v2026.06.09.17/notes.md)
            - [Retrospective](../../../release/2026/06/09/v2026.06.09.17/retrospective.md)
          - V2026.06.09.2
            - [Notes](../../../release/2026/06/09/v2026.06.09.2/notes.md)
            - [Retrospective](../../../release/2026/06/09/v2026.06.09.2/retrospective.md)
          - V2026.06.09.3
            - [Notes](../../../release/2026/06/09/v2026.06.09.3/notes.md)
            - [Retrospective](../../../release/2026/06/09/v2026.06.09.3/retrospective.md)
          - V2026.06.09.4
            - [Notes](../../../release/2026/06/09/v2026.06.09.4/notes.md)
            - [Retrospective](../../../release/2026/06/09/v2026.06.09.4/retrospective.md)
          - V2026.06.09.5
            - [Notes](../../../release/2026/06/09/v2026.06.09.5/notes.md)
            - [Retrospective](../../../release/2026/06/09/v2026.06.09.5/retrospective.md)
          - V2026.06.09.6
            - [Notes](../../../release/2026/06/09/v2026.06.09.6/notes.md)
            - [Retrospective](../../../release/2026/06/09/v2026.06.09.6/retrospective.md)
          - V2026.06.09.7
            - [Notes](../../../release/2026/06/09/v2026.06.09.7/notes.md)
            - [Retrospective](../../../release/2026/06/09/v2026.06.09.7/retrospective.md)
          - V2026.06.09.8
            - [Notes](../../../release/2026/06/09/v2026.06.09.8/notes.md)
            - [Retrospective](../../../release/2026/06/09/v2026.06.09.8/retrospective.md)
          - V2026.06.09.9
            - [Notes](../../../release/2026/06/09/v2026.06.09.9/notes.md)
            - [Retrospective](../../../release/2026/06/09/v2026.06.09.9/retrospective.md)
    - [Release <version>](../../../release/release-notes-template.md)
    - [Retrospective — <version>](../../../release/retrospective-template.md)
  - Setting
  - Template
  - [Getting started](../../../getting-started.md)
  - [Lessons learned](../../../lessons-learned-part1.md)
  - [Lessons learned (part 2)](../../../lessons-learned-part2.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
