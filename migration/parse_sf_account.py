#!/usr/bin/env python3
"""Parse Account entity package (wrapper for lib.parse_entity)."""

import sys

from common import REGISTRY_PATH, REPO_ROOT, ensure_migration_on_path
from lib.parse_entity import write_field_map

ensure_migration_on_path()


def main():
    out = write_field_map(REPO_ROOT, REGISTRY_PATH, "Account")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
