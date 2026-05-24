"""Load entity-registry.json and resolve paths."""

from __future__ import annotations

import json
from pathlib import Path


def load_registry(registry_path: Path) -> dict:
    return json.loads(registry_path.read_text(encoding="utf-8"))


def get_entity_entry(registry: dict, entity_package: str) -> dict:
    for entry in registry.get("entities", []):
        if entry["entityPackage"] == entity_package:
            return entry
    raise KeyError(f"Unknown entity package: {entity_package}")


def list_active_entities(registry: dict) -> list[dict]:
    return [
        e
        for e in registry.get("entities", [])
        if e.get("status") in ("pilot", "active")
    ]


def field_map_path(repo_root: Path, entry: dict) -> Path:
    rel = entry.get("fieldMapPath", f"migration/maps/{entry['entityPackage'].lower()}-field-map.json")
    return repo_root / rel
