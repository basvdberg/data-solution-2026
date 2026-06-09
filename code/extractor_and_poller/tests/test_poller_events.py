"""Tests for poller event publishers."""

from __future__ import annotations

import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from extractor_and_poller.poller.change_probe import PollResult
from extractor_and_poller.poller.events import KafkaPublisher, kafka_message_value
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

    def test_kafka_message_value_is_data_object_id_only(self) -> None:
        result = _sample_result()
        self.assertEqual(
            kafka_message_value(result),
            "source/openmeteo/daily-temperature",
        )

    @patch("extractor_and_poller.poller.events.KafkaPublisher._build_producer")
    def test_kafka_publisher_sends_data_object_id_as_value(self, mock_build) -> None:
        producer = MagicMock()
        future = MagicMock()
        producer.send.return_value = future
        mock_build.return_value = producer

        publisher = KafkaPublisher("localhost:9092")
        result = _sample_result()
        publisher.publish(result)

        producer.send.assert_called_once_with(
            POLL_TOPIC_CHANGE,
            key="source/openmeteo/daily-temperature",
            value="source/openmeteo/daily-temperature",
        )
        future.get.assert_called_once_with(timeout=10)


if __name__ == "__main__":
    unittest.main()
