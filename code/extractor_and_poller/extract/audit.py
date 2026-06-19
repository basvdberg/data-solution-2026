"""Extract run audit and idempotency (table ``extract_run_audit``)."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import uuid4

from extractor_and_poller.common.postgres_schema import ensure_metadata_schema
from extractor_and_poller.poller.poll_events import (
    EVENT_TYPE_CHANGE,
    EVENT_TYPE_PROCESSING_ERROR,
)
from extractor_and_poller.poller.state import default_postgres_dsn

log = logging.getLogger(__name__)


def event_type_for_status(status: str) -> str:
    """Map extract run status to orchestration glossary event type."""
    if status == "success":
        return EVENT_TYPE_CHANGE
    if status == "failed":
        return EVENT_TYPE_PROCESSING_ERROR
    return ""


class ExtractRunAudit:
    def __init__(self, dsn: str | None = None) -> None:
        self._dsn = dsn or default_postgres_dsn()
        self._conn = self._connect(self._dsn)
        self._ensure_schema()

    @staticmethod
    def _connect(dsn: str):
        try:
            import psycopg  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(
                "Extract audit requires 'psycopg'. Install with: pip install psycopg[binary]"
            ) from exc
        return psycopg.connect(dsn)

    def _extract_run_audit_exists(self) -> bool:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                select 1
                from information_schema.tables
                where table_schema = 'public'
                  and table_name = 'extract_run_audit'
                """
            )
            return cur.fetchone() is not None

    def _ensure_schema(self) -> None:
        ensure_metadata_schema(self._conn)
        if not self._extract_run_audit_exists():
            raise RuntimeError(
                "Postgres metadata schema was applied but table public.extract_run_audit "
                "is still missing"
            )

    def already_processed(self, event_id: str) -> bool:
        """Return True when a prior run for this event_id completed successfully."""
        with self._conn.cursor() as cur:
            cur.execute(
                """
                select 1 from extract_run_audit
                where event_id = %s and status = 'success'
                limit 1
                """,
                (event_id,),
            )
            return cur.fetchone() is not None

    def start(
        self,
        *,
        event_id: str,
        mapping_id: str,
        data_object_id: str,
        marker: str,
        change_scope: str | None = None,
    ) -> str:
        now = datetime.now(timezone.utc)
        with self._conn.cursor() as cur:
            cur.execute(
                """
                select run_id, status
                from extract_run_audit
                where event_id = %s
                limit 1
                """,
                (event_id,),
            )
            row = cur.fetchone()
            if row is not None:
                run_id, status = row[0], row[1]
                if status == "success":
                    return str(run_id)
                cur.execute(
                    """
                    update extract_run_audit
                    set status = %s,
                        mapping_id = %s,
                        data_object_id = %s,
                        marker = %s,
                        change_scope = %s,
                        event_type = null,
                        started_at_utc = %s,
                        finished_at_utc = null,
                        output_table = null,
                        row_count = null
                    where run_id = %s
                    """,
                    (
                        "running",
                        mapping_id,
                        data_object_id,
                        marker,
                        change_scope,
                        now,
                        run_id,
                    ),
                )
                self._conn.commit()
                return str(run_id)

            run_id = str(uuid4())
            cur.execute(
                """
                insert into extract_run_audit (
                    run_id,
                    event_id,
                    mapping_id,
                    data_object_id,
                    marker,
                    change_scope,
                    status,
                    started_at_utc
                )
                values (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    run_id,
                    event_id,
                    mapping_id,
                    data_object_id,
                    marker,
                    change_scope,
                    "running",
                    now,
                ),
            )
        self._conn.commit()
        return run_id

    def finish(
        self,
        run_id: str,
        *,
        status: str,
        output_table: str,
        row_count: int,
        event_type: str | None = None,
    ) -> str:
        resolved_event_type = event_type or event_type_for_status(status)
        with self._conn.cursor() as cur:
            cur.execute(
                """
                update extract_run_audit
                set status = %s,
                    event_type = %s,
                    finished_at_utc = %s,
                    output_table = %s,
                    row_count = %s
                where run_id = %s
                """,
                (
                    status,
                    resolved_event_type or None,
                    datetime.now(timezone.utc),
                    output_table,
                    row_count,
                    run_id,
                ),
            )
        self._conn.commit()
        return resolved_event_type
