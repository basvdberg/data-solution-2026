# CI/CD workflow (main only + server pull deploy)

## Table of contents

<!-- markdown-toc:start -->
- [Design patterns](#design-patterns)
- [Goal](#goal)
- [CI/CD model](#cicd-model)
- [Prerequisites](#prerequisites)
- [Versioning and release notes](#versioning-and-release-notes)
  - [Version format](#version-format)
  - [Release folder](#release-folder)
  - [Simple release flow on main](#simple-release-flow-on-main)
- [Deploy model without GitHub to NAS access](#deploy-model-without-github-to-nas-access)
- [Server-side deploy script](#server-side-deploy-script)
- [Auto trigger from Cursor on push](#auto-trigger-from-cursor-on-push)
- [Poller rollout merged into CI/CD](#poller-rollout-merged-into-cicd)
- [Rollback](#rollback)
- [Operational notes](#operational-notes)
<!-- markdown-toc:end -->

## Design patterns

CI/CD workflow for this repo. Pattern definitions: [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns/blob/main/readme.md#purpose).

- [Separate what and how](https://github.com/basvdberg/data-engineering-design-patterns/blob/main/design-patterns/generic/separate-what-and-how.md) — Git metadata is deployed; runtime code under `code/` and libraries in `extractor_and_poller/` implement *how* on NAS.
- [Simplicity](https://github.com/basvdberg/data-engineering-design-patterns/blob/main/design-patterns/generic/simplicity.md) — keep one straightforward main-line deployment path.

## Goal

Keep CI/CD simple: commit to `main`, run checks in GitHub Actions, then deploy from NAS by pulling from `main`. Track each deploy with a version and release notes.

## CI/CD model

- **Main only**: all development and deployment happens through `main`.
- **Git remote**: source of truth for commit history, tags, and release notes.
- **GitHub Actions** (`.github/workflows/deploy-main.yml`): on each push to `main`, sends an **ntfy** notification, runs tests, and publishes the GitHub release (no NAS deploy from GitHub).
- **pre-push hook** (local, via `core.hooksPath`): when you `git push` to `main` from this machine, starts a background watcher that waits for CI success and SSH-triggers NAS deploy (required when GitHub cannot reach the NAS).
- **NAS (runtime)**: deployment target for Airflow, poller, and extractor runtime.

## Prerequisites

- NAS has `git`, Python, and runtime dependencies installed.
- A deployment folder exists on NAS, for example `~/apps/data-solution-2026`.
- Secrets are stored on NAS in `.env` (or secret manager), never in Git.
- NAS can pull from Git remote (HTTPS token or SSH deploy key).
- Airflow/Kafka/Postgres are reachable from NAS runtime.
- Docker stacks are defined under `infra/` ([infra/readme.md](../../infra/readme.md)). [release/deploy-config.json](../../release/deploy-config.json) sets `sync_infra` automatically when meaningful `infra/` runtime files change; [deploy-on-nas.sh](../../release/scripts/deploy-on-nas.sh) runs [deploy-infra-on-nas.sh](../../infra/scripts/deploy-infra-on-nas.sh) when that flag is true (or when `RUN_INFRA_SYNC=1`).

## Versioning and release notes

### Version format

Use calendar versioning with an increment for same-day changes:

- `vYYYY.MM.DD.N` (example: `v2026.06.02.1`)

Rules:

- Increment `N` for each additional release on the same day.
- Create an annotated tag for each deployable release.
- Keep `release/VERSION` in sync with the latest intended release.

### Release folder

Use files under `release/` (see [release/readme.md](../../release/readme.md)):

- `release/VERSION`: next or current release version.
- `release/release-notes-template.md`: operator-facing template ([Keep a Changelog](https://keepachangelog.com/) sections).
- `release/YYYY/MM/DD/<version>/`: one folder per release — `notes.md` (required, published to GitHub Releases when ready); `readme.md`, `prompts.md`, and `retrospective.md` are optional and created only when they have meaningful content.
- `release/scripts/`: deploy, publish, and version-bump automation.
- `doc/operation/incident/`: blameless postmortems (INC-NNN) for significant failures.

### Simple release flow on main

Commits on `main` accumulate in the **open release** pointed to by `release/VERSION`. A new version folder is opened only after a successful GitHub Release (or when you force one).

1. **Pre-commit** (`cursor-config` → `pre_commit.py`):
   - `ensure-open-release.ps1` — creates a minimal `notes.md` stub for `release/VERSION` if missing (not a full template tree).
   - Skipped on non-`main` branches, when only release-metadata files are staged, or when `SKIP_RELEASE=1`.
   - Hooks refresh TOC, prompts (when transcript sessions exist), and release details (`readme.md` when needed).
2. **Commit**: edit `release/YYYY/MM/DD/<version>/notes.md` scope and changes in place across multiple commits.
3. **Push to `main`**: CI and NAS deploy always run. **GitHub Release** only when `notes.md` is publish-ready (real scope, change bullets, commit SHA filled) — see `release/scripts/test-release-notes-ready.ps1`.
4. **Post-publish** (`close-release.ps1`): bumps `VERSION` and opens the next minimal `notes.md` stub.
5. **Retrospective** (optional): agent creates `retrospective.md` from template when you run the release-retrospective skill.

Manual override:

```powershell
# Skip release hooks for one commit
$env:SKIP_RELEASE = "1"
git commit -m "chore: docs only"

# Force-open the next version before commit
$env:NEW_RELEASE = "1"
git commit -m "feat: start new release"

# Dry-run next version
powershell -File release/scripts/new-release.ps1 -WhatIf

# Remove unpublished scaffold folders
powershell -File release/scripts/prune-scaffold-releases.ps1 -Force
```

Legacy manual tagging (only if automation is disabled):

```bash
git tag -a vYYYY.MM.DD.N -m "Release vYYYY.MM.DD.N"
git push origin --tags
gh release create vYYYY.MM.DD.N --notes-file release/YYYY/MM/DD/vYYYY.MM.DD.N/notes.md
```

## Deploy model without GitHub to NAS access

GitHub-hosted runners usually cannot reach a LAN-only NAS. Deployment stays **pull-based** on the NAS, triggered after green CI:

1. Push commit to `main` → GitHub Actions notifies via **ntfy**, runs tests, publishes release.
2. **pre-push deploy hook** (from your dev machine on the LAN) waits for CI green, then SSH-runs `deploy-on-nas.sh`.
3. NAS updates to latest `origin/main` and applies runtime actions (Airflow DAG refresh; infra sync when `release/deploy-config.json` has `sync_infra: true`).

Workflow: `.github/workflows/deploy-main.yml` (notify → test → release).

## Server-side deploy script

Run on NAS from `~/apps/data-solution-2026` (app-only, no Docker required):

```bash
set -e
cd ~/apps/data-solution-2026
git fetch --all --tags
git checkout main
git reset --hard origin/main   # discard any local edits; deploy folder mirrors remote
# Optional poller smoke check only if Python is available:
# RUN_POLLER_CHECK=1 bash release/scripts/deploy-on-nas.sh
# Infra sync runs automatically when release/deploy-config.json has sync_infra: true
```

`release/deploy-config.json` is updated on each pre-commit by `release/scripts/update-deploy-config.ps1`. Meaningful changes include compose files and `.env.example` under `infra/airflow`, `infra/kafka`, and `infra/postgres` (not readme-only edits or `infra/scripts/*`, which deploy via `git pull`). Detection uses `git diff` since the latest `v*` tag plus staged files. When `sync_infra` is true, `infra_components` lists which stacks to sync (for example only `airflow` when Kafka and Postgres are unchanged).

The deploy script always **discards local changes** in the NAS clone before updating. Treat `~/apps/data-solution-2026` as read-only at runtime; never edit application code there—commit on your dev machine and push to `main` instead.

Optional automation on NAS:

- Cron every N minutes to run a deploy script after checking CI status manually.
- Systemd timer for controlled periodic pulls.
- Manual trigger from Cursor Remote SSH for full control.

## Auto trigger from Cursor on push

This repo sets `core.hooksPath` to `cursor-config/githooks` (shared pre-commit/post-commit). Deploy uses the **`pre-push`** hook there (Git has no `post-push` hook).

Verify once from repo root:

```powershell
powershell -ExecutionPolicy Bypass -File .\release\scripts\install-post-push-hook.ps1
```

Every **`git push origin main`** from this machine should complete the cycle (notify → CI → deploy):

1. **ntfy** on push: “Push to main” (immediate).
2. **GitHub Actions** on `origin/main`: ntfy “CI/CD started”, tests, release publish.
3. `pre-push` hook starts `wait-and-trigger-pull.ps1` in the background.
4. Watcher waits until the commit is on `origin/main` and CI is green.
5. Watcher SSH-triggers `deploy-on-nas.sh` (`git reset --hard origin/main` on NAS, discarding local edits) and sends ntfy success/failure.

Scripts in this repo:

- `release/scripts/wait-and-trigger-pull.ps1`
- `release/scripts/post-push-hook.ps1` (invoked from `cursor-config/githooks/pre-push`)
- `release/scripts/install-post-push-hook.ps1`
- `release/scripts/deploy-on-nas.sh`

Setup:

1. Edit `release/scripts/post-push-hook.ps1` and set your NAS SSH command.
2. Ensure `cursor-config/githooks/pre-push` exists (monorepo sibling) or copy it into your `core.hooksPath`.

Notes:

- The CI wait script uses `gh` CLI; run `gh auth login` in this environment.
- The watcher timeout and polling interval are configurable:
  - `-TimeoutMinutes` (default `20`)
  - `-PollSeconds` (default `15`)
- If CI fails, deployment is aborted automatically.
- `ntfy` is the default notification channel in the scripts.
- Default topic: `data-solution-2026-deploy` (must match `post-push-hook.ps1`).
- Subscribe using app/web/CLI before first run, for example:

```bash
ntfy sub data-solution-2026-deploy
```

- Or in browser:
  - `https://ntfy.sh/data-solution-2026-deploy`
- Notification options in `wait-and-trigger-pull.ps1`:
  - `-NotifyMode ntfy` (default)
  - `-NotifyMode console`
  - `-NotifyMode toast` (Windows desktop toast via BurntToast module)
  - `-NotifyMode webhook` (POST JSON to `-WebhookUrl`, useful for Teams/Slack/ntfy)
  - `-NotifyMode both` (toast + webhook)
- On deploy **success** or **failure**, ntfy includes the release version from `release/VERSION` and a link to the release notes on GitHub (`release/notes/<version>.md`). Tapping the notification opens that URL.

## Poller rollout merged into CI/CD

After NAS pull deploy:

1. Infra sync runs when `release/deploy-config.json` has `sync_infra: true` (or `RUN_INFRA_SYNC=1`). That applies Kafka + Airflow compose, sets `KAFKA_HOST` in `~/apache-airflow/.env`, and removes obsolete Airflow Variables.
2. DAG `openmeteo_data_object_poller` is bind-mounted from `code/airflow/dags/` (paused on creation; `catchup=false`, `max_active_runs=1`).
3. The DAG task always runs the poller with `--publish kafka`; broker address from `KAFKA_HOST`.
4. Optional: Airflow Variable `data_object_id` to override the default probe target.
5. Trigger one manual DAG run; verify Postgres row, `publish_poll_event` task success, and a message in Kafka UI.
6. Unpause the schedule after smoke validation.

## Rollback

If deployment fails:

1. On NAS, checkout previous known-good tag.
2. Reload/restart only the app services that consume repo code (if needed).
3. Disable/keep paused new Airflow schedule until validated.

```bash
cd ~/apps/data-solution-2026
git fetch --all --tags
git checkout <previous-tag>
```

## Operational notes

- Keep release notes mandatory for every deploy to `main`.
- Do not edit release code manually on NAS.
- Keep tags consistent for traceability.
- Never expose internal service ports publicly; use VPN or SSH.

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
        - [CI/CD workflow (main only + server pull deploy)](ci-cd.md)
      - Monitoring
        - [Monitoring architecture](../monitoring/monitoring-architecture.md)
      - [Airflow asset naming](../airflow-asset-naming.md)
      - [Event-based orchestration plan](../event-based-orchestration-plan.md)
      - [Meta data design](../meta-data-design.md)
    - Image
    - Implementation
      - [Implementation plan (Open-Meteo → event orchestration)](../../implementation/implementation-plan.md)
    - Linked In
      - [Linkedin Post Part3V2](../../linked-in/linkedin-post-part3v2.md)
    - Operation
      - [Event orchestration monitoring](../../operation/event-orchestration-monitoring.md)
    - Retrospective
      - Incident
        - [INC-001 — NAS non-interactive SSH environment](../../retrospective/incident/inc-001-nas-ssh-environment.md)
        - [INC-002 — Airflow standalone infra instability](../../retrospective/incident/inc-002-airflow-infra-stability.md)
        - [INC-003 — Agent rediscovery and false-done verification](../../retrospective/incident/inc-003-agent-process-gaps.md)
        - [INC-004 — Airflow PYTHONPATH drift (dag_run_guard import)](../../retrospective/incident/inc-004-airflow-pythonpath-drift.md)
        - [INC-<NNN> — <short title>](../../retrospective/incident/incident-template.md)
      - [Issue categories](../../retrospective/issue-category.md)
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
