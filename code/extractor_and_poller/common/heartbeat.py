"""Ensure at least one log line within a few seconds of starting a DAG task or CLI run."""

from __future__ import annotations

import logging
import threading
from types import TracebackType

_DEFAULT_WITHIN_SEC = 2.0


class EarlyProgressLog:
    """Log on entry; if work continues, log once more after *within_sec* (not repeatedly)."""

    def __init__(
        self,
        logger: logging.Logger,
        started_message: str | None,
        *,
        pending_message: str | None = None,
        within_sec: float = _DEFAULT_WITHIN_SEC,
    ) -> None:
        self._logger = logger
        self._started_message = started_message
        self._pending_message = pending_message
        self._within_sec = within_sec
        self._stopped = False
        self._timer: threading.Timer | None = None

    def _log_pending_once(self) -> None:
        if self._stopped:
            return
        message = self._pending_message
        if message is None and self._started_message:
            message = f"{self._started_message} (still in progress)"
        if message:
            self._logger.info(message)

    def __enter__(self) -> EarlyProgressLog:
        if self._started_message:
            self._logger.info(self._started_message)
        self._timer = threading.Timer(self._within_sec, self._log_pending_once)
        self._timer.daemon = True
        self._timer.start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self._stopped = True
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None


def log_early_progress(
    logger: logging.Logger,
    started_message: str | None,
    *,
    pending_message: str | None = None,
    within_sec: float = _DEFAULT_WITHIN_SEC,
) -> EarlyProgressLog:
    """Context manager: immediate *started_message*, optional single follow-up after *within_sec*."""
    return EarlyProgressLog(
        logger,
        started_message,
        pending_message=pending_message,
        within_sec=within_sec,
    )


# Backwards-compatible alias (one-shot behaviour, not periodic).
log_heartbeat = log_early_progress
LogHeartbeat = EarlyProgressLog
