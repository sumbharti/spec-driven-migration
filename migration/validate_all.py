#!/usr/bin/env python3
"""Validate all active/pilot entities in entity-registry.json."""

import sys

from common import REGISTRY_PATH, REPO_ROOT, ensure_migration_on_path, load_dataverse_env
from lib.registry import list_active_entities, load_registry
from lib.validate_entity import validate_entity

ensure_migration_on_path()


def main() -> int:
    load_dataverse_env()
    from auth import get_token  # noqa: WPS433

    registry = load_registry(REGISTRY_PATH)
    exit_code = 0
    for entry in list_active_entities(registry):
        package = entry["entityPackage"]
        print(f"\n--- Validating {package} ---")
        exit_code = max(
            exit_code,
            validate_entity(REPO_ROOT, REGISTRY_PATH, package, get_token),
        )
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
