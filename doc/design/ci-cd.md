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
- `release/YYYY/MM/DD/<version>/`: one folder per release — `notes.md` (published to GitHub Releases), `readme.md` (details), `prompts.md`, `retrospective.md`.
- `release/scripts/`: deploy, publish, and version-bump automation.
- `doc/operation/incident/`: blameless postmortems (INC-NNN) for significant failures.

### Simple release flow on main

Releases are automated when you commit and push on `main`:

1. **Pre-commit** (`cursor-config` → `pre_commit.py` → `release/scripts/new-release.ps1`):
   - Bumps `release/VERSION` (`vYYYY.MM.DD.N`, same-day `N` increments).
   - Scaffolds `release/YYYY/MM/DD/<version>/` (`notes.md`, `readme.md`, `prompts.md`, `retrospective.md`).
   - Skipped when only release-metadata files are staged, on non-`main` branches, or when `SKIP_RELEASE=1`.
2. **Commit**: edit the new release note scope/changes if needed; hooks refresh TOC, prompts, and release details.
3. **Push to `main`**: starts the CI/CD cycle:
   - **ntfy** immediately: “CI/CD started” (GitHub Actions) and “Push to main” (pre-push deploy hook, if installed).
   - **GitHub Actions**: tests → publish tag/release.
   - **Deploy watcher** (`wait-and-trigger-pull.ps1`, `-SkipPublish`):
     - Waits for the commit on `origin/main` and CI success.
     - Triggers NAS deploy via SSH (`deploy-on-nas.sh`).
4. **ntfy** on deploy success or failure (deploy watcher).
5. Optional: commit post-commit staged metadata (`chore: refresh release details`) or include in the next feature commit.

Manual override:

```powershell
# Skip version bump for one commit
$env:SKIP_RELEASE = "1"
git commit -m "chore: docs only"

# Dry-run next version
powershell -File release/scripts/new-release.ps1 -WhatIf
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
5. Trigger one manual DAG run; verify Postgres row, `event_published transport=kafka` in logs, and a message in Kafka UI.
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
- [Data Solution 2026](../../readme.md)
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
      - [Architecture](architecture.md)
      - [CI/CD workflow (main only + server pull deploy)](ci-cd.md)
      - [Event-based orchestration plan (single data object)](event-based-orchestration-plan.md)
      - [Kafka topic naming](kafka-topic-naming.md)
      - [Meta data design](meta-data-design.md)
    - Operation
      - Incident
        - [INC-001 — NAS non-interactive SSH environment](../operation/incident/inc-001-nas-ssh-environment.md)
        - [INC-002 — Airflow standalone infra instability](../operation/incident/inc-002-airflow-infra-stability.md)
        - [INC-003 — Agent rediscovery and false-done verification](../operation/incident/inc-003-agent-process-gaps.md)
        - [INC-004 — Airflow PYTHONPATH drift (dag_run_guard import)](../operation/incident/inc-004-airflow-pythonpath-drift.md)
        - [INC-<NNN> — <short title>](../operation/incident/incident-template.md)
      - [Issue categories](../operation/issue-category.md)
    - [Implementation plan (Open-Meteo → event orchestration)](../implementation-plan.md)
  - Docs
    - [LinkedIn post (part 3)](../../docs/linkedin-post-part3.md)
    - [Linkedin Post Part3V2](../../docs/linkedin-post-part3v2.md)
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
        - 08
          - V2026.06.08.1
            - [Notes](../../release/2026/06/08/v2026.06.08.1/notes.md)
            - [Retrospective](../../release/2026/06/08/v2026.06.08.1/retrospective.md)
          - V2026.06.08.2
            - [Notes](../../release/2026/06/08/v2026.06.08.2/notes.md)
            - [Retrospective](../../release/2026/06/08/v2026.06.08.2/retrospective.md)
        - 09
          - V2026.06.09.1
            - [Notes](../../release/2026/06/09/v2026.06.09.1/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.1/retrospective.md)
          - V2026.06.09.10
            - [Notes](../../release/2026/06/09/v2026.06.09.10/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.10/retrospective.md)
          - V2026.06.09.11
            - [Notes](../../release/2026/06/09/v2026.06.09.11/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.11/retrospective.md)
          - V2026.06.09.12
            - [Notes](../../release/2026/06/09/v2026.06.09.12/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.12/retrospective.md)
          - V2026.06.09.13
            - [Notes](../../release/2026/06/09/v2026.06.09.13/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.13/retrospective.md)
          - V2026.06.09.14
            - [Notes](../../release/2026/06/09/v2026.06.09.14/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.14/retrospective.md)
          - V2026.06.09.15
            - [Notes](../../release/2026/06/09/v2026.06.09.15/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.15/retrospective.md)
          - V2026.06.09.16
            - [Notes](../../release/2026/06/09/v2026.06.09.16/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.16/retrospective.md)
          - V2026.06.09.17
            - [Notes](../../release/2026/06/09/v2026.06.09.17/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.17/retrospective.md)
          - V2026.06.09.2
            - [Notes](../../release/2026/06/09/v2026.06.09.2/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.2/retrospective.md)
          - V2026.06.09.3
            - [Notes](../../release/2026/06/09/v2026.06.09.3/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.3/retrospective.md)
          - V2026.06.09.4
            - [Notes](../../release/2026/06/09/v2026.06.09.4/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.4/retrospective.md)
          - V2026.06.09.5
            - [Notes](../../release/2026/06/09/v2026.06.09.5/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.5/retrospective.md)
          - V2026.06.09.6
            - [Notes](../../release/2026/06/09/v2026.06.09.6/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.6/retrospective.md)
          - V2026.06.09.7
            - [Notes](../../release/2026/06/09/v2026.06.09.7/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.7/retrospective.md)
          - V2026.06.09.8
            - [Notes](../../release/2026/06/09/v2026.06.09.8/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.8/retrospective.md)
          - V2026.06.09.9
            - [Notes](../../release/2026/06/09/v2026.06.09.9/notes.md)
            - [Retrospective](../../release/2026/06/09/v2026.06.09.9/retrospective.md)
        - 11
          - V2026.06.11.1
            - [Notes](../../release/2026/06/11/v2026.06.11.1/notes.md)
            - [Retrospective](../../release/2026/06/11/v2026.06.11.1/retrospective.md)
          - V2026.06.11.2
            - [Notes](../../release/2026/06/11/v2026.06.11.2/notes.md)
            - [Retrospective](../../release/2026/06/11/v2026.06.11.2/retrospective.md)
          - V2026.06.11.3
            - [Notes](../../release/2026/06/11/v2026.06.11.3/notes.md)
            - [Retrospective](../../release/2026/06/11/v2026.06.11.3/retrospective.md)
          - V2026.06.11.4
            - [Notes](../../release/2026/06/11/v2026.06.11.4/notes.md)
            - [Retrospective](../../release/2026/06/11/v2026.06.11.4/retrospective.md)
          - V2026.06.11.5
            - [Notes](../../release/2026/06/11/v2026.06.11.5/notes.md)
            - [Retrospective](../../release/2026/06/11/v2026.06.11.5/retrospective.md)
          - V2026.06.11.6
            - [Notes](../../release/2026/06/11/v2026.06.11.6/notes.md)
            - [Retrospective](../../release/2026/06/11/v2026.06.11.6/retrospective.md)
          - V2026.06.11.7
            - [Notes](../../release/2026/06/11/v2026.06.11.7/notes.md)
            - [Retrospective](../../release/2026/06/11/v2026.06.11.7/retrospective.md)
    - [Release <version>](../../release/release-notes-template.md)
    - [Retrospective — <version>](../../release/retrospective-template.md)
  - Setting
  - Template
  - [Getting started](../../getting-started.md)
  - [Lessons learned](../../lessons-learned-part1.md)
  - [Lessons learned (part 2)](../../lessons-learned-part2.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
