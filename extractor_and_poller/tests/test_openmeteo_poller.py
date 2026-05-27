"""Unit tests for Open-Meteo poller (mocked HTTP)."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from extractor_and_poller.common import config as cfg_module
from extractor_and_poller.common.paths import PROJECT_ROOT
from extractor_and_poller.poller import change_probe
from extractor_and_poller.poller.state import FileStateStore
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

        self.assertEqual(marker, "2026-05-22")
        mock_get.assert_called_once()

    @patch("extractor_and_poller.openmeteo.extractor.client.requests.get")
    def test_poll_mapping_detects_change(self, mock_get) -> None:
        mock_resp = mock_get.return_value
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = OPENMETEO_FIXTURE

        result = change_probe.poll_mapping(
            self.mapping,
            self.config,
            previous_marker="2026-05-21",
        )

        self.assertTrue(result.changed)
        self.assertEqual(result.event_type, "data_object_change")
        self.assertEqual(result.current_marker, "2026-05-22")

    @patch("extractor_and_poller.openmeteo.extractor.client.requests.get")
    def test_poll_mapping_progress_when_unchanged(self, mock_get) -> None:
        mock_resp = mock_get.return_value
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = OPENMETEO_FIXTURE

        result = change_probe.poll_mapping(
            self.mapping,
            self.config,
            previous_marker="2026-05-22",
        )

        self.assertFalse(result.changed)
        self.assertEqual(result.event_type, "data_object_progress")

    @patch("extractor_and_poller.openmeteo.extractor.client.requests.get")
    def test_file_state_updates_on_change(self, mock_get) -> None:
        mock_resp = mock_get.return_value
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = OPENMETEO_FIXTURE

        with tempfile.TemporaryDirectory() as tmp:
            state_path = Path(tmp) / ".poller-state.json"
            store = FileStateStore(state_path)
            store.set(self.mapping.id, "2026-05-21")

            result = change_probe.poll_mapping(
                self.mapping,
                self.config,
                previous_marker=store.get(self.mapping.id),
            )
            if result.changed:
                store.set(result.mapping_id, result.current_marker)
            store.save()

            saved = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(saved[self.mapping.id], "2026-05-22")


if __name__ == "__main__":
    unittest.main()
