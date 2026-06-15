"""Tests for poller event envelopes."""

from __future__ import annotations

import json
import unittest
from datetime import datetime, timezone

from extractor_and_poller.poller.change_probe import PollResult
from extractor_and_poller.poller.events import poll_event_json, poll_event_payload
from extractor_and_poller.poller.poll_events import EVENT_TYPE_CHANGE, EVENT_TYPE_PROGRESS
from include.data_object_asset_uris import change_asset_uri


def _sample_result() -> PollResult:
    return PollResult(
        event_id="evt-1",
        run_id="run-1",
        data_object_id="source/openmeteo/daily-temperature",
        source_data_object_id="source/openmeteo/daily-temperature",
        target_data_object_id="staging/openmeteo/daily-temperature",
        current_marker="2026-05-26",
        previous_marker="2026-05-21",
        event_time_utc=datetime(2026, 5, 26, tzinfo=timezone.utc),
        event_type=EVENT_TYPE_CHANGE,
    )


class TestPollerEvents(unittest.TestCase):
    def test_change_asset_uri(self) -> None:
        self.assertEqual(
            change_asset_uri("source/openmeteo/daily-temperature"),
            "ds://source/openmeteo/daily-temperature/change",
        )

    def test_poll_event_payload_contains_envelope_fields(self) -> None:
        result = _sample_result()
        self.assertEqual(
            poll_event_payload(result),
            {
                "data_object_id": "source/openmeteo/daily-temperature",
                "event_type": EVENT_TYPE_CHANGE,
                "event_time_utc": "2026-05-26T00:00:00+00:00",
                "old_marker": "2026-05-21",
                "new_marker": "2026-05-26",
                "event_id": "evt-1",
            },
        )

    def test_poll_event_json_is_json_envelope(self) -> None:
        result = _sample_result()
        payload = json.loads(poll_event_json(result))
        self.assertEqual(payload["data_object_id"], "source/openmeteo/daily-temperature")
        self.assertEqual(payload["event_type"], EVENT_TYPE_CHANGE)
        self.assertEqual(payload["old_marker"], "2026-05-21")
        self.assertEqual(payload["new_marker"], "2026-05-26")
        self.assertIn("event_time_utc", payload)

    def test_progress_event_type_constant(self) -> None:
        self.assertEqual(EVENT_TYPE_PROGRESS, "data_object_progress")


if __name__ == "__main__":
    unittest.main()
