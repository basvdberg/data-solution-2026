#!/usr/bin/env bash
# Apply code/postgres/migrations/*.sql when the matching *.check.sql says they apply
# and the migration id is not yet recorded in schema_migrations.
#
# Usage (on BasNAS after app deploy):
#   bash infra/postgres/run-applicable-migrations.sh
#   POSTGRES_DEST=~/data-solution-postgres bash infra/postgres/run-applicable-migrations.sh
#
# Opt out: RUN_DB_MIGRATIONS=0 bash release/scripts/deploy-on-nas.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
POSTGRES_DEST="${POSTGRES_DEST:-$HOME/data-solution-postgres}"
ENV_FILE="${ENV_FILE:-${POSTGRES_DEST}/.env}"
CONTAINER="${POSTGRES_CONTAINER:-basnas_postgress}"
APP_DB="${DATA_SOLUTION_DB:-${POSTGRES_DB:-data-solution-2026}}"
MIGRATIONS_DIR="${MIGRATIONS_DIR:-${REPO_ROOT}/code/postgres/migrations}"
MANIFEST="${MANIFEST:-${MIGRATIONS_DIR}/manifest.txt}"
DRY_RUN="${DRY_RUN:-0}"

if [ -f "$ENV_FILE" ]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

ADMIN_USER="${POSTGRES_USER:-postgres}"
ADMIN_PASSWORD="${POSTGRES_PASSWORD:-}"

psql_admin() {
  if [ -n "$ADMIN_PASSWORD" ]; then
    docker exec -i -e PGPASSWORD="$ADMIN_PASSWORD" "$CONTAINER" \
      psql -v ON_ERROR_STOP=1 -U "$ADMIN_USER" -d "$APP_DB" "$@"
  else
    docker exec -i "$CONTAINER" \
      psql -v ON_ERROR_STOP=1 -U "$ADMIN_USER" -d "$APP_DB" "$@"
  fi
}

psql_scalar() {
  psql_admin -tAc "$1" | tr -d '[:space:]'
}

if ! docker inspect "$CONTAINER" >/dev/null 2>&1; then
  echo "Postgres container '${CONTAINER}' not found; skipping DB migrations."
  exit 0
fi

if [ "$(psql_scalar "select 1 from pg_database where datname = '${APP_DB}'")" != "1" ]; then
  echo "Database '${APP_DB}' not found; skipping DB migrations (run create-app-user.sh first)."
  exit 0
fi

if [ ! -d "$MIGRATIONS_DIR" ] || [ ! -f "$MANIFEST" ]; then
  echo "No migrations manifest at ${MANIFEST}; skipping DB migrations."
  exit 0
fi

echo "Ensuring schema_migrations table"
if [ "$DRY_RUN" = "1" ]; then
  echo "[dry-run] would create schema_migrations if missing"
else
  psql_admin <<'SQL'
create table if not exists schema_migrations (
    version text primary key,
    applied_at_utc timestamptz not null default now()
);
SQL
fi

applied=0
skipped=0

while IFS= read -r line || [ -n "$line" ]; do
  version="${line%%#*}"
  version="$(printf '%s' "$version" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
  [ -z "$version" ] && continue
  if ! printf '%s' "$version" | grep -Eq '^[0-9]{3}-[a-z0-9-]+$'; then
    echo "ERROR: invalid migration id in manifest: ${version}" >&2
    exit 1
  fi

  sql_file="${MIGRATIONS_DIR}/${version}.sql"
  check_file="${MIGRATIONS_DIR}/${version}.check.sql"

  if [ ! -f "$sql_file" ]; then
    echo "ERROR: missing migration SQL for ${version}: ${sql_file}" >&2
    exit 1
  fi
  if [ ! -f "$check_file" ]; then
    echo "ERROR: missing applicability check for ${version}: ${check_file}" >&2
    exit 1
  fi

  already="$(psql_scalar "select coalesce((select 1 from schema_migrations where version = '${version}'), 0)")"
  if [ "$already" = "1" ]; then
    echo "Migration ${version}: already applied — skipped"
    skipped=$((skipped + 1))
    continue
  fi

  applicable="$(psql_admin <"$check_file" | tr -d '[:space:]')"
  if [ -z "$applicable" ]; then
    echo "Migration ${version}: not applicable — skipped"
    skipped=$((skipped + 1))
    continue
  fi

  echo "Migration ${version}: applying ${sql_file}"
  if [ "$DRY_RUN" = "1" ]; then
    echo "[dry-run] would apply ${sql_file} and record ${version}"
    applied=$((applied + 1))
    continue
  fi

  psql_admin <"$sql_file"
  psql_admin -c "insert into schema_migrations (version) values ('${version}');"
  applied=$((applied + 1))
done <"$MANIFEST"

echo "DB migrations finished: applied=${applied} skipped=${skipped}"
