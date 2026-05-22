"""Simple file-backed last-known state for local poller runs."""

from __future__ import annotations

import json
from pathlib import Path


class FileStateStore:
    """JSON file keyed by mapping_id (Airflow uses PostgreSQL change_state)."""

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)

    def _load(self) -> dict[str, str]:
        if not self._path.exists():
            return {}
        with open(self._path, encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data: dict[str, str]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def get(self, mapping_id: str) -> str | None:
        return self._load().get(mapping_id)

    def set(self, mapping_id: str, value: str) -> None:
        data = self._load()
        data[mapping_id] = value
        self._save(data)
