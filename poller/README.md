# Poller

## Table of contents

<!-- markdown-toc:start -->
- [Event types](#event-types)
- [CLI](#cli)
<!-- markdown-toc:end -->

Detects whether a configured **data object** changed and **signals the event bus only**. The poller does not download payloads, write landing files, or run extractors.

| Responsibility | Owner |
|----------------|--------|
| Probe source marker, compare to baseline | `poller/` (`python -m poller`) |
| Publish `data_object_change` or `data_object_progress` | `poller/` → event bus (Kafka in production; CLI stdout locally) |
| Extract, parse, land Parquet | `extractor/<protocol>/` (triggered by orchestration after **change** events) |

Probe HTTP uses shared `extractor.*.client` helpers so detection rules stay aligned with extractors — without invoking extraction.

## Event types

| `event_type` | Meaning |
|--------------|---------|
| `data_object_change` | Change marker differs from baseline (or first poll) — orchestration may enqueue extract/load tasks |
| `data_object_progress` | Poll succeeded, marker unchanged — activity / heartbeat for monitoring |

Every poll emits **one** of these events. There is no silent “no message” path when polling succeeds.

## CLI

```powershell
# Full poll: compare baseline, emit event, update baseline on change
python -m poller --mapping openmeteo-daily-temperature

# Marker only (no baseline, no event) — debugging
python -m poller --probe-only --mapping openmeteo-daily-temperature

# JSON lines for a bus producer
python -m poller --mapping openmeteo-daily-temperature --json
```

Exit code `1` when at least one **`data_object_change`** was emitted (useful for Airflow branching); `0` when all outcomes were **progress** (or probe-only).

Mappings must include `trigger:data_object_change` (legacy `trigger:source_change` is still accepted).

See [data object poller plan](../plan/data-object-poller/airflow-kafka.md) and [event-based orchestration](https://github.com/basvdberg/data-engineering-design-patterns/blob/main/design-patterns/event-based-orchestration.md).

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](../readme.md)
  - Data
    - Staging
      - Openmeteo
        - Daily_Temperature
  - Data Object Mapping
    - Staging
      - Knmi
      - Openmeteo
  - Docs
  - Extractor
    - Common
    - Knmi
    - Odata
    - Openmeteo
    - Poller
    - Wfs
  - Plan
    - Data Object Poller
      - [Data object poller — Airflow + Kafka implementation](../plan/data-object-poller/airflow-kafka.md)
    - [Phase one: CBS OData extraction with event-based orchestration](../plan/plan1.md)
    - [Phase two: minimal Dutch government OData ingestion with event-based orchestration](../plan/plan2.md)
    - [Phase three: JSON-configured Dutch government OData ingestion](../plan/plan3.md)
  - Poller
  - Schema
    - [Schema follow-ups](../schema/data-objects-schema.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026)
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns)
<!-- markdown-project-structure:end -->
