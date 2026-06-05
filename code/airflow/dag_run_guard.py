"""Guard manual DAG triggers when another run is already active."""

from __future__ import annotations

import logging
from typing import Any

log = logging.getLogger(__name__)

_ACTIVE_RUN_STATES = frozenset({"running", "queued"})


def _is_manual_run(dag_run: Any) -> bool:
    run_type = getattr(dag_run, "run_type", None)
    if run_type is None:
        return False
    return str(run_type).lower().endswith("manual")


def _active_run_ids(dag_id: str, exclude_run_id: str, session: Any) -> list[str]:
    try:
        from airflow.models import DagRun
    except ImportError:  # pragma: no cover
        return []

    rows = (
        session.query(DagRun)
        .filter(
            DagRun.dag_id == dag_id,
            DagRun.run_id != exclude_run_id,
            DagRun.state.in_(_ACTIVE_RUN_STATES),
        )
        .all()
    )
    return [str(r.run_id) for r in rows]


def manual_trigger_conflict_message(dag_id: str, other_run_ids: list[str]) -> str:
    runs = ", ".join(other_run_ids)
    return (
        f"Manual trigger rejected for DAG '{dag_id}': another run is already active "
        f"({runs}). Wait for it to finish, or clear/fail that run before triggering again. "
        f"With max_active_runs=1, a manual trigger would otherwise stay queued with no task logs."
    )


def fail_manual_dag_run_if_busy(dag_run: Any, session: Any) -> bool:
    """Mark *dag_run* failed when manual and other active runs exist. Returns True if failed."""
    if not _is_manual_run(dag_run):
        return False

    dag_id = str(getattr(dag_run, "dag_id", ""))
    run_id = str(getattr(dag_run, "run_id", ""))
    other_ids = _active_run_ids(dag_id, run_id, session)
    if not other_ids:
        return False

    message = manual_trigger_conflict_message(dag_id, other_ids)
    log.warning(message)

    try:
        from airflow.utils.state import DagRunState

        dag_run.state = DagRunState.FAILED
    except ImportError:  # pragma: no cover
        dag_run.state = "failed"

    note = getattr(dag_run, "note", None)
    if note is None or not str(note).strip():
        if hasattr(dag_run, "note"):
            dag_run.note = message
        else:
            setattr(dag_run, "note", message)

    session.merge(dag_run)
    session.commit()
    return True


def assert_manual_trigger_allowed_from_context() -> None:
    """Raise :class:`airflow.exceptions.AirflowException` when manual run overlaps another."""
    try:
        from airflow.exceptions import AirflowException
        from airflow.sdk import get_current_context
    except ImportError:  # pragma: no cover - Airflow 2.x
        from airflow.exceptions import AirflowException  # type: ignore[no-redef]
        from airflow.operators.python import get_current_context  # type: ignore[no-redef]

    context = get_current_context()
    dag_run = context.get("dag_run")
    if dag_run is None or not _is_manual_run(dag_run):
        return

    dag_id = str(getattr(dag_run, "dag_id", ""))
    run_id = str(getattr(dag_run, "run_id", ""))

    try:
        from airflow.models import DagRun
        from airflow.utils.session import create_session
    except ImportError:  # pragma: no cover
        log.warning("Cannot inspect DAG runs for concurrency guard")
        return

    with create_session() as session:
        other_ids = _active_run_ids(dag_id, run_id, session)

    if other_ids:
        raise AirflowException(manual_trigger_conflict_message(dag_id, other_ids))
