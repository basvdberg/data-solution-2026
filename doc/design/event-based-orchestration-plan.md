# Event-based orchestration plan (single data object)

## Table of contents

<!-- markdown-toc:start -->
- [Scope](#scope)
- [Target architecture](#target-architecture)
- [Event contract (minimum)](#event-contract-minimum)
- [Data poller implementation plan](#data-poller-implementation-plan)
  - [Phase 1 - Poller hardening](#phase-1-poller-hardening)
  - [Phase 2 - Kafka publisher](#phase-2-kafka-publisher)
  - [Phase 3 - Airflow poller DAG](#phase-3-airflow-poller-dag)
- [Change-event orchestration plan](#change-event-orchestration-plan)
  - [Phase 4 - Event controller](#phase-4-event-controller)
  - [Phase 5 - Extract DAG and idempotency](#phase-5-extract-dag-and-idempotency)
- [Postgres schema plan](#postgres-schema-plan)
- [Configuration plan](#configuration-plan)
- [Tunnel vs production](#tunnel-vs-production)
- [Test plan](#test-plan)
  - [Unit tests](#unit-tests)
  - [Integration tests](#integration-tests)
  - [End-to-end smoke (NAS runtime)](#end-to-end-smoke-nas-runtime)
- [Rollout steps](#rollout-steps)
- [Definition of done](#definition-of-done)
<!-- markdown-toc:end -->

## Scope

Implement event-based orchestration for one mapping: `data-object-mapping/staging/openmeteo/daily-temperature`.

In scope:

- Data poller (change detection)
- Kafka event publication and consumption
- Airflow orchestration for extract on change
- Postgres persistence for state and event audit
- Operational checks and acceptance tests

Out of scope:

- Additional sources/mappings
- Multi-tenant routing
- Complex retry backoff policies beyond basic operational safety

## Target architecture

Runtime roles:

- **Poller**: periodically probes source marker and emits events
- **Kafka**: event bus with `data_object_change` and `data_object_unchanged`
- **Event controller**: consumes change events and triggers extract orchestration
- **Airflow**: runs DAGs for polling and extraction
- **Postgres**: stores poller baseline marker and event history
- **Extractor**: pulls Open-Meteo data and lands Parquet in `data/staging/openmeteo/daily-temperature/`

Flow:

1. Airflow schedules poller task.
2. Poller computes current marker for `daily-temperature`.
3. Poller compares marker to previous marker in Postgres.
4. Poller emits:
   - `data_object_change` if marker changed
   - `data_object_unchanged` if marker unchanged
5. Event controller consumes `data_object_change`.
6. Event controller triggers extract DAG run with mapping id and marker context.
7. Extract DAG runs extractor and writes landing file(s).
8. DAG emits success/failure operational event and updates observability metrics.

## Event contract (minimum)

Use one envelope for both event types:

- `event_id` (uuid)
- `event_type` (`data_object_change` or `data_object_unchanged`)
- `event_time_utc` (ISO-8601)
- `data_object_id` (`source/openmeteo/daily-temperature`)
- `source_data_object_id` (`source/openmeteo/daily-temperature`)
- `target_data_object_id` (`staging/openmeteo/daily-temperature`)
- `current_marker` (string)
- `previous_marker` (string or null)
- `run_id` (poller run correlation id)

Kafka topics:

- `data_object_change` (key: `data_object_id`)
- `data_object_unchanged` (key: `data_object_id`)

## Data poller implementation plan

### Phase 1 - Poller hardening

Deliverables:

- Keep `extractor_and_poller.poller` as the probe/decision engine.
- Add Postgres-backed state store implementation (parallel to current local file store).
- Ensure one authoritative marker per mapping in Postgres.
- Keep CLI behavior for local smoke runs (`--mapping`).

Acceptance:

- Poller returns `data_object_change` exactly once when marker advances.
- Re-running without marker changes produces only `data_object_unchanged`.
- Poller can recover from restart without losing baseline marker.

### Phase 2 - Kafka publisher

Deliverables:

- Add producer module for poll results -> Kafka event envelope.
- Publish to `data_object_change` and `data_object_unchanged` topics.
- Add idempotency key policy (`data_object_id + current_marker`) in producer metadata/logging.

Acceptance:

- Successful publish for both event types is visible with message key `data_object_id`.
- Temporary Kafka outage results in controlled failure (no silent success).

### Phase 3 - Airflow poller DAG

Deliverables:

- Poller DAG in `code/airflow/dags/` (for example `openmeteo_data_object_poller.py`), scheduled at fixed cadence (for example every hour).
- Task sequence:
  1) load mapping config,
  2) probe and compare,
  3) write marker state,
  4) publish event.
- Add retries and timeout guardrails.

Acceptance:

- DAG emits one poll event per run for the mapping.
- DAG logs include marker values and publish status.

## Change-event orchestration plan

### Phase 4 - Event controller

Deliverables:

- Add Kafka consumer service for topic `data_object_change`.
- Validate incoming event schema before triggering DAG.
- Trigger Airflow extract DAG with event payload (mapping id + marker + event_id).

Acceptance:

- Every valid change event creates one extract DAG run.
- Invalid payloads are rejected and logged with reason.

### Phase 5 - Extract DAG and idempotency

Deliverables:

- Implement extract DAG entrypoint for mapping `daily-temperature`.
- Call `python -m extractor_and_poller.openmeteo.extractor --mapping daily-temperature`.
- Write run metadata (event_id, marker, output path, row count, status) to Postgres audit table.
- Add idempotency rule: if `event_id` already processed, skip duplicate execution.

Acceptance:

- One change event -> one extract run -> landed parquet output.
- Replayed event does not duplicate extraction output.

## Postgres schema plan

Create or evolve these tables:

- `data_object_poller_log`:
  - `id` (pk)
  - `data_object_id`
  - `event_type`
  - `polled_at_utc`
  - `old_marker`
  - `new_marker`
  - `inserted_at_utc`
- `event_log`:
  - `event_id` (pk)
  - `event_type`
  - `mapping_id`
  - `current_marker`
  - `previous_marker`
  - `published_at_utc`
  - `publish_status`
- `extract_run_audit`:
  - `run_id` (pk)
  - `event_id`
  - `mapping_id`
  - `marker`
  - `status`
  - `started_at_utc`
  - `finished_at_utc`
  - `output_path`
  - `row_count`

## Configuration plan

Add environment-driven configuration for local/NAS parity:

- `KAFKA_HOST` (for tunnel: `localhost:19092`)
- `POSTGRES_HOST` (for tunnel: `localhost:15432`)
- `AIRFLOW_HOST` (for tunnel/UI: `localhost:18080`)

Keep these values out of Git-tracked secrets and loaded via `.env` or runtime secrets.

## Tunnel vs production

Use the same variable names in both environments and only change their values.

Tunnel/local values:

- `KAFKA_HOST=localhost:19092`
- `POSTGRES_HOST=localhost:15432`
- `AIRFLOW_HOST=localhost:18080`

Production values:

- `KAFKA_HOST=<kafka-host-or-ip>:9092`
- `POSTGRES_HOST=<postgres-host-or-ip>:5432`
- `AIRFLOW_HOST=<airflow-host-or-ip>:8080`

Runtime rule:

- Tunnel mode uses local forwarded ports over SSH.
- Production mode uses direct private-network host:port endpoints.

## Test plan

### Unit tests

- Marker comparison rules (changed vs unchanged)
- Event envelope validation
- Consumer input validation and idempotency checks

### Integration tests

- Poller -> Kafka publish with test broker
- Change event -> Airflow trigger
- Extract run writes parquet and audit rows

### End-to-end smoke (NAS runtime)

1. Trigger poller DAG manually.
2. Verify one event in topic.
3. Verify extract DAG triggered on change only.
4. Verify parquet landed under staging path.
5. Verify Postgres tables updated.

## Rollout steps

1. Enable poller DAG in Airflow with unchanged-only observation.
2. Enable `data_object_change` publication.
3. Deploy event controller in passive logging mode.
4. Enable active Airflow triggers from controller.
5. Enable idempotency guard and duplicate-event test.
6. Mark orchestration as production-ready for this single data object.

## Definition of done

- Poller baseline state is stored in Postgres and survives restart.
- Both Kafka topics receive valid events with stable schema.
- Change events trigger extract DAG automatically.
- Duplicate events do not produce duplicate extraction output.
- Runbook and troubleshooting notes exist in `doc/`.

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](../../readme.md)
  - Code
    - Airflow
      - Dags
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
    - Data Solution
      - Data Object Mapping
    - Design
      - [Architecture](architecture.md)
      - [CI/CD workflow (main only + server pull deploy)](ci-cd.md)
      - [Event-based orchestration plan (single data object)](event-based-orchestration-plan.md)
      - [Meta data design](meta-data-design.md)
    - [Implementation plan (Open-Meteo → event orchestration)](../implementation-plan.md)
  - Extractor_And_Poller
    - Common
    - Openmeteo
      - Extractor
      - Poller
    - Poller
    - Tests
  - Infra
    - Airflow
      - Dags
    - Kafka
  - Release
    - Details
      - V2026.06.02.1
      - V2026.06.02.2
      - V2026.06.03.1
      - V2026.06.03.2
    - Notes
      - [Release v2026.06.02.1](../../release/notes/v2026.06.02.1.md)
      - [Release v2026.06.02.2](../../release/notes/v2026.06.02.2.md)
      - [Release v2026.06.03.1](../../release/notes/v2026.06.03.1.md)
      - [Release v2026.06.03.2](../../release/notes/v2026.06.03.2.md)
    - [Release <version>](../../release/release-notes-template.md)
  - Setting
  - Template
  - [Getting started](../../getting-started.md)
  - [Lessons learned](../../lessons-learned-part1.md)
  - [Lessons learned (part 2)](../../lessons-learned-part2.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
