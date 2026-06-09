# Release artifacts

## Table of contents

<!-- markdown-toc:start -->
- [Artifact taxonomy](#artifact-taxonomy)
- [Release index](#release-index)
- [Flow per release](#flow-per-release)
- [Related documentation](#related-documentation)
<!-- markdown-toc:end -->

Versioned delivery and learning artifacts for data-solution-2026. Each layer has a distinct audience and lifecycle (aligned with [Keep a Changelog](https://keepachangelog.com/), GitHub Releases, and blameless postmortems).

## Artifact taxonomy

| Layer | Path | Audience | Purpose |
|-------|------|----------|---------|
| **Release notes** | `release/YYYY/MM/DD/<version>/notes.md` | Operators, GitHub Release readers | What changed — concise, deploy-oriented ([Keep a Changelog](https://keepachangelog.com/) sections) |
| **Release details** | `release/YYYY/MM/DD/<version>/readme.md` | Internal audit | When/how built — metadata, prompts, validation evidence, links |
| **Prompts** | `release/YYYY/MM/DD/<version>/prompts.md` | Internal audit | Prompts used during the release |
| **Retrospective** | `release/YYYY/MM/DD/<version>/retrospective.md` | Team / agent + you | Per-release process review — what went well, gaps, action items |
| **Incidents** | `doc/operation/incident/` | Ops / learning | Significant failures — postmortem format, may span releases |
| **Troubleshooting log** | `.cursor/troubleshooting-errors.md` | Agent (session) | Tactical ERR entries during debugging; promote to incident when significant |

```text
release/
  VERSION                          # next release version
  deploy-config.json               # auto: sync_infra when infra/ runtime files change
  release-notes-template.md        # scaffold for notes
  retrospective-template.md        # scaffold for retrospective
  scripts/                         # automation (deploy, publish, new-release)
  YYYY/MM/DD/vYYYY.MM.DD.N/        # all artifacts for one release
    notes.md
    readme.md
    prompts.md
    retrospective.md

doc/operation/
  readme.md                        # operations knowledge hub
  issue-category.md                # incident category taxonomy
  incident/                        # INC-NNN postmortems
```

## Release index

| Version | Date | Notes |
|---------|------|-------|
| [v2026.06.02.1](2026/06/02/v2026.06.02.1/notes.md) | 2026-06-02 | CI/CD and release folder bootstrap |
| [v2026.06.02.2](2026/06/02/v2026.06.02.2/notes.md) | 2026-06-02 | GitHub Actions and post-push fixes |
| [v2026.06.03.1](2026/06/03/v2026.06.03.1/notes.md) | 2026-06-03 | Infra PoC start |
| [v2026.06.03.2](2026/06/03/v2026.06.03.2/notes.md) | 2026-06-03 | Airflow standalone |
| [v2026.06.03.3](2026/06/03/v2026.06.03.3/notes.md) | 2026-06-03 | NAS deploy hardening |
| [v2026.06.03.4](2026/06/03/v2026.06.03.4/notes.md) | 2026-06-03 | Infra stability retro |
| [v2026.06.04.1](2026/06/04/v2026.06.04.1/notes.md) | 2026-06-04 | Postgres poller state |
| [v2026.06.05.6](2026/06/05/v2026.06.05.6/notes.md) | 2026-06-05 | Local-server terminology |

Empty scaffold releases (auto-bumped with no content) were removed during the 2026-06-08 folder reorganization.

## Flow per release

1. **Pre-commit** bumps `VERSION`, scaffolds `notes.md`, `readme.md`, `prompts.md`, and `retrospective.md` under `release/YYYY/MM/DD/<version>/`; updates `deploy-config.json` when meaningful `infra/` files changed since the last release tag.
2. **Develop** — agent logs ERR entries; promotes to INC when validation or deploy is impacted.
3. **Push** — CI, GitHub Release (from `notes.md`), NAS deploy.
4. **Validate** — checklist in release notes; failures become or update incidents.
5. **Retrospective** — agent drafts `retrospective.md` in the version folder; you approve action items and codification.
6. **Codify** — approved items become skills, rules, checklists, or `lessons-learned-part*.md` themes.

## Related documentation

- [CI/CD workflow](../doc/design/ci-cd.md)
- [Operations hub](../doc/operation/readme.md)
- [Issue categories](../doc/operation/issue-category.md)

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](../readme.md)
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
      - [Architecture](../doc/design/architecture.md)
      - [CI/CD workflow (main only + server pull deploy)](../doc/design/ci-cd.md)
      - [Event-based orchestration plan (single data object)](../doc/design/event-based-orchestration-plan.md)
      - [Meta data design](../doc/design/meta-data-design.md)
    - Operation
      - Incident
        - [INC-001 — NAS non-interactive SSH environment](../doc/operation/incident/inc-001-nas-ssh-environment.md)
        - [INC-002 — Airflow standalone infra instability](../doc/operation/incident/inc-002-airflow-infra-stability.md)
        - [INC-003 — Agent rediscovery and false-done verification](../doc/operation/incident/inc-003-agent-process-gaps.md)
        - [INC-004 — Airflow PYTHONPATH drift (dag_run_guard import)](../doc/operation/incident/inc-004-airflow-pythonpath-drift.md)
        - [INC-<NNN> — <short title>](../doc/operation/incident/incident-template.md)
      - [Issue categories](../doc/operation/issue-category.md)
    - [Implementation plan (Open-Meteo → event orchestration)](../doc/implementation-plan.md)
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
            - [Notes](2026/06/02/v2026.06.02.1/notes.md)
          - V2026.06.02.2
            - [Release v2026.06.02.2](2026/06/02/v2026.06.02.2/notes.md)
        - 03
          - V2026.06.03.1
            - [Release v2026.06.03.1](2026/06/03/v2026.06.03.1/notes.md)
          - V2026.06.03.2
            - [Release v2026.06.03.2](2026/06/03/v2026.06.03.2/notes.md)
          - V2026.06.03.3
            - [Release v2026.06.03.3](2026/06/03/v2026.06.03.3/notes.md)
          - V2026.06.03.4
            - [Release v2026.06.03.4](2026/06/03/v2026.06.03.4/notes.md)
            - [Retrospective](2026/06/03/v2026.06.03.4/retrospective.md)
        - 04
          - V2026.06.04.1
            - [Notes](2026/06/04/v2026.06.04.1/notes.md)
        - 05
          - V2026.06.05.6
            - [Notes](2026/06/05/v2026.06.05.6/notes.md)
            - [Retrospective](2026/06/05/v2026.06.05.6/retrospective.md)
        - 08
          - V2026.06.08.1
            - [Notes](2026/06/08/v2026.06.08.1/notes.md)
            - [Retrospective](2026/06/08/v2026.06.08.1/retrospective.md)
          - V2026.06.08.2
            - [Notes](2026/06/08/v2026.06.08.2/notes.md)
            - [Retrospective](2026/06/08/v2026.06.08.2/retrospective.md)
        - 09
          - V2026.06.09.1
            - [Notes](2026/06/09/v2026.06.09.1/notes.md)
            - [Retrospective](2026/06/09/v2026.06.09.1/retrospective.md)
          - V2026.06.09.2
            - [Notes](2026/06/09/v2026.06.09.2/notes.md)
            - [Retrospective](2026/06/09/v2026.06.09.2/retrospective.md)
          - V2026.06.09.3
            - [Notes](2026/06/09/v2026.06.09.3/notes.md)
            - [Retrospective](2026/06/09/v2026.06.09.3/retrospective.md)
          - V2026.06.09.4
            - [Notes](2026/06/09/v2026.06.09.4/notes.md)
            - [Retrospective](2026/06/09/v2026.06.09.4/retrospective.md)
          - V2026.06.09.5
            - [Notes](2026/06/09/v2026.06.09.5/notes.md)
            - [Retrospective](2026/06/09/v2026.06.09.5/retrospective.md)
    - [Release <version>](release-notes-template.md)
    - [Retrospective — <version>](retrospective-template.md)
  - Setting
  - Template
  - [Getting started](../getting-started.md)
  - [Lessons learned](../lessons-learned-part1.md)
  - [Lessons learned (part 2)](../lessons-learned-part2.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
