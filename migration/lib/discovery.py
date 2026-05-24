"""Discover entity packages under src/Entity and validate against registry."""

from __future__ import annotations

import json
from pathlib import Path


def discover_entity_packages(entity_root: Path) -> list[str]:
    """Return folder names under src/Entity that have objects/ and layouts/."""
    if not entity_root.is_dir():
        return []
    packages = []
    for child in sorted(entity_root.iterdir()):
        if not child.is_dir():
            continue
        if (child / "objects").is_dir() and (child / "layouts").is_dir():
            packages.append(child.name)
    return packages


def load_registry(registry_path: Path) -> dict:
    return json.loads(registry_path.read_text(encoding="utf-8"))


def validate_registry_vs_disk(registry_path: Path, entity_root: Path) -> list[str]:
    """
    Return list of error messages. Empty list means OK.
    Fails when a discovered package is missing from registry or registry points to missing folder.
    """
    errors: list[str] = []
    registry = load_registry(registry_path)
    registered = {e["entityPackage"] for e in registry.get("entities", [])}
    on_disk = set(discover_entity_packages(entity_root))

    for pkg in sorted(on_disk - registered):
        errors.append(f"Package '{pkg}' exists under src/Entity but is missing from {registry_path.name}")

    for pkg in sorted(registered - on_disk):
        entry = next(e for e in registry["entities"] if e["entityPackage"] == pkg)
        if entry.get("status") not in ("excluded",):
            errors.append(f"Registry entry '{pkg}' has no matching folder under src/Entity")

    return errors
