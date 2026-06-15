# Event orchestration monitoring

## Table of contents

<!-- markdown-toc:start -->
- [Scope](#scope)
- [Happy-path checks](#happy-path-checks)
- [Error-path checks](#error-path-checks)
- [Periodic runbook](#periodic-runbook)
- [Log patterns](#log-patterns)
- [Manual recovery](#manual-recovery)
<!-- markdown-toc:end -->

## Scope

End-to-end path: **poller DAG** → **Airflow change asset** → **extract DAG** → **Postgres staging + audit**.

DAG ids: `openmeteo_data_object_poller`, `openmeteo_daily_temperature_extract`.

## Happy-path checks

| Layer | Check | How | Expected |
|-------|-------|-----|----------|
| Poller schedule | Hourly runs | Airflow UI | 1 success/hour for poller DAG |
| Poller persistence | Marker rows | `SELECT * FROM poller_latest_first LIMIT 5` | New row each run |
| Change asset | Asset event on change | Airflow UI — Assets / extract DAG “Triggered by asset” | Event only on `data_object_change` |
| Extract triggered | Downstream run | Airflow UI — extract DAG | Run only when change asset updates |
| Extract success | Audit + staging | `SELECT * FROM extract_run_audit ORDER BY started_at_utc DESC LIMIT 5` | `status='success'`, `row_count > 0` |

## Error-path checks

| Failure | Symptom | Detection | Response |
|---------|---------|-----------|----------|
| Poller probe error | Task `probe_and_persist` failed | Airflow task log | Fix mapping/config; re-run poller DAG |
| Asset emit error | Task `emit_change_asset` failed | Airflow task log | Check task log; re-run poller DAG |
| Invalid asset extra | No extract run | Extract task log `Rejected asset event` | Inspect poller XCom / asset event extra |
| Extract transient error | Task `up_for_retry` | Airflow UI | Wait for retries (up to 5) |
| Extract exhausted retries | DAG run `failed` | Airflow UI + `extract_run_audit.status='failed'` | Manual replay (below) |
| Duplicate event | Skipped extract | Log `Skipping duplicate extract for event_id=` | Expected idempotency |
| Scheduler unhealthy | No asset-triggered runs | Airflow health / startup logs | Restart `airflow-standalone` container |

## Periodic runbook

**Daily (~5 min)**

1. Airflow UI: failed poller or extract runs in last 24h.
2. Postgres: `SELECT count(*) FROM extract_run_audit WHERE status='failed' AND started_at_utc > now() - interval '24 hours'`
3. Postgres: `SELECT count(*) FROM poller WHERE event_type='data_object_progress' AND polled_at_utc > now() - interval '24 hours'` (proves poller is alive).

**Weekly**

1. Compare latest `poller.new_marker` with max observation day in `staging.openmeteo_daily_temperature`.
2. Review extract task retry history in Airflow.

## Log patterns

| Pattern | Meaning |
|---------|---------|
| `Persisted poller row` | Probe + Postgres OK |
| `Accepted data_object_change` | Extract conf resolved from asset extra |
| `Rejected asset event` | Invalid or empty asset extra |
| `Skipping duplicate extract for event_id=` | Successful idempotency |
| `extractor exited with` | Extract failure (may retry) |

## Manual recovery

When extract fails after all 5 retries:

1. Find the failed event:

```sql
SELECT event_id, mapping_id, marker, run_id, started_at_utc
FROM extract_run_audit
WHERE status = 'failed'
ORDER BY started_at_utc DESC
LIMIT 10;
```

2. Re-trigger extract DAG in Airflow UI with conf:

```json
{
  "mapping_id": "daily-temperature",
  "marker": "<marker from audit>",
  "event_id": "<event_id from audit>"
}
```

3. Idempotency skips only prior **success** rows for the same `event_id`; failed rows are retried in-place on the next attempt.

Related: [Implementation plan — Step 3](../implementation/implementation-plan.md#step-3-react-to-change-assets-native-airflow-scheduling), [Issue categories](issue-category.md).

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](../../readme.md)
  - Code
    - Airflow
      - Dags
      - Include
      - Plugins
    - Extractor_And_Poller
      - Common
      - Extract
      - Openmeteo
        - Extractor
        - Poller
      - Poller
      - Tests
    - Postgres
      - Migrations
  - Connection
  - Data
    - Staging
      - Openmeteo
        - Daily_Temperature
  - Data Object
    - Source
      - Openmeteo
    - Staging
      - Openmeteo
  - Data Object Mapping
    - Staging
      - Openmeteo
  - Doc
    - Data Object Mapping
    - Design
      - [Airflow asset naming](../design/airflow-asset-naming.md)
      - [Architecture](../design/architecture.md)
      - [CI/CD workflow (main only + server pull deploy)](../design/ci-cd.md)
      - [Event-based orchestration plan (single data object)](../design/event-based-orchestration-plan.md)
      - [Meta data design](../design/meta-data-design.md)
    - Image
    - Implementation
      - [Implementation plan (Open-Meteo → event orchestration)](../implementation/implementation-plan.md)
    - Linked In
      - [Linkedin Post Part3V2](../linked-in/linkedin-post-part3v2.md)
    - Operation
      - Incident
        - [INC-001 — NAS non-interactive SSH environment](incident/inc-001-nas-ssh-environment.md)
        - [INC-002 — Airflow standalone infra instability](incident/inc-002-airflow-infra-stability.md)
        - [INC-003 — Agent rediscovery and false-done verification](incident/inc-003-agent-process-gaps.md)
        - [INC-004 — Airflow PYTHONPATH drift (dag_run_guard import)](incident/inc-004-airflow-pythonpath-drift.md)
        - [INC-<NNN> — <short title>](incident/incident-template.md)
      - [Event orchestration monitoring](event-orchestration-monitoring.md)
      - [Issue categories](issue-category.md)
  - Infra
    - Airflow
      - Dags
    - Kafka
    - Postgres
  - Release
    - 2026
      - 06
        - 02
          - V2026.06.02.1
            - [Notes](../../release/2026/06/02/v2026.06.02.1/notes.md)
          - V2026.06.02.2
            - [Release v2026.06.02.2](../../release/2026/06/02/v2026.06.02.2/notes.md)
        - 03
          - V2026.06.03.1
            - [Release v2026.06.03.1](../../release/2026/06/03/v2026.06.03.1/notes.md)
          - V2026.06.03.2
            - [Release v2026.06.03.2](../../release/2026/06/03/v2026.06.03.2/notes.md)
          - V2026.06.03.3
            - [Release v2026.06.03.3](../../release/2026/06/03/v2026.06.03.3/notes.md)
          - V2026.06.03.4
            - [Release v2026.06.03.4](../../release/2026/06/03/v2026.06.03.4/notes.md)
            - [Retrospective](../../release/2026/06/03/v2026.06.03.4/retrospective.md)
        - 04
          - V2026.06.04.1
            - [Notes](../../release/2026/06/04/v2026.06.04.1/notes.md)
        - 05
          - V2026.06.05.6
            - [Notes](../../release/2026/06/05/v2026.06.05.6/notes.md)
            - [Retrospective](../../release/2026/06/05/v2026.06.05.6/retrospective.md)
        - 12
          - V2026.06.12.1
            - [Release v2026.06.12.1](../../release/2026/06/12/v2026.06.12.1/notes.md)
    - [Release <version>](../../release/release-notes-template.md)
    - [Retrospective — <version>](../../release/retrospective-template.md)
  - [Getting started](../../getting-started.md)
  - [Lessons learned](../../lessons-learned-part1.md)
  - [Lessons learned (part 2)](../../lessons-learned-part2.md)
  - [Lessons learned (part 3)](../../lessons-learned-part3.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
