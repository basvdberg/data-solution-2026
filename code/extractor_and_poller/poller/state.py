"""Postgres-backed poller execution log (table ``poller``)."""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, Protocol

from extractor_and_poller.common.postgres_schema import ensure_metadata_schema

if TYPE_CHECKING:
    from extractor_and_poller.poller.change_probe import PollResult

log = logging.getLogger(__name__)

_POLLER_TABLE = "public.poller"


class StateStore(Protocol):
    def last_marker(self, data_object_id: str) -> str | None: ...
    def append(self, result: "PollResult") -> int: ...


def default_postgres_dsn() -> str:
    direct = os.getenv("POSTGRES_DSN")
    if direct:
        return direct
    host = os.getenv("POSTGRES_HOST") or "localhost:5432"
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    database = os.getenv("DATA_SOLUTION_DB") or os.getenv(
        "POSTGRES_DB", "data-solution-2026"
    )
    return f"postgresql://{user}:{password}@{host}/{database}"


def _is_insufficient_privilege(exc: BaseException) -> bool:
    try:
        from psycopg import errors as pg_errors  # type: ignore
    except Exception:
        return exc.__class__.__name__ == "InsufficientPrivilege"
    return isinstance(exc, pg_errors.InsufficientPrivilege)


class PostgresStateStore:
    """Append poll results to Postgres table ``poller``."""

    def __init__(self, dsn: str) -> None:
        self._dsn = dsn
        log.info("Connecting to Postgres metadata store")
        self._conn = self._connect(dsn)
        self._ensure_schema()
        log.info("Postgres metadata store ready (table public.poller)")

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

    def _poller_table_exists(self) -> bool:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                select 1
                from information_schema.tables
                where table_schema = 'public' and table_name = 'poller'
                """
            )
            return cur.fetchone() is not None

    def _ensure_schema(self) -> None:
        log.info("Ensuring Postgres metadata schema")
        try:
            ensure_metadata_schema(self._conn)
        except Exception as exc:
            if _is_insufficient_privilege(exc):
                raise RuntimeError(
                    "Cannot initialize poller metadata schema (permission denied on public). "
                    "Run infra/postgres/create-app-user.sh (grants CREATE on schema public) "
                    "or apply code/postgres/schema.sql as postgres."
                ) from exc
            raise RuntimeError(
                f"Failed to initialize Postgres metadata schema: {exc}"
            ) from exc

        if not self._poller_table_exists():
            raise RuntimeError(
                "Postgres metadata schema was applied but table public.poller is still missing"
            )
        log.info("Postgres metadata schema ready (table public.poller)")
        self._verify_table_writable()

    def _verify_table_writable(self) -> None:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                select has_table_privilege(current_user, %s, 'INSERT')
                """,
                (_POLLER_TABLE,),
            )
            row = cur.fetchone()
        if not row or not row[0]:
            raise RuntimeError(
                f"Current Postgres user cannot INSERT into {_POLLER_TABLE}. "
                "Run infra/postgres/create-app-user.sh to apply grants."
            )

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

    def append(self, result: "PollResult") -> int:
        polled_at = result.event_time_utc
        with self._conn.cursor() as cur:
            cur.execute(
                """
                insert into poller (
                    polled_at_utc,
                    data_object_id,
                    event_type,
                    change_scope,
                    old_marker,
                    new_marker,
                    event_id,
                    run_id
                )
                values (%s, %s, %s, %s, %s, %s, %s, %s)
                returning id
                """,
                (
                    polled_at,
                    result.data_object_id,
                    result.event_type,
                    result.change_scope,
                    result.previous_marker,
                    result.current_marker,
                    result.event_id,
                    result.run_id,
                ),
            )
            row = cur.fetchone()
        if not row:
            self._conn.rollback()
            raise RuntimeError("Insert into public.poller returned no row id")
        self._conn.commit()
        return int(row[0])
