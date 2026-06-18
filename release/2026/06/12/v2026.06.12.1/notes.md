# Release v2026.06.12.1

## Table of contents

<!-- markdown-toc:start -->
- [Metadata](#metadata)
- [Scope](#scope)
- [Changes](#changes)
  - [Added](#added)
  - [Changed](#changed)
  - [Fixed](#fixed)
- [Deployment](#deployment)
- [Related artifacts](#related-artifacts)
<!-- markdown-toc:end -->

Operator-facing release notes. Published to GitHub Releases via `publish-release.ps1`. Format follows [Keep a Changelog](https://keepachangelog.com/).

## Metadata

- Version: `v2026.06.12.1`
- Date: `2026-06-12`
- Branch: `main`
- Commit: `4b0040b1847eda6732ae002d16d99f9a48fd8169`

## Scope

Catch-up release consolidating work since `v2026.06.03.4`: Kafka-driven extract orchestration, poller and deploy hardening, CI fixes, documentation (LinkedIn part 3, architecture diagrams), and lean release-folder automation.

## Changes

### Added

- Kafka-driven extract orchestration with Postgres staging load.
- LinkedIn post part 3 documentation and GenAI architecture diagram assets.
- Lean release scripts: publish-ready gate, open-release window, scaffold pruning.

### Changed

- Poller defaults to Kafka; NAS deploy wiring automated via post-push hook.
- Poller schema simplified; conditional DB migrations on deploy.
- Release flow: no per-commit version bump; optional artifacts created only when meaningful.

### Fixed

- CI pytest by installing `extractor_and_poller` requirements.
- Airflow poller DAG simplified for Airflow 3.2 default logging.

## Deployment

- Push to `main` after review; CI and NAS deploy run as usual.

## Related artifacts

- Release details: [readme.md](readme.md)

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
        - 12
          - V2026.06.12.1
            - [Release v2026.06.12.1](notes.md)
    - [Release <version>](../../../../release-notes-template.md)
    - [Retrospective — <version>](../../../../retrospective-template.md)
  - Schema
  - [Getting started](../../../../../getting-started.md)
  - [Lessons learned](../../../../../lessons-learned-part1.md)
  - [Lessons learned (part 2)](../../../../../lessons-learned-part2.md)
  - [Lessons learned (part 3)](../../../../../lessons-learned-part3.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
