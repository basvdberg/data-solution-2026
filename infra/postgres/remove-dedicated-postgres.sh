#!/usr/bin/env bash
# Stop and remove the legacy data-solution-postgres container after migrating to basnas_postgress.
#
# Usage:
#   bash infra/postgres/remove-dedicated-postgres.sh
#   DRY_RUN=1 bash infra/postgres/remove-dedicated-postgres.sh

set -euo pipefail

DOCKER="${DOCKER:-/share/CACHEDEV1_DATA/.qpkg/container-station/bin/docker}"
if ! command -v docker >/dev/null 2>&1 && [ -x "$DOCKER" ]; then
  export PATH="$(dirname "$DOCKER"):$PATH"
fi

CONTAINER="${LEGACY_CONTAINER:-data-solution-postgres}"
COMPOSE_DIR="${LEGACY_COMPOSE_DIR:-$HOME/data-solution-postgres}"
DRY_RUN="${DRY_RUN:-0}"

run() {
  if [ "$DRY_RUN" = "1" ]; then
    printf '[dry-run] '; printf '%q ' "$@"; printf '\n'
  else
    "$@"
  fi
}

if ! docker inspect "$CONTAINER" >/dev/null 2>&1; then
  echo "Container '${CONTAINER}' not running; nothing to remove."
  exit 0
fi

echo "Stopping legacy Postgres container '${CONTAINER}'..."
run docker stop "$CONTAINER"
run docker rm "$CONTAINER"

if [ -f "${COMPOSE_DIR}/docker-compose.yml" ]; then
  echo "WARN: ${COMPOSE_DIR}/docker-compose.yml still exists (no longer deployed from this repo)."
  echo "      Data volume is preserved at ${COMPOSE_DIR}/data if you need a manual backup."
fi

echo "Legacy dedicated Postgres removed. Use basnas_postgress on host port 5432."
