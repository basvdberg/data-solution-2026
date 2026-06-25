#!/usr/bin/env bash
# Sync infra/ compose files to legacy BasNAS paths and optionally restart stacks.
# Airflow DAGs are not copied: compose mounts ${DATA_SOLUTION_ROOT}/code/airflow/dags.
#
# Usage (on NAS):
#   bash infra/scripts/deploy-infra-on-nas.sh
#
# Environment:
#   APP_ROOT            Repo clone (default: ~/apps/data-solution-2026)
#   AIRFLOW_DEST        Legacy Airflow folder (default: ~/apache-airflow)
#   KAFKA_DEST          Legacy Kafka folder (default: ~/kafka)
#   POSTGRES_DEST       Legacy Postgres config folder (default: ~/data-solution-postgres)
#   INFRA_COMPONENTS    Comma-separated subset: airflow,kafka,postgres (default: from deploy-config or all)
#   RUN_COMPOSE         1 = docker compose up -d after sync (default: 1)
#   RUN_DB_MIGRATIONS   1 = run Postgres migrations after postgres sync (default: 1)
#   DRY_RUN             1 = print actions only (default: 0)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=nas-remote-env.sh
source "${SCRIPT_DIR}/nas-remote-env.sh"

APP_ROOT="${APP_ROOT:-$HOME/apps/data-solution-2026}"
AIRFLOW_DEST="${AIRFLOW_DEST:-$HOME/apache-airflow}"
KAFKA_DEST="${KAFKA_DEST:-$HOME/kafka}"
POSTGRES_DEST="${POSTGRES_DEST:-$HOME/data-solution-postgres}"
RUN_COMPOSE="${RUN_COMPOSE:-1}"
RUN_DB_MIGRATIONS="${RUN_DB_MIGRATIONS:-1}"
DRY_RUN="${DRY_RUN:-0}"

# nas-remote-env.sh already extends PATH for git wrapper + Container Station.

INFRA="${APP_ROOT}/infra"
APP_ABS="$(cd "$APP_ROOT" && pwd)"
DEPLOY_CONFIG="${DEPLOY_CONFIG:-$APP_ROOT/release/deploy-config.json}"
SELECTED_COMPONENTS=()

run() {
  if [ "$DRY_RUN" = "1" ]; then
    printf '[dry-run] '; printf '%q ' "$@"; printf '\n'
  else
    "$@"
  fi
}

component_selected() {
  local name=$1
  local c
  for c in "${SELECTED_COMPONENTS[@]}"; do
    if [ "$c" = "$name" ]; then
      return 0
    fi
  done
  return 1
}

resolve_components() {
  if [ -n "${INFRA_COMPONENTS:-}" ]; then
    local item
    IFS=',' read -r -a _raw <<<"${INFRA_COMPONENTS}"
    for item in "${_raw[@]}"; do
      item="$(echo "$item" | tr -d '[:space:]')"
      case "$item" in
        airflow | kafka | postgres)
          SELECTED_COMPONENTS+=("$item")
          ;;
        "")
          ;;
        *)
          echo "ERROR: unknown infra component '${item}' (expected airflow, kafka, or postgres)" >&2
          exit 1
          ;;
      esac
    done
    return
  fi

  local config_reader="${APP_ROOT}/release/scripts/read-deploy-config.sh"
  if [ -x "$config_reader" ] && [ -f "$DEPLOY_CONFIG" ]; then
    local line
    while IFS= read -r line; do
      [ -n "$line" ] && SELECTED_COMPONENTS+=("$line")
    done < <(DEPLOY_CONFIG="$DEPLOY_CONFIG" "$config_reader" infra_components 2>/dev/null || true)
    if [ "${#SELECTED_COMPONENTS[@]}" -gt 0 ]; then
      return
    fi
  fi

  SELECTED_COMPONENTS=(airflow postgres)
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
  for key in POSTGRES_HOST POSTGRES_DOCKER_NETWORK DATA_SOLUTION_DB KAFKA_HOST; do
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

prune_obsolete_airflow_variables() {
  if [ "$DRY_RUN" = "1" ]; then
    echo "[dry-run] would delete obsolete Airflow Variables: publish_transport poller_publish kafka_host"
    return
  fi
  if ! docker ps --format '{{.Names}}' 2>/dev/null | grep -qx 'airflow-standalone'; then
    echo "WARN: airflow-standalone not running; skipping Airflow Variable cleanup" >&2
    return
  fi
  for obsolete in publish_transport poller_publish kafka_host; do
    if docker exec airflow-standalone airflow variables get "$obsolete" >/dev/null 2>&1; then
      echo "Removing obsolete Airflow Variable: ${obsolete}"
      docker exec airflow-standalone airflow variables delete "$obsolete" >/dev/null 2>&1 || true
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
  if ! grep -q '^POSTGRES_CONTAINER=' "$env_file" 2>/dev/null; then
    echo "Appending POSTGRES_CONTAINER to ${env_file}"
    if [ "$DRY_RUN" != "1" ]; then
      printf '\nPOSTGRES_CONTAINER=basnas_postgress\n' >>"$env_file"
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

sync_kafka() {
  run mkdir -p "${KAFKA_DEST}"
  copy_file "${INFRA}/kafka/docker-compose.yml" "${KAFKA_DEST}/docker-compose.yml"
  copy_file "${INFRA}/kafka/.env.example" "${KAFKA_DEST}/.env.example"
  ensure_kafka_env
  if [ "$RUN_COMPOSE" = "1" ]; then
    compose_up "$KAFKA_DEST"
  fi
}

sync_postgres() {
  run mkdir -p "${POSTGRES_DEST}"
  copy_file "${INFRA}/postgres/.env.example" "${POSTGRES_DEST}/.env.example"
  copy_file "${INFRA}/postgres/create-app-user.sh" "${POSTGRES_DEST}/create-app-user.sh"
  copy_file "${INFRA}/postgres/run-applicable-migrations.sh" \
    "${POSTGRES_DEST}/run-applicable-migrations.sh"
  copy_file "${INFRA}/postgres/migrate-poller-from-dedicated-postgres.sh" \
    "${POSTGRES_DEST}/migrate-poller-from-dedicated-postgres.sh"
  copy_file "${INFRA}/postgres/remove-dedicated-postgres.sh" \
    "${POSTGRES_DEST}/remove-dedicated-postgres.sh"
  copy_file "${INFRA}/postgres/apply-shared-postgres-on-nas.sh" \
    "${POSTGRES_DEST}/apply-shared-postgres-on-nas.sh"
  ensure_postgres_env
}

sync_airflow() {
  run mkdir -p "${AIRFLOW_DEST}/logs" "${AIRFLOW_DEST}/plugins"
  copy_file "${INFRA}/airflow/docker-compose.standalone.yaml" "${AIRFLOW_DEST}/docker-compose.standalone.yaml"
  copy_file "${INFRA}/airflow/.env.example" "${AIRFLOW_DEST}/.env.example"
  ensure_airflow_env
  ensure_data_dirs
  if [ "$RUN_COMPOSE" = "1" ]; then
    compose_up "$AIRFLOW_DEST" -f docker-compose.standalone.yaml
    prune_obsolete_airflow_variables
  fi
}

main() {
  if [ ! -d "$INFRA" ]; then
    echo "ERROR: infra folder not found at ${INFRA}. Set APP_ROOT or pull latest main." >&2
    exit 1
  fi

  resolve_components
  if [ "${#SELECTED_COMPONENTS[@]}" -eq 0 ]; then
    echo "No infra components selected; nothing to sync."
    exit 0
  fi

  echo "App root:      ${APP_ABS}"
  echo "Components:    ${SELECTED_COMPONENTS[*]}"
  echo "Airflow dest:  ${AIRFLOW_DEST}"
  echo "Kafka dest:    ${KAFKA_DEST}"
  echo "Postgres cfg:  ${POSTGRES_DEST} (shared basnas_postgress; no compose stack)"

  if [ -x "${SCRIPT_DIR}/setup-nas-ssh-env.sh" ]; then
    bash "${SCRIPT_DIR}/setup-nas-ssh-env.sh"
  fi

  if component_selected kafka; then
    sync_kafka
  fi
  if component_selected postgres; then
    sync_postgres
    if [ "$RUN_DB_MIGRATIONS" = "1" ]; then
      migration_runner="${APP_ROOT}/infra/postgres/run-applicable-migrations.sh"
      if [ -x "$migration_runner" ]; then
        echo "Running applicable Postgres migrations..."
        if [ "$DRY_RUN" = "1" ]; then
          echo "[dry-run] would run: bash ${migration_runner}"
        else
          bash "$migration_runner"
        fi
      else
        echo "WARN: ${migration_runner} is not executable; skipping DB migrations." >&2
      fi
    else
      echo "RUN_DB_MIGRATIONS=0: skipping Postgres migrations after sync."
    fi
  fi
  if component_selected airflow; then
    sync_airflow
  fi

  if [ "$RUN_COMPOSE" != "1" ]; then
    echo "RUN_COMPOSE=0: files synced; restart stacks manually if needed."
  fi

  echo "Infra deploy completed."
  if component_selected airflow; then
    echo "Airflow stack synced; orchestration uses Airflow-native triggers (no Kafka broker)."
  fi
  if component_selected postgres; then
    echo "Postgres: run bash infra/postgres/create-app-user.sh once if schema or app role is missing."
    echo "Postgres: deploy-on-nas.sh runs infra/postgres/run-applicable-migrations.sh when deploy-config run_db_migrations=true."
  fi
}

main "$@"
