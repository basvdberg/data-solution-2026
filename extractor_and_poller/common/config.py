"""Load DSA metadata JSON and expose ergonomic accessors.

Mapping files use path IDs and reference ``data-object`` / ``connection`` artifacts.
At load time, ``sourceDataObjectIds`` and ``targetDataObjectId`` are resolved into
embedded ``sourceDataObjects`` and ``targetDataObject`` for runtime code.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
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


def _artifact_json_path(solution_root: Path, artifact_id: str) -> Path:
    if artifact_id.startswith(("connection/", "data-object-mapping/")):
        return solution_root / f"{artifact_id}.json"
    return solution_root / "data-object" / f"{artifact_id}.json"


def _load_artifact(solution_root: Path, artifact_id: str) -> dict[str, Any]:
    path = _artifact_json_path(solution_root, artifact_id)
    if not path.is_file():
        raise FileNotFoundError(f"DSA artifact not found: {artifact_id} ({path})")
    with path.open(encoding="utf-8-sig") as f:
        data: dict[str, Any] = json.load(f)
    data.setdefault("id", artifact_id)
    return data


def _resolve_connection(solution_root: Path, connection_id: str) -> dict[str, Any]:
    return _load_artifact(solution_root, connection_id)


def _resolve_data_object(solution_root: Path, object_id: str) -> dict[str, Any]:
    obj = _load_artifact(solution_root, object_id)
    connection_id = obj.get("dataConnectionId")
    if connection_id:
        obj = dict(obj)
        obj["dataConnection"] = _resolve_connection(solution_root, connection_id)
    return obj


def _resolve_mapping(solution_root: Path, mapping: dict[str, Any]) -> dict[str, Any]:
    resolved = dict(mapping)
    if "sourceDataObjectIds" in resolved and "sourceDataObjects" not in resolved:
        resolved["sourceDataObjects"] = [
            _resolve_data_object(solution_root, oid)
            for oid in resolved["sourceDataObjectIds"]
        ]
    if "targetDataObjectId" in resolved and "targetDataObject" not in resolved:
        resolved["targetDataObject"] = _resolve_data_object(
            solution_root, resolved["targetDataObjectId"]
        )
    return resolved


def _solution_root_for(config_path: Path) -> Path:
    """Walk up until ``connection/`` or ``data-object/`` exists (solution root)."""
    for parent in [config_path.parent, *config_path.parents]:
        if (parent / "connection").is_dir() or (parent / "data-object").is_dir():
            return parent
    return config_path.parent


def _mapping_entries(raw: dict[str, Any]) -> list[dict[str, Any]]:
    if "dataObjectMappings" in raw:
        return list(raw["dataObjectMappings"])
    if any(
        key in raw
        for key in (
            "sourceDataObjectIds",
            "sourceDataObjects",
            "targetDataObjectId",
            "targetDataObject",
        )
    ):
        return [raw]
    return []


def _normalize_raw(raw: dict[str, Any], config_path: Path) -> dict[str, Any]:
    solution_root = _solution_root_for(config_path)
    entries = _mapping_entries(raw)
    resolved = [_resolve_mapping(solution_root, m) for m in entries]
    if "dataObjectMappings" in raw:
        return {**raw, "dataObjectMappings": resolved}
    return {"dataObjectMappings": resolved, "extensions": raw.get("extensions", [])}


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
                return c[len(token) :]
        return None

    def source_data_objects(self) -> list[SourceDataObject]:
        return [
            SourceDataObject(name=o["name"], raw=o)
            for o in self.raw.get("sourceDataObjects", [])
        ]

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
            if m.id.endswith(f"/{mapping_id}") or m.id.split("/")[-1] == mapping_id:
                return m
        return None


def load(path: str) -> Config:
    """Load a DSA mapping JSON file from disk and resolve path references."""
    config_path = Path(path)
    with config_path.open(encoding="utf-8-sig") as f:
        raw = json.load(f)
    normalized = _normalize_raw(raw, config_path)
    log.info(
        "Loaded config '%s' with %d mapping(s)",
        path,
        len(normalized.get("dataObjectMappings", [])),
    )
    return Config(raw=normalized, path=path)
