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
      - [Airflow asset naming](../../../../../doc/design/airflow-asset-naming.md)
      - [Architecture](../../../../../doc/design/architecture.md)
      - [CI/CD workflow (main only + server pull deploy)](../../../../../doc/design/ci-cd.md)
      - [Event-based orchestration plan (single data object)](../../../../../doc/design/event-based-orchestration-plan.md)
      - [Meta data design](../../../../../doc/design/meta-data-design.md)
    - Image
    - Implementation
      - [Implementation plan (Open-Meteo → event orchestration)](../../../../../doc/implementation/implementation-plan.md)
    - Linked In
      - [Linkedin Post Part3V2](../../../../../doc/linked-in/linkedin-post-part3v2.md)
    - Operation
      - Incident
        - [INC-001 — NAS non-interactive SSH environment](../../../../../doc/operation/incident/inc-001-nas-ssh-environment.md)
        - [INC-002 — Airflow standalone infra instability](../../../../../doc/operation/incident/inc-002-airflow-infra-stability.md)
        - [INC-003 — Agent rediscovery and false-done verification](../../../../../doc/operation/incident/inc-003-agent-process-gaps.md)
        - [INC-004 — Airflow PYTHONPATH drift (dag_run_guard import)](../../../../../doc/operation/incident/inc-004-airflow-pythonpath-drift.md)
        - [INC-<NNN> — <short title>](../../../../../doc/operation/incident/incident-template.md)
      - [Event orchestration monitoring](../../../../../doc/operation/event-orchestration-monitoring.md)
      - [Issue categories](../../../../../doc/operation/issue-category.md)
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
        - 12
          - V2026.06.12.1
            - [Release v2026.06.12.1](../../12/v2026.06.12.1/notes.md)
    - [Release <version>](../../../../release-notes-template.md)
    - [Retrospective — <version>](../../../../retrospective-template.md)
  - [Getting started](../../../../../getting-started.md)
  - [Lessons learned](../../../../../lessons-learned-part1.md)
  - [Lessons learned (part 2)](../../../../../lessons-learned-part2.md)
  - [Lessons learned (part 3)](../../../../../lessons-learned-part3.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
