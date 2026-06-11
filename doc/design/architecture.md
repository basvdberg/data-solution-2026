# Architecture

## Table of contents

<!-- markdown-toc:start -->
- [Flow](#flow)
<!-- markdown-toc:end -->

## Flow

![Architecture](architecture-staging.png)

The flow, left to right:

1. **Git holds the configuration.** `data-object-mapping/staging/openmeteo/` describes the source; staging targets and loads are defined in the same DSA metadata. Design patterns set the shape of the orchestration.
2. **Airflow + Kafka run ingestion.** A scheduled **poller** DAG probes the source and publishes only to the event bus: `ds.poll.data_object_change` when the marker moved, `ds.poll.data_object_progress` when it did not. The event controller reacts to **change** events and enqueues **extract** tasks; the extractor writes Parquet under `data/staging/`. The poller never runs the extractor. **PostgreSQL** stores all runtime metadata (poller history in table `poller`, future event and extract audit tables); configuration stays in Git. Topic naming: [Kafka topic naming](kafka-topic-naming.md).
3. **ADL generates staging artefacts.** Reading the same DSA metadata, ADL renders the Handlebars templates in `template/` into DDL and load SQL under `output/`, which load the Parquet landing files into the **100 Landing Area**.

This solution follows the [separate what and how](https://github.com/basvdberg/data-engineering-design-patterns/blob/main/design-patterns/separate-what-and-how.md) design pattern: DSA metadata files specify *what* must happen, while Airflow DAGs and the extractor/poller libraries under `code/`, and ADL-generated load procedures under `output/`, specify *how* it is executed.

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](../../readme.md)
  - Code
    - Airflow
      - Dags
      - Plugins
    - Extractor_And_Poller
      - Common
      - Controller
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
    - Data Solution
      - Data Object Mapping
    - Design
      - [Architecture](architecture.md)
      - [CI/CD workflow (main only + server pull deploy)](ci-cd.md)
      - [Event-based orchestration plan (single data object)](event-based-orchestration-plan.md)
      - [Kafka topic naming](kafka-topic-naming.md)
      - [Meta data design](meta-data-design.md)
    - Operation
      - Incident
        - [INC-001 — NAS non-interactive SSH environment](../operation/incident/inc-001-nas-ssh-environment.md)
        - [INC-002 — Airflow standalone infra instability](../operation/incident/inc-002-airflow-infra-stability.md)
        - [INC-003 — Agent rediscovery and false-done verification](../operation/incident/inc-003-agent-process-gaps.md)
        - [INC-004 — Airflow PYTHONPATH drift (dag_run_guard import)](../operation/incident/inc-004-airflow-pythonpath-drift.md)
        - [INC-<NNN> — <short title>](../operation/incident/incident-template.md)
      - [Issue categories](../operation/issue-category.md)
    - [Implementation plan (Open-Meteo → event orchestration)](../implementation-plan.md)
  - Docs
    - [LinkedIn post (part 3)](../../docs/linkedin-post-part3.md)
    - [Linkedin Post Part3V2](../../docs/linkedin-post-part3v2.md)
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
            - [Notes](../../release/2026/06/02/v2026.06.02.1/notes.md)
          - V2026.06.02.2
            - [Release v2026.06.02.2](../../release/2026/06/02/v2026.06.02.2/notes.md)
        - 03
          - V2026.06.03.1
            - [Release v2026.06.03.1](../../release/2026/06/03/v2026.06.03.1/notes.md)
          - V2026.06.03.2
            - [Release v2026.06.03.2](../../release/2026/06/03/v2026.06.03.2/notes.md)
          - V2026.06.03.3
            - [Release v2026.06.03.3](../../release/2026/06/03/v2026.06.03.3/notes.md)
          - V2026.06.03.4
            - [Release v2026.06.03.4](../../release/2026/06/03/v2026.06.03.4/notes.md)
            - [Retrospective](../../release/2026/06/03/v2026.06.03.4/retrospective.md)
        - 04
          - V2026.06.04.1
            - [Notes](../../release/2026/06/04/v2026.06.04.1/notes.md)
        - 05
          - V2026.06.05.6
            - [Notes](../../release/2026/06/05/v2026.06.05.6/notes.md)
            - [Retrospective](../../release/2026/06/05/v2026.06.05.6/retrospective.md)
        - 08
          - V2026.06.08.1
            - [Notes](../../release/2026/06/08/v2026.06.08.1/notes.md)
            - [Retrospective](../../release/2026/06/08/v2026.06.08.1/retrospective.md)
          - V2026.06.08.2
            - [Notes](../../release/2026/06/08/v2026.06.08.2/notes.md)
            - [Retrospective](../../release/2026/06/08/v2026.06.08.2/retrospective.md)
        - 09
          - V2026.06.09.1
            - [Notes](../../release/2026/06/09/v2026.06.09.1/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.1/retrospective.md)
          - V2026.06.09.10
            - [Notes](../../release/2026/06/09/v2026.06.09.10/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.10/retrospective.md)
          - V2026.06.09.11
            - [Notes](../../release/2026/06/09/v2026.06.09.11/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.11/retrospective.md)
          - V2026.06.09.12
            - [Notes](../../release/2026/06/09/v2026.06.09.12/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.12/retrospective.md)
          - V2026.06.09.13
            - [Notes](../../release/2026/06/09/v2026.06.09.13/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.13/retrospective.md)
          - V2026.06.09.14
            - [Notes](../../release/2026/06/09/v2026.06.09.14/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.14/retrospective.md)
          - V2026.06.09.15
            - [Notes](../../release/2026/06/09/v2026.06.09.15/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.15/retrospective.md)
          - V2026.06.09.16
            - [Notes](../../release/2026/06/09/v2026.06.09.16/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.16/retrospective.md)
          - V2026.06.09.17
            - [Notes](../../release/2026/06/09/v2026.06.09.17/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.17/retrospective.md)
          - V2026.06.09.2
            - [Notes](../../release/2026/06/09/v2026.06.09.2/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.2/retrospective.md)
          - V2026.06.09.3
            - [Notes](../../release/2026/06/09/v2026.06.09.3/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.3/retrospective.md)
          - V2026.06.09.4
            - [Notes](../../release/2026/06/09/v2026.06.09.4/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.4/retrospective.md)
          - V2026.06.09.5
            - [Notes](../../release/2026/06/09/v2026.06.09.5/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.5/retrospective.md)
          - V2026.06.09.6
            - [Notes](../../release/2026/06/09/v2026.06.09.6/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.6/retrospective.md)
          - V2026.06.09.7
            - [Notes](../../release/2026/06/09/v2026.06.09.7/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.7/retrospective.md)
          - V2026.06.09.8
            - [Notes](../../release/2026/06/09/v2026.06.09.8/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.8/retrospective.md)
          - V2026.06.09.9
            - [Notes](../../release/2026/06/09/v2026.06.09.9/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.9/retrospective.md)
        - 11
          - V2026.06.11.1
            - [Notes](../../release/2026/06/11/v2026.06.11.1/notes.md)
            - [Retrospective](../../release/2026/06/11/v2026.06.11.1/retrospective.md)
          - V2026.06.11.2
            - [Notes](../../release/2026/06/11/v2026.06.11.2/notes.md)
            - [Retrospective](../../release/2026/06/11/v2026.06.11.2/retrospective.md)
          - V2026.06.11.3
            - [Notes](../../release/2026/06/11/v2026.06.11.3/notes.md)
            - [Retrospective](../../release/2026/06/11/v2026.06.11.3/retrospective.md)
          - V2026.06.11.4
            - [Notes](../../release/2026/06/11/v2026.06.11.4/notes.md)
            - [Retrospective](../../release/2026/06/11/v2026.06.11.4/retrospective.md)
          - V2026.06.11.5
            - [Notes](../../release/2026/06/11/v2026.06.11.5/notes.md)
            - [Retrospective](../../release/2026/06/11/v2026.06.11.5/retrospective.md)
          - V2026.06.11.6
            - [Notes](../../release/2026/06/11/v2026.06.11.6/notes.md)
            - [Retrospective](../../release/2026/06/11/v2026.06.11.6/retrospective.md)
          - V2026.06.11.7
            - [Notes](../../release/2026/06/11/v2026.06.11.7/notes.md)
            - [Retrospective](../../release/2026/06/11/v2026.06.11.7/retrospective.md)
    - [Release <version>](../../release/release-notes-template.md)
    - [Retrospective — <version>](../../release/retrospective-template.md)
  - Setting
  - Template
  - [Getting started](../../getting-started.md)
  - [Lessons learned](../../lessons-learned-part1.md)
  - [Lessons learned (part 2)](../../lessons-learned-part2.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
