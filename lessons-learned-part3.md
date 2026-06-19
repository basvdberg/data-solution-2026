# Lessons learned (part 3)

## Table of contents

<!-- markdown-toc:start -->
- [Purpose](#purpose)
- [Kafka was too heavy for the local server](#kafka-was-too-heavy-for-the-local-server)
- [Data object refresh scheduling looks simple until it is not](#data-object-refresh-scheduling-looks-simple-until-it-is-not)
<!-- markdown-toc:end -->

## Purpose

This part documents architectural lessons from running the proof of concept on a relatively small local server (QNAP NAS). Part 1 introduced [Apache Kafka](https://kafka.apache.org/) as part of the stack; part 2 covered platform and infra friction. Part 3 covers **right-sizing** that stack when a component costs more than it delivers on constrained hardware, and **designing refresh scheduling** before implementation when orchestration moves to Airflow-native triggers.

## Kafka was too heavy for the local server

As it turned out, Kafka was consuming a lot of resources on my relatively small local server. The NAS became slow overall — not only for Kafka consumers and producers, but for Airflow, Postgres, and ordinary SSH troubleshooting. Cursor sessions timed out because even **debugging** took too long on an overloaded host.

I shut down Kafka and created a plan for alternatives. [Apache Airflow](https://airflow.apache.org/) already has functionality to implement event-based orchestration: you can define how processes are triggered by other processes, on a schedule or on the completion of another process. For this PoC — poller detects change, extractor runs on change — that is enough without a separate message broker.

Removing Kafka from the architecture applies the [Simplicity](https://github.com/basvdberg/data-engineering-design-patterns/blob/main/design-patterns/generic/simplicity.md) design pattern. The solution is easier to understand, has fewer moving parts to operate on the NAS, and runs faster on the local server. The trade-off is explicit: Kafka’s decoupling and replay semantics are valuable at scale, but on a small PoC host they were overhead before the pipeline had proven value.

Planned direction: [Event-based orchestration plan (single data object)](doc/design/event-based-orchestration-plan.md) and [Implementation plan (Open-Meteo → event orchestration)](doc/implementation/implementation-plan.md), updated to use Airflow-native triggers instead of Kafka publication and consumption.

**Takeaway:** Match infrastructure to host capacity and PoC scope. When a broker slows down the whole platform — including the tools you use to fix it — simplify first; add Kafka back only when event volume, fan-out, or replay requirements justify the cost.

## Data object refresh scheduling looks simple until it is not

Something that can seem quite simple — *when should this data object refresh?* — turned out to be one of the more complex design problems in the PoC. Our new way of working dictates that we describe the [design pattern](https://github.com/basvdberg/data-engineering-design-patterns/blob/main/design-patterns/data-engineering/data-object-scheduling.md) first, before generating any code, with AI as a sparring partner rather than a code generator.

Working through the use cases with that discipline produced an elaborated definition of when a data object may refresh: **time-based**, **dependency-based**, or **hybrid** (both). It also forced explicit answers to the exceptions — for example, what happens when a dataset was not delivered on schedule but arrives a day later? The answer depends on the data object's **refresh scope** (full, subset, or partition), not on a one-size-fits-all cron rule.

Specifying scope and triggers in a `RefreshContract` per object prevents subtle mistakes — such as refreshing a downstream object with upstream sources that each carry a different refresh scope. An added bonus: by stating **consumer expectations** in the same contract, actual delivery can be compared to what was agreed, so service levels become monitorable and visualisable instead of tribal knowledge.

The lesson learned here is that by using this way of working and AI, the designer of a data solution is now able to specify behavior more efficiently and with better quality, and thus prevent issues during production caused by unspecified behavior or behavior that did not fit the covered use cases of the design.

**Takeaway:** Treat refresh scheduling as a design-pattern problem, not a DAG detail. Write the contract — triggers, scope, late-data rules, consumer promise — before Airflow or extractor code; the upfront analysis pays for itself in fewer mismatched refreshes and measurable SLAs.

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](readme.md)
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
        - [CI/CD workflow (main only + server pull deploy)](doc/design/cicd/ci-cd.md)
      - Monitoring
        - [Monitoring architecture](doc/design/monitoring/monitoring-architecture.md)
      - [Airflow asset naming](doc/design/airflow-asset-naming.md)
      - [Event-based orchestration plan](doc/design/event-based-orchestration-plan.md)
      - [Meta data design](doc/design/meta-data-design.md)
    - Image
    - Implementation
      - [Implementation plan (Open-Meteo → event orchestration)](doc/implementation/implementation-plan.md)
    - Linked In
      - [Linkedin Post Part3V2](doc/linked-in/linkedin-post-part3v2.md)
    - Operation
      - [Event orchestration monitoring](doc/operation/event-orchestration-monitoring.md)
    - Retrospective
      - Incident
        - [INC-001 — NAS non-interactive SSH environment](doc/retrospective/incident/inc-001-nas-ssh-environment.md)
        - [INC-002 — Airflow standalone infra instability](doc/retrospective/incident/inc-002-airflow-infra-stability.md)
        - [INC-003 — Agent rediscovery and false-done verification](doc/retrospective/incident/inc-003-agent-process-gaps.md)
        - [INC-004 — Airflow PYTHONPATH drift (dag_run_guard import)](doc/retrospective/incident/inc-004-airflow-pythonpath-drift.md)
        - [INC-<NNN> — <short title>](doc/retrospective/incident/incident-template.md)
      - [Issue categories](doc/retrospective/issue-category.md)
    - [Implementation plan](doc/implementation-plan.md)
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
        - 12
          - V2026.06.12.1
            - [Release v2026.06.12.1](release/2026/06/12/v2026.06.12.1/notes.md)
    - [Release <version>](release/release-notes-template.md)
    - [Retrospective — <version>](release/retrospective-template.md)
  - Schema
  - [Getting started](getting-started.md)
  - [Lessons learned](lessons-learned-part1.md)
  - [Lessons learned (part 2)](lessons-learned-part2.md)
  - [Lessons learned (part 3)](lessons-learned-part3.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
