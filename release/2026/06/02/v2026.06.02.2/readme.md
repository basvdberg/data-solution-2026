## Table of contents

<!-- markdown-toc:start -->
- [Release metadata](#release-metadata)
- [Sequential summary of applied changes](#sequential-summary-of-applied-changes)
- [Linked files](#linked-files)
<!-- markdown-toc:end -->

## Table of contents


﻿## Table of contents


﻿## Table of contents


﻿## Table of contents


﻿# Release v2026.06.02.2 - Details

## Release metadata

- Version: `v2026.06.02.2`
- Development start: `2026-06-02T15:37:35+02:00`
- Development end: `2026-06-03T10:18:07+02:00`
- Release branch: `main`
- Release commit: `233f2ad05dc62a7e15f3aa5e3ea6070223380e56`
- Published release URL: <https://github.com/basvdberg/data-solution-2026/releases/tag/v2026.06.02.2>

## Sequential summary of applied changes

1. Tested the new CI/CD setup and inspected failing GitHub Actions run.
2. Identified root cause in CI dependency installation (`pip install -e .`) due to multi top-level package discovery.
3. Updated workflow install step to explicit test dependencies (`pytest`, `requests`).
4. Fixed post-push script parameter handling for `RequireCiSuccess` across shell invocations.
5. Re-tested local workflow behavior:
   - tests pass locally
   - watcher correctly blocks deploy when CI fails
6. Updated release version to `v2026.06.02.2`, created release notes, tagged, and published GitHub release.

## Linked files

- Release note: [`notes.md`](notes.md)

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](../../../../../readme.md)
  - Code
    - Airflow
      - Dags
      - Plugins
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
      - [Architecture](../../../../../doc/design/architecture.md)
      - [CI/CD workflow (main only + server pull deploy)](../../../../../doc/design/ci-cd.md)
      - [Event-based orchestration plan (single data object)](../../../../../doc/design/event-based-orchestration-plan.md)
      - [Meta data design](../../../../../doc/design/meta-data-design.md)
    - Operation
      - Incident
        - [INC-001 — NAS non-interactive SSH environment](../../../../../doc/operation/incident/inc-001-nas-ssh-environment.md)
        - [INC-002 — Airflow standalone infra instability](../../../../../doc/operation/incident/inc-002-airflow-infra-stability.md)
        - [INC-003 — Agent rediscovery and false-done verification](../../../../../doc/operation/incident/inc-003-agent-process-gaps.md)
        - [INC-004 — Airflow PYTHONPATH drift (dag_run_guard import)](../../../../../doc/operation/incident/inc-004-airflow-pythonpath-drift.md)
        - [INC-<NNN> — <short title>](../../../../../doc/operation/incident/incident-template.md)
      - [Issue categories](../../../../../doc/operation/issue-category.md)
    - [Implementation plan (Open-Meteo → event orchestration)](../../../../../doc/implementation-plan.md)
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
            - [Notes](../v2026.06.02.1/notes.md)
          - V2026.06.02.2
            - [Release v2026.06.02.2](notes.md)
        - 03
          - V2026.06.03.1
            - [Release v2026.06.03.1](../../03/v2026.06.03.1/notes.md)
          - V2026.06.03.2
            - [Release v2026.06.03.2](../../03/v2026.06.03.2/notes.md)
          - V2026.06.03.3
            - [Release v2026.06.03.3](../../03/v2026.06.03.3/notes.md)
          - V2026.06.03.4
            - [Release v2026.06.03.4](../../03/v2026.06.03.4/notes.md)
            - [Retrospective](../../03/v2026.06.03.4/retrospective.md)
        - 04
          - V2026.06.04.1
            - [Notes](../../04/v2026.06.04.1/notes.md)
        - 05
          - V2026.06.05.6
            - [Notes](../../05/v2026.06.05.6/notes.md)
            - [Retrospective](../../05/v2026.06.05.6/retrospective.md)
        - 08
          - V2026.06.08.1
            - [Notes](../../08/v2026.06.08.1/notes.md)
            - [Retrospective](../../08/v2026.06.08.1/retrospective.md)
          - V2026.06.08.2
            - [Notes](../../08/v2026.06.08.2/notes.md)
            - [Retrospective](../../08/v2026.06.08.2/retrospective.md)
    - [Release <version>](../../../../release-notes-template.md)
    - [Retrospective — <version>](../../../../retrospective-template.md)
  - Setting
  - Template
  - [Getting started](../../../../../getting-started.md)
  - [Lessons learned](../../../../../lessons-learned-part1.md)
  - [Lessons learned (part 2)](../../../../../lessons-learned-part2.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
