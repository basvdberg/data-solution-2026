# Release v2026.06.02.2

## Table of contents

<!-- markdown-toc:start -->
- [Metadata](#metadata)
- [Scope](#scope)
- [Changes](#changes)
- [Validation](#validation)
- [Rollback plan](#rollback-plan)
- [Notes](#notes)
<!-- markdown-toc:end -->

## Metadata

- Version: `v2026.06.02.2`
- Date: `2026-06-02`
- Branch: `main`
- Commit: `<fill-after-commit>`

## Scope

- Fix CI workflow install step so tests run reliably on GitHub Actions.
- Harden post-push CI gate argument parsing for Windows PowerShell invocation.
- Keep deploy trigger behavior unchanged: only trigger NAS deploy after CI success.

## Changes

- Changed:
  - `.github/workflows/deploy-main.yml` install step now installs test dependencies directly.
  - `release/scripts/wait-and-trigger-pull.ps1` now parses `RequireCiSuccess` safely from string input.
  - `release/scripts/post-push-hook.ps1` passes `RequireCiSuccess` as numeric truthy value.

## Validation

- [x] Local test run succeeded (`pytest`)
- [x] Local watcher script validates CI status and aborts on failure
- [ ] GitHub Actions run on this release commit succeeded
- [ ] NAS trigger validated after CI success

## Rollback plan

- Previous stable tag: `v2026.06.02.1`

```bash
cd ~/apps/data-solution-2026
git fetch --all --tags
git checkout v2026.06.02.1
docker compose up -d
```

## Notes

- After push, update `Commit` and validation checkboxes with actual CI result.

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](../../../../../readme.md)
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
      - [Architecture](../../../../../doc/design/architecture.md)
      - [CI/CD workflow (main only + server pull deploy)](../../../../../doc/design/ci-cd.md)
      - [Event-based orchestration plan (single data object)](../../../../../doc/design/event-based-orchestration-plan.md)
      - [Kafka topic naming](../../../../../doc/design/kafka-topic-naming.md)
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
  - Docs
    - [LinkedIn post (part 3)](../../../../../docs/linkedin-post-part3.md)
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
        - 09
          - V2026.06.09.1
            - [Notes](../../09/v2026.06.09.1/notes.md)
            - [Retrospective](../../09/v2026.06.09.1/retrospective.md)
          - V2026.06.09.10
            - [Notes](../../09/v2026.06.09.10/notes.md)
            - [Retrospective](../../09/v2026.06.09.10/retrospective.md)
          - V2026.06.09.11
            - [Notes](../../09/v2026.06.09.11/notes.md)
            - [Retrospective](../../09/v2026.06.09.11/retrospective.md)
          - V2026.06.09.12
            - [Notes](../../09/v2026.06.09.12/notes.md)
            - [Retrospective](../../09/v2026.06.09.12/retrospective.md)
          - V2026.06.09.13
            - [Notes](../../09/v2026.06.09.13/notes.md)
            - [Retrospective](../../09/v2026.06.09.13/retrospective.md)
          - V2026.06.09.14
            - [Notes](../../09/v2026.06.09.14/notes.md)
            - [Retrospective](../../09/v2026.06.09.14/retrospective.md)
          - V2026.06.09.15
            - [Notes](../../09/v2026.06.09.15/notes.md)
            - [Retrospective](../../09/v2026.06.09.15/retrospective.md)
          - V2026.06.09.16
            - [Notes](../../09/v2026.06.09.16/notes.md)
            - [Retrospective](../../09/v2026.06.09.16/retrospective.md)
          - V2026.06.09.17
            - [Notes](../../09/v2026.06.09.17/notes.md)
            - [Retrospective](../../09/v2026.06.09.17/retrospective.md)
          - V2026.06.09.2
            - [Notes](../../09/v2026.06.09.2/notes.md)
            - [Retrospective](../../09/v2026.06.09.2/retrospective.md)
          - V2026.06.09.3
            - [Notes](../../09/v2026.06.09.3/notes.md)
            - [Retrospective](../../09/v2026.06.09.3/retrospective.md)
          - V2026.06.09.4
            - [Notes](../../09/v2026.06.09.4/notes.md)
            - [Retrospective](../../09/v2026.06.09.4/retrospective.md)
          - V2026.06.09.5
            - [Notes](../../09/v2026.06.09.5/notes.md)
            - [Retrospective](../../09/v2026.06.09.5/retrospective.md)
          - V2026.06.09.6
            - [Notes](../../09/v2026.06.09.6/notes.md)
            - [Retrospective](../../09/v2026.06.09.6/retrospective.md)
          - V2026.06.09.7
            - [Notes](../../09/v2026.06.09.7/notes.md)
            - [Retrospective](../../09/v2026.06.09.7/retrospective.md)
          - V2026.06.09.8
            - [Notes](../../09/v2026.06.09.8/notes.md)
            - [Retrospective](../../09/v2026.06.09.8/retrospective.md)
          - V2026.06.09.9
            - [Notes](../../09/v2026.06.09.9/notes.md)
            - [Retrospective](../../09/v2026.06.09.9/retrospective.md)
        - 11
          - V2026.06.11.1
            - [Notes](../../11/v2026.06.11.1/notes.md)
            - [Retrospective](../../11/v2026.06.11.1/retrospective.md)
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
