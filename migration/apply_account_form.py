#!/usr/bin/env python3
"""Apply Account main form (wrapper for lib.apply_form)."""

import sys

from common import REGISTRY_PATH, REPO_ROOT, ensure_migration_on_path, load_dataverse_env
from lib.apply_form import apply_form

ensure_migration_on_path()


def main():
    load_dataverse_env()
    from auth import get_token  # noqa: E402

    return apply_form(REPO_ROOT, REGISTRY_PATH, "Account", get_token)


if __name__ == "__main__":
    sys.exit(main())
