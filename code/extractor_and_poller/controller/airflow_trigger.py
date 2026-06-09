"""Trigger Airflow extract DAG runs via the REST API."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import requests

log = logging.getLogger(__name__)

DEFAULT_EXTRACT_DAG_ID = "openmeteo_daily_temperature_extract"


def default_airflow_base_url() -> str:
    host = os.getenv("AIRFLOW_HOST", "http://localhost:8080")
    if not host.startswith("http"):
        host = f"http://{host}"
    return host.rstrip("/")


def trigger_extract_dag(
    *,
    mapping_id: str,
    marker: str,
    event_id: str | None,
    dag_id: str | None = None,
    base_url: str | None = None,
    username: str | None = None,
    password: str | None = None,
) -> str:
    """Queue an extract DAG run; returns the Airflow ``dag_run_id``."""
    dag_id = dag_id or os.getenv("EXTRACT_DAG_ID", DEFAULT_EXTRACT_DAG_ID)
    base_url = (base_url or default_airflow_base_url()).rstrip("/")
    username = username or os.getenv("AIRFLOW_USER", "admin")
    password = password or os.getenv("AIRFLOW_PASSWORD") or os.getenv("AIRFLOW_ADMIN_PASSWORD", "admin")

    logical_date = datetime.now(timezone.utc).isoformat()
    dag_run_id = f"event-{uuid4()}"
    conf: dict[str, Any] = {
        "mapping_id": mapping_id,
        "marker": marker,
    }
    if event_id:
        conf["event_id"] = event_id

    url = f"{base_url}/api/v2/dags/{dag_id}/dagRuns"
    response = requests.post(
        url,
        json={
            "dag_run_id": dag_run_id,
            "logical_date": logical_date,
            "conf": conf,
        },
        auth=(username, password),
        timeout=30,
    )
    response.raise_for_status()
    body = response.json()
    returned_id = str(body.get("dag_run_id", dag_run_id))
    log.info(
        "Triggered Airflow dag_id=%s dag_run_id=%s mapping=%s marker=%s",
        dag_id,
        returned_id,
        mapping_id,
        marker,
    )
    return returned_id
