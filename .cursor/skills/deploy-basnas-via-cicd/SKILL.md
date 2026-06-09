---
name: deploy-basnas-via-cicd
description: >-
  Deploy this repo to local server: commit and push to main; GitHub Actions runs tests
  and release; the pre-push hook deploys to NAS after CI succeeds. Use when the
  user wants changes on local server, NAS deploy, production rollout, or after finishing
  implementation—do not SSH git pull unless CI/CD failed or asked manually.
---

# Deploy to local server via CI/CD

**Agents:** after code or doc changes that should reach local server, **commit and push to `main` yourself** (unless the user forbids commits). Do not ask the user to deploy manually. Do not SSH to local server for routine deploys.

## Agent deploy steps

1. **Commit** on `main` (pre-commit may bump `release/VERSION` and scaffold release notes).
2. **`git push origin main`**.
3. Tell the user to watch ntfy topic `data-solution-2026-deploy` (or GitHub Actions) for CI and NAS deploy status—do not instruct them to run `git pull` or `deploy-on-nas.sh` on the NAS.

## What runs automatically

| Step | Where |
|------|--------|
| Tests + GitHub release | GitHub Actions (`.github/workflows/deploy-main.yml`) |
| `git pull` on NAS | `release/scripts/deploy-on-nas.sh` via `cursor-config/githooks/pre-push` |

DAGs and app code are bind-mounted from `~/apps/data-solution-2026`; no manual copy to Airflow.

## One-time hook verify

```powershell
powershell -ExecutionPolicy Bypass -File .\release\scripts\install-post-push-hook.ps1
```

Needs `gh auth login` and `ssh $LOCAL_SERVER_SSH` (`docker -v` works bare after **basnas-ssh** setup).

## Infra compose changes

If `infra/` changed, after deploy run on NAS:

```bash
RUN_INFRA_SYNC=1 bash ~/apps/data-solution-2026/release/scripts/deploy-on-nas.sh
```

## More detail

- [CI/CD workflow](../../doc/design/ci-cd.md)
- [Implementation plan](../../doc/implementation-plan.md)
- Personal skill (same rules): `deploy-data-solution-basnas` in `~/.cursor/skills/`
