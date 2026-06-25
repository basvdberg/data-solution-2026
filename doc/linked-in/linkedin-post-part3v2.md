## Table of contents

<!-- markdown-toc:start -->
_No sections yet._
<!-- markdown-toc:end -->

## Table of contents


Lessons from building a data engineering PoC with an AI agent. Part 3

In my May post (https://github.com/basvdberg/data-engineering-2026) I described a new way of working with GenAI. In June I shared progress on the Data Solution 2026 (https://github.com/basvdberg/data-solution-2026) proof of concept. Here is what I learned along the way.

Working with an AI agent feels like having a junior assistant — working really hard to help you out. I emphasize junior because it does require me to fully specify what needs to be done.

A concrete example: I asked for Airflow DAG code assuming it would use the latest version. It followed Airflow 2 patterns while my server runs Airflow 3. The task looked stuck ("no logs available") while it crashed on an API that no longer exists. A single line in the prompt ("we run Airflow 3.2") would have avoided that.

SSH troubleshooting ate more time than it should. The agent runs commands on my local NAS over SSH. Non-interactive sessions had a minimal PATH (docker not found), nested quoting from PowerShell broke remote commands, and the same workarounds were rediscovered session after session. Fixing the default path and codifying copy-paste patterns in a Cursor skill cleared a lot of noise — but the agent will not do that by itself.

Capture fixes or you pay twice. A fix that lives only in chat is not organisational learning. I now log recurring errors during debugging, write incidents when impact is real, and run a retrospective after each release to promote patterns into skills, rules, and pipeline changes — for example, infra-aware deploy when only infra/ files change, with progress alerts to my phone.

Learning by doing beat reading docs. I was new to Apache Airflow and Apache Kafka. Learning from working examples in my architecture — with the agent as tutor — got me productive faster than documentation or YouTube alone.

Making tacit knowledge explicit pays off. DevOps habits, automatic deployment, testing, documenting, versioning — all of it matters more when an agent is doing the implementation. The attached diagram captures that model.

Design before implementation. I generated code quickly, but the first version stored state on the local filesystem. Fine on a laptop; wrong on a NAS with containers and concurrent jobs. Moving to PostgreSQL meant rework I could have avoided by deciding persistence up front.

Infrastructure needs reboot tests, not one browser check. Unpinned admin passwords and hostname/port mismatches came back after every Docker or server restart. "It works once" is not enough.

What is running today: a poller that checks a public data source every hour. When data changes, it publishes a change event to Kafka. Consumers can subscribe to those events to trigger extraction only when something actually changed.

Full notes (infra, SSH, Airflow version mismatch, CI/CD, incidents):

https://github.com/basvdberg/data-solution-2026/blob/main/lessons-learned-part1.md

https://github.com/basvdberg/data-solution-2026/blob/main/lessons-learned-part2.md

#DataEngineering #GenAI #ApacheAirflow #ApacheKafka #ProofOfConcept #DataArchitecture

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](../../readme.md)
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
        - [CI/CD workflow (main only + server pull deploy)](../design/cicd/ci-cd.md)
      - Monitoring
        - [Monitoring architecture](../design/monitoring/monitoring-architecture.md)
      - [Airflow asset naming](../design/airflow-asset-naming.md)
      - [Event-based orchestration plan](../design/event-based-orchestration-plan.md)
      - [Meta data design](../design/meta-data-design.md)
    - Image
    - Implementation
      - [Implementation plan (Open-Meteo → event orchestration)](../implementation/implementation-plan.md)
    - Linked In
      - [Data object quality of service](data-object-quality-of-service.md)
      - [Linkedin Post Part3V2](linkedin-post-part3v2.md)
    - Operation
      - [Event orchestration monitoring](../operation/event-orchestration-monitoring.md)
    - Retrospective
      - Incident
        - [INC-001 — NAS non-interactive SSH environment](../retrospective/incident/inc-001-nas-ssh-environment.md)
        - [INC-002 — Airflow standalone infra instability](../retrospective/incident/inc-002-airflow-infra-stability.md)
        - [INC-003 — Agent rediscovery and false-done verification](../retrospective/incident/inc-003-agent-process-gaps.md)
        - [INC-004 — Airflow PYTHONPATH drift (dag_run_guard import)](../retrospective/incident/inc-004-airflow-pythonpath-drift.md)
        - [INC-<NNN> — <short title>](../retrospective/incident/incident-template.md)
      - [Issue categories](../retrospective/issue-category.md)
    - [Implementation plan](../implementation-plan.md)
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
        - 12
          - V2026.06.12.1
            - [Release v2026.06.12.1](../../release/2026/06/12/v2026.06.12.1/notes.md)
    - [Release <version>](../../release/release-notes-template.md)
    - [Retrospective — <version>](../../release/retrospective-template.md)
  - Schema
  - [Getting started](../../getting-started.md)
  - [Lessons learned](../../lessons-learned-part1.md)
  - [Lessons learned (part 2)](../../lessons-learned-part2.md)
  - [Lessons learned (part 3)](../../lessons-learned-part3.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
