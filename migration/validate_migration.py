#!/usr/bin/env python3
"""Validate Account migration (wrapper for lib.validate_entity)."""

import sys

from common import REGISTRY_PATH, REPO_ROOT, ensure_migration_on_path, load_dataverse_env
from lib.validate_entity import validate_entity

ensure_migration_on_path()


def main():
    load_dataverse_env()
    from auth import get_token  # noqa: E402

    return validate_entity(REPO_ROOT, REGISTRY_PATH, "Account", get_token)


if __name__ == "__main__":
    sys.exit(main())
