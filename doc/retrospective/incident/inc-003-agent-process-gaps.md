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
        - [CI/CD workflow (main only + server pull deploy)](../../design/cicd/ci-cd.md)
      - Monitoring
        - [Monitoring architecture](../../design/monitoring/monitoring-architecture.md)
      - [Airflow asset naming](../../design/airflow-asset-naming.md)
      - [Event-based orchestration plan](../../design/event-based-orchestration-plan.md)
      - [Meta data design](../../design/meta-data-design.md)
    - Image
    - Implementation
      - [Implementation plan (Open-Meteo → event orchestration)](../../implementation/implementation-plan.md)
    - Linked In
      - [Data object quality of service](../../linked-in/data-object-quality-of-service.md)
      - [Linkedin Post Part3V2](../../linked-in/linkedin-post-part3v2.md)
    - Operation
      - [Event orchestration monitoring](../../operation/event-orchestration-monitoring.md)
    - Retrospective
      - Incident
        - [INC-001 — NAS non-interactive SSH environment](inc-001-nas-ssh-environment.md)
        - [INC-002 — Airflow standalone infra instability](inc-002-airflow-infra-stability.md)
        - [INC-003 — Agent rediscovery and false-done verification](inc-003-agent-process-gaps.md)
        - [INC-004 — Airflow PYTHONPATH drift (dag_run_guard import)](inc-004-airflow-pythonpath-drift.md)
        - [INC-<NNN> — <short title>](incident-template.md)
      - [Issue categories](../issue-category.md)
    - [Implementation plan](../../implementation-plan.md)
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
        - 12
          - V2026.06.12.1
            - [Release v2026.06.12.1](../../../release/2026/06/12/v2026.06.12.1/notes.md)
    - [Release <version>](../../../release/release-notes-template.md)
    - [Retrospective — <version>](../../../release/retrospective-template.md)
  - Schema
  - [Getting started](../../../getting-started.md)
  - [Lessons learned](../../../lessons-learned-part1.md)
  - [Lessons learned (part 2)](../../../lessons-learned-part2.md)
  - [Lessons learned (part 3)](../../../lessons-learned-part3.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
