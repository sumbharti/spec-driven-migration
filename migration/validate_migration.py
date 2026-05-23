#!/usr/bin/env python3
"""Automated validation for Account metadata migration."""

import json
import sys

from common import FIELD_MAP_PATH, INVENTORY_PATH, load_dataverse_env

load_dataverse_env()

from env_inventory import list_account_attributes, list_main_forms  # noqa: E402
import apply_account_views as views  # noqa: E402


def main():
    field_map = json.loads(FIELD_MAP_PATH.read_text(encoding="utf-8"))
    expected = [f["dataverseLogicalName"] for f in field_map["customFields"]]
    existing = {a["logicalName"] for a in list_account_attributes("crcc0")}
    missing_fields = [n for n in expected if n not in existing]

    forms = list_main_forms()
    form_names = {f["name"] for f in forms}
    form_ok = "Account - Salesforce Layout" in form_names

    view_checks = []
    for view in field_map["listViews"]:
        name = view["dataverseName"]
        view_checks.append((name, views.view_exists(name)))

    failed = []
    if missing_fields:
        failed.append(f"Missing columns: {', '.join(missing_fields)}")
    if not form_ok:
        failed.append("Form 'Account - Salesforce Layout' not found")
    for name, ok in view_checks:
        if not ok:
            failed.append(f"View missing: {name}")

    print("=== Account Migration Validation ===")
    print(f"Custom columns: {len(expected) - len(missing_fields)}/{len(expected)}")
    print(f"Form present: {form_ok}")
    for name, ok in view_checks:
        print(f"  View '{name}': {'PASS' if ok else 'FAIL'}")

    if failed:
        print("\nFAILED:")
        for item in failed:
            print(f"  - {item}")
        return 1

    print("\nAll automated checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
