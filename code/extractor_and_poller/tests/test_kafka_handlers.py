"""Tests for native Airflow Kafka handlers."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

AIRFLOW_INCLUDE = Path(__file__).resolve().parents[2] / "airflow"
if str(AIRFLOW_INCLUDE) not in sys.path:
    sys.path.insert(0, str(AIRFLOW_INCLUDE))

from include.kafka_handlers import mapping_for_data_object, poll_change_apply_function


class TestPollChangeApplyFunction(unittest.TestCase):
    def test_accepts_change_event(self) -> None:
        payload = {
            "data_object_id": "source/openmeteo/daily-temperature",
            "event_type": "data_object_change",
            "event_time_utc": "2026-05-26T00:00:00+00:00",
            "old_marker": "2026-05-21",
            "new_marker": "2026-05-26",
            "event_id": "evt-1",
        }
        message = MagicMock()
        message.value.return_value = json.dumps(payload).encode("utf-8")

        with patch(
            "include.kafka_handlers.mapping_for_data_object",
            return_value="daily-temperature",
        ):
            result = poll_change_apply_function(message)

        self.assertEqual(
            result,
            {
                "mapping_id": "daily-temperature",
                "marker": "2026-05-26",
                "data_object_id": "source/openmeteo/daily-temperature",
                "event_id": "evt-1",
            },
        )

    def test_ignores_progress_event(self) -> None:
        payload = {
            "data_object_id": "source/openmeteo/daily-temperature",
            "event_type": "data_object_progress",
            "event_time_utc": "2026-05-26T00:00:00+00:00",
            "new_marker": "2026-05-26",
        }
        message = MagicMock()
        message.value.return_value = json.dumps(payload).encode("utf-8")
        self.assertIsNone(poll_change_apply_function(message))

    def test_rejects_invalid_json(self) -> None:
        message = MagicMock()
        message.value.return_value = b"not-json"
        self.assertIsNone(poll_change_apply_function(message))


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
