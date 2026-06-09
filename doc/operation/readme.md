# Operations

## Table of contents

<!-- markdown-toc:start -->
- [Structure](#structure)
- [Lifecycle](#lifecycle)
- [Retrospective → lessons ceremony](#retrospective-lessons-ceremony)
- [Related](#related)
<!-- markdown-toc:end -->

Cross-release operational knowledge: incidents, categories, and links to per-release retrospectives.

## Structure

| Path | Purpose |
|------|---------|
| [issue-category.md](issue-category.md) | Taxonomy for classifying incidents and retro patterns |
| [incident/readme.md](incident/readme.md) | Incident register (INC-NNN) |
| [incident/incident-template.md](incident/incident-template.md) | Scaffold for new postmortems |
| [../release/retrospective/](../release/retrospective/) | Per-release sprint retrospectives |
| [../../.cursor/troubleshooting-errors.md](../../.cursor/troubleshooting-errors.md) | Session-level ERR log (agent-maintained) |

## Lifecycle

```text
ERR (tactical, session)  →  INC (significant event)  →  retro (per release)  →  guardrails
```

- **ERR** — logged immediately on failure during debugging (`troubleshooting-error-log` skill).
- **INC** — promoted when impact is blocker/degraded, release validation fails, or root cause is worth preserving.
- **Retrospective** — aggregates incidents and ERR patterns for one release; produces action items.
- **Guardrails** — skills, rules, validation checklists, infra runbooks, design patterns, or [lessons learned](../../lessons-learned-part2.md) (after your approval).

## Retrospective → lessons ceremony

1. Run per-release retro (`release/retrospective/<version>.md`).
2. Roll up **Patterns by category**; compare with [issue-category.md](issue-category.md).
3. Promote mature themes into `lessons-learned-part2.md` (narrative) and update **Generalized lessons by category**.
4. Check off retro **Promotions** when codified.

## Related

- [Release artifacts](../../release/readme.md)
- [CI/CD](../design/ci-cd.md)
- [Lessons learned (part 1)](../../lessons-learned-part1.md)
- [Lessons learned (part 2)](../../lessons-learned-part2.md)
- [Category lessons](issue-category.md#generalized-lessons-by-category)

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
      - [Architecture](../design/architecture.md)
      - [CI/CD workflow (main only + server pull deploy)](../design/ci-cd.md)
      - [Event-based orchestration plan (single data object)](../design/event-based-orchestration-plan.md)
      - [Kafka topic naming](../design/kafka-topic-naming.md)
      - [Meta data design](../design/meta-data-design.md)
    - Operation
      - Incident
        - [INC-001 — NAS non-interactive SSH environment](incident/inc-001-nas-ssh-environment.md)
        - [INC-002 — Airflow standalone infra instability](incident/inc-002-airflow-infra-stability.md)
        - [INC-003 — Agent rediscovery and false-done verification](incident/inc-003-agent-process-gaps.md)
        - [INC-004 — Airflow PYTHONPATH drift (dag_run_guard import)](incident/inc-004-airflow-pythonpath-drift.md)
        - [INC-<NNN> — <short title>](incident/incident-template.md)
      - [Issue categories](issue-category.md)
    - [Implementation plan (Open-Meteo → event orchestration)](../implementation-plan.md)
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
