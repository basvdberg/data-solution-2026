## Table of contents

<!-- markdown-toc:start -->
- [Release metadata](#release-metadata)
- [Summary](#summary)
- [Linked files](#linked-files)
<!-- markdown-toc:end -->

## Table of contents


﻿## Table of contents


﻿## Table of contents


﻿# Release v2026.06.04.1 - Details

## Release metadata

- Version: `v2026.06.04.1`
- Development start: `2026-06-04T13:04:38+02:00`
- Development end: `2026-06-04T13:04:51+02:00`
- Release branch: `main`
- Release commit: `3f87b1ab4826b259c657d79e2277ee60faaa4b1d`

## Summary

- Update scope and changes in `notes.md`.

## Linked files

- Release note: [`notes.md`](notes.md)

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
      - Cicd
        - [CI/CD workflow (main only + server pull deploy)](../../../../../doc/design/cicd/ci-cd.md)
      - Monitoring
        - [Monitoring architecture](../../../../../doc/design/monitoring/monitoring-architecture.md)
      - [Airflow asset naming](../../../../../doc/design/airflow-asset-naming.md)
      - [Event-based orchestration plan](../../../../../doc/design/event-based-orchestration-plan.md)
      - [Meta data design](../../../../../doc/design/meta-data-design.md)
    - Image
    - Implementation
      - [Implementation plan (Open-Meteo → event orchestration)](../../../../../doc/implementation/implementation-plan.md)
    - Linked In
      - [Linkedin Post Part3V2](../../../../../doc/linked-in/linkedin-post-part3v2.md)
    - Operation
      - [Event orchestration monitoring](../../../../../doc/operation/event-orchestration-monitoring.md)
    - Retrospective
      - Incident
        - [INC-001 — NAS non-interactive SSH environment](../../../../../doc/retrospective/incident/inc-001-nas-ssh-environment.md)
        - [INC-002 — Airflow standalone infra instability](../../../../../doc/retrospective/incident/inc-002-airflow-infra-stability.md)
        - [INC-003 — Agent rediscovery and false-done verification](../../../../../doc/retrospective/incident/inc-003-agent-process-gaps.md)
        - [INC-004 — Airflow PYTHONPATH drift (dag_run_guard import)](../../../../../doc/retrospective/incident/inc-004-airflow-pythonpath-drift.md)
        - [INC-<NNN> — <short title>](../../../../../doc/retrospective/incident/incident-template.md)
      - [Issue categories](../../../../../doc/retrospective/issue-category.md)
    - [Implementation plan](../../../../../doc/implementation-plan.md)
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
            - [Notes](notes.md)
        - 05
          - V2026.06.05.6
            - [Notes](../../05/v2026.06.05.6/notes.md)
            - [Retrospective](../../05/v2026.06.05.6/retrospective.md)
        - 12
          - V2026.06.12.1
            - [Release v2026.06.12.1](../../12/v2026.06.12.1/notes.md)
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
