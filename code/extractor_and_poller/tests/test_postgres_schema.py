"""Tests for Postgres metadata schema loading."""

from __future__ import annotations

import unittest

from extractor_and_poller.common.postgres_schema import (
    load_schema_sql,
    schema_statements,
)


class TestPostgresSchema(unittest.TestCase):
    def test_load_schema_sql_contains_poller_table(self) -> None:
        sql = load_schema_sql()
        self.assertIn("create table if not exists poller", sql.lower())
        self.assertIn("change_scope", sql.lower())
        self.assertIn("poller_data_object_polled_idx", sql.lower())

    def test_poller_table_lists_correlation_columns_last(self) -> None:
        sql = load_schema_sql().lower()
        new_marker_pos = sql.index("new_marker")
        event_id_pos = sql.index("event_id")
        run_id_pos = sql.index("run_id")
        self.assertLess(new_marker_pos, event_id_pos)
        self.assertLess(event_id_pos, run_id_pos)

    def test_schema_statements_split_script(self) -> None:
        statements = schema_statements(
            """
            -- comment
            create table if not exists poller (id int);
            create index if not exists poller_idx on poller (id);
            """
        )
        self.assertEqual(len(statements), 2)
        self.assertTrue(statements[0].startswith("create table"))
        self.assertTrue(statements[1].startswith("create index"))


if __name__ == "__main__":
    unittest.main()
