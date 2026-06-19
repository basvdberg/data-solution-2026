"""Orchestration event type constants (event-based orchestration glossary)."""

from __future__ import annotations

EVENT_TYPE_CHANGE = "data_object_change"
EVENT_TYPE_UNCHANGED = "data_object_unchanged"
EVENT_TYPE_PROCESSING_ERROR = "processing_error"

CHANGE_SCOPE_INCREMENTAL_UPDATE = "incremental_update"
CHANGE_SCOPE_FULL_REWRITE = "full_rewrite"
CHANGE_SCOPE_HISTORICAL_REWRITE = "historical_rewrite"
