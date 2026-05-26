"""CLI: Open-Meteo data object poller (defaults to Open-Meteo staging mapping)."""

from __future__ import annotations

import sys

from extractor_and_poller.common.paths import PROJECT_ROOT, ensure_project_root_on_path

ensure_project_root_on_path()

from extractor_and_poller.poller.__main__ import DEFAULT_CONFIG, main

OPENMETEO_CONFIG = DEFAULT_CONFIG
OPENMETEO_MAPPING = "openmeteo-daily-temperature"


def _openmeteo_argv(argv: list[str] | None) -> list[str]:
    args = list(argv or sys.argv[1:])
    if not any(a.startswith("--config") or a == "-h" or a == "--help" for a in args):
        if "--config" not in args:
            args = ["--config", str(OPENMETEO_CONFIG), *args]
    if not any(a.startswith("--mapping") for a in args) and "--list" not in args:
        if "--mapping" not in args and "-h" not in args and "--help" not in args:
            args = ["--mapping", OPENMETEO_MAPPING, *args]
    return args


if __name__ == "__main__":
    raise SystemExit(main(_openmeteo_argv(None)))
