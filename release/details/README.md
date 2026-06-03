# Release Details

## Table of contents

<!-- markdown-toc:start -->
- [Structure](#structure)
- [Releases](#releases)
- [Sequential Change History](#sequential-change-history)
  - [1) v2026.06.02.1](#1-v202606021)
  - [2) v2026.06.02.2](#2-v202606022)
- [Maintenance](#maintenance)
<!-- markdown-toc:end -->

This folder stores detailed, audit-friendly release content per version.

## Structure

- One subfolder per release version: `release/details/<version>/`
- Required files per release:
  - `README.md` (release metadata + sequential change log)
  - `prompts.md` (all prompts used for that release)

## Releases

1. [`v2026.06.02.1`](v2026.06.02.1/README.md)
2. [`v2026.06.02.2`](v2026.06.02.2/README.md)

## Sequential Change History

### 1) `v2026.06.02.1`

- Established a main-only CI/CD approach (no feature branches).
- Added release versioning and release notes files under `release/`.
- Added CI workflow on `main` and transitioned deployment design to NAS pull-based execution.
- Added post-push automation scripts to wait for commit visibility and CI completion before triggering NAS deploy.
- Added notification support with `ntfy` as default.

### 2) `v2026.06.02.2`

- Fixed GitHub Actions failure by replacing editable package install with explicit test dependencies.
- Hardened post-push boolean argument handling for `RequireCiSuccess` under Windows PowerShell invocation.
- Published release tag and GitHub release with updated release notes.

## Maintenance

- Update this folder for every release tag.
- Keep the release details synchronized with:
  - `release/VERSION`
  - `release/notes/<version>.md`
  - commit history and CI/CD changes.

- [$version](v2026.06.02.2/README.md)

- [$version](v2026.06.03.1/README.md)

- [$version](v2026.06.03.2/README.md)

- [$version](v2026.06.03.3/README.md)

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](../../readme.md)
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
      - [Architecture](../../doc/design/architecture.md)
      - [CI/CD workflow (main only + server pull deploy)](../../doc/design/ci-cd.md)
      - [Event-based orchestration plan (single data object)](../../doc/design/event-based-orchestration-plan.md)
      - [Meta data design](../../doc/design/meta-data-design.md)
    - [Implementation plan (Open-Meteo → event orchestration)](../../doc/implementation-plan.md)
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
      - [Release v2026.06.02.1](../notes/v2026.06.02.1.md)
      - [Release v2026.06.02.2](../notes/v2026.06.02.2.md)
      - [Release v2026.06.03.1](../notes/v2026.06.03.1.md)
      - [Release v2026.06.03.2](../notes/v2026.06.03.2.md)
      - [Release v2026.06.03.3](../notes/v2026.06.03.3.md)
      - [Release v2026.06.03.4](../notes/v2026.06.03.4.md)
    - [Release <version>](../release-notes-template.md)
  - Setting
  - Template
  - [Getting started](../../getting-started.md)
  - [Lessons learned](../../lessons-learned-part1.md)
  - [Lessons learned (part 2)](../../lessons-learned-part2.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->

- [$version](v2026.06.03.4/README.md)
