# INC-002 — Airflow standalone infra instability

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

Initial Airflow PoC on the NAS required multiple fix cycles: incomplete first install, admin password regeneration on recreate, UI errors after reboot, Bad Gateway during startup, and task log URLs without hostname.

## Metadata

| Field | Value |
|-------|-------|
| **ID** | INC-002 |
| **When** | 2026-06-03 |
| **Category** | orchestration |
| **Severity** | blocker |
| **Release(s)** | pre-release (infra PoC) |
| **Related ERR** | ERR-003, ERR-004, ERR-005, ERR-006, ERR-008 |
| **Status** | resolved |

## Impact

- Airflow UI unusable or misleading after deploy, recreate, or host reboot
- Task logs showed invalid URLs (`http://:8793/`)
- Operators could not log in after container recreate until password re-documented

## Timeline

| Time | Event |
|------|-------|
| 2026-06-03 | First install missing metadata DB and logging pieces |
| 2026-06-03 | Admin password changed on almost every recreate |
| 2026-06-03 | UI errors after reboot; log links stale IPs/ports |
| 2026-06-03 | 502 Bad Gateway / missing scheduler during startup window |
| 2026-06-03 | Task log hostname empty (`getfqdn` in Docker on QNAP) |
| 2026-06-03 | Pinned compose: hostname, network, HOSTNAME_CALLABLE, AIRFLOW_ADMIN_PASSWORD |

## Root cause

Stack was partially invented on NAS instead of deployed from versioned compose. Identity (hostname, ports, password) was not pinned. Startup race and NGINX network membership were not accounted for in validation.

## Detection gap

Single browser check treated as “done” without reboot or full down/up cycle. No health endpoint wait before declaring failure.

## Resolution

- Use [infra/airflow/docker-compose.standalone.yaml](../../../infra/airflow/docker-compose.standalone.yaml) from repo
- Pin `AIRFLOW_ADMIN_PASSWORD` in `.env`
- Pin `hostname`, named network, `AIRFLOW__CORE__HOSTNAME_CALLABLE`, fixed `AIRFLOW_HOST_PORT`
- Wait 3–5 min then `curl` health endpoint; ensure NGINX on `apache-airflow_default` network
- Trigger **new** DAG run after hostname fix (old runs keep bad URLs in DB)

## Prevention

- Start from versioned compose; sync via `deploy-infra-on-nas.sh`
- Never mark infra done without login verify after `compose up -d`
- Mandatory reboot verification for infra changes
- See [infra/readme.md](../../../infra/readme.md) Airflow troubleshooting

## Action items

| # | Action | Type | Owner | Status |
|---|--------|------|-------|--------|
| 1 | Add reboot verification to release validation checklist | checklist | agent | codified |
| 2 | Document Bad Gateway startup window in infra readme | runbook | agent | codified |
| 3 | Pin hostname/password in compose and .env.example | infra | agent | codified |

## Related artifacts

- Troubleshooting: [ERR-003–006, ERR-008](../../../.cursor/troubleshooting-errors.md)
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
