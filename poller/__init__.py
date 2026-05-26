"""Data object poller — detect changes and signal the event bus only.

Lives at project root, not under ``extractor/``. Reuses ``extractor.*.client`` for
probes; never runs extractors.
"""

from poller.change_probe import (  # noqa: F401
    ChangeDetectionResult,
    is_poll_trigger,
    probe_current_value,
    poll_mapping,
    poll_registry,
)
from poller.events import (  # noqa: F401
    EVENT_DATA_OBJECT_CHANGE,
    EVENT_DATA_OBJECT_PROGRESS,
    PollerEvent,
    from_poll_result,
)
