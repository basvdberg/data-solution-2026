"""Tests for extract audit orchestration event metadata."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from extractor_and_poller.extract.audit import ExtractRunAudit, event_type_for_status
from extractor_and_poller.poller.poll_events import (
    EVENT_TYPE_CHANGE,
    EVENT_TYPE_PROCESSING_ERROR,
)


class TestExtractAudit(unittest.TestCase):
    def test_event_type_for_status(self) -> None:
        self.assertEqual(event_type_for_status("success"), EVENT_TYPE_CHANGE)
        self.assertEqual(event_type_for_status("failed"), EVENT_TYPE_PROCESSING_ERROR)
        self.assertEqual(event_type_for_status("running"), "")

    @patch("extractor_and_poller.extract.audit.ExtractRunAudit._connect")
    def test_finish_sets_event_type_on_success(self, mock_connect) -> None:
        conn = MagicMock()
        cursor = MagicMock()
        mock_connect.return_value = conn
        conn.cursor.return_value.__enter__.return_value = cursor
        cursor.fetchone.side_effect = [(1,)]  # table exists

        audit = ExtractRunAudit("postgresql://example")
        event_type = audit.finish(
            "run-1",
            status="success",
            output_table="staging.openmeteo_daily_temperature",
            row_count=8,
        )

        self.assertEqual(event_type, EVENT_TYPE_CHANGE)
        update_sql = cursor.execute.call_args_list[-1][0][0]
        self.assertIn("event_type", update_sql)

    @patch("extractor_and_poller.extract.audit.ExtractRunAudit._connect")
    def test_finish_sets_processing_error_on_failure(self, mock_connect) -> None:
        conn = MagicMock()
        cursor = MagicMock()
        mock_connect.return_value = conn
        conn.cursor.return_value.__enter__.return_value = cursor
        cursor.fetchone.side_effect = [(1,)]

        audit = ExtractRunAudit("postgresql://example")
        event_type = audit.finish(
            "run-1",
            status="failed",
            output_table="",
            row_count=0,
        )

        self.assertEqual(event_type, EVENT_TYPE_PROCESSING_ERROR)


if __name__ == "__main__":
    unittest.main()
