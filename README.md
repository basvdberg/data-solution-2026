# Data Solution 2026

## Table of contents

<!-- markdown-toc:start -->
- [Purpose](#purpose)
- [Proof of concept](#proof-of-concept)
- [📈 Progress](#progress)
- [Documentation](#documentation)
- [Design patterns changed](#design-patterns-changed)
  - [Created](#created)
  - [Modified (pre-existing)](#modified-pre-existing)
<!-- markdown-toc:end -->

## Purpose

Proof of concept for the GenAI way of working as described in [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026).

Intent is specified with [data-engineering-design-patterns](https://github.com/basvdberg/data-engineering-design-patterns) as building blocks. Implementation code and orchestration are generated and refined with Cursor. Data transformations are specified with meta data. 

## Proof of concept

A **staging layer** for daily mean temperature across the Netherlands.
  
| Aspect | Choice |
|--------|--------|
| Source | [Open-Meteo](https://open-meteo.com/) — public API, no key, continuously updated models |
| Metadata | [DSA](https://github.com/data-solution-automation-engine/data-warehouse-automation-metadata-schema) connections, data objects, and mappings |
| Extraction | GenAI-generated Python poller and extractor (`code/extractor_and_poller/`) |
| Runtime metadata | PostgreSQL table `poller` (markers and poll history) |
| Orchestration | Apache Airflow and Apache Kafka (`code/` DAGs; hosted on local NAS for this PoC) |

## 📈 Progress

**June 1, 2026** — follow-up to the May 19 LinkedIn post on data engineering with Gen-AI.

**Done**

- Infrastructure on the local server: Airflow and Kafka deployed and tuned via GenAI over SSH.
- Design patterns created and modified to specify intent. See [design patterns changed](#design-patterns-changed).
- After discovering that the KNMI API was actually quite old and not providing any recent data updates, we switched to a new public data API, which was relatively easy because of the new way of working.
- Open-Meteo extractor and poller implemented.

**Next**

- Event-based orchestration for source-to-staging: poller publishes change events on Kafka; Airflow reacts and triggers extract (see [event-based orchestration plan](doc/design/event-based-orchestration-plan.md)).

**Lessons so far** ([full notes](lessons-learned.md)).

## Documentation

| Topic | Document |
|-------|----------|
| Run locally | [Getting started](getting-started.md) |
| Generated runtime (DAGs) | [code/](code/readme.md) |
| Docker (Airflow, Kafka) | [Infrastructure](infra/readme.md) |
| Architecture and flow | [Architecture](doc/design/architecture.md) |
| DSA layout in Git | [Meta data design](doc/design/meta-data-design.md) |
| Event orchestration | [Event-based orchestration plan](doc/design/event-based-orchestration-plan.md) |
| Implementation checklist | [Implementation plan](doc/implementation-plan.md) |
| Observations | [Lessons learned](lessons-learned.md) |

## Design patterns changed

Since the [May 19 LinkedIn post](https://github.com/basvdberg/data-engineering-2026), the [data-engineering-design-patterns](https://github.com/basvdberg/data-engineering-design-patterns) catalogue grew to support this PoC. Patterns live under `design-patterns/data-engineering/` and `design-patterns/generic/` (reorganized 1 June 2026).

### Created

| Pattern | Summary |
|--------|---------|
| [Separate what and how](https://github.com/basvdberg/data-engineering-design-patterns/blob/main/design-patterns/generic/separate-what-and-how.md) | Declarative specification (*what*) vs imperative implementation (*how*); DSA in Git, tools and code for execution. |
| [Data extractor](https://github.com/basvdberg/data-engineering-design-patterns/blob/main/design-patterns/data-engineering/data-extractor.md) | Reads a source via protocol and format adapter; writes the target with integrity and observability. |
| [Data object poller](https://github.com/basvdberg/data-engineering-design-patterns/blob/main/design-patterns/data-engineering/data-object-poller.md) | Detects marker changes on a schedule; publishes events without full payload reads. |
| [Data object](https://github.com/basvdberg/data-engineering-design-patterns/blob/main/design-patterns/data-engineering/data-object.md) | Atomic unit: identity, location, schema, classification (table, file, API dataset). |
| [Data object container](https://github.com/basvdberg/data-engineering-design-patterns/blob/main/design-patterns/data-engineering/data-object-container.md) | Hierarchical scope (database, folder, layer) with inherited properties; groups objects, no payload. |
| [Data solution layer](https://github.com/basvdberg/data-engineering-design-patterns/blob/main/design-patterns/data-engineering/data-solution-layer.md) | Staging → raw → integrated → presentation; unidirectional flow. |
| [Simplicity](https://github.com/basvdberg/data-engineering-design-patterns/blob/main/design-patterns/generic/simplicity.md) | Prefer the simpler correct design; keep the system boundary small. |
| [Functional decomposition](https://github.com/basvdberg/data-engineering-design-patterns/blob/main/design-patterns/generic/functional-decomposition.md) | Decompose by responsibility; express variation in configuration. |
| [Data object tree](https://github.com/basvdberg/data-engineering-design-patterns/blob/main/design-patterns/data-engineering/data-object-tree.md) | Parent–child hierarchy and discovery of objects in a solution. |
| [Data object tree property inheritance](https://github.com/basvdberg/data-engineering-design-patterns/blob/main/design-patterns/data-engineering/data-object-tree-property-inheritance.md) | Properties on tree nodes; child overrides parent, else inherit from ancestor. |

**Removed:** *Object property tree* — split into **Data object tree** and **Data object tree property inheritance**. [Prefer simple decomposition](https://github.com/basvdberg/data-engineering-design-patterns/blob/main/design-patterns/generic/prefer-simple-decomposition.md) is now a stub pointing to **Simplicity** and **Functional decomposition**.

### Modified (pre-existing)

| Pattern | Summary |
|--------|---------|
| [Data solution](https://github.com/basvdberg/data-engineering-design-patterns/blob/main/design-patterns/data-engineering/data-solution.md) | Linked to new data-engineering patterns and PoC vocabulary. |
| [Event-based orchestration](https://github.com/basvdberg/data-engineering-design-patterns/blob/main/design-patterns/data-engineering/event-based-orchestration.md) | Aligned with poller events, extractor tasks, and Kafka/Airflow flow used here. |
| [Historic bitemporal table](https://github.com/basvdberg/data-engineering-design-patterns/blob/main/design-patterns/data-engineering/historic-bitemporal-table.md) | Cross-links and structure refresh alongside the catalogue. |

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](readme.md)
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
      - [Architecture](doc/design/architecture.md)
      - [CI/CD workflow (main only + server pull deploy)](doc/design/ci-cd.md)
      - [Event-based orchestration plan (single data object)](doc/design/event-based-orchestration-plan.md)
      - [Meta data design](doc/design/meta-data-design.md)
    - Operation
      - Incident
        - [INC-001 — NAS non-interactive SSH environment](doc/operation/incident/inc-001-nas-ssh-environment.md)
        - [INC-002 — Airflow standalone infra instability](doc/operation/incident/inc-002-airflow-infra-stability.md)
        - [INC-003 — Agent rediscovery and false-done verification](doc/operation/incident/inc-003-agent-process-gaps.md)
        - [INC-004 — Airflow PYTHONPATH drift (dag_run_guard import)](doc/operation/incident/inc-004-airflow-pythonpath-drift.md)
        - [INC-<NNN> — <short title>](doc/operation/incident/incident-template.md)
      - [Issue categories](doc/operation/issue-category.md)
    - [Implementation plan (Open-Meteo → event orchestration)](doc/implementation-plan.md)
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
            - [Notes](release/2026/06/02/v2026.06.02.1/notes.md)
          - V2026.06.02.2
            - [Release v2026.06.02.2](release/2026/06/02/v2026.06.02.2/notes.md)
        - 03
          - V2026.06.03.1
            - [Release v2026.06.03.1](release/2026/06/03/v2026.06.03.1/notes.md)
          - V2026.06.03.2
            - [Release v2026.06.03.2](release/2026/06/03/v2026.06.03.2/notes.md)
          - V2026.06.03.3
            - [Release v2026.06.03.3](release/2026/06/03/v2026.06.03.3/notes.md)
          - V2026.06.03.4
            - [Release v2026.06.03.4](release/2026/06/03/v2026.06.03.4/notes.md)
            - [Retrospective](release/2026/06/03/v2026.06.03.4/retrospective.md)
        - 04
          - V2026.06.04.1
            - [Notes](release/2026/06/04/v2026.06.04.1/notes.md)
        - 05
          - V2026.06.05.6
            - [Notes](release/2026/06/05/v2026.06.05.6/notes.md)
            - [Retrospective](release/2026/06/05/v2026.06.05.6/retrospective.md)
        - 08
          - V2026.06.08.1
            - [Notes](release/2026/06/08/v2026.06.08.1/notes.md)
            - [Retrospective](release/2026/06/08/v2026.06.08.1/retrospective.md)
          - V2026.06.08.2
            - [Notes](release/2026/06/08/v2026.06.08.2/notes.md)
            - [Retrospective](release/2026/06/08/v2026.06.08.2/retrospective.md)
        - 09
          - V2026.06.09.1
            - [Notes](release/2026/06/09/v2026.06.09.1/notes.md)
            - [Retrospective](release/2026/06/09/v2026.06.09.1/retrospective.md)
          - V2026.06.09.2
            - [Notes](release/2026/06/09/v2026.06.09.2/notes.md)
            - [Retrospective](release/2026/06/09/v2026.06.09.2/retrospective.md)
          - V2026.06.09.3
            - [Notes](release/2026/06/09/v2026.06.09.3/notes.md)
            - [Retrospective](release/2026/06/09/v2026.06.09.3/retrospective.md)
          - V2026.06.09.4
            - [Notes](release/2026/06/09/v2026.06.09.4/notes.md)
            - [Retrospective](release/2026/06/09/v2026.06.09.4/retrospective.md)
          - V2026.06.09.5
            - [Notes](release/2026/06/09/v2026.06.09.5/notes.md)
            - [Retrospective](release/2026/06/09/v2026.06.09.5/retrospective.md)
    - [Release <version>](release/release-notes-template.md)
    - [Retrospective — <version>](release/retrospective-template.md)
  - Setting
  - Template
  - [Getting started](getting-started.md)
  - [Lessons learned](lessons-learned-part1.md)
  - [Lessons learned (part 2)](lessons-learned-part2.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
