# CI/CD workflow (local + NAS)

## Table of contents

<!-- markdown-toc:start -->
- [Design patterns](#design-patterns)
- [Goal](#goal)
- [CI/CD model](#cicd-model)
- [Prerequisites](#prerequisites)
- [Local development in Cursor](#local-development-in-cursor)
  - [1) Create a feature branch](#1-create-a-feature-branch)
  - [2) Develop locally](#2-develop-locally)
  - [3) Push and open PR](#3-push-and-open-pr)
- [Test on NAS using Cursor Remote SSH](#test-on-nas-using-cursor-remote-ssh)
  - [1) Open NAS workspace in Cursor](#1-open-nas-workspace-in-cursor)
  - [2) Sync branch or release candidate](#2-sync-branch-or-release-candidate)
  - [3) Run NAS-specific tests](#3-run-nas-specific-tests)
  - [4) Validate logs and side effects](#4-validate-logs-and-side-effects)
- [Deploy release to NAS](#deploy-release-to-nas)
  - [1) Prepare and push release tag from laptop](#1-prepare-and-push-release-tag-from-laptop)
  - [2) Update NAS clone to the release](#2-update-nas-clone-to-the-release)
  - [3) Apply release actions](#3-apply-release-actions)
  - [4) Verify deployment](#4-verify-deployment)
- [Rollback](#rollback)
- [Operational notes](#operational-notes)
<!-- markdown-toc:end -->

## Design patterns

CI/CD workflow for this repo. Pattern definitions: [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns/blob/main/readme.md#purpose).

- [Separate what and how](https://github.com/basvdberg/data-engineering-design-patterns/blob/main/design-patterns/generic/separate-what-and-how.md) — Git metadata is deployed; runtime code and DAGs implement *how* on NAS.
- [Simplicity](https://github.com/basvdberg/data-engineering-design-patterns/blob/main/design-patterns/generic/simplicity.md) — manual tag-and-clone deploy before full automation.

## Goal

Use a simple CI/CD loop where development happens locally in Cursor, validation happens both locally and on NAS, releases are deployed to NAS from tagged Git commits.

## CI/CD model

- **Local machine (Cursor)**: write and review code, run fast unit checks, prepare release.
- **Git remote**: source of truth for branches, pull requests, and release tags.
- **NAS (runtime)**: integration testing and deployment target.

## Prerequisites

- NAS has `git`, Python, and runtime dependencies installed.
- A deployment folder exists on NAS, for example `~/apps/data-solution-2026`.
- Secrets are stored on NAS in `.env` (or a secret manager), never committed to Git.
- Cursor Remote SSH is configured for your NAS host.

## Local development in Cursor

### 1) Create a feature branch

```bash
git checkout main
git pull
git checkout -b feat/<short-topic>
```

### 2) Develop locally

- Implement changes in Cursor on your laptop.
- Keep commits small and focused.
- Run fast local checks before pushing.

Example:

```bash
python -m pytest -q
```

### 3) Push and open PR

```bash
git push -u origin feat/<short-topic>
```

Create a pull request and wait for CI to pass.

## Test on NAS using Cursor Remote SSH

### 1) Open NAS workspace in Cursor

- Connect to NAS using Cursor Remote SSH.
- Open `~/apps/data-solution-2026` (or your NAS clone path).

### 2) Sync branch or release candidate

```bash
cd ~/apps/data-solution-2026
git fetch --all --tags
git checkout feat/<short-topic>
git pull
```

### 3) Run NAS-specific tests

Run integration checks that need NAS services, network, storage, or scheduler behavior.

Example:

```bash
python -m pytest -m integration -q
```

### 4) Validate logs and side effects

- Check service logs.
- Confirm outputs were written where expected.
- Validate one end-to-end data flow (extract -> stage -> map).

## Deploy release to NAS

### 1) Prepare and push release tag from laptop

```bash
git checkout main
git pull
git tag -a vYYYY.MM.DD.N -m "Release vYYYY.MM.DD.N"
git push origin main --tags
```

### 2) Update NAS clone to the release

```bash
cd ~/apps/data-solution-2026
git fetch --all --tags
git checkout vYYYY.MM.DD.N
```

### 3) Apply release actions

- Run required database/schema migration steps.
- Ensure NAS `.env` has production values.
- Restart services.

If you use Docker Compose:

```bash
docker compose pull
docker compose up -d
```

### 4) Verify deployment

- Confirm all services are healthy.
- Run one smoke pipeline run.
- Check logs for startup/runtime errors.

## Rollback

If verification fails, switch to the previous known-good tag and restart services:

```bash
git checkout <previous-tag>
docker compose up -d
```

## Operational notes

- Do not edit release code manually on NAS; use Git branches/tags.
- Keep release notes with migration and restart steps.
- Keep tags consistent for traceability.
- Never expose internal service ports publicly; use VPN or SSH.

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](../../readme.md)
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
      - [CI/CD workflow (local + NAS)](ci-cd.md)
      - [Event-based orchestration plan (single data object)](event-based-orchestration-plan.md)
      - [Meta data design](meta-data-design.md)
  - Extractor_And_Poller
    - Common
    - Openmeteo
      - Extractor
      - Poller
    - Poller
    - Tests
  - Setting
  - Template
  - [Getting started](../../getting-started.md)
  - [Lessons learned](../../lessons-learned.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
