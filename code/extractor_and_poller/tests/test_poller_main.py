"""Tests for poller CLI exit codes and Postgres persistence checks."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from extractor_and_poller.poller import __main__ as poller_main


class TestPollerMain(unittest.TestCase):
    @patch("extractor_and_poller.poller.state.PostgresStateStore")
    @patch("extractor_and_poller.common.config.load")
    @patch("extractor_and_poller.poller.change_probe.iter_poll_results")
    def test_main_fails_when_no_rows_persisted(
        self,
        mock_iter_results,
        mock_load,
        mock_store_cls,
    ) -> None:
        mapping = MagicMock()
        mapping.enabled = True
        mapping.primary_source_data_object_id.return_value = "source/openmeteo/daily-temperature"

        config = MagicMock()
        config.enabled_mappings.return_value = [mapping]
        config.get_mapping.return_value = mapping
        mock_load.return_value = config

        store = MagicMock()
        store.last_marker.return_value = None
        mock_store_cls.return_value = store
        mock_iter_results.return_value = iter([])

        exit_code = poller_main.main(
            [
                "--config",
                "ignored.json",
                "--data-object",
                "source/openmeteo/daily-temperature",
            ]
        )

        self.assertEqual(exit_code, 3)
        store.append.assert_not_called()


if __name__ == "__main__":
    unittest.main()
