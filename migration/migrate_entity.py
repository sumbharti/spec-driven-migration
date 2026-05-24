#!/usr/bin/env python3
"""CLI: parse, apply metadata/form, or validate one or all entity packages."""

import argparse
import sys

from common import REGISTRY_PATH, REPO_ROOT, ensure_migration_on_path, load_dataverse_env
from lib.discovery import validate_registry_vs_disk
from lib.parse_entity import write_field_map
from lib.registry import list_active_entities, load_registry

ensure_migration_on_path()


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate Salesforce entity package(s) to Dataverse")
    parser.add_argument(
        "--entity",
        required=True,
        help="Entity package folder name (e.g. Account) or 'all'",
    )
    parser.add_argument(
        "--steps",
        default="parse,metadata,form,validate",
        help="Comma-separated: parse, metadata, form, validate",
    )
    parser.add_argument(
        "--skip-registry-check",
        action="store_true",
        help="Skip validate_registry_vs_disk",
    )
    args = parser.parse_args()
    steps = {s.strip() for s in args.steps.split(",") if s.strip()}

    if not args.skip_registry_check:
        errors = validate_registry_vs_disk(REGISTRY_PATH, REPO_ROOT / "src" / "Entity")
        if errors:
            for err in errors:
                print(f"Registry error: {err}", file=sys.stderr)
            return 1

    registry = load_registry(REGISTRY_PATH)
    if args.entity.lower() == "all":
        packages = [e["entityPackage"] for e in list_active_entities(registry)]
    else:
        packages = [args.entity]

    needs_env = bool(steps & {"metadata", "form", "validate"})
    get_token = None
    if needs_env:
        load_dataverse_env()
        from auth import get_token as _get_token  # noqa: WPS433

        get_token = _get_token

    exit_code = 0
    for package in packages:
        print(f"\n=== {package} ===")
        if "parse" in steps:
            out = write_field_map(REPO_ROOT, REGISTRY_PATH, package)
            print(f"Wrote {out}")
        if "metadata" in steps:
            from lib.apply_metadata import apply_metadata

            exit_code = max(exit_code, apply_metadata(REPO_ROOT, REGISTRY_PATH, package, get_token))
        if "form" in steps:
            from lib.apply_form import apply_form

            exit_code = max(exit_code, apply_form(REPO_ROOT, REGISTRY_PATH, package, get_token))
        if "validate" in steps:
            from lib.validate_entity import validate_entity

            exit_code = max(exit_code, validate_entity(REPO_ROOT, REGISTRY_PATH, package, get_token))

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
