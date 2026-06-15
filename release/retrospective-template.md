# Retrospective — <version>

## Table of contents

<!-- markdown-toc:start -->
- [Release context](#release-context)
- [What went well](#what-went-well)
- [What did not go well](#what-did-not-go-well)
- [Incidents this release](#incidents-this-release)
- [Patterns (by category)](#patterns-by-category)
- [Root causes (generalized)](#root-causes-generalized)
- [Metrics](#metrics)
- [Action items](#action-items)
- [Promotions (approval gate)](#promotions-approval-gate)
- [Lessons promoted](#lessons-promoted)
- [Related artifacts](#related-artifacts)
<!-- markdown-toc:end -->

Per-release sprint retrospective. Agent drafts; user approves promotions and action items.

## Release context

| Field | Value |
|-------|-------|
| **Version** | <version> |
| **Date** | <YYYY-MM-DD> |
| **Commit** | `<sha>` |
| **Validation** | pass / fail / partial — brief outcome |

## What went well

-

## What did not go well

-

## Incidents this release

| ID | Title | Severity |
|----|-------|----------|
| | | |

## Patterns (by category)

| Category | Count | Example IDs | Theme |
|----------|-------|-------------|-------|
| | | | |

## Root causes (generalized)

1.

## Metrics

| Metric | Value |
|--------|-------|
| ERR entries | |
| Repeat ERR (Count > 1) | |
| Incidents (INC) | |
| Validation checklist | |

## Action items

| Item | Owner | Destination |
|------|-------|-------------|
| | | skill / rule / checklist / runbook / lessons-learned |

## Promotions (approval gate)

- [ ] Skill or rule update
- [ ] Release notes template / validation step
- [ ] Infra or deploy runbook
- [ ] Lessons learned / issue category heat map

## Lessons promoted

| Category | Theme | lessons-learned anchor |
|----------|-------|------------------------|
| | | |

## Related artifacts

- Release notes: [`notes.md`](notes.md)
- Release details: [`readme.md`](readme.md)
- Incident register: [`doc/operation/incident/`](../../doc/operation/incident/readme.md)

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](../readme.md)
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
      - [Airflow asset naming](../doc/design/airflow-asset-naming.md)
      - [Architecture](../doc/design/architecture.md)
      - [CI/CD workflow (main only + server pull deploy)](../doc/design/ci-cd.md)
      - [Event-based orchestration plan (single data object)](../doc/design/event-based-orchestration-plan.md)
      - [Meta data design](../doc/design/meta-data-design.md)
    - Image
    - Implementation
      - [Implementation plan (Open-Meteo → event orchestration)](../doc/implementation/implementation-plan.md)
    - Linked In
      - [Linkedin Post Part3V2](../doc/linked-in/linkedin-post-part3v2.md)
    - Operation
      - Incident
        - [INC-001 — NAS non-interactive SSH environment](../doc/operation/incident/inc-001-nas-ssh-environment.md)
        - [INC-002 — Airflow standalone infra instability](../doc/operation/incident/inc-002-airflow-infra-stability.md)
        - [INC-003 — Agent rediscovery and false-done verification](../doc/operation/incident/inc-003-agent-process-gaps.md)
        - [INC-004 — Airflow PYTHONPATH drift (dag_run_guard import)](../doc/operation/incident/inc-004-airflow-pythonpath-drift.md)
        - [INC-<NNN> — <short title>](../doc/operation/incident/incident-template.md)
      - [Event orchestration monitoring](../doc/operation/event-orchestration-monitoring.md)
      - [Issue categories](../doc/operation/issue-category.md)
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
            - [Notes](2026/06/02/v2026.06.02.1/notes.md)
          - V2026.06.02.2
            - [Release v2026.06.02.2](2026/06/02/v2026.06.02.2/notes.md)
        - 03
          - V2026.06.03.1
            - [Release v2026.06.03.1](2026/06/03/v2026.06.03.1/notes.md)
          - V2026.06.03.2
            - [Release v2026.06.03.2](2026/06/03/v2026.06.03.2/notes.md)
          - V2026.06.03.3
            - [Release v2026.06.03.3](2026/06/03/v2026.06.03.3/notes.md)
          - V2026.06.03.4
            - [Release v2026.06.03.4](2026/06/03/v2026.06.03.4/notes.md)
            - [Retrospective](2026/06/03/v2026.06.03.4/retrospective.md)
        - 04
          - V2026.06.04.1
            - [Notes](2026/06/04/v2026.06.04.1/notes.md)
        - 05
          - V2026.06.05.6
            - [Notes](2026/06/05/v2026.06.05.6/notes.md)
            - [Retrospective](2026/06/05/v2026.06.05.6/retrospective.md)
        - 12
          - V2026.06.12.1
            - [Release v2026.06.12.1](2026/06/12/v2026.06.12.1/notes.md)
    - [Release <version>](release-notes-template.md)
    - [Retrospective — <version>](retrospective-template.md)
  - [Getting started](../getting-started.md)
  - [Lessons learned](../lessons-learned-part1.md)
  - [Lessons learned (part 2)](../lessons-learned-part2.md)
  - [Lessons learned (part 3)](../lessons-learned-part3.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
