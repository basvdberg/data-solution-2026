"""Make ``code/`` and the solution root importable when pytest runs from the repo."""

from __future__ import annotations

import sys
from pathlib import Path

_CODE_ROOT = Path(__file__).resolve().parents[2]
_PROJECT_ROOT = _CODE_ROOT.parent
for entry in (str(_CODE_ROOT), str(_PROJECT_ROOT)):
    if entry not in sys.path:
        sys.path.insert(0, entry)
