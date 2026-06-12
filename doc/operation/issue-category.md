# Issue categories

## Table of contents

<!-- markdown-toc:start -->
- [Categories](#categories)
- [Generalized lessons by category](#generalized-lessons-by-category)
  - [infra-environment](#infra-environment)
  - [orchestration](#orchestration)
  - [release-cicd](#release-cicd)
  - [application](#application)
  - [agent-efficiency](#agent-efficiency)
  - [process-verification](#process-verification)
- [Cross-cutting themes](#cross-cutting-themes)
- [Incidents by category](#incidents-by-category)
- [Heat map](#heat-map)
- [Usage](#usage)
<!-- markdown-toc:end -->

Stable taxonomy for incidents (`INC-NNN`), retrospective roll-ups, and trend tracking. Assign **one primary category** per incident.

Generalized lessons below are promoted from retrospectives [v2026.06.03.4](../../release/retrospective/v2026.06.03.4.md) and [v2026.06.05.6](../../release/retrospective/v2026.06.05.6.md) into [lessons learned (part 2)](../../lessons-learned-part2.md).

## Categories

| ID | Name | Scope | Examples |
|----|------|-------|----------|
| `infra-environment` | Infra and environment | Docker, NAS SSH, PATH, networking, reboot drift | docker not on PATH, libcharset, NGINX bridge |
| `orchestration` | Orchestration | Airflow DAGs, scheduler, task logs, deploy sync | incomplete install, log URL hostname, PYTHONPATH drift |
| `release-cicd` | Release and CI/CD | Versioning, deploy scripts, CI gates, tag/release publish | empty release notes, version churn without validation |
| `application` | Application | Poller, extractor, metadata, Kafka, Postgres | happy-path logs without row verify, smoke test failures |
| `agent-efficiency` | Agent efficiency | Repeated commands, wrong cwd, rediscovery loops | same `which docker` twice, script path assumption |
| `process-verification` | Process and verification | False “done”, missing checklist, chat-only fixes | infra done without reboot test; fix not logged to ERR/INC |

## Generalized lessons by category

### infra-environment

**Theme:** Non-interactive automation ≠ your interactive shell.

- Source PATH and libraries once per session (`nas-remote-env.sh`); do not rediscover `docker` or `git` paths.
- QNAP SSH, Container Station, and optional QPKG paths are not on default `PATH` / `LD_LIBRARY_PATH`.
- Expect brief SSH outage when changing `sshd` settings.
- PowerShell → SSH quoting (pipes, `grep -E`, `docker --format`) fails silently; review executed commands at release retro and promote patterns to **basnas-ssh**.

**Incidents:** [INC-001](incident/inc-001-nas-ssh-environment.md)  
**Lessons:** [Remote SSH troubleshooting](../../lessons-learned-part2.md#remote-ssh-troubleshooting), [Local server interaction: learn from SSH commands](../../lessons-learned-part2.md#local-server-interaction-learn-from-ssh-commands), [Agent troubleshooting efficiency](../../lessons-learned-part2.md#agent-troubleshooting-efficiency)

### orchestration

**Theme:** Pin identity and sync the stack that runs the scheduler — not only the Git tree.

- Airflow needs pinned password, hostname, network, and startup wait — not a one-off browser check.
- DAG imports depend on container `PYTHONPATH`; app `git pull` does not update `~/apache-airflow/` compose.
- Task log URLs and worker callbacks break when hostname drifts (reboot, recreate).
- Validate with `airflow dags list-import-errors` after every deploy that touches DAGs or `infra/`.

**Incidents:** [INC-002](incident/inc-002-airflow-infra-stability.md), [INC-004](incident/inc-004-airflow-pythonpath-drift.md)  
**Lessons:** [Infrastructure deployment](../../lessons-learned-part2.md#infrastructure-deployment), [App deploy versus infra deploy](../../lessons-learned-part2.md#app-deploy-versus-infra-deploy)

### release-cicd

**Theme:** A release is a deliverable, not a hook side effect.

- Release notes must state scope, changes, and validation outcome before publish.
- Same-day version bumps without documented substance create noise in history.
- CI green + NAS pull does not imply runtime validation ran.
- Prompt capture in `release/details/<version>/prompts.md` is part of audit trail.

**Incidents:** *(process gap in v2026.06.05.6; no dedicated INC)*  
**Lessons:** [CI/CD process](../../lessons-learned-part2.md#cicd-process)

### application

**Theme:** Green logs ≠ persisted data.

- Verify side effects (query Postgres, row counts) — do not trust “success” log lines alone.
- Fail the task when persistence checks fail; treat “no exception” as insufficient proof.

**Incidents:** *(documented in lessons; no INC yet)*  
**Lessons:** [Junior-programmer mistakes](../../lessons-learned-part2.md#junior-programmer-mistakes), [Design the platform before application code](../../lessons-learned-part2.md#design-the-platform-before-application-code)

### agent-efficiency

**Theme:** Backtracking should move forward, not circle.

- Read `.cursor/troubleshooting-errors.md` before retrying; increment `Count` on repeats.
- Persist environment fixes for the whole session after first `command not found`.
- Verify script paths (`Test-Path`, `Get-Command`) before invoke.

**Incidents:** [INC-003](incident/inc-003-agent-process-gaps.md)  
**Lessons:** [Agent troubleshooting efficiency](../../lessons-learned-part2.md#agent-troubleshooting-efficiency)

### process-verification

**Theme:** Define “done” with evidence, and record failures where the org can see them.

- Infra: health curl → HTTPS UI → **reboot or full down/up** → new DAG run / log check.
- Every release-impacting fix → ERR log → INC if blocker/degraded → retro → lessons.
- Retros must scan ERR log, incidents, **and** chat transcripts when gaps are reported.

**Incidents:** [INC-003](incident/inc-003-agent-process-gaps.md), [INC-004](incident/inc-004-airflow-pythonpath-drift.md) (capture gap)  
**Lessons:** [Issue inventory and retrospectives](../../lessons-learned-part2.md#issue-inventory-and-retrospectives), [Working with agents](../../lessons-learned-part2.md#working-with-agents)

## Cross-cutting themes

These patterns span multiple categories:

| Theme | Categories | Guardrail |
|-------|------------|-----------|
| **Works once ≠ durable** | orchestration, process-verification | Reboot / down-up validation |
| **Two deploy paths** | orchestration, release-cicd | App pull vs `deploy-infra-on-nas.sh` |
| **Chat is not inventory** | process-verification, agent-efficiency | ERR → INC → retro → lessons |
| **Agent as implementer** | agent-efficiency, infra-environment, application | Document platform first; verify outcomes |
| **Platform before app** | application, orchestration, infra-environment | Postgres, compose, CI/CD design before codegen |

## Incidents by category

| Category | IDs |
|----------|-----|
| infra-environment | INC-001 |
| orchestration | INC-002, INC-004 |
| agent-efficiency | INC-003 (primary) |
| process-verification | INC-003, INC-004 (capture gap) |

## Heat map

| Category | Releases (recent) | Open guardrails |
|----------|-------------------|-----------------|
| infra-environment | v2026.06.03.4 | — |
| orchestration | v2026.06.03.4, v2026.06.05.6 | infra readme: app vs infra deploy |
| release-cicd | v2026.06.05.6 | release-details-updater: non-empty scope |
| application | — | require persistence checks in DAG/poller review |
| agent-efficiency | v2026.06.03.4 | — (skill codified) |
| process-verification | v2026.06.03.4, v2026.06.05.6 | lessons-learned themes promoted 2026-06-08 |

Update this table during each release retrospective. When one category appears in **three consecutive** retrospectives, change the way of working (not another one-off fix).

## Usage

- **Incidents** — set `Category` in the postmortem metadata table.
- **Retrospectives** — roll up counts in **Patterns**; link here for generalized lessons.
- **Lessons learned** — add narrative sections when a category theme matures (after retro promotion approval).

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
      - [Architecture](../design/architecture.md)
      - [CI/CD workflow (main only + server pull deploy)](../design/ci-cd.md)
      - [Event-based orchestration plan (single data object)](../design/event-based-orchestration-plan.md)
      - [Kafka topic naming](../design/kafka-topic-naming.md)
      - [Meta data design](../design/meta-data-design.md)
    - Image
    - Implementation
      - [Implementation plan (Open-Meteo → event orchestration)](../implementation/implementation-plan.md)
    - Linked In
      - [Linkedin Post Part3V2](../linked-in/linkedin-post-part3v2.md)
    - Operation
      - Incident
        - [INC-001 — NAS non-interactive SSH environment](incident/inc-001-nas-ssh-environment.md)
        - [INC-002 — Airflow standalone infra instability](incident/inc-002-airflow-infra-stability.md)
        - [INC-003 — Agent rediscovery and false-done verification](incident/inc-003-agent-process-gaps.md)
        - [INC-004 — Airflow PYTHONPATH drift (dag_run_guard import)](incident/inc-004-airflow-pythonpath-drift.md)
        - [INC-<NNN> — <short title>](incident/incident-template.md)
      - [Event orchestration monitoring](event-orchestration-monitoring.md)
      - [Issue categories](issue-category.md)
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
  - [Getting started](../../getting-started.md)
  - [Lessons learned](../../lessons-learned-part1.md)
  - [Lessons learned (part 2)](../../lessons-learned-part2.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
