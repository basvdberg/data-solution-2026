# Extractor and poller

## Table of contents

<!-- markdown-toc:start -->
- [Overview](#overview)
- [Poller metadata](#poller-metadata)
<!-- markdown-toc:end -->

## Overview

Open-Meteo extractor and poller driven by `data-object-mapping/` JSON. Lives under `code/extractor_and_poller/` (runtime *how* code).

Run from the solution root with `code/` on `PYTHONPATH`:

```powershell
cd "c:\Dev2\Data Engineering 2.0\data-solution-2026"
$env:PYTHONPATH = "code"
python -m extractor_and_poller.poller --list
python -m extractor_and_poller.poller --data-object source/openmeteo/daily-temperature
python -m extractor_and_poller.openmeteo.extractor --mapping daily-temperature
```

Event-oriented poller options:

```powershell
# Publish event envelopes to stdout or Kafka (state always in Postgres)
python -m extractor_and_poller.poller --data-object source/openmeteo/daily-temperature --publish stdout
python -m extractor_and_poller.poller --data-object source/openmeteo/daily-temperature --publish kafka
```

The `openmeteo/` subfolder holds `extractor/` and `poller/` probes. Shared helpers live under `common/`; the generic poller CLI is in `poller/`.

Airflow DAGs: [`code/airflow/`](../airflow/readme.md).

## Poller metadata

- No local files or directories are created by the poller.
- Each run appends one row to Postgres table `poller` (see [../postgres/schema.sql](../postgres/schema.sql)).
- Environment: `POSTGRES_HOST`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` (default `data_solution`), or `POSTGRES_DSN`.
