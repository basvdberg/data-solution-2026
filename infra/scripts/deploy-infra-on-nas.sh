#!/usr/bin/env bash
# Sync infra/ compose files to legacy BasNAS paths and optionally restart stacks.
# Airflow DAGs are not copied: compose mounts ${DATA_SOLUTION_ROOT}/code/airflow/dags.
#
# Usage (on NAS):
#   bash infra/scripts/deploy-infra-on-nas.sh
#
# Environment:
#   APP_ROOT          Repo clone (default: ~/apps/data-solution-2026)
#   AIRFLOW_DEST      Legacy Airflow folder (default: ~/apache-airflow)
#   KAFKA_DEST        Legacy Kafka folder (default: ~/kafka)
#   POSTGRES_DEST     Legacy Postgres folder (default: ~/data-solution-postgres)
#   RUN_COMPOSE       1 = docker compose up -d after sync (default: 1)
#   DRY_RUN           1 = print actions only (default: 0)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=nas-remote-env.sh
source "${SCRIPT_DIR}/nas-remote-env.sh"

APP_ROOT="${APP_ROOT:-$HOME/apps/data-solution-2026}"
AIRFLOW_DEST="${AIRFLOW_DEST:-$HOME/apache-airflow}"
KAFKA_DEST="${KAFKA_DEST:-$HOME/kafka}"
POSTGRES_DEST="${POSTGRES_DEST:-$HOME/data-solution-postgres}"
RUN_COMPOSE="${RUN_COMPOSE:-1}"
DRY_RUN="${DRY_RUN:-0}"

# nas-remote-env.sh already extends PATH for git wrapper + Container Station.

INFRA="${APP_ROOT}/infra"
APP_ABS="$(cd "$APP_ROOT" && pwd)"

run() {
  if [ "$DRY_RUN" = "1" ]; then
    printf '[dry-run] '; printf '%q ' "$@"; printf '\n'
  else
    "$@"
  fi
}

copy_file() {
  local src=$1 dest=$2
  if [ ! -f "$src" ]; then
    echo "ERROR: missing source file: $src" >&2
    exit 1
  fi
  run mkdir -p "$(dirname "$dest")"
  run cp -p "$src" "$dest"
  echo "Synced: $dest"
}

ensure_airflow_env() {
  local env_file="${AIRFLOW_DEST}/.env"
  if [ ! -f "$env_file" ]; then
    echo "Creating ${env_file} from .env.example"
    if [ "$DRY_RUN" = "1" ]; then
      echo "[dry-run] would create $env_file with DATA_SOLUTION_ROOT=${APP_ABS}"
      return
    fi
    sed "s|^DATA_SOLUTION_ROOT=.*|DATA_SOLUTION_ROOT=${APP_ABS}|" \
      "${INFRA}/airflow/.env.example" >"$env_file"
    return
  fi
  if ! grep -q '^DATA_SOLUTION_ROOT=' "$env_file" 2>/dev/null; then
    echo "Appending DATA_SOLUTION_ROOT to ${env_file}"
    if [ "$DRY_RUN" != "1" ]; then
      printf '\nDATA_SOLUTION_ROOT=%s\n' "$APP_ABS" >>"$env_file"
    fi
  fi
  if ! grep -q '^AIRFLOW_ADMIN_PASSWORD=' "$env_file" 2>/dev/null; then
    echo "Appending AIRFLOW_ADMIN_PASSWORD to ${env_file} (change it after deploy)"
    if [ "$DRY_RUN" != "1" ]; then
      printf '\nAIRFLOW_ADMIN_PASSWORD=changeme\n' >>"$env_file"
    fi
  fi
  for key in POSTGRES_HOST DATA_SOLUTION_DB; do
    if ! grep -q "^${key}=" "$env_file" 2>/dev/null; then
      value="$(grep -E "^${key}=" "${INFRA}/airflow/.env.example" | tail -1 | cut -d= -f2- || true)"
      if [ -n "$value" ]; then
        echo "Appending ${key} to ${env_file}"
        if [ "$DRY_RUN" != "1" ]; then
          printf '%s=%s\n' "$key" "$value" >>"$env_file"
        fi
      fi
    fi
  done
}

ensure_kafka_env() {
  local env_file="${KAFKA_DEST}/.env"
  if [ -f "$env_file" ]; then
    return
  fi
  if [ -f "${INFRA}/kafka/.env.example" ]; then
    echo "Creating ${env_file} from .env.example (optional)"
    run cp -n "${INFRA}/kafka/.env.example" "$env_file" 2>/dev/null || true
  fi
}

ensure_postgres_env() {
  local env_file="${POSTGRES_DEST}/.env"
  if [ ! -f "$env_file" ]; then
    echo "Creating ${env_file} from .env.example"
    if [ "$DRY_RUN" = "1" ]; then
      echo "[dry-run] would create $env_file with DATA_SOLUTION_ROOT=${APP_ABS}"
      return
    fi
    sed "s|^DATA_SOLUTION_ROOT=.*|DATA_SOLUTION_ROOT=${APP_ABS}|" \
      "${INFRA}/postgres/.env.example" >"$env_file"
    return
  fi
  if ! grep -q '^DATA_SOLUTION_ROOT=' "$env_file" 2>/dev/null; then
    echo "Appending DATA_SOLUTION_ROOT to ${env_file}"
    if [ "$DRY_RUN" != "1" ]; then
      printf '\nDATA_SOLUTION_ROOT=%s\n' "$APP_ABS" >>"$env_file"
    fi
  fi
}

ensure_data_dirs() {
  local env_file="${AIRFLOW_DEST}/.env"
  local airflow_uid="1000"
  if [ -f "$env_file" ]; then
    airflow_uid="$(grep -E '^AIRFLOW_UID=' "$env_file" | tail -1 | cut -d= -f2- || true)"
    airflow_uid="${airflow_uid:-1000}"
  fi
  run mkdir -p "${APP_ABS}/data/staging/openmeteo/daily_temperature"
  if [ "$DRY_RUN" != "1" ]; then
    chown -R "${airflow_uid}:0" "${APP_ABS}/data" 2>/dev/null || true
  fi
  echo "Ensured extractor landing dirs at ${APP_ABS}/data"
}

docker_compose_cmd() {
  if docker compose version >/dev/null 2>&1; then
    echo "docker compose"
  elif command -v docker-compose >/dev/null 2>&1; then
    echo "docker-compose"
  else
    echo ""
  fi
}

compose_up() {
  local dir=$1
  shift
  local compose_cmd
  compose_cmd="$(docker_compose_cmd)"
  if [ -z "$compose_cmd" ]; then
    echo "WARN: docker compose not found; skipping stack restart in ${dir}" >&2
    return 0
  fi
  echo "Applying compose in ${dir}..."
  if [ "$DRY_RUN" = "1" ]; then
    echo "[dry-run] cd ${dir} && ${compose_cmd} $* up -d"
    return
  fi
  (
    cd "$dir"
    # shellcheck disable=SC2086
    $compose_cmd "$@" up -d
  )
}

main() {
  if [ ! -d "$INFRA" ]; then
    echo "ERROR: infra folder not found at ${INFRA}. Set APP_ROOT or pull latest main." >&2
    exit 1
  fi

  echo "App root:     ${APP_ABS}"
  echo "Airflow dest: ${AIRFLOW_DEST}"
  echo "Kafka dest:     ${KAFKA_DEST}"
  echo "Postgres dest:  ${POSTGRES_DEST}"

  if [ -x "${SCRIPT_DIR}/setup-nas-ssh-env.sh" ]; then
    bash "${SCRIPT_DIR}/setup-nas-ssh-env.sh"
  fi

  run mkdir -p "${AIRFLOW_DEST}/logs" "${AIRFLOW_DEST}/plugins"
  run mkdir -p "${KAFKA_DEST}" "${POSTGRES_DEST}/data"

  copy_file "${INFRA}/kafka/docker-compose.yml" "${KAFKA_DEST}/docker-compose.yml"
  copy_file "${INFRA}/kafka/.env.example" "${KAFKA_DEST}/.env.example"
  copy_file "${INFRA}/postgres/docker-compose.yml" "${POSTGRES_DEST}/docker-compose.yml"
  copy_file "${INFRA}/postgres/.env.example" "${POSTGRES_DEST}/.env.example"
  copy_file "${INFRA}/airflow/docker-compose.standalone.yaml" "${AIRFLOW_DEST}/docker-compose.standalone.yaml"
  copy_file "${INFRA}/airflow/.env.example" "${AIRFLOW_DEST}/.env.example"

  ensure_kafka_env
  ensure_postgres_env
  ensure_airflow_env
  ensure_data_dirs

  if [ "$RUN_COMPOSE" = "1" ]; then
    compose_up "$POSTGRES_DEST"
    compose_up "$KAFKA_DEST"
    compose_up "$AIRFLOW_DEST" -f docker-compose.standalone.yaml
  else
    echo "RUN_COMPOSE=0: files synced; restart stacks manually if needed."
  fi

  echo "Infra deploy completed."
}

main "$@"
