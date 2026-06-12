# INC-001 — NAS non-interactive SSH environment

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

Agent and automation sessions over SSH to the QNAP NAS failed or behaved inconsistently because non-interactive shells lack Container Station `docker` on PATH, QNAP `git` shared libraries, and executable bits on infra scripts after `git pull`.

## Metadata

| Field | Value |
|-------|-------|
| **ID** | INC-001 |
| **When** | 2026-06-03 |
| **Category** | infra-environment |
| **Severity** | degraded |
| **Release(s)** | pre-release (infra PoC) |
| **Related ERR** | ERR-001, ERR-007, ERR-009, ERR-010 |
| **Status** | resolved |

## Impact

- `docker` and `git` commands failed over bare SSH (exit 127 / missing `.so`)
- Setup scripts failed with permission denied or `sudo: command not found`
- Brief SSH connection refused during `sshd` reload

## Timeline

| Time | Event |
|------|-------|
| 2026-06-03 | `docker ps` → command not found on SSH |
| 2026-06-03 | `git pull` → libcharset.so.1 missing |
| 2026-06-03 | `enable-nas-ssh-user-env.sh` permission/sudo issues |
| 2026-06-03 | Transient SSH refused during PermitUserEnvironment enable |
| 2026-06-03 | Resolved via `nas-remote-env.sh`, `setup-nas-ssh-env.sh`, `bash` invocation |

## Root cause

QNAP non-interactive SSH uses a minimal environment. Container Station and optional QPKG paths are not on default PATH/LD_LIBRARY_PATH. Scripts assumed an interactive login shell.

## Detection gap

No pre-flight check in agent workflow to source NAS env before first `docker`/`git` command. Deploy scripts were correct but ad-hoc agent SSH was not.

## Resolution

- Run `bash infra/scripts/setup-nas-ssh-env.sh` once on NAS
- Set `bas` login shell to `~/.local/bin/nas-login-sh` in `/etc/passwd` (`sudo sed`; QTS admin password) — survives QNAP reboot
- Source `infra/scripts/nas-remote-env.sh` in deploy scripts (already in `deploy-on-nas.sh`)
- Do **not** rely on manual `PermitUserEnvironment` in `/etc/config/ssh/sshd_config` (regenerated on reboot)
- Running sshd as `bas` without sudo (`setsid /etc/init.d/login.sh restart`) can segfault

## Prevention

- Use **basnas-ssh** Cursor skill: plain `ssh bas@basnas 'docker …'` after one-time setup
- Do not default to `bash -lc` + `nas-path.sh` per command
- Do not set global `LD_LIBRARY_PATH` in `~/.profile` (breaks QNAP bash)
- See [infra/readme.md](../../../infra/readme.md) SSH troubleshooting sections

## Action items

| # | Action | Type | Owner | Status |
|---|--------|------|-------|--------|
| 1 | **basnas-ssh** skill + deploy-basnas-container link | skill | agent | codified |
| 2 | Source env in deploy-on-nas.sh | script | agent | codified |
| 3 | `enable-nas-login-shell.sh` + fix `enable-nas-ssh-user-env.sh` for QNAP active config | script | agent | pending |

## Related artifacts

- Troubleshooting: [ERR-001, ERR-007, ERR-009, ERR-010](../../../.cursor/troubleshooting-errors.md)
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
      - [Architecture](../../design/architecture.md)
      - [CI/CD workflow (main only + server pull deploy)](../../design/ci-cd.md)
      - [Event-based orchestration plan (single data object)](../../design/event-based-orchestration-plan.md)
      - [Kafka topic naming](../../design/kafka-topic-naming.md)
      - [Meta data design](../../design/meta-data-design.md)
    - Image
    - Implementation
      - [Implementation plan (Open-Meteo → event orchestration)](../../implementation/implementation-plan.md)
    - Linked In
      - [Linkedin Post Part3V2](../../linked-in/linkedin-post-part3v2.md)
    - Operation
      - Incident
        - [INC-001 — NAS non-interactive SSH environment](inc-001-nas-ssh-environment.md)
        - [INC-002 — Airflow standalone infra instability](inc-002-airflow-infra-stability.md)
        - [INC-003 — Agent rediscovery and false-done verification](inc-003-agent-process-gaps.md)
        - [INC-004 — Airflow PYTHONPATH drift (dag_run_guard import)](inc-004-airflow-pythonpath-drift.md)
        - [INC-<NNN> — <short title>](incident-template.md)
      - [Event orchestration monitoring](../event-orchestration-monitoring.md)
      - [Issue categories](../issue-category.md)
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
  - [Getting started](../../../getting-started.md)
  - [Lessons learned](../../../lessons-learned-part1.md)
  - [Lessons learned (part 2)](../../../lessons-learned-part2.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
