# Release <version>

## Table of contents

<!-- markdown-toc:start -->
- [Metadata](#metadata)
- [Scope](#scope)
- [Changes](#changes)
- [Poller and Airflow impact](#poller-and-airflow-impact)
- [Deployment steps](#deployment-steps)
- [Validation](#validation)
- [Rollback plan](#rollback-plan)
- [Notes](#notes)
<!-- markdown-toc:end -->

## Metadata

- Version: `<version>`
- Date: `<YYYY-MM-DD>`
- Branch: `main`
- Commit: `<sha>`

## Scope

- Brief description of what is included in this release.

## Changes

- Added:
- Changed:
- Fixed:

## Poller and Airflow impact

- Poller mapping:
- Airflow DAG (`code/airflow/dags/`):
- Runtime variables changed:

## Deployment steps

- Auto deployment trigger: push to `main`
- NAS actions required after deploy:
  - [ ] Dependencies updated
  - [ ] Services restarted
  - [ ] Airflow DAGs available

## Validation

- [ ] Unit tests passed
- [ ] Integration checks passed
- [ ] Airflow poller manual run passed
- [ ] Kafka publish verified (or stdout in smoke mode)
- [ ] Postgres state persistence verified

## Rollback plan

- Previous stable tag: `<tag>`
- Rollback command:

```bash
cd ~/apps/data-solution-2026
git fetch --all --tags
git checkout <tag>
docker compose up -d
```

## Notes

- Additional operational notes.

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](../readme.md)
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
      - [Architecture](../doc/design/architecture.md)
      - [CI/CD workflow (main only + server pull deploy)](../doc/design/ci-cd.md)
      - [Event-based orchestration plan (single data object)](../doc/design/event-based-orchestration-plan.md)
      - [Meta data design](../doc/design/meta-data-design.md)
    - [Implementation plan (Open-Meteo → event orchestration)](../doc/implementation-plan.md)
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
    - Notes
      - [Release v2026.06.02.1](notes/v2026.06.02.1.md)
      - [Release v2026.06.02.2](notes/v2026.06.02.2.md)
      - [Release v2026.06.03.1](notes/v2026.06.03.1.md)
    - [Release <version>](release-notes-template.md)
  - Setting
  - Template
  - [Getting started](../getting-started.md)
  - [Lessons learned](../lessons-learned-part1.md)
  - [Lessons learned (part 2)](../lessons-learned-part2.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
