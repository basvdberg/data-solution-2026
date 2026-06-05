"""Tests for manual DAG trigger guard helpers (no Airflow runtime required)."""

from __future__ import annotations

import unittest
from types import SimpleNamespace

from dag_run_guard import manual_trigger_conflict_message


class TestDagRunGuard(unittest.TestCase):
    def test_manual_trigger_conflict_message(self) -> None:
        msg = manual_trigger_conflict_message(
            "openmeteo_data_object_poller",
            ["scheduled__2026-06-04T14:00:00+00:00"],
        )
        self.assertIn("Manual trigger rejected", msg)
        self.assertIn("openmeteo_data_object_poller", msg)
        self.assertIn("scheduled__2026-06-04T14:00:00+00:00", msg)

    def test_is_manual_run_detection(self) -> None:
        from dag_run_guard import _is_manual_run

        self.assertTrue(_is_manual_run(SimpleNamespace(run_type="manual")))
        self.assertFalse(_is_manual_run(SimpleNamespace(run_type="scheduled")))


if __name__ == "__main__":
    unittest.main()
