# Release artifacts

## Table of contents

<!-- markdown-toc:start -->
- [Artifact taxonomy](#artifact-taxonomy)
- [Release index](#release-index)
- [Flow per release](#flow-per-release)
  - [Publish-ready notes.md](#publish-ready-notesmd)
- [Related documentation](#related-documentation)
<!-- markdown-toc:end -->

Versioned delivery and learning artifacts for data-solution-2026. Each layer has a distinct audience and lifecycle (aligned with [Keep a Changelog](https://keepachangelog.com/), GitHub Releases, and blameless postmortems).

## Artifact taxonomy

| Layer | Path | Audience | Purpose |
|-------|------|----------|---------|
| **Release notes** | `release/YYYY/MM/DD/<version>/notes.md` | Operators, GitHub Release readers | What changed — concise, deploy-oriented ([Keep a Changelog](https://keepachangelog.com/) sections) |
| **Release details** | `release/YYYY/MM/DD/<version>/readme.md` | Internal audit | When/how built — metadata, prompts, validation evidence, links |
| **Prompts** | `release/YYYY/MM/DD/<version>/prompts.md` | Internal audit | Prompts used during the release |
| **Retrospective** | `release/YYYY/MM/DD/<version>/retrospective.md` | Team / agent + you | Per-release process review (optional — created on demand) |
| **Incidents** | `doc/operation/incident/` | Ops / learning | Significant failures — postmortem format, may span releases |
| **Troubleshooting log** | `.cursor/troubleshooting-errors.md` | Agent (session) | Tactical ERR entries during debugging; promote to incident when significant |

```text
release/
  VERSION                          # next release version
  deploy-config.json               # auto: sync_infra when infra/ runtime files change
  release-notes-template.md        # scaffold for notes
  retrospective-template.md        # scaffold for retrospective
  scripts/                         # automation (deploy, publish, new-release)
  YYYY/MM/DD/vYYYY.MM.DD.N/        # artifacts for one release
    notes.md                       # required (minimal stub at open)
    readme.md                      # optional (metadata when refreshed)
    prompts.md                     # optional (when transcript sessions exist)
    retrospective.md               # optional (agent retro on demand)

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
| [v2026.06.12.1](2026/06/12/v2026.06.12.1/notes.md) | 2026-06-12 | Catch-up: Kafka extract, deploy hardening, lean release flow |

Unpublished scaffold releases (Jun 08–11 auto-bumps) were removed in the 2026-06-12 consolidation. Use `release/scripts/prune-scaffold-releases.ps1` for future cleanups.

## Flow per release

1. **Pre-commit** ensures the open `release/VERSION` has a minimal `notes.md` stub (`ensure-open-release.ps1`); updates `deploy-config.json` when meaningful `infra/` files changed since the last release tag. Set `NEW_RELEASE=1` to force the next version; `SKIP_RELEASE=1` to skip hooks.
2. **Develop** — multiple commits update the same `notes.md`; agent logs ERR entries; promotes to INC when validation or deploy is impacted.
3. **Push** — CI and NAS deploy always. GitHub Release only when `notes.md` is publish-ready (`test-release-notes-ready.ps1`).
4. **Post-publish** — `close-release.ps1` bumps `VERSION` and opens the next minimal stub.
5. **Validate** — checklist in release notes; failures become or update incidents.
6. **Retrospective** (optional) — agent creates `retrospective.md` on demand; you approve action items and codification.
7. **Codify** — approved items become skills, rules, checklists, or `lessons-learned-part*.md` themes.

### Publish-ready `notes.md`

All of the following must be true before `publish-release.ps1` tags and creates a GitHub Release:

- Scope is not the template placeholder (`Brief description of what is included in this release.`).
- At least one non-empty change bullet under **Changes** (or `### Added` / `Changed` / etc.).
- Commit metadata is filled (not `<fill-after-commit>`).

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
      - [Architecture](../doc/design/architecture.md)
      - [CI/CD workflow (main only + server pull deploy)](../doc/design/ci-cd.md)
      - [Event-based orchestration plan (single data object)](../doc/design/event-based-orchestration-plan.md)
      - [Kafka topic naming](../doc/design/kafka-topic-naming.md)
      - [Meta data design](../doc/design/meta-data-design.md)
    - Image
    - Implementation
      - [Implementation plan (Open-Meteo → event orchestration)](../doc/implementation/implementation-plan.md)
    - Linked In
      - [Linkedin Post Part3V2](../doc/linked-in/linkedin-post-part3v2.md)
    - Operation
      - Incident
        - [INC-001 — NAS non-interactive SSH environment](../doc/operation/incident/inc-001-nas-ssh-environment.md)
        - [INC-002 — Airflow standalone infra instability](../doc/operation/incident/inc-002-airflow-infra-stability.md)
        - [INC-003 — Agent rediscovery and false-done verification](../doc/operation/incident/inc-003-agent-process-gaps.md)
        - [INC-004 — Airflow PYTHONPATH drift (dag_run_guard import)](../doc/operation/incident/inc-004-airflow-pythonpath-drift.md)
        - [INC-<NNN> — <short title>](../doc/operation/incident/incident-template.md)
      - [Event orchestration monitoring](../doc/operation/event-orchestration-monitoring.md)
      - [Issue categories](../doc/operation/issue-category.md)
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
        - 12
          - V2026.06.12.1
            - [Release v2026.06.12.1](2026/06/12/v2026.06.12.1/notes.md)
    - [Release <version>](release-notes-template.md)
    - [Retrospective — <version>](retrospective-template.md)
  - [Getting started](../getting-started.md)
  - [Lessons learned](../lessons-learned-part1.md)
  - [Lessons learned (part 2)](../lessons-learned-part2.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
