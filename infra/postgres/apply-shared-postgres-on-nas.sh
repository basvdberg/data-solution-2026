#!/usr/bin/env bash
# One-time NAS cutover: basnas_postgress replaces data-solution-postgres.
# Run on BasNAS after pulling infra changes:
#   bash infra/postgres/apply-shared-postgres-on-nas.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
DOCKER="${DOCKER:-/share/CACHEDEV1_DATA/.qpkg/container-station/bin/docker}"
export PATH="${HOME}/.local/bin:${PATH}"

AF_ENV="${AIRFLOW_ENV:-${HOME}/apache-airflow/.env}"
PG_ENV="${ENV_FILE:-${HOME}/data-solution-postgres/.env}"

if ! command -v docker >/dev/null 2>&1; then
  if [ -x "$DOCKER" ]; then
    export PATH="$(dirname "$DOCKER"):$PATH"
  fi
fi

BASNAS_PG_PW="$(
  docker inspect basnas_postgress 2>/dev/null | grep -o 'POSTGRES_PASSWORD=[^,"]*' | head -1 | cut -d= -f2-
)"
if [ -z "$BASNAS_PG_PW" ]; then
  echo "ERROR: could not read POSTGRES_PASSWORD from basnas_postgress container." >&2
  exit 1
fi

APP_PW="$(grep -E '^POSTGRES_PASSWORD=' "$AF_ENV" 2>/dev/null | tail -1 | cut -d= -f2- || true)"
if [ -z "$APP_PW" ]; then
  APP_PW="$(grep -E '^DATA_SOLUTION_APP_PASSWORD=' "$AF_ENV" 2>/dev/null | tail -1 | cut -d= -f2- || true)"
fi

mkdir -p "$(dirname "$PG_ENV")"
touch "$PG_ENV"
grep -q '^POSTGRES_CONTAINER=' "$PG_ENV" 2>/dev/null || printf '\nPOSTGRES_CONTAINER=basnas_postgress\n' >>"$PG_ENV"
if grep -q '^POSTGRES_PASSWORD=' "$PG_ENV"; then
  sed -i "s|^POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=${BASNAS_PG_PW}|" "$PG_ENV"
else
  printf 'POSTGRES_PASSWORD=%s\n' "$BASNAS_PG_PW" >>"$PG_ENV"
fi
sed -i '/^POSTGRES_HOST_PORT=/d' "$PG_ENV" 2>/dev/null || true

if grep -q '^POSTGRES_HOST=' "$AF_ENV"; then
  sed -i 's|^POSTGRES_HOST=.*|POSTGRES_HOST=basnas_postgress:5432|' "$AF_ENV"
else
  printf 'POSTGRES_HOST=basnas_postgress:5432\n' >>"$AF_ENV"
fi
grep -q '^POSTGRES_DOCKER_NETWORK=' "$AF_ENV" || printf 'POSTGRES_DOCKER_NETWORK=immich_default\n' >>"$AF_ENV"

cd "$APP_ROOT"
ENV_FILE="$PG_ENV" POSTGRES_CONTAINER=basnas_postgress DATA_SOLUTION_APP_PASSWORD="$APP_PW" \
  bash infra/postgres/create-app-user.sh
bash infra/postgres/migrate-poller-from-dedicated-postgres.sh

cd "${HOME}/apache-airflow"
docker compose -f docker-compose.standalone.yaml up -d

docker exec basnas_postgress psql -U postgres -d data-solution-2026 \
  -c 'SELECT count(*) AS poller_rows FROM public.poller;'
bash "${APP_ROOT}/infra/postgres/remove-dedicated-postgres.sh"
echo "Shared Postgres cutover completed."
