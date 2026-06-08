#!/usr/bin/env bash
# One-time copy of public.poller rows from data-solution-postgres -> basnas_postgress.
# Safe to re-run when the target table is empty, or with FORCE=1 to append.
#
# Usage:
#   bash infra/postgres/migrate-poller-from-dedicated-postgres.sh
#   FORCE=1 bash infra/postgres/migrate-poller-from-dedicated-postgres.sh

set -euo pipefail

DOCKER="${DOCKER:-/share/CACHEDEV1_DATA/.qpkg/container-station/bin/docker}"
if ! command -v docker >/dev/null 2>&1 && [ -x "$DOCKER" ]; then
  export PATH="$(dirname "$DOCKER"):$PATH"
fi

SOURCE_CONTAINER="${SOURCE_CONTAINER:-data-solution-postgres}"
TARGET_CONTAINER="${POSTGRES_CONTAINER:-basnas_postgress}"
APP_DB="${DATA_SOLUTION_DB:-data-solution-2026}"
FORCE="${FORCE:-0}"

POSTGRES_DEST="${POSTGRES_DEST:-$HOME/data-solution-postgres}"
ENV_FILE="${ENV_FILE:-${POSTGRES_DEST}/.env}"
if [ -f "$ENV_FILE" ]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

ADMIN_USER="${POSTGRES_USER:-postgres}"
ADMIN_PASSWORD="${POSTGRES_PASSWORD:-}"

psql_in() {
  local container=$1
  shift
  if [ -n "$ADMIN_PASSWORD" ]; then
    docker exec -i -e PGPASSWORD="$ADMIN_PASSWORD" "$container" \
      psql -v ON_ERROR_STOP=1 -U "$ADMIN_USER" -d "$APP_DB" "$@"
  else
    docker exec -i "$container" \
      psql -v ON_ERROR_STOP=1 -U "$ADMIN_USER" -d "$APP_DB" "$@"
  fi
}

container_running() {
  docker inspect "$1" >/dev/null 2>&1
}

if ! container_running "$SOURCE_CONTAINER"; then
  echo "Source container '${SOURCE_CONTAINER}' not found; nothing to migrate."
  exit 0
fi

if ! container_running "$TARGET_CONTAINER"; then
  echo "ERROR: target container '${TARGET_CONTAINER}' not found." >&2
  exit 1
fi

source_count="$(
  psql_in "$SOURCE_CONTAINER" -tAc "select count(*) from public.poller" | tr -d '[:space:]'
)"
target_count="$(
  psql_in "$TARGET_CONTAINER" -tAc "select coalesce((select 1 from information_schema.tables where table_schema='public' and table_name='poller'), 0)" | tr -d '[:space:]'
)"

if [ "$target_count" = "1" ]; then
  target_rows="$(
    psql_in "$TARGET_CONTAINER" -tAc "select count(*) from public.poller" | tr -d '[:space:]'
  )"
else
  target_rows="0"
fi

if [ "${source_count:-0}" = "0" ]; then
  echo "Source public.poller is empty; migration skipped."
  exit 0
fi

if [ "${target_rows:-0}" != "0" ] && [ "$FORCE" != "1" ]; then
  echo "Target public.poller already has ${target_rows} row(s). Set FORCE=1 to copy anyway."
  exit 0
fi

echo "Copying ${source_count} row(s) from ${SOURCE_CONTAINER} to ${TARGET_CONTAINER}..."

dump_file="$(mktemp)"
trap 'rm -f "$dump_file"' EXIT

docker exec -e PGPASSWORD="$ADMIN_PASSWORD" "$SOURCE_CONTAINER" \
  pg_dump -U "$ADMIN_USER" -d "$APP_DB" -t public.poller --data-only --column-inserts >"$dump_file"

psql_in "$TARGET_CONTAINER" <"$dump_file"

final_count="$(
  psql_in "$TARGET_CONTAINER" -tAc "select count(*) from public.poller" | tr -d '[:space:]'
)"
echo "Migration finished. Target public.poller row count: ${final_count}"
