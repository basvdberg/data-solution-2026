# Airflow (generated)

## Table of contents

<!-- markdown-toc:start -->
- [DAGs](#dags)
- [Configuration](#configuration)
- [Poller DAG](#poller-dag)
<!-- markdown-toc:end -->

## DAGs

Python files under [dags/](dags/) are loaded by the Airflow scheduler from `/opt/airflow/dags` in the container.

## Configuration

Set Airflow Variables (Admin → Variables) to override defaults used by the poller DAG:

| Variable | Default | Purpose |
|----------|---------|---------|
| `poller_data_object_id` | `source/openmeteo/daily-temperature` | `--data-object` for the poller CLI |
| `poller_publish` | `none` | `none`, `stdout`, or `kafka` |

Poller state is always stored in Postgres (table `poller`). Postgres connection settings use container environment variables (`POSTGRES_HOST`, `POSTGRES_USER`, etc.). See [Implementation plan](../../doc/implementation-plan.md).

## Poller DAG

| Property | Value |
|----------|--------|
| File | `dags/openmeteo_data_object_poller.py` |
| `dag_id` | `openmeteo_data_object_poller` |
| Schedule | `@hourly` (paused on creation until smoke passes) |

Task command (equivalent):

```bash
python -m extractor_and_poller.poller \
  --data-object source/openmeteo/daily-temperature \
  --publish none
```

Run from repo root inside the container: `cwd=/opt/data-solution`, `PYTHONPATH=/opt/data-solution/code:/opt/data-solution`.
