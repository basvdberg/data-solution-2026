"""Tests for Postgres staging reload."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock

from extractor_and_poller.common.postgres_load import columns_from_data_object, reload_staging_table


class TestPostgresLoad(unittest.TestCase):
    def test_columns_from_data_object_orders_by_ordinal(self) -> None:
        data_object = {
            "id": "staging/openmeteo/daily-temperature",
            "dataItems": [
                {"name": "value", "ordinalPosition": 2, "dataType": "double"},
                {"name": "station_id", "ordinalPosition": 1, "dataType": "string"},
            ],
        }
        self.assertEqual(
            columns_from_data_object(data_object),
            [("station_id", "text"), ("value", "double precision")],
        )

    def test_reload_staging_table_truncates_and_inserts(self) -> None:
        conn = MagicMock()
        cursor = MagicMock()
        conn.cursor.return_value.__enter__.return_value = cursor

        records = [{"station_id": "AMS", "value": 12.5}]
        qualified, row_count = reload_staging_table(
            conn,
            source_data_object_id="source/openmeteo/daily-temperature",
            columns=[("station_id", "text"), ("value", "double precision")],
            records=records,
        )

        self.assertEqual(qualified, "staging.openmeteo_daily_temperature")
        self.assertEqual(row_count, 1)
        executed_sql = " ".join(str(call.args[0]) for call in cursor.execute.call_args_list)
        self.assertIn("truncate", executed_sql.lower())
        cursor.executemany.assert_called_once()
        conn.commit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
