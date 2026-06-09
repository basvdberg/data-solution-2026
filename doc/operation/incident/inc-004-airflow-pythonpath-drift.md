# INC-004 — Airflow PYTHONPATH drift (dag_run_guard import)

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

After deploy, `openmeteo_data_object_poller` failed DAG parse with `ModuleNotFoundError: No module named 'dag_run_guard'`. The module exists in the repo at `code/airflow/dag_run_guard.py`, but the Airflow container on the local server used a stale compose file without `/opt/data-solution/code/airflow` on `PYTHONPATH`.

## Metadata

| Field | Value |
|-------|-------|
| **ID** | INC-004 |
| **When** | 2026-06-05 |
| **Category** | orchestration |
| **Severity** | blocker |
| **Release(s)** | v2026.06.05.6 (operational; not in git commits) |
| **Related ERR** | ERR-013 |
| **Status** | resolved |
| **Source chat** | [dag_run_guard import error](cedbaac2-52cd-4054-9696-197659e47a7b) (user ref: `a672de17-cc52-409f-b6a6-b3326360ae3e`) |

## Impact

- Poller DAG did not load; manual trigger blocked
- Release validation item “Airflow DAGs available” would have failed if checked
- Issue fixed in a separate Cursor session but not captured in ERR/INC until retro review

## Timeline

| Time | Event |
|------|-------|
| 2026-06-05 | User saw DAG import traceback for `dag_run_guard` |
| 2026-06-05 | Diagnosis: `~/apache-airflow/docker-compose.standalone.yaml` behind repo |
| 2026-06-05 | `deploy-infra-on-nas.sh` synced compose and recreated container |
| 2026-06-05 | `airflow dags list-import-errors` → no errors; DAG listed |
| 2026-06-08 | Backfilled ERR-013 and INC-004; added to retro v2026.06.05.6 |

## Root cause

Two deploy paths diverged:

1. **App deploy** (`deploy-on-nas.sh`) — `git pull` only; does not update `~/apache-airflow/`
2. **Infra deploy** (`deploy-infra-on-nas.sh`) — syncs compose including `PYTHONPATH`

Repo already had correct `PYTHONPATH` in `infra/airflow/docker-compose.standalone.yaml`; runtime copy was stale.

## Detection gap

- No `airflow dags list-import-errors` in release validation checklist
- Issue fixed in chat only; not logged to `.cursor/troubleshooting-errors.md` at time of fix
- Retro workflow did not scan agent transcripts

## Resolution

```bash
bash ~/apps/data-solution-2026/infra/scripts/deploy-infra-on-nas.sh
```

Verified:

- `PYTHONPATH=/opt/data-solution/code:/opt/data-solution:/opt/data-solution/code/airflow`
- `airflow dags list-import-errors` empty
- `openmeteo_data_object_poller` in DAG list

## Prevention

- Add `airflow dags list-import-errors` to release validation (template updated)
- When `infra/` or DAG imports change: use `RUN_INFRA_SYNC=1` or run infra deploy script
- Log ERR and promote to INC when validation fails; do not leave fixes chat-only
- Retro skill: search agent transcripts when user supplies chat ID or release period has gaps

## Action items

| # | Action | Type | Owner | Status |
|---|--------|------|-------|--------|
| 1 | Add DAG import check to release-notes-template Validation | checklist | agent | codified |
| 2 | Extend release-retrospective skill — chat transcript scan | skill | agent | codified |
| 3 | Document app vs infra deploy split in retro action items | runbook | agent | pending |

## Related artifacts

- Troubleshooting: [ERR-013](../../../.cursor/troubleshooting-errors.md)
- Retrospective: [v2026.06.05.6](../../release/retrospective/v2026.06.05.6.md)
- Compose: [`infra/airflow/docker-compose.standalone.yaml`](../../../infra/airflow/docker-compose.standalone.yaml)

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
