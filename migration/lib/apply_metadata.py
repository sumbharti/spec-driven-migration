"""Idempotently create custom columns from field-map JSON."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

from lib.registry import field_map_path, get_entity_entry, load_registry


def label(text: str) -> dict:
    return {
        "@odata.type": "Microsoft.Dynamics.CRM.Label",
        "LocalizedLabels": [
            {
                "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
                "Label": text,
                "LanguageCode": 1033,
            }
        ],
    }


def schema_name(logical: str) -> str:
    if "_" not in logical:
        return logical
    prefix, rest = logical.split("_", 1)
    return f"{prefix}_{rest[0].upper()}{rest[1:]}"


def attribute_exists(target_entity: str, logical_name: str, get_token) -> bool:
    env = os.environ["DATAVERSE_URL"].rstrip("/")
    token = get_token()
    url = (
        f"{env}/api/data/v9.2/EntityDefinitions(LogicalName='{target_entity}')"
        f"/Attributes(LogicalName='{logical_name}')"
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
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status == 200
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False
        raise


def post_attribute(target_entity: str, body: dict, solution_name: str, get_token) -> None:
    env = os.environ["DATAVERSE_URL"].rstrip("/")
    token = get_token()
    req = urllib.request.Request(
        f"{env}/api/data/v9.2/EntityDefinitions(LogicalName='{target_entity}')/Attributes",
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
            "MSCRM.SolutionUniqueName": solution_name,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            resp.read()
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Create attribute failed ({e.code}): {e.read().decode()}") from e


def build_attribute_payload(field: dict) -> dict:
    logical = field["dataverseLogicalName"]
    schema = schema_name(logical)
    display = field["displayName"]
    dv_type = field["dataverseType"]
    required_level = "ApplicationRequired" if field.get("required") else "None"
    base = {
        "SchemaName": schema,
        "DisplayName": label(display),
        "Description": label("Migrated from Salesforce"),
        "RequiredLevel": {"Value": required_level},
    }

    if dv_type == "bool":
        return {
            **base,
            "@odata.type": "Microsoft.Dynamics.CRM.BooleanAttributeMetadata",
            "DefaultValue": field.get("defaultValue", False),
            "OptionSet": {
                "@odata.type": "Microsoft.Dynamics.CRM.BooleanOptionSetMetadata",
                "FalseOption": {"Value": 0, "Label": label("No")},
                "TrueOption": {"Value": 1, "Label": label("Yes")},
            },
        }
    if dv_type == "string":
        return {
            **base,
            "@odata.type": "Microsoft.Dynamics.CRM.StringAttributeMetadata",
            "MaxLength": 100,
            "FormatName": {"Value": "Text"},
        }
    if dv_type == "int":
        return {
            **base,
            "@odata.type": "Microsoft.Dynamics.CRM.IntegerAttributeMetadata",
            "MinValue": 0,
            "MaxValue": 999,
            "Format": "None",
        }
    if dv_type == "date":
        return {
            **base,
            "@odata.type": "Microsoft.Dynamics.CRM.DateTimeAttributeMetadata",
            "Format": "DateOnly",
            "DateTimeBehavior": {"Value": "UserLocal"},
        }
    if dv_type == "memo":
        return {
            **base,
            "@odata.type": "Microsoft.Dynamics.CRM.MemoAttributeMetadata",
            "MaxLength": 100000,
        }
    if dv_type == "picklist":
        options = []
        for idx, name in enumerate(field.get("picklistValues", [])):
            options.append({"Value": 100000000 + idx, "Label": label(name)})
        return {
            **base,
            "@odata.type": "Microsoft.Dynamics.CRM.PicklistAttributeMetadata",
            "OptionSet": {
                "@odata.type": "Microsoft.Dynamics.CRM.OptionSetMetadata",
                "IsGlobal": False,
                "OptionSetType": "Picklist",
                "Options": options,
            },
        }
    raise ValueError(f"Unsupported type: {dv_type}")


def retry_metadata(fn, description: str, max_attempts: int = 5):
    for attempt in range(max_attempts):
        try:
            return fn()
        except Exception as e:
            err = str(e).lower()
            if "another" in err and "running" in err:
                wait = 10 * (attempt + 1)
                print(f"  {description}: lock contention, waiting {wait}s...")
                time.sleep(wait)
                continue
            raise


def apply_metadata(repo_root: Path, registry_path: Path, entity_package: str, get_token) -> int:
    registry = load_registry(registry_path)
    entry = get_entity_entry(registry, entity_package)
    map_path = field_map_path(repo_root, entry)
    field_map = json.loads(map_path.read_text(encoding="utf-8"))
    target = field_map["targetEntity"]
    solution = field_map["solutionName"]

    created = []
    skipped = []

    for field in field_map["customFields"]:
        logical = field["dataverseLogicalName"]
        if attribute_exists(target, logical, get_token):
            print(f"  Skip (exists): {logical}")
            skipped.append(logical)
            continue

        print(f"  Creating: {logical} ({field['dataverseType']})")

        def do_create(f=field):
            post_attribute(target, build_attribute_payload(f), solution, get_token)
            time.sleep(3)

        retry_metadata(do_create, logical)
        created.append(logical)

    if created:
        print(f"Waiting 15s for metadata propagation after {len(created)} column(s)...")
        time.sleep(15)

    print(f"Metadata done. Created: {len(created)}, Skipped: {len(skipped)}")
    return 0
