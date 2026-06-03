## Table of contents

<!-- markdown-toc:start -->
- [Release metadata](#release-metadata)
- [Summary](#summary)
- [Linked files](#linked-files)
<!-- markdown-toc:end -->

﻿# Release v2026.06.03.4 - Details

## Release metadata


- Development end: `2026-06-03T11:47:34+02:00`
- Development start: `2026-06-03T11:47:34+02:00`
- Version: `v2026.06.03.4`
- Release branch: `main`
- Release commit: `9577fc901211402c33964e506c1f1d244d355bbc`

## Summary

Deploy success/failure ntfy notifications include release version and GitHub release notes URL.

## Linked files

- Release note: [`release/notes/v2026.06.03.4.md`](../../notes/v2026.06.03.4.md)

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](../../../readme.md)
  - Code
    - Airflow
      - Dags
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
      - [Architecture](../../../doc/design/architecture.md)
      - [CI/CD workflow (main only + server pull deploy)](../../../doc/design/ci-cd.md)
      - [Event-based orchestration plan (single data object)](../../../doc/design/event-based-orchestration-plan.md)
      - [Meta data design](../../../doc/design/meta-data-design.md)
    - [Implementation plan (Open-Meteo → event orchestration)](../../../doc/implementation-plan.md)
  - Extractor_And_Poller
    - Common
    - Openmeteo
      - Extractor
      - Poller
    - Poller
    - Tests
  - Infra
    - Airflow
      - Dags
    - Kafka
  - Release
    - Details
      - V2026.06.02.1
      - V2026.06.02.2
      - V2026.06.03.1
      - V2026.06.03.2
      - V2026.06.03.3
      - V2026.06.03.4
    - Notes
      - [Release v2026.06.02.1](../../notes/v2026.06.02.1.md)
      - [Release v2026.06.02.2](../../notes/v2026.06.02.2.md)
      - [Release v2026.06.03.1](../../notes/v2026.06.03.1.md)
      - [Release v2026.06.03.2](../../notes/v2026.06.03.2.md)
      - [Release v2026.06.03.3](../../notes/v2026.06.03.3.md)
      - [Release v2026.06.03.4](../../notes/v2026.06.03.4.md)
    - [Release <version>](../../release-notes-template.md)
  - Setting
  - Template
  - [Getting started](../../../getting-started.md)
  - [Lessons learned](../../../lessons-learned-part1.md)
  - [Lessons learned (part 2)](../../../lessons-learned-part2.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
