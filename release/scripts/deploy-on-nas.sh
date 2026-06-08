#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="${APP_ROOT:-$HOME/apps/data-solution-2026}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Non-interactive SSH uses a minimal PATH; load git wrapper and tooling paths.
# shellcheck source=../../infra/scripts/nas-remote-env.sh
source "${APP_ROOT}/infra/scripts/nas-remote-env.sh"

# App-only deployment defaults (no Docker requirement):
# - Set APP_ROOT if your clone is not under ~/apps/data-solution-2026
# - Set RUN_POLLER_CHECK=1 to run optional Python poller smoke check
# - Set RUN_INFRA_SYNC=1 to force infra sync (overrides release/deploy-config.json)
# - release/deploy-config.json: sync_infra set automatically when infra/ runtime files change
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

echo "App deploy completed: $(git rev-parse --short HEAD) $(git log -1 --oneline)"

if [ "$RUN_INFRA_SYNC" != "1" ]; then
  if [ -x "${SCRIPT_DIR}/read-deploy-config.sh" ]; then
    config_sync="$("${SCRIPT_DIR}/read-deploy-config.sh" sync_infra)"
    if [ "$config_sync" = "true" ]; then
      RUN_INFRA_SYNC=1
      config_reason="$("${SCRIPT_DIR}/read-deploy-config.sh" reason)"
      echo "deploy-config: sync_infra=true — ${config_reason}"
    fi
  elif [ -f "${APP_ROOT}/release/deploy-config.json" ]; then
    if grep -qE '"sync_infra"[[:space:]]*:[[:space:]]*true' "${APP_ROOT}/release/deploy-config.json"; then
      RUN_INFRA_SYNC=1
      echo "deploy-config: sync_infra=true (grep fallback)"
    fi
  fi
fi

if [ "$RUN_INFRA_SYNC" = "1" ]; then
  echo "Running infra sync (deploy-infra-on-nas.sh)..."
  bash "${APP_ROOT}/infra/scripts/deploy-infra-on-nas.sh"
else
  echo "Infra sync skipped (deploy-config sync_infra=false; set RUN_INFRA_SYNC=1 to force)."
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
