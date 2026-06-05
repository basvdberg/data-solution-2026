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

Releases are automated when you commit and push on `main`:

1. **Pre-commit** (`cursor-config` → `pre_commit.py` → `release/scripts/new-release.ps1`):
   - Bumps `release/VERSION` (`vYYYY.MM.DD.N`, same-day `N` increments).
   - Scaffolds `release/notes/<version>.md` and `release/details/<version>/`.
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
gh release create vYYYY.MM.DD.N --notes-file release/notes/vYYYY.MM.DD.N.md
```

## Deploy model without GitHub to NAS access

GitHub-hosted runners usually cannot reach a LAN-only NAS. Deployment stays **pull-based** on the NAS, triggered after green CI:

1. Push commit to `main` → GitHub Actions notifies via **ntfy**, runs tests, publishes release.
2. **pre-push deploy hook** (from your dev machine on the LAN) waits for CI green, then SSH-runs `deploy-on-nas.sh`.
3. NAS updates to latest `origin/main` and applies runtime actions (Airflow DAG refresh, optional `RUN_INFRA_SYNC=1`).

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
```

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

Use this sequence after NAS pull deploy is active:

1. Confirm runtime root is `data-solution-2026/` on NAS.
2. Configure Airflow variables for poller mode:
   - `poller_mapping_id=daily-temperature`
   - `poller_data_object_id=source/openmeteo/daily-temperature`
   - `poller_publish=stdout` for first smoke run, then `kafka`
3. Deploy DAG `openmeteo_data_object_poller` from `code/airflow/dags/` (paused on creation):
   - `catchup=false`
   - `max_active_runs=1`
   - retries/timeouts configured
4. Run command in DAG task:
   - `python -m extractor_and_poller.poller --data-object source/openmeteo/daily-temperature --publish kafka`
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
      - Plugins
    - Extractor_And_Poller
      - Common
      - Openmeteo
        - Extractor
        - Poller
      - Poller
      - Tests
    - Postgres
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
  - Infra
    - Airflow
      - Dags
    - Kafka
    - Postgres
  - Release
    - Details
      - V2026.06.02.1
      - V2026.06.02.2
      - V2026.06.03.1
      - V2026.06.03.2
      - V2026.06.03.3
      - V2026.06.03.4
      - V2026.06.04.1
      - V2026.06.04.2
      - V2026.06.04.3
      - V2026.06.04.4
      - V2026.06.04.5
      - V2026.06.04.6
      - V2026.06.04.7
      - V2026.06.04.8
      - V2026.06.04.9
      - V2026.06.05.1
      - V2026.06.05.2
      - V2026.06.05.3
      - V2026.06.05.4
      - V2026.06.05.5
    - Notes
      - [Release v2026.06.02.1](../../release/notes/v2026.06.02.1.md)
      - [Release v2026.06.02.2](../../release/notes/v2026.06.02.2.md)
      - [Release v2026.06.03.1](../../release/notes/v2026.06.03.1.md)
      - [Release v2026.06.03.2](../../release/notes/v2026.06.03.2.md)
      - [Release v2026.06.03.3](../../release/notes/v2026.06.03.3.md)
      - [Release v2026.06.03.4](../../release/notes/v2026.06.03.4.md)
      - [V2026.06.04.1](../../release/notes/v2026.06.04.1.md)
      - [V2026.06.04.2](../../release/notes/v2026.06.04.2.md)
      - [V2026.06.04.3](../../release/notes/v2026.06.04.3.md)
      - [V2026.06.04.4](../../release/notes/v2026.06.04.4.md)
      - [V2026.06.04.5](../../release/notes/v2026.06.04.5.md)
      - [V2026.06.04.6](../../release/notes/v2026.06.04.6.md)
      - [V2026.06.04.7](../../release/notes/v2026.06.04.7.md)
      - [V2026.06.04.8](../../release/notes/v2026.06.04.8.md)
      - [V2026.06.04.9](../../release/notes/v2026.06.04.9.md)
      - [V2026.06.05.1](../../release/notes/v2026.06.05.1.md)
      - [V2026.06.05.2](../../release/notes/v2026.06.05.2.md)
      - [V2026.06.05.3](../../release/notes/v2026.06.05.3.md)
      - [V2026.06.05.4](../../release/notes/v2026.06.05.4.md)
      - [V2026.06.05.5](../../release/notes/v2026.06.05.5.md)
    - [Release <version>](../../release/release-notes-template.md)
  - Setting
  - Template
  - [Getting started](../../getting-started.md)
  - [Lessons learned](../../lessons-learned-part1.md)
  - [Lessons learned (part 2)](../../lessons-learned-part2.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
