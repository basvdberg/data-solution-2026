## Table of contents

<!-- markdown-toc:start -->
- [Release metadata](#release-metadata)
- [Sequential summary of applied changes](#sequential-summary-of-applied-changes)
- [Linked files](#linked-files)
<!-- markdown-toc:end -->

## Table of contents


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

- Release note: [`release/notes/v2026.06.02.2.md`](../../notes/v2026.06.02.2.md)

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](../../../readme.md)
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
      - [Architecture](../../../doc/design/architecture.md)
      - [CI/CD workflow (main only + server pull deploy)](../../../doc/design/ci-cd.md)
      - [Event-based orchestration plan (single data object)](../../../doc/design/event-based-orchestration-plan.md)
      - [Meta data design](../../../doc/design/meta-data-design.md)
    - [Implementation plan (Open-Meteo → event orchestration)](../../../doc/implementation-plan.md)
  - Infra
    - Airflow
      - Dags
    - Kafka
    - Postgres
  - Release
    - Details
      - V2026.06.02.1
      - V2026.06.02.2
      - V2026.06.03.1
      - V2026.06.03.2
      - V2026.06.03.3
      - V2026.06.03.4
      - V2026.06.04.1
      - V2026.06.04.2
      - V2026.06.04.3
      - V2026.06.04.4
      - V2026.06.04.5
      - V2026.06.04.6
      - V2026.06.04.7
      - V2026.06.04.8
      - V2026.06.04.9
      - V2026.06.05.1
      - V2026.06.05.2
      - ﻿V2026.06.04.1
      - ﻿V2026.06.04.2
      - ﻿V2026.06.04.3
      - ﻿V2026.06.04.4
      - ﻿V2026.06.04.5
      - ﻿V2026.06.04.6
      - ﻿V2026.06.04.7
      - ﻿V2026.06.04.8
      - ﻿V2026.06.04.9
      - ﻿V2026.06.05.1
    - Notes
      - [Release v2026.06.02.1](../../notes/v2026.06.02.1.md)
      - [Release v2026.06.02.2](../../notes/v2026.06.02.2.md)
      - [Release v2026.06.03.1](../../notes/v2026.06.03.1.md)
      - [Release v2026.06.03.2](../../notes/v2026.06.03.2.md)
      - [Release v2026.06.03.3](../../notes/v2026.06.03.3.md)
      - [Release v2026.06.03.4](../../notes/v2026.06.03.4.md)
      - [V2026.06.04.1](../../notes/v2026.06.04.1.md)
      - [V2026.06.04.2](../../notes/v2026.06.04.2.md)
      - [V2026.06.04.3](../../notes/v2026.06.04.3.md)
      - [V2026.06.04.4](../../notes/v2026.06.04.4.md)
      - [V2026.06.04.5](../../notes/v2026.06.04.5.md)
      - [V2026.06.04.6](../../notes/v2026.06.04.6.md)
      - [V2026.06.04.7](../../notes/v2026.06.04.7.md)
      - [V2026.06.04.8](../../notes/v2026.06.04.8.md)
      - [V2026.06.04.9](../../notes/v2026.06.04.9.md)
      - [V2026.06.05.1](../../notes/v2026.06.05.1.md)
      - [V2026.06.05.2](../../notes/v2026.06.05.2.md)
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
