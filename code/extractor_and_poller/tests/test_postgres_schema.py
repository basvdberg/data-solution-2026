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
        self.assertIn("poller_data_object_polled_idx", sql.lower())

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
