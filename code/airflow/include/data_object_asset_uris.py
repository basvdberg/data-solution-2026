"""Airflow Asset URI helpers for data-object orchestration signals."""

from __future__ import annotations

ASSET_SCHEME = "ds"


def change_asset_uri(data_object_id: str) -> str:
    """URI for a source data object change signal."""
    return f"{ASSET_SCHEME}://{data_object_id}/change"
