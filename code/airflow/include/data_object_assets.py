"""Airflow Asset objects for data-object orchestration signals."""

from __future__ import annotations

from airflow.sdk import Asset

from include.data_object_asset_uris import change_asset_uri


def change_asset(data_object_id: str, *, name: str | None = None) -> Asset:
    """Build an Airflow Asset for a source data object change signal."""
    uri = change_asset_uri(data_object_id)
    if name is None:
        name = data_object_id.replace("/", "_") + "_change"
    return Asset(uri=uri, name=name)
