"""Tests for extract conf from Airflow asset event extra."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

AIRFLOW_INCLUDE = Path(__file__).resolve().parents[2] / "airflow"
if str(AIRFLOW_INCLUDE) not in sys.path:
    sys.path.insert(0, str(AIRFLOW_INCLUDE))

from include.asset_conf import extract_conf_from_asset_extra, mapping_for_data_object


class TestExtractConfFromAssetExtra(unittest.TestCase):
    def test_accepts_change_extra(self) -> None:
        extra = {
            "data_object_id": "source/openmeteo/daily-temperature",
            "event_type": "data_object_change",
            "marker": "2026-05-26",
            "event_id": "evt-1",
            "mapping_id": "daily-temperature",
        }
        self.assertEqual(
            extract_conf_from_asset_extra(extra),
            {
                "mapping_id": "daily-temperature",
                "marker": "2026-05-26",
                "data_object_id": "source/openmeteo/daily-temperature",
                "event_id": "evt-1",
            },
        )

    def test_resolves_mapping_when_missing(self) -> None:
        extra = {
            "data_object_id": "source/openmeteo/daily-temperature",
            "event_type": "data_object_change",
            "marker": "2026-05-26",
            "event_id": "evt-1",
        }
        with patch(
            "include.asset_conf.mapping_for_data_object",
            return_value="daily-temperature",
        ):
            result = extract_conf_from_asset_extra(extra)
        self.assertEqual(result["mapping_id"], "daily-temperature")

    def test_ignores_unchanged_extra(self) -> None:
        extra = {
            "data_object_id": "source/openmeteo/daily-temperature",
            "event_type": "data_object_unchanged",
            "marker": "2026-05-26",
        }
        self.assertIsNone(extract_conf_from_asset_extra(extra))

    def test_rejects_empty_extra(self) -> None:
        self.assertIsNone(extract_conf_from_asset_extra(None))
        self.assertIsNone(extract_conf_from_asset_extra({}))


class TestMappingForDataObject(unittest.TestCase):
    @patch("extractor_and_poller.common.config.load")
    def test_resolves_mapping_slug(self, mock_load) -> None:
        mapping = MagicMock()
        mapping.enabled = True
        mapping.primary_source_data_object_id.return_value = "source/openmeteo/daily-temperature"
        mapping.id = "staging/openmeteo/daily-temperature"

        config = MagicMock()
        config.enabled_mappings.return_value = [mapping]
        mock_load.return_value = config

        result = mapping_for_data_object("ignored.json", "source/openmeteo/daily-temperature")
        self.assertEqual(result, "daily-temperature")


if __name__ == "__main__":
    unittest.main()
