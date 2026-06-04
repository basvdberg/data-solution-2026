#!/usr/bin/env bash
# One-time rename: data_solution -> data-solution-2026 (database and app role).
# Safe to re-run; skips when the new names already exist.
#
# Usage (BasNAS or any host with the Postgres container):
#   bash infra/postgres/migrate-database-name.sh

set -euo pipefail

POSTGRES_DEST="${POSTGRES_DEST:-$HOME/data-solution-postgres}"
ENV_FILE="${ENV_FILE:-${POSTGRES_DEST}/.env}"
CONTAINER="${POSTGRES_CONTAINER:-data-solution-postgres}"
OLD_DB="data_solution"
NEW_DB="data-solution-2026"
OLD_USER="data_solution_app"
NEW_USER="data-solution-2026_app"

if [ -f "$ENV_FILE" ]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

ADMIN_USER="${POSTGRES_USER:-postgres}"
ADMIN_PASSWORD="${POSTGRES_PASSWORD:-}"

if ! docker inspect "$CONTAINER" >/dev/null 2>&1; then
  echo "ERROR: container '${CONTAINER}' not found." >&2
  exit 1
fi

psql_admin() {
  if [ -n "$ADMIN_PASSWORD" ]; then
    docker exec -i -e PGPASSWORD="$ADMIN_PASSWORD" "$CONTAINER" \
      psql -v ON_ERROR_STOP=1 -U "$ADMIN_USER" "$@"
  else
    docker exec -i "$CONTAINER" psql -v ON_ERROR_STOP=1 -U "$ADMIN_USER" "$@"
  fi
}

db_exists() {
  psql_admin -d postgres -tAc "select 1 from pg_database where datname = '$1'" | tr -d '[:space:]'
}

role_exists() {
  psql_admin -d postgres -tAc "select 1 from pg_roles where rolname = '$1'" | tr -d '[:space:]'
}

if [ "$(db_exists "$OLD_DB")" = "1" ] && [ "$(db_exists "$NEW_DB")" != "1" ]; then
  echo "Renaming database ${OLD_DB} -> ${NEW_DB}"
  psql_admin -d postgres -c "alter database ${OLD_DB} rename to \"${NEW_DB}\";"
else
  echo "Database rename skipped (old missing or new already present)."
fi

if [ "$(role_exists "$OLD_USER")" = "1" ] && [ "$(role_exists "$NEW_USER")" != "1" ]; then
  echo "Renaming role ${OLD_USER} -> ${NEW_USER}"
  psql_admin -d postgres -c "alter role ${OLD_USER} rename to \"${NEW_USER}\";"
else
  echo "Role rename skipped (old missing or new already present)."
fi

echo "Migration finished."
echo "Update ${ENV_FILE}: POSTGRES_DB=${NEW_DB}, DATA_SOLUTION_APP_USER=${NEW_USER} (keep POSTGRES_USER=postgres)."
echo "Update Airflow .env: POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD. Then run create-app-user.sh."
