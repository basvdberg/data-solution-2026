"""Load a DWA-style metadata JSON config and expose ergonomic accessors.

The config file holds a top-level ``data-object-mapping`` array. Each mapping has:

- ``id``, ``name``, ``enabled``
- ``classifications``: list of ``{classification: "key:value"}`` tags
- ``extensions``: list of ``{key, value}`` pairs
- ``sourceDataObjects``: list of ``{name, dataConnection: {name, extensions}}``
- ``targetDataObject``: ``{name, dataConnection: {name, extensions}}``

The shape mirrors the Data Warehouse Automation Metadata Schema v2.0; this module
reads the file as plain JSON and does not enforce the schema (validation is a
separate concern).
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Mapping as MappingT, Sequence

log = logging.getLogger(__name__)


def _extensions_to_dict(extensions: Sequence[MappingT[str, Any]] | None) -> dict[str, str]:
    return {e["key"]: str(e.get("value", "")) for e in (extensions or []) if "key" in e}


def _classification_token(entry: MappingT[str, Any]) -> str:
    """Normalize ADL-style group+classification or legacy ``prefix:value`` tokens."""
    group = entry.get("group")
    classification = entry.get("classification", "")
    if group and classification:
        return f"{group}:{classification}"
    return str(classification)


@dataclass(frozen=True)
class SourceDataObject:
    name: str
    raw: dict[str, Any]

    def connection_name(self) -> str:
        return self.raw.get("dataConnection", {}).get("name", "")

    def connection_ext(self, key: str, default: str | None = None) -> str:
        ext = _extensions_to_dict(self.raw.get("dataConnection", {}).get("extensions"))
        if key in ext:
            return ext[key]
        if default is not None:
            return default
        raise KeyError(
            f"connection extension '{key}' missing on source object '{self.name}'"
        )


@dataclass(frozen=True)
class Mapping:
    raw: dict[str, Any]

    @property
    def id(self) -> str:
        return self.raw["id"]

    @property
    def name(self) -> str:
        return self.raw.get("name", self.id)

    @property
    def enabled(self) -> bool:
        return bool(self.raw.get("enabled", True))

    def extensions_dict(self, defaults: MappingT[str, str] | None = None) -> dict[str, str]:
        merged: dict[str, str] = dict(defaults or {})
        merged.update(_extensions_to_dict(self.raw.get("extensions")))
        return merged

    def classifications(self) -> list[str]:
        return [
            token
            for c in self.raw.get("classifications", [])
            if (token := _classification_token(c))
        ]

    def has_classification(self, full: str) -> bool:
        return full in self.classifications()

    def get_classification_value(self, prefix: str) -> str | None:
        """Return the suffix of a ``prefix:value`` classification (or ``None``)."""
        token = f"{prefix}:"
        for c in self.classifications():
            if c.startswith(token):
                return c[len(token):]
        return None

    def source_data_objects(self) -> list[SourceDataObject]:
        return [SourceDataObject(name=o["name"], raw=o) for o in self.raw.get("sourceDataObjects", [])]

    def target_name(self) -> str:
        return self.raw.get("targetDataObject", {}).get("name", "")


@dataclass(frozen=True)
class Config:
    raw: dict[str, Any]
    path: str

    def defaults(self) -> dict[str, str]:
        """Top-level ``extensions`` on the config (used as fallback defaults)."""
        return _extensions_to_dict(self.raw.get("extensions"))

    def mappings(self) -> list[Mapping]:
        return [Mapping(raw=m) for m in self.raw.get("dataObjectMappings", [])]

    def enabled_mappings(self) -> list[Mapping]:
        return [m for m in self.mappings() if m.enabled]

    def get_mapping(self, mapping_id: str) -> Mapping | None:
        for m in self.mappings():
            if m.id == mapping_id:
                return m
        return None


def load(path: str) -> Config:
    """Load a DWA-style metadata JSON file from disk."""
    with open(path, "r", encoding="utf-8-sig") as f:
        raw = json.load(f)
    log.info(
        "Loaded config '%s' with %d mapping(s)",
        path,
        len(raw.get("dataObjectMappings", [])),
    )
    return Config(raw=raw, path=path)
