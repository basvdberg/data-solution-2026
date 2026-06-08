"""Tests for shared logging configuration."""

from __future__ import annotations

import logging
import os
import unittest

from extractor_and_poller.common.logging_setup import configure_logging, running_in_airflow_task


class TestLoggingSetup(unittest.TestCase):
    def tearDown(self) -> None:
        os.environ.pop("AIRFLOW_CTX_DAG_ID", None)
        root = logging.getLogger()
        root.handlers.clear()
        root.setLevel(logging.WARNING)

    def test_running_in_airflow_task_detects_context_env(self) -> None:
        self.assertFalse(running_in_airflow_task())
        os.environ["AIRFLOW_CTX_DAG_ID"] = "demo"
        self.assertTrue(running_in_airflow_task())

    def test_configure_logging_preserves_handlers_under_airflow(self) -> None:
        root = logging.getLogger()
        sentinel = logging.StreamHandler()
        root.addHandler(sentinel)

        os.environ["AIRFLOW_CTX_DAG_ID"] = "openmeteo_data_object_poller"
        configure_logging(verbose=True)

        self.assertIn(sentinel, root.handlers)
        self.assertEqual(root.level, logging.DEBUG)

    def test_configure_logging_replaces_handlers_for_cli(self) -> None:
        root = logging.getLogger()
        sentinel = logging.StreamHandler()
        root.addHandler(sentinel)

        configure_logging()

        self.assertNotIn(sentinel, root.handlers)
        self.assertEqual(len(root.handlers), 1)


if __name__ == "__main__":
    unittest.main()
