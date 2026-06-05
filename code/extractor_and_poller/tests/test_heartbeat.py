"""Tests for early progress logging (within 2s of start, not periodic)."""

from __future__ import annotations

import logging
import time
import unittest

from extractor_and_poller.common.heartbeat import EarlyProgressLog


class TestEarlyProgressLog(unittest.TestCase):
    def test_logs_started_message_immediately(self) -> None:
        logger = logging.getLogger("test.early.start")
        with self.assertLogs(logger, level="INFO") as captured:
            with EarlyProgressLog(logger, "task invoked", within_sec=10.0):
                pass

        self.assertEqual(captured.records[0].getMessage(), "task invoked")

    def test_logs_pending_once_after_interval(self) -> None:
        logger = logging.getLogger("test.early.pending")
        with self.assertLogs(logger, level="INFO") as captured:
            with EarlyProgressLog(
                logger,
                "task invoked",
                pending_message="still running",
                within_sec=0.05,
            ):
                time.sleep(0.12)

        messages = [r.getMessage() for r in captured.records]
        self.assertEqual(messages[0], "task invoked")
        self.assertEqual(messages.count("still running"), 1)

    def test_no_pending_when_finished_before_interval(self) -> None:
        logger = logging.getLogger("test.early.fast")
        with self.assertLogs(logger, level="INFO") as captured:
            with EarlyProgressLog(
                logger,
                "task invoked",
                pending_message="still running",
                within_sec=0.5,
            ):
                pass

        messages = [r.getMessage() for r in captured.records]
        self.assertEqual(messages, ["task invoked"])


if __name__ == "__main__":
    unittest.main()
