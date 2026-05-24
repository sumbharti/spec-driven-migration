"""Validate migrated columns and main form for one entity package."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from lib.registry import field_map_path, get_entity_entry, load_registry


def list_attributes(target_entity: str, prefix: str, get_token) -> list[dict]:
    env = os.environ["DATAVERSE_URL"].rstrip("/")
    token = get_token()
    flt = urllib.parse.quote(f"startswith(LogicalName,'{prefix}')")
    url = (
        f"{env}/api/data/v9.2/EntityDefinitions(LogicalName='{target_entity}')"
        f"/Attributes?$select=LogicalName,DisplayName,RequiredLevel&$filter={flt}"
    )
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    return data.get("value", [])


def list_main_forms(target_entity: str, get_token) -> list[dict]:
    env = os.environ["DATAVERSE_URL"].rstrip("/")
    token = get_token()
    url = (
        f"{env}/api/data/v9.2/systemforms?"
        f"$filter=objecttypecode eq '{target_entity}' and type eq 2&$select=name,formid"
    )
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    return data.get("value", [])


def validate_entity(repo_root: Path, registry_path: Path, entity_package: str, get_token) -> int:
    registry = load_registry(registry_path)
    entry = get_entity_entry(registry, entity_package)
    map_path = field_map_path(repo_root, entry)
    field_map = json.loads(map_path.read_text(encoding="utf-8"))
    prefix = field_map["publisherPrefix"]
    target = field_map["targetEntity"]
    form_name = field_map.get("formDisplayName") or entry["formDisplayName"]

    expected = [f["dataverseLogicalName"] for f in field_map["customFields"]]
    existing = {a["LogicalName"].lower() for a in list_attributes(target, prefix, get_token)}
    missing_fields = [n for n in expected if n.lower() not in existing]

    form_names = {f["name"] for f in list_main_forms(target, get_token)}
    form_ok = form_name in form_names

    required_issues = []
    attrs_by_name = {a["LogicalName"].lower(): a for a in list_attributes(target, prefix, get_token)}
    for field in field_map["customFields"]:
        if not field.get("required"):
            continue
        logical = field["dataverseLogicalName"].lower()
        attr = attrs_by_name.get(logical)
        if attr:
            level = (attr.get("RequiredLevel") or {}).get("Value", "None")
            if level == "None":
                required_issues.append(f"{logical} should be required but RequiredLevel is None")

    failed = []
    if missing_fields:
        failed.append(f"Missing columns: {', '.join(missing_fields)}")
    if not form_ok:
        failed.append(f"Form '{form_name}' not found")
    failed.extend(required_issues)

    print(f"=== {entity_package} Migration Validation ===")
    print(f"Custom columns: {len(expected) - len(missing_fields)}/{len(expected)}")
    print(f"Form present: {form_ok}")
    if required_issues:
        for issue in required_issues:
            print(f"  Required: {issue}")

    if failed:
        print("\nFAILED:")
        for item in failed:
            print(f"  - {item}")
        return 1

    print("\nAll automated checks passed.")
    return 0
