"""Baseline storage for local poller runs."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Protocol

log = logging.getLogger(__name__)


class StateStore(Protocol):
    def get(self, mapping_id: str) -> str | None: ...

    def set(self, mapping_id: str, marker: str) -> None: ...


class FileStateStore:
    """Persist last-known markers in a JSON file (``data/.poller-state.json``)."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._data: dict[str, str] = {}
        self._load()

    def _load(self) -> None:
        if not self._path.is_file():
            return
        try:
            raw = json.loads(self._path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            log.warning("Could not read poller state %s: %s", self._path, exc)
            return
        if isinstance(raw, dict):
            self._data = {str(k): str(v) for k, v in raw.items()}

    def save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            json.dumps(self._data, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def get(self, mapping_id: str) -> str | None:
        return self._data.get(mapping_id)

    def set(self, mapping_id: str, marker: str) -> None:
        self._data[mapping_id] = marker
