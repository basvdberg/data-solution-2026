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
#   RUN_COMPOSE       1 = docker compose up -d after sync (default: 1)
#   DRY_RUN           1 = print actions only (default: 0)

set -euo pipefail

APP_ROOT="${APP_ROOT:-$HOME/apps/data-solution-2026}"
AIRFLOW_DEST="${AIRFLOW_DEST:-$HOME/apache-airflow}"
KAFKA_DEST="${KAFKA_DEST:-$HOME/kafka}"
RUN_COMPOSE="${RUN_COMPOSE:-1}"
DRY_RUN="${DRY_RUN:-0}"

export PATH="${PATH}:/share/CACHEDEV1_DATA/.qpkg/container-station/bin:/share/CACHEDEV1_DATA/.qpkg/Entware/bin:/opt/bin:/usr/local/bin"

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
  echo "Kafka dest:   ${KAFKA_DEST}"

  run mkdir -p "${AIRFLOW_DEST}/logs" "${AIRFLOW_DEST}/plugins"
  run mkdir -p "${KAFKA_DEST}"

  copy_file "${INFRA}/kafka/docker-compose.yml" "${KAFKA_DEST}/docker-compose.yml"
  copy_file "${INFRA}/kafka/.env.example" "${KAFKA_DEST}/.env.example"
  copy_file "${INFRA}/airflow/docker-compose.standalone.yaml" "${AIRFLOW_DEST}/docker-compose.standalone.yaml"
  copy_file "${INFRA}/airflow/.env.example" "${AIRFLOW_DEST}/.env.example"

  ensure_kafka_env
  ensure_airflow_env

  if [ "$RUN_COMPOSE" = "1" ]; then
    compose_up "$KAFKA_DEST"
    compose_up "$AIRFLOW_DEST" -f docker-compose.standalone.yaml
  else
    echo "RUN_COMPOSE=0: files synced; restart stacks manually if needed."
  fi

  echo "Infra deploy completed."
}

main "$@"
