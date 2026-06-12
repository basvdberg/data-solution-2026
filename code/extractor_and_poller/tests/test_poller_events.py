"""Tests for poller event envelopes."""

from __future__ import annotations

import json
import unittest
from datetime import datetime, timezone

from extractor_and_poller.poller.change_probe import PollResult
from extractor_and_poller.poller.events import kafka_event_payload, kafka_message_value
from extractor_and_poller.poller.kafka_topic import (
    EVENT_TYPE_PROGRESS,
    POLL_TOPIC_CHANGE,
    POLL_TOPIC_PROGRESS,
    kafka_topic_for_event,
)


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
        event_type="data_object_change",
    )


class TestPollerEvents(unittest.TestCase):
    def test_kafka_topic_for_poll_event_types(self) -> None:
        self.assertEqual(
            kafka_topic_for_event("data_object_change"),
            POLL_TOPIC_CHANGE,
        )
        self.assertEqual(
            kafka_topic_for_event(EVENT_TYPE_PROGRESS),
            POLL_TOPIC_PROGRESS,
        )

    def test_kafka_event_payload_contains_envelope_fields(self) -> None:
        result = _sample_result()
        self.assertEqual(
            kafka_event_payload(result),
            {
                "data_object_id": "source/openmeteo/daily-temperature",
                "event_type": "data_object_change",
                "event_time_utc": "2026-05-26T00:00:00+00:00",
                "old_marker": "2026-05-21",
                "new_marker": "2026-05-26",
                "event_id": "evt-1",
            },
        )

    def test_kafka_message_value_is_json_envelope(self) -> None:
        result = _sample_result()
        payload = json.loads(kafka_message_value(result))
        self.assertEqual(payload["data_object_id"], "source/openmeteo/daily-temperature")
        self.assertEqual(payload["event_type"], "data_object_change")
        self.assertEqual(payload["old_marker"], "2026-05-21")
        self.assertEqual(payload["new_marker"], "2026-05-26")
        self.assertIn("event_time_utc", payload)


if __name__ == "__main__":
    unittest.main()
