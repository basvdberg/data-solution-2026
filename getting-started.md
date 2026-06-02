# Getting started

## Table of contents

<!-- markdown-toc:start -->
- [Prerequisites](#prerequisites)
- [Quick start](#quick-start)
- [Run key components](#run-key-components)
<!-- markdown-toc:end -->

## Prerequisites

- Python 3.11+
- Dependencies installed for `data-solution-2026` (including optional `psycopg` and `kafka-python` when using those backends)
- Run commands from the `data-solution-2026/` root

## Quick start

```powershell
cd "c:\Dev2\Data Engineering 2.0\data-solution-2026"
```

## Run key components

```powershell
# 1) List Enabled data object poller
python -m extractor_and_poller.poller --list

# 2) Poll source/openmeteo/daily-temperature
python -m extractor_and_poller.poller --data-object source/openmeteo/daily-temperature

# 3) Run extractor for OpenMeteo data object
python -m extractor_and_poller.openmeteo.extractor --mapping daily-temperature
```

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](readme.md)
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
      - [Architecture](doc/design/architecture.md)
      - [CI/CD workflow (main only + server pull deploy)](doc/design/ci-cd.md)
      - [Event-based orchestration plan (single data object)](doc/design/event-based-orchestration-plan.md)
      - [Meta data design](doc/design/meta-data-design.md)
  - Extractor_And_Poller
    - Common
    - Openmeteo
      - Extractor
      - Poller
    - Poller
    - Tests
  - Release
    - Notes
      - [Release v2026.06.02.1](release/notes/v2026.06.02.1.md)
    - [Release <version>](release/release-notes-template.md)
  - Setting
  - Template
  - [Getting started](getting-started.md)
  - [Lessons learned](lessons-learned.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
