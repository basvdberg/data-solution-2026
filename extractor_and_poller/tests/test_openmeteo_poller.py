"""Unit tests for Open-Meteo poller (mocked HTTP)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from extractor_and_poller.common import config as cfg_module
from extractor_and_poller.common.paths import PROJECT_ROOT
from extractor_and_poller.poller import change_probe
from extractor_and_poller.poller.events import event_payload
from extractor_and_poller.poller.state import FileStateStore, PollerLogEntry
from extractor_and_poller.openmeteo.poller import probe as openmeteo_probe


OPENMETEO_FIXTURE = {
    "daily": {
        "time": ["2026-05-20", "2026-05-21", "2026-05-22", "2026-05-26"],
        "temperature_2m_mean": [12.1, 13.2, 14.0, 15.0],
    }
}


class TestOpenMeteoPoller(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config_path = (
            PROJECT_ROOT
            / "data-object-mapping"
            / "staging"
            / "openmeteo"
            / "daily-temperature.json"
        )
        cls.config = cfg_module.load(str(cls.config_path))
        cls.mapping = cls.config.get_mapping("data-object-mapping/staging/openmeteo/daily-temperature")
        assert cls.mapping is not None

    @patch("extractor_and_poller.openmeteo.extractor.client.requests.get")
    def test_probe_returns_latest_completed_day(self, mock_get) -> None:
        mock_resp = mock_get.return_value
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = OPENMETEO_FIXTURE

        marker = openmeteo_probe.probe(self.mapping, self.config)

        self.assertEqual(marker, "2026-05-26")
        mock_get.assert_called_once()

    @patch("extractor_and_poller.openmeteo.extractor.client.requests.get")
    def test_poll_mapping_detects_change(self, mock_get) -> None:
        mock_resp = mock_get.return_value
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = OPENMETEO_FIXTURE

        result = change_probe.poll_mapping(
            self.mapping,
            self.config,
            run_id="run-1",
            previous_marker="2026-05-21",
        )

        self.assertTrue(result.changed)
        self.assertEqual(result.event_type, "data_object_change")
        self.assertEqual(result.current_marker, "2026-05-26")

    @patch("extractor_and_poller.openmeteo.extractor.client.requests.get")
    def test_poll_mapping_unchanged_when_marker_same(self, mock_get) -> None:
        mock_resp = mock_get.return_value
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = OPENMETEO_FIXTURE

        result = change_probe.poll_mapping(
            self.mapping,
            self.config,
            run_id="run-1",
            previous_marker="2026-05-26",
        )

        self.assertFalse(result.changed)
        self.assertEqual(result.event_type, "data_object_unchanged")

    @patch("extractor_and_poller.openmeteo.extractor.client.requests.get")
    def test_file_log_table_appends_poll_entry(self, mock_get) -> None:
        mock_resp = mock_get.return_value
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = OPENMETEO_FIXTURE

        with tempfile.TemporaryDirectory() as tmp:
            state_path = Path(tmp) / "daily_temperature" / "data-object-poller-log.csv"
            store = FileStateStore(state_path)
            store.append(
                PollerLogEntry(
                    event_type="data_object_change",
                    polled_at_utc="2026-05-26T00:00:00+00:00",
                    old_marker=None,
                    new_marker="2026-05-21",
                )
            )

            result = change_probe.poll_mapping(
                self.mapping,
                self.config,
                run_id="run-1",
                previous_marker=store.last_marker(),
            )
            store.append(PollerLogEntry.from_poll_result(result))
            store.save()

            lines = state_path.read_text(encoding="utf-8").splitlines()
            self.assertGreaterEqual(len(lines), 3)
            self.assertEqual(
                lines[0],
                "event_type,polled_at_utc,old_marker,new_marker",
            )
            self.assertIn("2026-05-21", lines[-1])
            self.assertIn("2026-05-26", lines[-1])

    @patch("extractor_and_poller.openmeteo.extractor.client.requests.get")
    def test_event_payload_contract_fields(self, mock_get) -> None:
        mock_resp = mock_get.return_value
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = OPENMETEO_FIXTURE

        result = change_probe.poll_mapping(
            self.mapping,
            self.config,
            run_id="run-42",
            previous_marker="2026-05-21",
        )
        payload = event_payload(result)

        self.assertEqual(payload["run_id"], "run-42")
        self.assertEqual(
            payload["data_object_id"],
            "source/openmeteo/daily-temperature",
        )
        self.assertEqual(
            payload["source_data_object_id"],
            "source/openmeteo/daily-temperature",
        )
        self.assertEqual(
            payload["target_data_object_id"],
            "staging/openmeteo/daily-temperature",
        )
        self.assertEqual(payload["event_type"], "data_object_change")
        self.assertEqual(payload["current_marker"], "2026-05-26")
        self.assertEqual(payload["previous_marker"], "2026-05-21")


if __name__ == "__main__":
    unittest.main()
