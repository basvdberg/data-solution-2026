#!/usr/bin/env bash
# Create (or update) the application Postgres role for data-solution-2026.
#
# Usage (on host with Docker, e.g. BasNAS):
#   bash infra/postgres/create-app-user.sh
#   POSTGRES_DEST=~/data-solution-postgres bash infra/postgres/create-app-user.sh
#
# Reads POSTGRES_* and DATA_SOLUTION_APP_* from ${POSTGRES_DEST}/.env when present.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
POSTGRES_DEST="${POSTGRES_DEST:-$HOME/data-solution-postgres}"
ENV_FILE="${ENV_FILE:-${POSTGRES_DEST}/.env}"
CONTAINER="${POSTGRES_CONTAINER:-data-solution-postgres}"
APP_USER="${DATA_SOLUTION_APP_USER:-data-solution-2026_app}"
APP_DB="${DATA_SOLUTION_DB:-${POSTGRES_DB:-data-solution-2026}}"
GRANT_SQL="${GRANT_SQL:-${REPO_ROOT}/code/postgres/grant-app-user.sql}"

if [ -f "$ENV_FILE" ]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

ADMIN_USER="${POSTGRES_USER:-postgres}"
ADMIN_PASSWORD="${POSTGRES_PASSWORD:-}"
APP_PASSWORD="${DATA_SOLUTION_APP_PASSWORD:-}"

if [ -z "$APP_PASSWORD" ]; then
  if command -v openssl >/dev/null 2>&1; then
    APP_PASSWORD="$(openssl rand -base64 24 | tr -d '/+=' | head -c 32)"
  else
    APP_PASSWORD="$(tr -dc 'A-Za-z0-9' </dev/urandom | head -c 32)"
  fi
  echo "Generated DATA_SOLUTION_APP_PASSWORD (add to ${ENV_FILE} and Airflow .env)."
fi

if ! docker inspect "$CONTAINER" >/dev/null 2>&1; then
  echo "ERROR: container '${CONTAINER}' not found. Start Postgres first." >&2
  exit 1
fi

if [ ! -f "$GRANT_SQL" ]; then
  echo "ERROR: missing grant SQL at ${GRANT_SQL}" >&2
  exit 1
fi

psql_admin() {
  if [ -n "$ADMIN_PASSWORD" ]; then
    docker exec -i -e PGPASSWORD="$ADMIN_PASSWORD" "$CONTAINER" \
      psql -v ON_ERROR_STOP=1 -U "$ADMIN_USER" -d "$APP_DB" "$@"
  else
    docker exec -i "$CONTAINER" \
      psql -v ON_ERROR_STOP=1 -U "$ADMIN_USER" -d "$APP_DB" "$@"
  fi
}

escape_sql_literal() {
  printf '%s' "$1" | sed "s/'/''/g"
}

sql_quote_ident() {
  printf '"%s"' "${1//\"/\"\"}"
}

APP_USER_LITERAL="$(escape_sql_literal "$APP_USER")"
role_exists="$(
  psql_admin -tAc "select 1 from pg_roles where rolname = '${APP_USER_LITERAL}'" | tr -d '[:space:]'
)"

APP_PASSWORD_SQL="$(escape_sql_literal "$APP_PASSWORD")"
APP_USER_IDENT="$(sql_quote_ident "$APP_USER")"

if [ "$role_exists" = "1" ]; then
  echo "Role ${APP_USER} exists; updating password and grants."
  psql_admin -c "alter role ${APP_USER_IDENT} with login password '${APP_PASSWORD_SQL}';"
else
  echo "Creating role ${APP_USER}."
  psql_admin -c "create role ${APP_USER_IDENT} with login password '${APP_PASSWORD_SQL}';"
fi

psql_admin <"$GRANT_SQL"

update_env_var() {
  local file=$1 key=$2 value=$3
  if [ ! -f "$file" ]; then
    return 0
  fi
  if grep -q "^${key}=" "$file" 2>/dev/null; then
    if [ "${UPDATE_ENV:-0}" = "1" ]; then
      sed -i "s|^${key}=.*|${key}=${value}|" "$file"
      echo "Updated ${key} in ${file}"
    fi
  else
    printf '\n%s=%s\n' "$key" "$value" >>"$file"
    echo "Appended ${key} to ${file}"
  fi
}

update_env_var "$ENV_FILE" "DATA_SOLUTION_APP_USER" "$APP_USER"
update_env_var "$ENV_FILE" "DATA_SOLUTION_APP_PASSWORD" "$APP_PASSWORD"

AIRFLOW_ENV="${AIRFLOW_ENV:-$HOME/apache-airflow/.env}"
update_env_var "$AIRFLOW_ENV" "POSTGRES_USER" "$APP_USER"
if [ "${UPDATE_ENV:-0}" = "1" ]; then
  update_env_var "$AIRFLOW_ENV" "POSTGRES_PASSWORD" "$APP_PASSWORD"
else
  update_env_var "$AIRFLOW_ENV" "DATA_SOLUTION_APP_PASSWORD" "$APP_PASSWORD"
fi

echo "Application user ready: ${APP_USER} on database ${APP_DB}"
echo "Set POSTGRES_USER=${APP_USER} and POSTGRES_PASSWORD in Airflow .env if not already."
