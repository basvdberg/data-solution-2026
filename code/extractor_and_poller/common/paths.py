"""Project paths for CLI entry points."""

from __future__ import annotations

from pathlib import Path

_PACKAGE_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = _PACKAGE_DIR.parent
CODE_ROOT = PACKAGE_ROOT.parent
PROJECT_ROOT = CODE_ROOT.parent


def ensure_project_root_on_path() -> None:
    import sys

    for root in (CODE_ROOT, PROJECT_ROOT):
        entry = str(root)
        if entry not in sys.path:
            sys.path.insert(0, entry)
