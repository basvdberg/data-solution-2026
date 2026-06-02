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
- **GitHub Actions**: runs checks on each commit to `main`.
- **NAS (runtime)**: deployment target for Airflow, poller, and extractor runtime.

## Prerequisites

- NAS has `git`, Python, and runtime dependencies installed.
- A deployment folder exists on NAS, for example `~/apps/data-solution-2026`.
- Secrets are stored on NAS in `.env` (or secret manager), never in Git.
- NAS can pull from Git remote (HTTPS token or SSH deploy key).
- Airflow/Kafka/Postgres are reachable from NAS runtime.
- Docker stacks are defined under `infra/` ([infra/readme.md](../../infra/readme.md)). Sync to legacy NAS paths with `infra/scripts/deploy-infra-on-nas.sh` or `RUN_INFRA_SYNC=1` on [deploy-on-nas.sh](../../release/scripts/deploy-on-nas.sh).

## Versioning and release notes

### Version format

Use calendar versioning with an increment for same-day changes:

- `vYYYY.MM.DD.N` (example: `v2026.06.02.1`)

Rules:

- Increment `N` for each additional release on the same day.
- Create an annotated tag for each deployable release.
- Keep `release/VERSION` in sync with the latest intended release.

### Release folder

Use files under `release/`:

- `release/VERSION`: next or current release version.
- `release/release-notes-template.md`: template for every release note.
- `release/notes/`: one file per release, for example `v2026.06.02.1.md`.

### Simple release flow on main

1. Pull latest `main`.
2. Make your changes directly on `main`.
3. Update `release/VERSION`.
4. Create `release/notes/<version>.md` from the template.
5. Commit and push to `main` (this triggers CI checks).
6. On NAS, run deploy script to pull latest `main`.
7. If deploy is healthy, create and push annotated tag for traceability.

Example:

```bash
git checkout main
git pull
# edit files + release/VERSION + release/notes/vYYYY.MM.DD.N.md
git add .
git commit -m "release: vYYYY.MM.DD.N"
git push origin main
git tag -a vYYYY.MM.DD.N -m "Release vYYYY.MM.DD.N"
git push origin --tags
```

## Deploy model without GitHub to NAS access

Because GitHub cannot reach the local/NAS server, deployment is pull-based:

1. Push commit to `main`.
2. GitHub Actions runs CI checks only.
3. After CI is green, trigger deploy from NAS (manual command or scheduled job).
4. NAS updates to latest `origin/main`.
5. NAS applies app-level runtime actions (for example Airflow DAG/code refresh and optional migrations).
6. NAS runs smoke checks.

GitHub workflow used for checks: `.github/workflows/deploy-main.yml`.

## Server-side deploy script

Run on NAS from `~/apps/data-solution-2026` (app-only, no Docker required):

```bash
set -e
cd ~/apps/data-solution-2026
git fetch --all --tags
git checkout main
git pull origin main
# Optional poller smoke check only if Python is available:
# RUN_POLLER_CHECK=1 bash release/scripts/deploy-on-nas.sh
```

Optional automation on NAS:

- Cron every N minutes to run a deploy script after checking CI status manually.
- Systemd timer for controlled periodic pulls.
- Manual trigger from Cursor Remote SSH for full control.

## Auto trigger from Cursor on push

You can auto-trigger NAS deployment from this development environment right after each push to `main`.

How it works:

1. `post-push` hook starts a background script.
2. Script waits until the commit is visible on `origin/main`.
3. Script waits until GitHub Actions CI is successful for that commit.
4. Script runs a trigger command (typically SSH to NAS deploy script).

Scripts in this repo:

- `release/scripts/wait-and-trigger-pull.ps1`
- `release/scripts/post-push-hook.ps1`
- `release/scripts/install-post-push-hook.ps1`
- `release/scripts/deploy-on-nas.sh`

Setup:

1. Edit `release/scripts/post-push-hook.ps1` and set your NAS SSH command.
2. Install the Git hook once from repo root:

```powershell
powershell -ExecutionPolicy Bypass -File .\release\scripts\install-post-push-hook.ps1
```

Notes:

- The CI wait script uses `gh` CLI; run `gh auth login` in this environment.
- The watcher timeout and polling interval are configurable:
  - `-TimeoutMinutes` (default `20`)
  - `-PollSeconds` (default `15`)
- If CI fails, deployment is aborted automatically.
- `ntfy` is the default notification channel in the scripts.
- Default topic: `bas-data-solution-deploy`.
- Subscribe using app/web/CLI before first run, for example:

```bash
ntfy sub bas-data-solution-deploy
```

- Or in browser:
  - `https://ntfy.sh/bas-data-solution-deploy`
- Notification options in `wait-and-trigger-pull.ps1`:
  - `-NotifyMode ntfy` (default)
  - `-NotifyMode console`
  - `-NotifyMode toast` (Windows desktop toast via BurntToast module)
  - `-NotifyMode webhook` (POST JSON to `-WebhookUrl`, useful for Teams/Slack/ntfy)
  - `-NotifyMode both` (toast + webhook)

## Poller rollout merged into CI/CD

Use this sequence after NAS pull deploy is active:

1. Confirm runtime root is `data-solution-2026/` on NAS.
2. Configure Airflow variables for poller mode:
   - `poller_mapping_id=daily-temperature`
   - `poller_data_object_id=source/openmeteo/daily-temperature`
   - `poller_state_backend=postgres`
   - `poller_publish=stdout` for first smoke run, then `kafka`
3. Deploy DAG `openmeteo_data_object_poller` from `code/airflow/dags/` (paused on creation):
   - `catchup=false`
   - `max_active_runs=1`
   - retries/timeouts configured
4. Run command in DAG task:
   - `python -m extractor_and_poller.poller --mapping daily-temperature --state-backend postgres --publish kafka`
5. Trigger manual run and verify logs:
   - marker compare result (`data_object_change` or `data_object_unchanged`)
   - state persisted
   - publish status
6. Unpause schedule only after successful smoke validation.

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
      - [Meta data design](meta-data-design.md)
    - [Implementation plan (Open-Meteo → event orchestration)](../implementation-plan.md)
  - Extractor_And_Poller
    - Common
    - Openmeteo
      - Extractor
      - Poller
    - Poller
    - Tests
  - Infra
    - Airflow
      - Dags
    - Kafka
  - Release
    - Details
      - V2026.06.02.1
      - V2026.06.02.2
    - Notes
      - [Release v2026.06.02.1](../../release/notes/v2026.06.02.1.md)
      - [Release v2026.06.02.2](../../release/notes/v2026.06.02.2.md)
    - [Release <version>](../../release/release-notes-template.md)
  - Setting
  - Template
  - [Getting started](../../getting-started.md)
  - [Lessons learned](../../lessons-learned.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
