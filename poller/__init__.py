"""Generic data object poller — protocol-agnostic change detection.

Delegates probes to the same HTTP clients as the extractors (OData, WFS).
"""

from poller.change_probe import (  # noqa: F401
    ChangeDetectionResult,
    probe_current_value,
    poll_mapping,
    poll_registry,
)
