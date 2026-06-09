#!/usr/bin/env bash
# Read release/deploy-config.json on NAS (no jq required).
# Usage: read-deploy-config.sh [key]
#   key: sync_infra | run_db_migrations | paths | reason | version (default: sync_infra)
set -euo pipefail

APP_ROOT="${APP_ROOT:-$HOME/apps/data-solution-2026}"
CONFIG="${DEPLOY_CONFIG:-$APP_ROOT/release/deploy-config.json}"
KEY="${1:-sync_infra}"

if [ ! -f "$CONFIG" ]; then
  if [ "$KEY" = "sync_infra" ]; then
    echo "false"
  fi
  exit 0
fi

_read_python() {
  local py=$1
  "$py" - "$CONFIG" "$KEY" <<'PY'
import json
import sys

path, key = sys.argv[1], sys.argv[2]
with open(path, encoding="utf-8") as f:
    data = json.load(f)

if key == "sync_infra":
    print("true" if data.get("sync_infra") else "false")
elif key == "run_db_migrations":
    print("true" if data.get("run_db_migrations") else "false")
elif key == "paths":
    for p in data.get("paths") or []:
        print(p)
elif key == "reason":
    print(data.get("reason") or "")
elif key == "version":
    print(data.get("version") or "")
else:
    print(data.get(key, ""))
PY
}

if command -v python3 >/dev/null 2>&1; then
  _read_python python3
elif command -v python >/dev/null 2>&1; then
  _read_python python
elif [ "$KEY" = "sync_infra" ]; then
  if grep -qE '"sync_infra"[[:space:]]*:[[:space:]]*true' "$CONFIG"; then
    echo "true"
  else
    echo "false"
  fi
else
  echo "WARN: python not found; only sync_infra is supported via grep fallback" >&2
  exit 1
fi
