"""Shared logging configuration for extractor and poller CLIs.

Provides a compact, colorized formatter with clear separation of:
- timestamp
- log level
- logger name
- message
"""

from __future__ import annotations

import logging
import os
import sys
from datetime import datetime

_RESET = "\x1b[0m"
_DIM = "\x1b[2m"
_BOLD = "\x1b[1m"

_TS_COLOR = "\x1b[90m"  # bright black / gray
_MESSAGE_COLOR = "\x1b[37m"  # bright white

_LEVEL_COLORS: dict[int, str] = {
    logging.DEBUG: "\x1b[36m",  # cyan
    logging.INFO: "\x1b[32m",  # green
    logging.WARNING: "\x1b[33m",  # yellow
    logging.ERROR: "\x1b[31m",  # red
    logging.CRITICAL: "\x1b[35m",  # magenta
}


class PrettyColorFormatter(logging.Formatter):
    """Formatter that keeps logs readable in color and plain modes."""

    def __init__(self, use_color: bool) -> None:
        super().__init__()
        self.use_color = use_color

    def formatTime(self, record: logging.LogRecord, datefmt: str | None = None) -> str:
        dt = datetime.fromtimestamp(record.created)
        # Include milliseconds for better traceability during quick poll loops.
        return dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    def format(self, record: logging.LogRecord) -> str:
        timestamp = self.formatTime(record)
        level = record.levelname
        logger_name = record.name
        message = record.getMessage()

        if record.exc_info:
            message = f"{message}\n{self.formatException(record.exc_info)}"
        if record.stack_info:
            message = f"{message}\n{self.formatStack(record.stack_info)}"

        if not self.use_color:
            return f"{timestamp} | {level:<8} | {logger_name} | {message}"

        level_color = _LEVEL_COLORS.get(record.levelno, "\x1b[34m")
        return (
            f"{_TS_COLOR}{timestamp}{_RESET} | "
            f"{_BOLD}{level_color}{level:<8}{_RESET} | "
            f"{_DIM}{logger_name}{_RESET} | "
            f"{_MESSAGE_COLOR}{message}{_RESET}"
        )


class FlushingStreamHandler(logging.StreamHandler):
    """Stream handler that flushes after each record (needed for Airflow/bash tails)."""

    def emit(self, record: logging.LogRecord) -> None:
        super().emit(record)
        self.flush()


def running_in_airflow_task() -> bool:
    """True when code runs inside an Airflow task subprocess."""
    return bool(os.environ.get("AIRFLOW_CTX_DAG_ID"))


def configure_logging(*, verbose: bool = False) -> None:
    """Configure root logger with a single stream handler.

    When invoked from an Airflow task, keep Airflow's task log handlers intact.
    Clearing the root logger there sends output only to stderr and delays or
    hides lines in the Airflow UI.
    """
    level = logging.DEBUG if verbose else logging.INFO
    root = logging.getLogger()
    root.setLevel(level)

    if running_in_airflow_task():
        return

    use_color = sys.stderr.isatty()
    handler = FlushingStreamHandler()
    handler.setFormatter(PrettyColorFormatter(use_color=use_color))

    root.handlers.clear()
    root.addHandler(handler)
