"""Load extractor records into Postgres staging tables (truncate + reload)."""

from __future__ import annotations

import logging
from typing import Any, Mapping, Sequence

from psycopg import sql

from extractor_and_poller.common.staging_table import STAGING_SCHEMA, staging_table_name

log = logging.getLogger(__name__)

_DSA_TO_PG: dict[str, str] = {
    "string": "text",
    "double": "double precision",
    "integer": "bigint",
    "boolean": "boolean",
}


def pg_type_for_data_item(data_type: str) -> str:
    pg_type = _DSA_TO_PG.get(data_type.lower())
    if pg_type is None:
        raise ValueError(f"Unsupported data item type for Postgres load: {data_type!r}")
    return pg_type


def columns_from_data_object(data_object: Mapping[str, Any]) -> list[tuple[str, str]]:
    """Ordered ``(column_name, pg_type)`` from a resolved DSA data object."""
    items = sorted(
        data_object.get("dataItems", []),
        key=lambda item: int(item.get("ordinalPosition", 0)),
    )
    columns: list[tuple[str, str]] = []
    for item in items:
        name = str(item.get("name") or item.get("id", "").split("/")[-1])
        data_type = str(item.get("dataType", "string"))
        columns.append((name, pg_type_for_data_item(data_type)))
    if not columns:
        raise ValueError(f"Data object {data_object.get('id')!r} has no dataItems")
    return columns


def reload_staging_table(
    conn,
    *,
    source_data_object_id: str,
    columns: Sequence[tuple[str, str]],
    records: Sequence[Mapping[str, Any]],
) -> tuple[str, int]:
    """Ensure ``staging.<source>_<table>`` exists, truncate it, and insert ``records``."""
    schema = STAGING_SCHEMA
    table = staging_table_name(source_data_object_id)
    column_names = [name for name, _ in columns]

    with conn.cursor() as cur:
        cur.execute(
            """
            select 1
            from information_schema.schemata
            where schema_name = %s
            """,
            (schema,),
        )
        if cur.fetchone() is None:
            cur.execute(
                sql.SQL("create schema {}").format(sql.Identifier(schema))
            )
        cur.execute(
            sql.SQL("create table if not exists {}.{} ({})").format(
                sql.Identifier(schema),
                sql.Identifier(table),
                sql.SQL(", ").join(
                    sql.SQL("{} {}").format(sql.Identifier(name), sql.SQL(pg_type))
                    for name, pg_type in columns
                ),
            )
        )
        cur.execute(
            sql.SQL("truncate table {}.{}").format(
                sql.Identifier(schema),
                sql.Identifier(table),
            )
        )
        if records:
            placeholders = sql.SQL(", ").join(sql.Placeholder() * len(column_names))
            insert_stmt = sql.SQL("insert into {}.{} ({}) values ({})").format(
                sql.Identifier(schema),
                sql.Identifier(table),
                sql.SQL(", ").join(sql.Identifier(name) for name in column_names),
                placeholders,
            )
            rows = [
                tuple(record.get(name) for name in column_names)
                for record in records
            ]
            cur.executemany(insert_stmt, rows)

    conn.commit()
    qualified = f"{schema}.{table}"
    row_count = len(records)
    log.info("Reloaded %s (%s rows)", qualified, f"{row_count:,}")
    return qualified, row_count
