"""Staging Postgres table naming from source data object ids."""

from __future__ import annotations

STAGING_SCHEMA = "staging"


def staging_table_name(source_data_object_id: str) -> str:
    """Return ``{source}_{table_name}`` for a path id like ``source/openmeteo/daily-temperature``."""
    parts = source_data_object_id.strip("/").split("/")
    if len(parts) < 3 or parts[0] != "source":
        raise ValueError(
            f"Expected source data object id 'source/<source>/<table>', got {source_data_object_id!r}"
        )
    source_name = parts[1].replace("-", "_")
    table_name = parts[2].replace("-", "_")
    return f"{source_name}_{table_name}"


def qualified_staging_table(source_data_object_id: str) -> str:
    """Fully qualified ``staging.<source>_<table>`` name."""
    return f"{STAGING_SCHEMA}.{staging_table_name(source_data_object_id)}"
