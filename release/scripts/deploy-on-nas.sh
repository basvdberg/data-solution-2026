#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="${APP_ROOT:-$HOME/apps/data-solution-2026}"
# Non-interactive SSH uses a minimal PATH; load git wrapper and tooling paths.
# shellcheck source=../../infra/scripts/nas-remote-env.sh
source "${APP_ROOT}/infra/scripts/nas-remote-env.sh"

# App-only deployment defaults (no Docker requirement):
# - Set APP_ROOT if your clone is not under ~/apps/data-solution-2026
# - Set RUN_POLLER_CHECK=1 to run optional Python poller smoke check
# - Set RUN_INFRA_SYNC=1 to sync infra/ to ~/apache-airflow and ~/kafka
RUN_POLLER_CHECK="${RUN_POLLER_CHECK:-0}"
RUN_INFRA_SYNC="${RUN_INFRA_SYNC:-0}"

cd "$APP_ROOT"
git fetch --all --tags
git checkout main
if [ -n "$(git status --porcelain)" ]; then
  echo "WARN: discarding local changes in ${APP_ROOT}"
  git status --short
fi
git reset --hard origin/main

echo "App-only deploy completed: $(git rev-parse --short HEAD) $(git log -1 --oneline)"

if [ "$RUN_INFRA_SYNC" = "1" ]; then
  bash "${APP_ROOT}/infra/scripts/deploy-infra-on-nas.sh"
fi

if [ "$RUN_POLLER_CHECK" = "1" ]; then
  if command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
  elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
  else
    echo "WARN: python/python3 not found; skipping poller smoke check."
    echo "NAS deploy completed."
    exit 0
  fi
  "$PYTHON_BIN" -m extractor_and_poller.poller --list
fi

echo "NAS deploy completed."
