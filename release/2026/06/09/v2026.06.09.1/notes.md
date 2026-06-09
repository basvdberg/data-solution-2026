## Table of contents

<!-- markdown-toc:start -->
- [Metadata](#metadata)
- [Scope](#scope)
- [Changes](#changes)
  - [Added](#added)
  - [Changed](#changed)
  - [Deprecated](#deprecated)
  - [Removed](#removed)
  - [Fixed](#fixed)
  - [Security](#security)
- [Poller and Airflow impact](#poller-and-airflow-impact)
- [Deployment](#deployment)
- [Validation](#validation)
- [Rollback](#rollback)
- [Related artifacts](#related-artifacts)
- [Notes](#notes)
<!-- markdown-toc:end -->

## Table of contents


﻿# Release v2026.06.09.1

Operator-facing release notes. Published to GitHub Releases via `publish-release.ps1`. Format follows [Keep a Changelog](https://keepachangelog.com/).

## Metadata

- Version: `v2026.06.09.1`
- Date: `2026-06-09`
- Branch: `main`
- Commit: `<fill-after-commit>`

## Scope

Brief description of what is included in this release.

## Changes

### Added

-

### Changed

-

### Deprecated

-

### Removed

-

### Fixed

-

### Security

-

## Poller and Airflow impact

- Poller mapping:
- Airflow DAG (`code/airflow/dags/`):
- Runtime variables changed:

## Deployment

- Trigger: push to `main` → CI → NAS pull deploy
- Infra sync: automatic when `release/deploy-config.json` has `sync_infra: true` (set by pre-commit when compose/env under `infra/` changes)
- NAS actions after deploy:
  - [ ] Dependencies updated
  - [ ] Services restarted
  - [ ] Airflow DAGs parse and appear in UI

## Validation

- [ ] Unit tests passed (CI)
- [ ] Integration checks passed
- [ ] Airflow `dags list-import-errors` empty on NAS (`docker exec airflow-standalone airflow dags list-import-errors`)
- [ ] Airflow poller manual run passed
- [ ] Kafka publish verified (or stdout in smoke mode)
- [ ] Postgres state persistence verified
- [ ] Infra change only: host reboot or full down/up cycle verified (if `infra/` changed)

## Rollback

- Previous stable tag: `v2026.06.08.1`

```bash
cd ~/apps/data-solution-2026
git fetch --all --tags
git checkout v2026.06.08.1
docker compose up -d
```

## Related artifacts

- Release details (internal): [`readme.md`](readme.md) *(same folder as this file after scaffold)*
- Retrospective: [`retrospective.md`](retrospective.md)
- Incidents: *(link INC-NNN from [incident register](../../doc/operation/incident/readme.md) if any)*

## Notes

Additional operational notes.

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
            - [Notes](../../02/v2026.06.02.1/notes.md)
          - V2026.06.02.2
            - [Release v2026.06.02.2](../../02/v2026.06.02.2/notes.md)
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
            - [Notes](notes.md)
            - [Retrospective](retrospective.md)
          - V2026.06.09.2
            - [Notes](../v2026.06.09.2/notes.md)
            - [Retrospective](../v2026.06.09.2/retrospective.md)
          - V2026.06.09.3
            - [Notes](../v2026.06.09.3/notes.md)
            - [Retrospective](../v2026.06.09.3/retrospective.md)
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
