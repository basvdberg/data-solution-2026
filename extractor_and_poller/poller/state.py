"""Append-only poller execution logging backends."""

from __future__ import annotations

import csv
import logging
import os
from dataclasses import dataclass
from datetime import timezone
from pathlib import Path
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from extractor_and_poller.poller.change_probe import PollResult

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class PollerLogEntry:
    event_type: str
    polled_at_utc: str
    old_marker: str | None
    new_marker: str

    @classmethod
    def from_poll_result(cls, result: "PollResult") -> "PollerLogEntry":
        return cls(
            event_type=result.event_type,
            polled_at_utc=result.event_time_utc.astimezone(timezone.utc).isoformat(),
            old_marker=result.previous_marker,
            new_marker=result.current_marker,
        )


class StateStore(Protocol):
    def last_marker(self) -> str | None: ...
    def append(self, entry: PollerLogEntry) -> None: ...
    def save(self) -> None: ...


class FileStateStore:
    """Append poller executions to a local fixed-width CSV logging table."""

    _HEADER = [
        "event_type",
        "polled_at_utc",
        "old_marker",
        "new_marker",
    ]
    _WIDTHS = {
        "event_type": 24,
        "polled_at_utc": 30,
        "old_marker": 20,
        "new_marker": 20,
    }

    def __init__(self, path: Path) -> None:
        self._path = path
        self._rows: list[PollerLogEntry] = []
        self._latest_marker: str | None = None
        self._load()

    def _load(self) -> None:
        if not self._path.is_file():
            return
        try:
            with self._path.open("r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                loaded: list[PollerLogEntry] = []
                latest_marker: str | None = None
                for row in reader:
                    entry = PollerLogEntry(
                        event_type=(row.get("event_type") or "").strip(),
                        polled_at_utc=(row.get("polled_at_utc") or "").strip(),
                        old_marker=((row.get("old_marker") or "").strip() or None),
                        new_marker=(row.get("new_marker") or "").strip(),
                    )
                    if not entry.new_marker:
                        continue
                    loaded.append(entry)
                    latest_marker = entry.new_marker
                self._rows = loaded
                self._latest_marker = latest_marker
        except OSError as exc:
            log.warning("Could not read poller state %s: %s", self._path, exc)
            return

    @classmethod
    def _fixed(cls, key: str, value: str | None) -> str:
        width = cls._WIDTHS[key]
        text = (value or "")
        return text[:width].ljust(width)

    def save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self._HEADER)
            writer.writeheader()
            for row in self._rows:
                writer.writerow(
                    {
                        "event_type": self._fixed("event_type", row.event_type),
                        "polled_at_utc": self._fixed("polled_at_utc", row.polled_at_utc),
                        "old_marker": self._fixed("old_marker", row.old_marker),
                        "new_marker": self._fixed("new_marker", row.new_marker),
                    }
                )

    def last_marker(self) -> str | None:
        return self._latest_marker

    def append(self, entry: PollerLogEntry) -> None:
        self._rows.append(entry)
        self._latest_marker = entry.new_marker


def default_postgres_dsn() -> str:
    direct = os.getenv("POSTGRES_DSN")
    if direct:
        return direct
    host = os.getenv("POSTGRES_HOST", "localhost:5432")
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    database = os.getenv("POSTGRES_DB", "postgres")
    return f"postgresql://{user}:{password}@{host}/{database}"


class PostgresStateStore:
    """Append poller executions to Postgres table ``data_object_poller_log``."""

    def __init__(self, dsn: str) -> None:
        self._dsn = dsn
        self._conn = self._connect(dsn)
        self._ensure_table()

    @staticmethod
    def _connect(dsn: str):
        try:
            import psycopg  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "Postgres state backend requested but 'psycopg' is not installed. "
                "Install with: pip install psycopg[binary]"
            ) from exc
        return psycopg.connect(dsn)

    def _ensure_table(self) -> None:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                create table if not exists data_object_poller_log (
                    id bigserial primary key,
                    event_type text not null,
                    polled_at_utc timestamptz not null,
                    old_marker text,
                    new_marker text not null,
                    inserted_at_utc timestamptz not null default now()
                )
                """
            )
        self._conn.commit()

    def last_marker(self) -> str | None:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                select new_marker
                from data_object_poller_log
                order by polled_at_utc desc, id desc
                limit 1
                """
            )
            row = cur.fetchone()
        return str(row[0]) if row else None

    def append(self, entry: PollerLogEntry) -> None:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                insert into data_object_poller_log (
                    event_type,
                    polled_at_utc,
                    old_marker,
                    new_marker
                )
                values (%s, %s, %s, %s)
                """,
                (
                    entry.event_type,
                    entry.polled_at_utc,
                    entry.old_marker,
                    entry.new_marker,
                ),
            )
        self._conn.commit()

    def save(self) -> None:
        # Writes are committed in ``set``.
        return None
