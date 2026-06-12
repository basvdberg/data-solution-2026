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
  - [Phase 4 - Native Airflow Kafka subscription](#phase-4-native-airflow-kafka-subscription)
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
- **Kafka**: event bus with poll topics `ds.poll.data_object_change` and `ds.poll.data_object_progress` (see [Kafka topic naming](kafka-topic-naming.md))
- **Airflow Asset Watcher**: subscribes to change events and schedules extract orchestration
- **Airflow**: runs DAGs for polling and extraction
- **Postgres**: stores poller baseline marker and event history
- **Extractor**: pulls Open-Meteo data and lands Parquet in `data/staging/openmeteo/daily-temperature/`

Flow:

1. Airflow schedules poller task.
2. Poller computes current marker for `daily-temperature`.
3. Poller compares marker to previous marker in Postgres.
4. Poller emits:
   - `data_object_change` if marker changed → topic `ds.poll.data_object_change`
   - `data_object_progress` if marker unchanged → topic `ds.poll.data_object_progress`
5. Airflow Asset Watcher on extract DAG consumes `ds.poll.data_object_change`.
6. Extract DAG runs with mapping id, marker, and event_id from the Kafka message.
7. Extract DAG runs extractor and writes landing file(s).
8. DAG emits success/failure operational event and updates observability metrics.

## Event contract (minimum)

Kafka message **value** is a JSON envelope (topics `ds.poll.data_object_change` and `ds.poll.data_object_progress`; partition key is `data_object_id`):

- `data_object_id` (`source/openmeteo/daily-temperature`)
- `event_type` (`data_object_change` or `data_object_progress`)
- `event_time_utc` (ISO-8601)
- `old_marker` (string or null)
- `new_marker` (string)

Postgres table `poller` stores the same markers plus correlation fields (`event_id`, `run_id`); query `poller_latest_first` for newest rows first.

Stdout publish (`--publish stdout`) emits an extended envelope for local debugging (adds `event_id`, `run_id`, `source_data_object_id`, `target_data_object_id`, and `current_marker` / `previous_marker` field names from `PollResult`).

Kafka topics (see [Kafka topic naming](kafka-topic-naming.md)):

- `ds.poll.data_object_change` (key: `data_object_id`, value: JSON envelope above)
- `ds.poll.data_object_progress` (key: `data_object_id`, value: JSON envelope above)

## Data poller implementation plan

### Phase 1 - Poller hardening

Deliverables:

- Keep `extractor_and_poller.poller` as the probe/decision engine (under `code/extractor_and_poller/`).
- Persist all poller runs in Postgres table `poller` (no local files).
- Ensure one authoritative marker per `data_object_id` in Postgres.
- Keep CLI behavior for local smoke runs (`--mapping`).

Acceptance:

- Poller returns `data_object_change` exactly once when marker advances.
- Re-running without marker changes produces only `data_object_progress`.
- Poller can recover from restart without losing baseline marker.

### Phase 2 - Kafka publisher

Deliverables:

- Poller DAG `ProduceToTopicOperator` publishes JSON poll envelope (`data_object_id`, `event_type`, `event_time_utc`, `old_marker`, `new_marker`).
- Publish to `ds.poll.data_object_change` and `ds.poll.data_object_progress` (key: `data_object_id`).

Acceptance:

- Successful publish for both event types is visible with a JSON value containing the envelope fields.
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

### Phase 4 - Native Airflow Kafka subscription

Deliverables:

- Extract DAG `schedule=[poll_change_asset]` with `AssetWatcher` + `MessageQueueTrigger` on `ds.poll.data_object_change`.
- Handler module [`code/airflow/include/kafka_handlers.py`](../../code/airflow/include/kafka_handlers.py) validates incoming JSON and resolves mapping id.
- Airflow Connection `kafka_default` and providers `apache-airflow-providers-apache-kafka`, `apache-airflow-providers-common-messaging`.
- Remove custom `extractor_and_poller.controller` package.

Acceptance:

- Every valid change event creates one extract DAG run (triggered by asset).
- Invalid payloads are rejected and logged with reason.
- No separate controller process runs on the NAS.

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

- `poller` (implemented; see [code/postgres/schema.sql](../../code/postgres/schema.sql)):
  - `id` (pk)
  - `polled_at_utc`, `data_object_id`, `event_type`, `old_marker`, `new_marker`
  - `event_id`, `run_id` (correlation; see event contract above)
- View `poller_latest_first`: same columns, newest `polled_at_utc` first
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
2. Enable `ds.poll.data_object_change` publication.
3. Deploy extract DAG with asset watcher (verify triggerer healthy).
4. Enable asset-scheduled extract runs on change events.
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
      - [Architecture](architecture.md)
      - [CI/CD workflow (main only + server pull deploy)](ci-cd.md)
      - [Event-based orchestration plan (single data object)](event-based-orchestration-plan.md)
      - [Kafka topic naming](kafka-topic-naming.md)
      - [Meta data design](meta-data-design.md)
    - Image
    - Implementation
      - [Implementation plan (Open-Meteo → event orchestration)](../implementation/implementation-plan.md)
    - Linked In
      - [Linkedin Post Part3V2](../linked-in/linkedin-post-part3v2.md)
    - Operation
      - Incident
        - [INC-001 — NAS non-interactive SSH environment](../operation/incident/inc-001-nas-ssh-environment.md)
        - [INC-002 — Airflow standalone infra instability](../operation/incident/inc-002-airflow-infra-stability.md)
        - [INC-003 — Agent rediscovery and false-done verification](../operation/incident/inc-003-agent-process-gaps.md)
        - [INC-004 — Airflow PYTHONPATH drift (dag_run_guard import)](../operation/incident/inc-004-airflow-pythonpath-drift.md)
        - [INC-<NNN> — <short title>](../operation/incident/incident-template.md)
      - [Event orchestration monitoring](../operation/event-orchestration-monitoring.md)
      - [Issue categories](../operation/issue-category.md)
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
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
