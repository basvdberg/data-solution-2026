"""Extract run audit and idempotency (table ``extract_run_audit``)."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import uuid4

from extractor_and_poller.poller.state import default_postgres_dsn

log = logging.getLogger(__name__)


class ExtractRunAudit:
    def __init__(self, dsn: str | None = None) -> None:
        self._dsn = dsn or default_postgres_dsn()
        self._conn = self._connect(self._dsn)

    @staticmethod
    def _connect(dsn: str):
        try:
            import psycopg  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(
                "Extract audit requires 'psycopg'. Install with: pip install psycopg[binary]"
            ) from exc
        return psycopg.connect(dsn)

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
        marker: str,
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
                        marker = %s,
                        started_at_utc = %s,
                        finished_at_utc = null,
                        output_table = null,
                        row_count = null
                    where run_id = %s
                    """,
                    ("running", marker, now, run_id),
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
                    marker,
                    status,
                    started_at_utc
                )
                values (%s, %s, %s, %s, %s, %s)
                """,
                (
                    run_id,
                    event_id,
                    mapping_id,
                    marker,
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
    ) -> None:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                update extract_run_audit
                set status = %s,
                    finished_at_utc = %s,
                    output_table = %s,
                    row_count = %s
                where run_id = %s
                """,
                (
                    status,
                    datetime.now(timezone.utc),
                    output_table,
                    row_count,
                    run_id,
                ),
            )
        self._conn.commit()
