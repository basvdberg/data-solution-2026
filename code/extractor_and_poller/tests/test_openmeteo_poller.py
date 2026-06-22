"""Unit tests for Open-Meteo poller (mocked HTTP and Postgres)."""

from __future__ import annotations

import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from extractor_and_poller.common import config as cfg_module
from extractor_and_poller.common.paths import PROJECT_ROOT
from extractor_and_poller.poller import change_probe
from extractor_and_poller.poller.events import event_payload
from extractor_and_poller.poller.state import PostgresStateStore
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
        self.assertEqual(result.change_scope, "incremental_update")
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
        self.assertIsNone(result.change_scope)

    @patch("extractor_and_poller.poller.state.PostgresStateStore._connect")
    def test_poller_table_append_and_last_marker(self, mock_connect) -> None:
        conn = MagicMock()
        cursor = MagicMock()
        mock_connect.return_value = conn
        conn.cursor.return_value.__enter__.return_value = cursor
        cursor.fetchone.side_effect = [
            (1,),  # table exists
            (True,),  # INSERT privilege
            ("2026-05-21",),  # last_marker
            (42,),  # append returning id
        ]

        store = PostgresStateStore("postgresql://example")
        self.assertEqual(
            store.last_marker("source/openmeteo/daily-temperature"),
            "2026-05-21",
        )

        result = change_probe.PollResult(
            event_id="evt-1",
            run_id="run-1",
            data_object_id="source/openmeteo/daily-temperature",
            source_data_object_id="source/openmeteo/daily-temperature",
            target_data_object_id="staging/openmeteo/daily-temperature",
            current_marker="2026-05-26",
            previous_marker="2026-05-21",
            event_time_utc=datetime(2026, 5, 26, tzinfo=timezone.utc),
            event_type="data_object_change",
            change_scope="incremental_update",
        )
        row_id = store.append(result)
        self.assertEqual(row_id, 42)

        insert_sql = cursor.execute.call_args_list[-1][0][0]
        self.assertIn("insert into poller", insert_sql.lower())
        self.assertIn("returning id", insert_sql.lower())
        insert_args = cursor.execute.call_args_list[-1][0][1]
        self.assertEqual(insert_args[1], "source/openmeteo/daily-temperature")
        self.assertEqual(insert_args[3], "incremental_update")
        self.assertEqual(insert_args[5], "2026-05-26")

    @patch("extractor_and_poller.poller.state.PostgresStateStore._connect")
    def test_poller_raises_when_table_missing(self, mock_connect) -> None:
        conn = MagicMock()
        cursor = MagicMock()
        mock_connect.return_value = conn
        conn.cursor.return_value.__enter__.return_value = cursor
        cursor.fetchone.return_value = None

        with self.assertRaisesRegex(RuntimeError, "public.poller is missing"):
            PostgresStateStore("postgresql://example")

        executed_sql = " ".join(
            call.args[0].lower() for call in cursor.execute.call_args_list
        )
        self.assertNotIn("create table", executed_sql)
        conn.commit.assert_not_called()

    @patch("extractor_and_poller.poller.state.PostgresStateStore._connect")
    def test_poller_never_runs_ddl_when_table_exists(self, mock_connect) -> None:
        conn = MagicMock()
        cursor = MagicMock()
        mock_connect.return_value = conn
        conn.cursor.return_value.__enter__.return_value = cursor
        cursor.fetchone.side_effect = [
            (1,),  # table exists
            (True,),  # INSERT privilege
        ]

        PostgresStateStore("postgresql://example")

        executed_sql = " ".join(
            call.args[0].lower() for call in cursor.execute.call_args_list
        )
        self.assertNotIn("create index if not exists poller_data_object_polled_idx", executed_sql)
        self.assertNotIn("create or replace view poller_latest_first", executed_sql)
        conn.commit.assert_not_called()

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
        self.assertEqual(payload["change_scope"], "incremental_update")
        self.assertEqual(payload["current_marker"], "2026-05-26")
        self.assertEqual(payload["previous_marker"], "2026-05-21")


if __name__ == "__main__":
    unittest.main()
