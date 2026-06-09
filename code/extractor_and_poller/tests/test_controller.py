"""Tests for Kafka controller event handling."""

from __future__ import annotations

import json
import unittest
from unittest.mock import MagicMock, patch

from extractor_and_poller.controller.events import parse_change_event
from extractor_and_poller.controller.handlers import on_data_object_change


class TestControllerEvents(unittest.TestCase):
    def test_parse_change_event_accepts_envelope(self) -> None:
        payload = {
            "data_object_id": "source/openmeteo/daily-temperature",
            "event_type": "data_object_change",
            "event_time_utc": "2026-05-26T00:00:00+00:00",
            "old_marker": "2026-05-21",
            "new_marker": "2026-05-26",
            "event_id": "evt-1",
        }
        event = parse_change_event(json.dumps(payload))
        self.assertEqual(event.data_object_id, "source/openmeteo/daily-temperature")
        self.assertEqual(event.new_marker, "2026-05-26")
        self.assertEqual(event.event_id, "evt-1")

    def test_parse_change_event_rejects_progress(self) -> None:
        payload = {
            "data_object_id": "source/openmeteo/daily-temperature",
            "event_type": "data_object_progress",
            "event_time_utc": "2026-05-26T00:00:00+00:00",
            "new_marker": "2026-05-26",
        }
        with self.assertRaises(ValueError):
            parse_change_event(json.dumps(payload))


class TestOnDataObjectChange(unittest.TestCase):
    @patch("extractor_and_poller.controller.handlers.mapping_for_data_object")
    def test_on_data_object_change_starts_extract(self, mock_mapping_for) -> None:
        mock_mapping_for.return_value = "daily-temperature"
        starter = MagicMock()
        starter.start_extract.return_value = "dag-run-1"

        payload = {
            "data_object_id": "source/openmeteo/daily-temperature",
            "event_type": "data_object_change",
            "event_time_utc": "2026-05-26T00:00:00+00:00",
            "old_marker": "2026-05-21",
            "new_marker": "2026-05-26",
            "event_id": "evt-1",
        }
        event = parse_change_event(json.dumps(payload))
        run_id = on_data_object_change(event, config_path="ignored.json", starter=starter)

        self.assertEqual(run_id, "dag-run-1")
        starter.start_extract.assert_called_once_with(
            mapping_id="daily-temperature",
            marker="2026-05-26",
            event_id="evt-1",
        )


if __name__ == "__main__":
    unittest.main()
