"""Tests for staging Postgres table naming."""

from __future__ import annotations

import unittest

from extractor_and_poller.common.staging_table import (
    qualified_staging_table,
    staging_table_name,
)


class TestStagingTable(unittest.TestCase):
    def test_staging_table_name_from_source_data_object_id(self) -> None:
        self.assertEqual(
            staging_table_name("source/openmeteo/daily-temperature"),
            "openmeteo_daily_temperature",
        )

    def test_qualified_staging_table(self) -> None:
        self.assertEqual(
            qualified_staging_table("source/openmeteo/daily-temperature"),
            "staging.openmeteo_daily_temperature",
        )

    def test_invalid_source_data_object_id_raises(self) -> None:
        with self.assertRaises(ValueError):
            staging_table_name("staging/openmeteo/daily-temperature")


if __name__ == "__main__":
    unittest.main()
