# Troubleshooting errors

Agent-maintained log of failures during debugging. Backfilled from lessons learned, infra readme, and session review (2026-06-03). Do not edit by hand unless correcting facts.

## Session: 2026-06-03 (backfill)

### ERR-001 — docker: command not found (SSH)

| Field | Value |
|-------|-------|
| **When** | 2026-06-03 (backfill) |
| **Context** | SSH bas@basnas, non-interactive session |
| **Command** | `docker ps` / `docker compose …` |
| **Error** | bash: docker: command not found (127) |
| **Description** | Non-interactive SSH uses minimal PATH; Container Station `docker` is under `/share/CACHEDEV*_DATA/.qpkg/container-station/bin`, not on default PATH. |
| **Solution** | Run once on NAS: `bash infra/scripts/setup-nas-ssh-env.sh`; for automation source `infra/scripts/nas-remote-env.sh`; for bare `ssh … 'docker …'` run `bash infra/scripts/enable-nas-ssh-user-env.sh` once. |
| **Prevention** | First command block on every NAS SSH session: source `nas-remote-env.sh` or verify `ssh bas@basnas 'docker --version'`. See [infra/readme.md](../infra/readme.md#ssh-docker-command-not-found). |
| **Count** | 1 |

### ERR-002 — Repeated which/find for docker (same session)

| Field | Value |
|-------|-------|
| **When** | 2026-06-03 (backfill) |
| **Context** | SSH bas@basnas, agent troubleshooting |
| **Command** | `which docker`, `find /share -name docker` (repeated) |
| **Error** | N/A — efficiency anti-pattern after ERR-001 |
| **Description** | Agent rediscovered docker location multiple times in one session instead of persisting PATH fix once. |
| **Solution** | Apply ERR-001 solution once; do not run discovery commands again in the same session. |
| **Prevention** | Read this log before retrying; if ERR-001 exists, source env immediately. Log Count increment if repeat occurs. |
| **Count** | 1 |

### ERR-003 — Airflow incomplete first install

| Field | Value |
|-------|-------|
| **When** | 2026-06-03 (backfill) |
| **Context** | NAS, initial Airflow PoC deploy |
| **Command** | Various `docker compose` / UI checks |
| **Error** | Missing metadata DB, logging not working; multiple fix cycles |
| **Description** | First agent-driven install omitted pieces of standalone stack setup. |
| **Solution** | Use [infra/airflow/docker-compose.standalone.yaml](../infra/airflow/docker-compose.standalone.yaml) from repo; follow [infra/readme.md](../infra/readme.md) Airflow section and health check. |
| **Prevention** | Start from versioned compose in repo; do not invent layout on NAS without syncing `deploy-infra-on-nas.sh`. |
| **Count** | 1 |

### ERR-004 — Admin password changes on container recreate

| Field | Value |
|-------|-------|
| **When** | 2026-06-03 (backfill) |
| **Context** | NAS Airflow, after `docker compose` recreate |
| **Command** | Airflow UI login |
| **Error** | Admin password no longer works after almost every infra change / Docker restart |
| **Description** | Stack regenerated random admin password on recreate until explicitly pinned. |
| **Solution** | Set `AIRFLOW_ADMIN_PASSWORD` in `~/apache-airflow/.env` (or synced `.env`); compose writes Simple Auth Manager passwords file on container start. |
| **Prevention** | Never call Airflow infra “done” without documenting password in `.env.example` and verifying login after `compose up -d`. |
| **Count** | 1 |

### ERR-005 — Airflow UI errors after host reboot

| Field | Value |
|-------|-------|
| **When** | 2026-06-03 (backfill) |
| **Context** | NAS, after server reboot or Docker restart |
| **Command** | Open `https://airflow.basnas/` |
| **Error** | Multiple UI errors (count varies); log links / worker callbacks use stale IPs or ports |
| **Description** | Hostname, published ports, or bridge networking still drift on reboot; compose fixes did not hold through full reboot test. |
| **Solution** | Pin `hostname`, named network, `AIRFLOW__CORE__HOSTNAME_CALLABLE`, fixed `AIRFLOW_HOST_PORT`; run full cycle: `compose down` → host reboot → browse UI and trigger new DAG run. |
| **Prevention** | Mandatory reboot verification for infra changes (see ERR-012). Treat recurring UI errors as identity not pinned. |
| **Count** | 1 |

### ERR-006 — UI Bad Gateway / missing Meta DB / Scheduler / Triggerer

| Field | Value |
|-------|-------|
| **When** | 2026-06-03 (backfill) |
| **Context** | NAS Airflow via NGINX `https://airflow.basnas/` |
| **Command** | Browser / `curl` health |
| **Error** | 502 Bad Gateway; UI shows missing Meta Database, Scheduler, or Triggerer |
| **Description** | Stack still starting (pip + DB init 3–5 min), log volume permissions, or NGINX not on same Docker network as Airflow container. |
| **Solution** | Wait then `curl -s http://127.0.0.1:8081/api/v2/monitor/health`; set `AIRFLOW_UID` in `.env`; ensure NGINX shares `apache-airflow_default` network (`patch-bridge-upstreams.sh` after recreates). |
| **Prevention** | Read [infra/readme.md](../infra/readme.md#ui-shows-bad-gateway-or-missing-meta-database-scheduler-triggerer) before declaring failure; do not restart compose repeatedly during startup window. |
| **Count** | 1 |

### ERR-007 — git fails: libcharset.so.1 (SSH)

| Field | Value |
|-------|-------|
| **When** | 2026-06-03 (backfill) |
| **Context** | SSH bas@basnas, `git pull` / deploy |
| **Command** | `git …` |
| **Error** | error while loading shared libraries: libcharset.so.1 |
| **Description** | QNAP `/usr/bin/git` needs libs from optional QPKG; non-interactive SSH does not load `~/.profile`. |
| **Solution** | `bash infra/scripts/setup-nas-ssh-env.sh`; `bash infra/scripts/enable-nas-ssh-user-env.sh` for bare `ssh … git`; deploy scripts source `nas-remote-env.sh`. |
| **Prevention** | Do not set global `LD_LIBRARY_PATH` in `~/.profile` (breaks QNAP bash / Cursor Remote SSH). See [infra/readme.md](../infra/readme.md#non-interactive-ssh-git-fails-with-libcharsetso1). |
| **Count** | 1 |

### ERR-008 — Task logs http://:8793/ no host supplied

| Field | Value |
|-------|-------|
| **When** | 2026-06-03 (backfill) |
| **Context** | Airflow 3 UI, task log view |
| **Command** | View task logs in UI |
| **Error** | Invalid URL 'http://:8793/...': No host supplied |
| **Description** | `getfqdn` returns empty hostname in Docker on QNAP; log URLs built without host. |
| **Solution** | `hostname: airflow-standalone` and `AIRFLOW__CORE__HOSTNAME_CALLABLE=airflow.utils.net.get_host_ip_address` in compose; redeploy; trigger **new** DAG run (old runs keep bad hostname in DB). |
| **Prevention** | Verify compose pins before debugging UI; use `docker exec airflow-standalone cat …log` for immediate read. See [infra/readme.md](../infra/readme.md#task-logs-show-http8793-no-host-supplied). |
| **Count** | 1 |

### ERR-009 — NAS script permission denied / sudo without bash

| Field | Value |
|-------|-------|
| **When** | 2026-06-03 |
| **Context** | SSH bas@basnas, `infra/scripts/` |
| **Command** | `~/apps/data-solution-2026/infra/scripts/enable-nas-ssh-user-env.sh` or `sudo …/enable-nas-ssh-user-env.sh` |
| **Error** | Permission denied; or `sudo: … command not found` |
| **Description** | Script not executable; invoking without `bash` or wrong shebang handling under sudo. |
| **Solution** | `chmod +x` if needed; always `bash ~/apps/data-solution-2026/infra/scripts/enable-nas-ssh-user-env.sh` (admin password when sudo required). |
| **Prevention** | `test -x` before run; never `sudo ./script.sh` on NAS without verifying executable bit after `git pull`. |
| **Count** | 1 |

### ERR-010 — SSH connection refused after sshd change

| Field | Value |
|-------|-------|
| **When** | 2026-06-03 |
| **Context** | Local → basnas, immediately after enable-nas-ssh-user-env |
| **Command** | `ssh bas@basnas` |
| **Error** | ssh: connect to host 192.168.2.2 port 22: Connection refused |
| **Description** | Brief outage while SSH service restarts during PermitUserEnvironment enable. |
| **Solution** | Wait and retry SSH; if script warns, reload SSH from QNAP Control Panel. |
| **Prevention** | Expect transient disconnect; do not run parallel SSH sessions during enable script. |
| **Count** | 1 |

### ERR-011 — Local script not found (wrong cwd)

| Field | Value |
|-------|-------|
| **When** | 2026-06-03 |
| **Context** | PowerShell, `C:\Dev2\Data Engineering 2.0` (monorepo root) |
| **Command** | `.\manage-bookmarks.cmd` |
| **Error** | The term '.\manage-bookmarks.cmd' is not recognized |
| **Description** | Bookmark script lives in cursor-config repo, not monorepo root. |
| **Solution** | Run from cursor-config path or use documented wrapper; see `browser-bookmarks-sync` skill. |
| **Prevention** | Verify script path with `Get-Command` / `Test-Path` before invoke; read skill for repo layout. |
| **Count** | 1 |

### ERR-012 — Infra “done” without reboot verification (false positive)

| Field | Value |
|-------|-------|
| **When** | 2026-06-03 (backfill) |
| **Context** | Agent infra troubleshooting |
| **Command** | N/A — process failure |
| **Error** | UI works once; fails again after reboot (related ERR-005) |
| **Description** | Agent treated single successful browser check as complete fix; no `compose down` / host reboot / browse cycle. |
| **Solution** | Add explicit verification step to infra tasks; re-open ERR-005 if reboot test fails. |
| **Prevention** | Infra checklist: health curl → HTTPS UI → **host reboot or full down/up** → UI + one new DAG log. Document in release notes when verified. |
| **Count** | 1 |
