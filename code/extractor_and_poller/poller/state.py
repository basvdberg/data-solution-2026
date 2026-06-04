"""Postgres-backed poller execution log (table ``poller``)."""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from extractor_and_poller.poller.change_probe import PollResult

log = logging.getLogger(__name__)

_POLLER_DDL = """
create table if not exists poller (
    id bigserial primary key,
    event_id text not null,
    run_id text not null,
    data_object_id text not null,
    source_data_object_id text not null,
    target_data_object_id text not null,
    event_type text not null,
    polled_at_utc timestamptz not null,
    old_marker text,
    new_marker text not null,
    inserted_at_utc timestamptz not null default now()
)
"""

_POLLER_INDEX_DDL = """
create index if not exists poller_data_object_polled_idx
    on poller (data_object_id, polled_at_utc desc, id desc)
"""


class StateStore(Protocol):
    def last_marker(self, data_object_id: str) -> str | None: ...
    def append(self, result: "PollResult") -> None: ...


def default_postgres_dsn() -> str:
    direct = os.getenv("POSTGRES_DSN")
    if direct:
        return direct
    host = os.getenv("POSTGRES_HOST", "localhost:5432")
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    database = os.getenv("POSTGRES_DB", "data_solution")
    return f"postgresql://{user}:{password}@{host}/{database}"


class PostgresStateStore:
    """Append poll results to Postgres table ``poller``."""

    def __init__(self, dsn: str) -> None:
        self._dsn = dsn
        self._conn = self._connect(dsn)
        self._ensure_schema()

    @staticmethod
    def _connect(dsn: str):
        try:
            import psycopg  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "Postgres metadata store requires 'psycopg'. "
                "Install with: pip install psycopg[binary]"
            ) from exc
        return psycopg.connect(dsn)

    def _ensure_schema(self) -> None:
        with self._conn.cursor() as cur:
            cur.execute(_POLLER_DDL)
            cur.execute(_POLLER_INDEX_DDL)
        self._conn.commit()

    def last_marker(self, data_object_id: str) -> str | None:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                select new_marker
                from poller
                where data_object_id = %s
                order by polled_at_utc desc, id desc
                limit 1
                """,
                (data_object_id,),
            )
            row = cur.fetchone()
        return str(row[0]) if row else None

    def append(self, result: "PollResult") -> None:
        polled_at = result.event_time_utc
        with self._conn.cursor() as cur:
            cur.execute(
                """
                insert into poller (
                    event_id,
                    run_id,
                    data_object_id,
                    source_data_object_id,
                    target_data_object_id,
                    event_type,
                    polled_at_utc,
                    old_marker,
                    new_marker
                )
                values (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    result.event_id,
                    result.run_id,
                    result.data_object_id,
                    result.source_data_object_id,
                    result.target_data_object_id,
                    result.event_type,
                    polled_at,
                    result.previous_marker,
                    result.current_marker,
                ),
            )
        self._conn.commit()
