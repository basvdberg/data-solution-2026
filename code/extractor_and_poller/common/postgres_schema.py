"""Postgres DDL for poller metadata (source: ``code/postgres/schema.sql``)."""

from __future__ import annotations

from pathlib import Path

from extractor_and_poller.common.paths import CODE_ROOT

# Kept in sync with code/postgres/schema.sql for environments where only the
# Python package is on PYTHONPATH (no dependency on the solution ``data/`` tree).
_EMBEDDED_SCHEMA_SQL = """
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
);

create index if not exists poller_data_object_polled_idx
    on poller (data_object_id, polled_at_utc desc, id desc);
""".strip()

_SCHEMA_PATH = CODE_ROOT / "postgres" / "schema.sql"


def load_schema_sql() -> str:
    """Return the full Postgres metadata schema script."""
    if _SCHEMA_PATH.is_file():
        return _SCHEMA_PATH.read_text(encoding="utf-8-sig").strip()
    return _EMBEDDED_SCHEMA_SQL


def schema_statements(sql: str | None = None) -> list[str]:
    """Split a schema script into executable statements (comments stripped)."""
    script = (sql if sql is not None else load_schema_sql()).strip()
    statements: list[str] = []
    for part in script.split(";"):
        lines = [
            line
            for line in part.splitlines()
            if line.strip() and not line.strip().startswith("--")
        ]
        stmt = "\n".join(lines).strip()
        if stmt:
            statements.append(stmt)
    return statements
