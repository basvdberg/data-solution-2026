# INC-003 — Agent rediscovery and false-done verification

## Table of contents

<!-- markdown-toc:start -->
- [Summary](#summary)
- [Metadata](#metadata)
- [Impact](#impact)
- [Timeline](#timeline)
- [Root cause](#root-cause)
- [Detection gap](#detection-gap)
- [Resolution](#resolution)
- [Prevention](#prevention)
- [Action items](#action-items)
- [Related artifacts](#related-artifacts)
<!-- markdown-toc:end -->

## Summary

During infra troubleshooting the agent repeated environment discovery commands, invoked scripts from wrong working directories, and declared fixes complete without reboot verification — wasting time and leaving latent failures.

## Metadata

| Field | Value |
|-------|-------|
| **ID** | INC-003 |
| **When** | 2026-06-03 |
| **Category** | agent-efficiency (primary), process-verification |
| **Severity** | degraded |
| **Release(s)** | pre-release (infra PoC) |
| **Related ERR** | ERR-002, ERR-011, ERR-012 |
| **Status** | codified |

## Impact

- Same `which`/`find` for docker run multiple times in one session
- Local script invoked from monorepo root instead of cursor-config path
- Airflow UI worked once then failed after reboot (false positive “done”)

## Timeline

| Time | Event |
|------|-------|
| 2026-06-03 | Repeated docker discovery after ERR-001 already documented |
| 2026-06-03 | `manage-bookmarks.cmd` not found (wrong cwd) |
| 2026-06-03 | Infra marked done without reboot test; ERR-005 recurred |

## Root cause

No mandatory read of troubleshooting log before retry. No explicit infra verification checklist. Assumption that one successful UI check equals durable fix.

## Detection gap

Process rules existed only implicitly in chat, not in agent skills or release validation.

## Resolution

- Introduced `.cursor/troubleshooting-errors.md` and `troubleshooting-error-log` skill
- ERR-012 prevention: infra checklist includes reboot/full cycle
- Log Count increment on repeat signatures

## Prevention

- Read troubleshooting log before retrying known signatures
- If `Count > 1`, stop and apply documented Solution
- Infra checklist: health curl → HTTPS UI → **host reboot or full down/up** → UI + new DAG log
- Verify script path with `Test-Path` / `Get-Command` before invoke

## Action items

| # | Action | Type | Owner | Status |
|---|--------|------|-------|--------|
| 1 | troubleshooting-error-log skill with dedup and review | skill | agent | codified |
| 2 | Add infra reboot item to release-notes-template Validation | checklist | agent | codified |
| 3 | Issue inventory + per-release retrospective workflow | process | agent | codified |

## Related artifacts

- Troubleshooting: [ERR-002, ERR-011, ERR-012](../../../.cursor/troubleshooting-errors.md)
- Retrospective: [v2026.06.03.4](../../release/retrospective/v2026.06.03.4.md)

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](../../../readme.md)
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
      - [Architecture](../../design/architecture.md)
      - [CI/CD workflow (main only + server pull deploy)](../../design/ci-cd.md)
      - [Event-based orchestration plan (single data object)](../../design/event-based-orchestration-plan.md)
      - [Kafka topic naming](../../design/kafka-topic-naming.md)
      - [Meta data design](../../design/meta-data-design.md)
    - Operation
      - Incident
        - [INC-001 — NAS non-interactive SSH environment](inc-001-nas-ssh-environment.md)
        - [INC-002 — Airflow standalone infra instability](inc-002-airflow-infra-stability.md)
        - [INC-003 — Agent rediscovery and false-done verification](inc-003-agent-process-gaps.md)
        - [INC-004 — Airflow PYTHONPATH drift (dag_run_guard import)](inc-004-airflow-pythonpath-drift.md)
        - [INC-<NNN> — <short title>](incident-template.md)
      - [Issue categories](../issue-category.md)
    - [Implementation plan (Open-Meteo → event orchestration)](../../implementation-plan.md)
  - Docs
    - [LinkedIn post (part 3)](../../../docs/linkedin-post-part3.md)
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
            - [Notes](../../../release/2026/06/02/v2026.06.02.1/notes.md)
          - V2026.06.02.2
            - [Release v2026.06.02.2](../../../release/2026/06/02/v2026.06.02.2/notes.md)
        - 03
          - V2026.06.03.1
            - [Release v2026.06.03.1](../../../release/2026/06/03/v2026.06.03.1/notes.md)
          - V2026.06.03.2
            - [Release v2026.06.03.2](../../../release/2026/06/03/v2026.06.03.2/notes.md)
          - V2026.06.03.3
            - [Release v2026.06.03.3](../../../release/2026/06/03/v2026.06.03.3/notes.md)
          - V2026.06.03.4
            - [Release v2026.06.03.4](../../../release/2026/06/03/v2026.06.03.4/notes.md)
            - [Retrospective](../../../release/2026/06/03/v2026.06.03.4/retrospective.md)
        - 04
          - V2026.06.04.1
            - [Notes](../../../release/2026/06/04/v2026.06.04.1/notes.md)
        - 05
          - V2026.06.05.6
            - [Notes](../../../release/2026/06/05/v2026.06.05.6/notes.md)
            - [Retrospective](../../../release/2026/06/05/v2026.06.05.6/retrospective.md)
        - 08
          - V2026.06.08.1
            - [Notes](../../../release/2026/06/08/v2026.06.08.1/notes.md)
            - [Retrospective](../../../release/2026/06/08/v2026.06.08.1/retrospective.md)
          - V2026.06.08.2
            - [Notes](../../../release/2026/06/08/v2026.06.08.2/notes.md)
            - [Retrospective](../../../release/2026/06/08/v2026.06.08.2/retrospective.md)
        - 09
          - V2026.06.09.1
            - [Notes](../../../release/2026/06/09/v2026.06.09.1/notes.md)
            - [Retrospective](../../../release/2026/06/09/v2026.06.09.1/retrospective.md)
          - V2026.06.09.10
            - [Notes](../../../release/2026/06/09/v2026.06.09.10/notes.md)
            - [Retrospective](../../../release/2026/06/09/v2026.06.09.10/retrospective.md)
          - V2026.06.09.11
            - [Notes](../../../release/2026/06/09/v2026.06.09.11/notes.md)
            - [Retrospective](../../../release/2026/06/09/v2026.06.09.11/retrospective.md)
          - V2026.06.09.12
            - [Notes](../../../release/2026/06/09/v2026.06.09.12/notes.md)
            - [Retrospective](../../../release/2026/06/09/v2026.06.09.12/retrospective.md)
          - V2026.06.09.13
            - [Notes](../../../release/2026/06/09/v2026.06.09.13/notes.md)
            - [Retrospective](../../../release/2026/06/09/v2026.06.09.13/retrospective.md)
          - V2026.06.09.14
            - [Notes](../../../release/2026/06/09/v2026.06.09.14/notes.md)
            - [Retrospective](../../../release/2026/06/09/v2026.06.09.14/retrospective.md)
          - V2026.06.09.15
            - [Notes](../../../release/2026/06/09/v2026.06.09.15/notes.md)
            - [Retrospective](../../../release/2026/06/09/v2026.06.09.15/retrospective.md)
          - V2026.06.09.16
            - [Notes](../../../release/2026/06/09/v2026.06.09.16/notes.md)
            - [Retrospective](../../../release/2026/06/09/v2026.06.09.16/retrospective.md)
          - V2026.06.09.17
            - [Notes](../../../release/2026/06/09/v2026.06.09.17/notes.md)
            - [Retrospective](../../../release/2026/06/09/v2026.06.09.17/retrospective.md)
          - V2026.06.09.2
            - [Notes](../../../release/2026/06/09/v2026.06.09.2/notes.md)
            - [Retrospective](../../../release/2026/06/09/v2026.06.09.2/retrospective.md)
          - V2026.06.09.3
            - [Notes](../../../release/2026/06/09/v2026.06.09.3/notes.md)
            - [Retrospective](../../../release/2026/06/09/v2026.06.09.3/retrospective.md)
          - V2026.06.09.4
            - [Notes](../../../release/2026/06/09/v2026.06.09.4/notes.md)
            - [Retrospective](../../../release/2026/06/09/v2026.06.09.4/retrospective.md)
          - V2026.06.09.5
            - [Notes](../../../release/2026/06/09/v2026.06.09.5/notes.md)
            - [Retrospective](../../../release/2026/06/09/v2026.06.09.5/retrospective.md)
          - V2026.06.09.6
            - [Notes](../../../release/2026/06/09/v2026.06.09.6/notes.md)
            - [Retrospective](../../../release/2026/06/09/v2026.06.09.6/retrospective.md)
          - V2026.06.09.7
            - [Notes](../../../release/2026/06/09/v2026.06.09.7/notes.md)
            - [Retrospective](../../../release/2026/06/09/v2026.06.09.7/retrospective.md)
          - V2026.06.09.8
            - [Notes](../../../release/2026/06/09/v2026.06.09.8/notes.md)
            - [Retrospective](../../../release/2026/06/09/v2026.06.09.8/retrospective.md)
          - V2026.06.09.9
            - [Notes](../../../release/2026/06/09/v2026.06.09.9/notes.md)
            - [Retrospective](../../../release/2026/06/09/v2026.06.09.9/retrospective.md)
        - 11
          - V2026.06.11.1
            - [Notes](../../../release/2026/06/11/v2026.06.11.1/notes.md)
            - [Retrospective](../../../release/2026/06/11/v2026.06.11.1/retrospective.md)
    - [Release <version>](../../../release/release-notes-template.md)
    - [Retrospective — <version>](../../../release/retrospective-template.md)
  - Setting
  - Template
  - [Getting started](../../../getting-started.md)
  - [Lessons learned](../../../lessons-learned-part1.md)
  - [Lessons learned (part 2)](../../../lessons-learned-part2.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
