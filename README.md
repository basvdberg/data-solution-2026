# Data Solution 2026

## Table of contents

<!-- markdown-toc:start -->
- [Purpose](#purpose)
- [Proof of concept](#proof-of-concept)
<!-- markdown-toc:end -->

> [!WARNING]
> **This project is under construction.** Please check back later, or [watch the repository](https://github.com/basvdberg/data-solution-2026/watchers) on GitHub for updates.

## Purpose

Proof of concept for the GenAI way of working as described in [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026). 

Specification of intent is done generically by specifying design patterns here [data-engineering-design-patterns](https://github.com/basvdberg/data-engineering-design-patterns). 

Design patterns are the building blocks for specifying your customized data solution.

## Proof of concept

This PoC implements a **staging layer** for daily mean temperature across the Netherlands. The source is [Open-Meteo](https://open-meteo.com/) — no API key, models refreshed continuously. 

Python extraction code was generated with GenAI. Orchestration follows patterns from [data-engineering-design-patterns](https://github.com/basvdberg/data-engineering-design-patterns); AI-assisted tool selection led to Apache Airflow and Apache Kafka for this use case.

Architecture and flow are documented in [Architecture](doc/design/architecture.md).

For quick run instructions, see [Getting started](getting-started.md).

Lessons and observations are captured in [Lessons learned](lessons-learned.md).

Open-Meteo blends national models into a gridded daily mean at reference coordinates. Data is [CC BY 4.0](https://open-meteo.com/); attribute Open-Meteo in production use.

Details: [extractor_and_poller/openmeteo/](extractor_and_poller/openmeteo/).

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
      - [CI/CD workflow (local + NAS)](doc/design/ci-cd.md)
      - [Event-based orchestration plan (single data object)](doc/design/event-based-orchestration-plan.md)
      - [Meta data design](doc/design/meta-data-design.md)
  - Extractor_And_Poller
    - Common
    - Openmeteo
      - Extractor
      - Poller
    - Poller
    - Tests
  - Setting
  - Template
  - [Getting started](getting-started.md)
  - [Lessons learned](lessons-learned.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026)
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns)
<!-- markdown-project-structure:end -->
