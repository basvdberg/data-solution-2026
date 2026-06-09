# Lessons learned

## Table of contents

<!-- markdown-toc:start -->
- [Infrastructure deployment](#infrastructure-deployment)
- [Keep Gen AI under control](#keep-gen-ai-under-control)
- [Data Solution Automation metadata](#data-solution-automation-metadata)
- [Agnostic Data Labs](#agnostic-data-labs)
- [Data extraction via API](#data-extraction-via-api)
- [Learning new tools](#learning-new-tools)
- [Versioned Cursor configuration](#versioned-cursor-configuration)
- [Use Voice2Text](#use-voice2text)
<!-- markdown-toc:end -->

## Infrastructure deployment

This proof of concept needed [Apache Airflow](https://airflow.apache.org/) and [Apache Kafka](https://kafka.apache.org/). Because I prefer not to spend costs on spinning up cloud resources, I decided to use my local QNAP NAS as the **local server**. That required remote SSH so the agent could edit files and run commands on the server. Installing and tuning services from prompts worked well once SSH was in place.

I wanted services to have friendly URLs (for example `https://kafka.example` on the local server). This took noticeable effort installing HTTPS and local DNS. To keep browser access manageable, a small sync tool merges Chrome and Brave bookmarks with service URLs from deployment config ([local-server.env.example](infra/local-server.env.example), [service-url-map.yaml](https://github.com/basvdberg/cursor-config/blob/main/skills/deploy-basnas-container/service-url-map.yaml)).

**Takeaway:** Local NAS hosting is viable for PoC infrastructure when deployed via Gen-AI. Cursor is really good at solving installation issues via a backtracking mechanism. It just keeps firing PowerShell scripts to try out different approaches until the issue is fixed.

## Keep Gen AI under control

A pitfall when using GenAI is generating too much. Because it is easy to change the design, scope can grow quickly. A good design is also a simple one, as described in the [Simplicity](https://github.com/basvdberg/data-engineering-design-patterns/blob/main/design-patterns/generic/simplicity.md) design pattern.

Two controls helped:

- **Review every change** — although I sometimes clicked “Keep all” without reading every diff.
- **Refactor deliberately** — as understanding evolved, I deleted outdated design documents and asked Cursor to rewrite them, dropping historical decisions that no longer fit.

**Takeaway:** Treat generated artefacts as drafts; pair GenAI speed with human review and occasional “reset and rewrite” when the design has drifted.

## Data Solution Automation metadata

[Data Solution Automation (DSA)](https://github.com/data-solution-automation-engine/data-warehouse-automation-metadata-schema) metadata is an open JSON exchange format for connections, data objects, and source-to-target mappings—the *what* of a data solution without locking it to one ETL product or cloud stack. [Roelant Vos](https://roelantvos.com/blog/interface-for-data-warehouse-automation-metadata-released/) has written about the intent behind meta data driven automation for years.

After more than twenty years in data engineering I have seen many frameworks and vendors come and go, while the underlying transformation logic stays more or less the same. Describing that logic in a shared, human and AI agent-readable standard pays off:

1. **Shared vocabulary** — other engineers can read mappings and data objects without learning a project-specific config dialect.
2. **Longer-lived specifications** — a data solution specification can outlive a single implementation and be reused on a new platform or toolchain.
3. **Ecosystem and conventions** — common standards make collaboration easier.

In this PoC, working with DSA also surfaced practical gaps:

1. **Condensed mappings** — the published schema can express a mapping as one condensed JSON document that embeds data objects and connections. For Git-based workflows, separate elemental artifacts (as in [meta data design](doc/design/meta-data-design.md)) avoid redundancy when the same data object appears in multiple mappings. [Agnostic Data Labs](#agnostic-data-labs) follows the same decomposition when it loads metadata.
2. **Readable identities** — metadata should stay as simple and legible as possible. Path-based IDs (for example `staging/openmeteo/daily-temperature`) reveal name and location better than opaque hashes and make a separate `name` field redundant, in line with the [Simplicity](https://github.com/basvdberg/data-engineering-design-patterns/blob/main/design-patterns/generic/simplicity.md) pattern.

**Takeaway:** DSA is a strong interchange format; for day-to-day authoring in Git, prefer decomposed artifacts and path IDs over monolithic mapping bundles.

## Agnostic Data Labs

[Agnostic Data Labs](https://docs.agnosticdatalabs.com/docs/) (ADL) is a free companion to visualize [DSA metadata](https://data-solution-automation-engine.github.io/data-warehouse-automation-metadata-schema/). The UI and feature set are impressive, but two issues blocked deeper use in this PoC:

1. **Validation feedback** — JSON that matched the published automation schema did not always load in ADL, with little feedback on *why*. After reporting this, the developer fixed it quickly.
2. **On-disk shape** — When importing Data Object Mappings as defined by DSA, ADL decomposes the JSON into elemental components, which changes the on-disk representation. For round-tripping and GenAI workflows, a model centred on those elemental components may be clearer. 

**Takeaway:** ADL is a nice-to-have for this PoC; I kept it out of the critical path for now. Perhaps I will get back to it at a later stage. 

## Data extraction via API

**Old way of working without AI:** Extracting from a source with a well-defined API typically took one to two weeks—collecting and reading sometimes incomplete documentation, then iteratively building and testing the client.

**New way of working:** With generative AI (Cursor in this project), the [Open-Meteo extractor](extractor_and_poller/readme.md) was produced in a handful of prompts. End-to-end validation, including a smoke test against the live service, fit within about an hour.

**Takeaway:** A large efficiency gain; in this PoC the generated client was stronger and faster to test than a typical hand-written first version.

## Learning new tools

**Old way of working without AI:** Learning Airflow, Kafka, [Agnostic Data Labs](https://docs.agnosticdatalabs.com/docs/), or a new protocol client is normal work, but it often costs weeks of courses and trial-and-error before you ship confidently.

**New way of working:** AI explains how a tool fits a concrete use case in *your* architecture and generates starter code (DAGs, parsers, mapping JSON). You learn from working examples without mastering every aspect of the tool first. That shortens time-to-market for new tooling, makes it easier to compare or replace components, and supports a more technology-agnostic architecture.

## Versioned Cursor configuration

Skills and rules lived only under a local folder (for example `%USERPROFILE%\.cursor\`) until I moved them into a dedicated **cursor-config** project in this workspace. Versioning that configuration in Git gives history, makes the same setup portable across machines and repos, and reduces the risk of losing skills when you reinstall the IDE or switch computers.

**Takeaway:** Treat Cursor skills and rules like other engineering assets—version them, review changes, and reuse them across projects.

## Use Voice2Text

I bought a very good microphone and used Wispr Flow to translate my voice to text in order to spare my arms from typing that much text in my cursor chat dialogue.

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
