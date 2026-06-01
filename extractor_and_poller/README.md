# Extractor and poller

## Table of contents

<!-- markdown-toc:start -->
- [Overview](#overview)
<!-- markdown-toc:end -->

## Overview

Open-Meteo extractor and poller driven by `data-object-mapping/` JSON.

Run from the solution root (`data-solution-2026/`):

```powershell
# List Enabled data object poller
python -m extractor_and_poller.poller --list

# Poll source/openmeteo/daily-temperature
python -m extractor_and_poller.poller --mapping daily-temperature

# Run extractor for OpenMeteo data object
python -m extractor_and_poller.openmeteo.extractor --mapping daily-temperature
```

Event-oriented poller options:

```powershell
# Persist state in Postgres and publish envelopes to Kafka
python -m extractor_and_poller.poller --mapping daily-temperature --state-backend postgres --publish kafka

# Local smoke run: publish event payloads to stdout
python -m extractor_and_poller.poller --mapping daily-temperature --publish stdout
```

The `openmeteo/` subfolder holds the `extractor/` and `poller/` packages. Shared helpers live under `common/`; the generic poller CLI is in `poller/`.

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](../readme.md)
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
      - [CI/CD workflow (local + NAS)](../doc/design/ci-cd.md)
      - [Event-based orchestration plan (single data object)](../doc/design/event-based-orchestration-plan.md)
      - [Meta data design](../doc/design/meta-data-design.md)
  - Extractor_And_Poller
    - Common
    - Openmeteo
      - Extractor
      - Poller
    - Poller
    - Tests
  - Setting
  - Template
  - [Getting started](../getting-started.md)
  - [Lessons learned](../lessons-learned.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
