#!/usr/bin/env python3
"""Inventory existing account crcc0_* columns and main forms in Dataverse."""

import json
import os
import sys
import urllib.parse
import urllib.request

from common import INVENTORY_PATH, PUBLISHER_PREFIX, load_dataverse_env

load_dataverse_env()

from auth import get_credential, get_token  # noqa: E402
from PowerPlatform.Dataverse.client import DataverseClient  # noqa: E402


def web_get(path: str) -> dict:
    env = os.environ["DATAVERSE_URL"].rstrip("/")
    token = get_token()
    if "?" in path:
        base, query = path.split("?", 1)
        path = f"{base}?{urllib.parse.quote(query, safe='=$&(),')}"
    req = urllib.request.Request(
        f"{env}/api/data/v9.2/{path}",
        headers={
            "Authorization": f"Bearer {token}",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def list_account_attributes(prefix: str) -> list[dict]:
    data = web_get(
        "EntityDefinitions(LogicalName='account')/Attributes"
        "?$select=LogicalName,AttributeType,DisplayName,SchemaName"
    )
    attrs = []
    for item in data.get("value", []):
        logical = item.get("LogicalName") or ""
        if not logical.startswith(prefix):
            continue
        display = ""
        dn = item.get("DisplayName") or {}
        labels = dn.get("LocalizedLabels") or []
        if labels:
            display = labels[0].get("Label", "")
        attrs.append(
            {
                "logicalName": logical,
                "schemaName": item.get("SchemaName"),
                "attributeType": item.get("AttributeType"),
                "displayName": display,
            }
        )
    return sorted(attrs, key=lambda x: x["logicalName"])


def list_main_forms() -> list[dict]:
    data = web_get(
        "systemforms?$filter=objecttypecode eq 'account' and type eq 2"
        "&$select=formid,name,description,isdefault"
    )
    return [
        {
            "formid": f["formid"],
            "name": f["name"],
            "description": f.get("description"),
            "isdefault": (f.get("isdefault") or {}).get("Value"),
        }
        for f in data.get("value", [])
    ]


def main():
    url = os.environ["DATAVERSE_URL"]
    client = DataverseClient(url, get_credential())

    expected = [
        "crcc0_readyforai",
        "crcc0_active",
        "crcc0_aisummary",
        "crcc0_upsellopportunity",
        "crcc0_customerpriority",
        "crcc0_sla",
        "crcc0_slaexpirationdate",
        "crcc0_slaserialnumber",
        "crcc0_numberoflocations",
    ]
    existing = list_account_attributes(PUBLISHER_PREFIX)
    existing_names = {a["logicalName"] for a in existing}
    missing = [n for n in expected if n not in existing_names]

    forms = list_main_forms()
    inventory = {
        "environment": url,
        "publisherPrefix": PUBLISHER_PREFIX,
        "existingCustomAttributes": existing,
        "expectedCustomAttributes": expected,
        "missingCustomAttributes": missing,
        "mainForms": forms,
    }
    INVENTORY_PATH.write_text(json.dumps(inventory, indent=2), encoding="utf-8")
    print(f"Wrote {INVENTORY_PATH}")
    print(f"  Existing {PUBLISHER_PREFIX}_* attributes: {len(existing)}")
    print(f"  Missing (to create): {len(missing)}")
    if missing:
        print("  ", ", ".join(missing))
    print(f"  Main forms: {len(forms)}")
    for f in forms[:5]:
        print(f"    - {f['name']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
