## Table of contents

<!-- markdown-toc:start -->
- [Release context](#release-context)
- [What went well](#what-went-well)
- [What did not go well](#what-did-not-go-well)
- [Incidents this release](#incidents-this-release)
- [Patterns (by category)](#patterns-by-category)
- [Root causes (generalized)](#root-causes-generalized)
- [Metrics](#metrics)
- [Action items](#action-items)
- [Promotions (approval gate)](#promotions-approval-gate)
- [Lessons promoted](#lessons-promoted)
- [Related artifacts](#related-artifacts)
<!-- markdown-toc:end -->

## Table of contents


﻿# Retrospective — v2026.06.05.6

Per-release sprint retrospective. Updated after backfill of chat-session issue (INC-004 / ERR-013).

## Release context

| Field | Value |
|-------|-------|
| **Version** | v2026.06.05.6 |
| **Date** | 2026-06-05 |
| **Commit** | `4322ead3138c1373874c532e4174f8eb7bea4867` |
| **Validation** | fail — Airflow DAG import error occurred; checklist not run; fixed ops-only |

## What went well

- **Terminology alignment** — infra and CI/CD docs consistently use *local server* instead of host-specific naming (`286f471`). Improves portability and matches `infra/local-server.env.example`.
- **Deploy path clarity** — `deploy-on-nas.sh` and post-push hook docs reference local-server env.
- **Release automation** — pre-commit hook bumped version and synced details/README metadata.
- **INC-004 resolved** — `deploy-infra-on-nas.sh` restored correct `PYTHONPATH`; `airflow dags list-import-errors` empty after fix.

## What did not go well

- **Airflow DAG import failure (INC-004)** — `ModuleNotFoundError: No module named 'dag_run_guard'` because `~/apache-airflow/docker-compose.standalone.yaml` was behind repo (`PYTHONPATH` missing `/opt/data-solution/code/airflow`). App-only deploy does not sync infra compose.
- **Issue not captured at fix time** — resolved in separate Cursor chat ([dag_run_guard import error](cedbaac2-52cd-4054-9696-197659e47a7b)); never logged as ERR/INC until retro review.
- **Initial retro was wrong** — claimed “no new incidents” because inputs were git + empty ERR log only; missed chat-session failures.
- **Release notes incomplete** — scope filled retroactively; validation checklist still unchecked.
- **Empty prompts capture** — `prompts.md` blank.

## Incidents this release

| ID | Title | Severity |
|----|-------|----------|
| [INC-004](../../doc/operation/incident/inc-004-airflow-pythonpath-drift.md) | Airflow PYTHONPATH drift (dag_run_guard import) | blocker |

Prior incidents (INC-001–003) are from the 2026-06-03 infra PoC.

## Patterns (by category)

| Category | Count | Example IDs | Theme |
|----------|-------|-------------|-------|
| orchestration | 1 | ERR-013, INC-004 | App deploy ≠ infra compose sync |
| release-cicd | 1 | — | Version bumps without validation evidence |
| process-verification | 2 | INC-004 | Chat-only fixes bypass inventory; retro missed transcripts |

## Root causes (generalized)

1. **Split deploy paths** — `git pull` updates app code; `~/apache-airflow/` compose updates only via infra sync.
2. **Capture gap** — failures fixed in Cursor chat never reached ERR log or incident register.
3. **Retro input too narrow** — git commits + ERR log insufficient; operational failures invisible in docs-only releases.

## Metrics

- ERR entries this period: 1 (ERR-013, backfilled)
- Incidents opened: 1 (INC-004) | resolved: 1 | codified: 0
- Validation checklist: fail (DAG import error; not checked before fix)
- Commits in release window: 4 (docs alignment + release bump + metadata refresh)

## Action items

| # | Action | Type | Owner | Status |
|---|--------|------|-------|--------|
| 1 | Add `airflow dags list-import-errors` to release validation template | checklist | agent | codified |
| 2 | Extend release-retrospective skill — scan agent transcripts / chat IDs | skill | agent | codified |
| 3 | Log ERR and promote INC when fixing release-impacting Airflow errors | process | agent | codified |
| 4 | Run full validation after deploy or mark N/A with reason | checklist | user | pending |
| 5 | Commit issue-inventory workflow in next release | process | agent | pending |

## Promotions (approval gate)

- [x] Update `release/release-notes-template.md` validation — DAG import check
- [x] Update skill: release-retrospective — chat transcript scan
- [x] Add themes to `lessons-learned-part2.md` — issue inventory, app vs infra deploy, release discipline
- [x] Generalize categories in `doc/operation/issue-category.md`
- [ ] Update skill: release-details-updater — require non-empty scope before release complete
- [ ] Update `infra/readme.md` — app vs infra deploy when PYTHONPATH changes

## Lessons promoted

| Category | Theme | Destination |
|----------|-------|-------------|
| process-verification | Chat fixes must enter inventory | [lessons-learned-part2.md#issue-inventory-and-retrospectives](../../lessons-learned-part2.md#issue-inventory-and-retrospectives) |
| orchestration | App deploy ≠ infra compose sync | [lessons-learned-part2.md#app-deploy-versus-infra-deploy](../../lessons-learned-part2.md#app-deploy-versus-infra-deploy) |
| release-cicd | Release notes as deliverable | [lessons-learned-part2.md#cicd-process](../../lessons-learned-part2.md#cicd-process) |
| *(all)* | Generalized by category | [issue-category.md#generalized-lessons-by-category](../../doc/operation/issue-category.md#generalized-lessons-by-category) |

## Related artifacts

- Release notes: [`notes.md`](../notes/v2026.06.05.6.md)
- Release details: [`readme.md`](readme.md)
- Incident: [INC-004](../../doc/operation/incident/inc-004-airflow-pythonpath-drift.md)
- ERR log: [ERR-013](../../.cursor/troubleshooting-errors.md)
- Source chat: [dag_run_guard import error](cedbaac2-52cd-4054-9696-197659e47a7b)
- Prior retro: [`v2026.06.03.4`](v2026.06.03.4.md)

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](../../../../../readme.md)
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
      - [Architecture](../../../../../doc/design/architecture.md)
      - [CI/CD workflow (main only + server pull deploy)](../../../../../doc/design/ci-cd.md)
      - [Event-based orchestration plan (single data object)](../../../../../doc/design/event-based-orchestration-plan.md)
      - [Kafka topic naming](../../../../../doc/design/kafka-topic-naming.md)
      - [Meta data design](../../../../../doc/design/meta-data-design.md)
    - Image
    - Implementation
      - [Implementation plan (Open-Meteo → event orchestration)](../../../../../doc/implementation/implementation-plan.md)
    - Linked In
      - [Linkedin Post Part3V2](../../../../../doc/linked-in/linkedin-post-part3v2.md)
    - Operation
      - Incident
        - [INC-001 — NAS non-interactive SSH environment](../../../../../doc/operation/incident/inc-001-nas-ssh-environment.md)
        - [INC-002 — Airflow standalone infra instability](../../../../../doc/operation/incident/inc-002-airflow-infra-stability.md)
        - [INC-003 — Agent rediscovery and false-done verification](../../../../../doc/operation/incident/inc-003-agent-process-gaps.md)
        - [INC-004 — Airflow PYTHONPATH drift (dag_run_guard import)](../../../../../doc/operation/incident/inc-004-airflow-pythonpath-drift.md)
        - [INC-<NNN> — <short title>](../../../../../doc/operation/incident/incident-template.md)
      - [Event orchestration monitoring](../../../../../doc/operation/event-orchestration-monitoring.md)
      - [Issue categories](../../../../../doc/operation/issue-category.md)
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
            - [Notes](../../02/v2026.06.02.1/notes.md)
          - V2026.06.02.2
            - [Release v2026.06.02.2](../../02/v2026.06.02.2/notes.md)
        - 03
          - V2026.06.03.1
            - [Release v2026.06.03.1](../../03/v2026.06.03.1/notes.md)
          - V2026.06.03.2
            - [Release v2026.06.03.2](../../03/v2026.06.03.2/notes.md)
          - V2026.06.03.3
            - [Release v2026.06.03.3](../../03/v2026.06.03.3/notes.md)
          - V2026.06.03.4
            - [Release v2026.06.03.4](../../03/v2026.06.03.4/notes.md)
            - [Retrospective](../../03/v2026.06.03.4/retrospective.md)
        - 04
          - V2026.06.04.1
            - [Notes](../../04/v2026.06.04.1/notes.md)
        - 05
          - V2026.06.05.6
            - [Notes](notes.md)
            - [Retrospective](retrospective.md)
        - 12
          - V2026.06.12.1
            - [Release v2026.06.12.1](../../12/v2026.06.12.1/notes.md)
    - [Release <version>](../../../../release-notes-template.md)
    - [Retrospective — <version>](../../../../retrospective-template.md)
  - [Getting started](../../../../../getting-started.md)
  - [Lessons learned](../../../../../lessons-learned-part1.md)
  - [Lessons learned (part 2)](../../../../../lessons-learned-part2.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
