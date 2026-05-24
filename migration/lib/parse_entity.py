"""Parse Salesforce entity package XML into field-map JSON contract."""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path

from lib.account_config import CUSTOM_FIELD_MAP, STANDARD_FIELD_MAP
from lib.registry import field_map_path, get_entity_entry, load_registry

NS = {"sf": "http://soap.sforce.com/2006/04/metadata"}


def _parse_picklist_values(root: ET.Element) -> list[str]:
    values = []
    for value_el in root.findall(".//sf:value", NS):
        label_el = value_el.find("sf:label", NS)
        if label_el is not None and label_el.text:
            values.append(label_el.text.strip())
        elif value_el.find("sf:fullName", NS) is not None:
            values.append(value_el.find("sf:fullName", NS).text.strip())
    return values


def _account_paths(repo_root: Path, entry: dict) -> tuple[Path, Path, Path]:
    source = repo_root / entry["sourcePath"]
    sf_object = entry["salesforceObject"]
    fields_dir = source / "objects" / sf_object / "fields"
    layout_glob = entry["mainLayoutGlob"]
    layouts = list((source / "layouts").glob(layout_glob))
    if not layouts:
        raise FileNotFoundError(f"No layout matching {layout_glob} under {source / 'layouts'}")
    return fields_dir, layouts[0], source


def parse_custom_fields(fields_dir: Path, publisher_prefix: str) -> list[dict]:
    fields = []
    for path in sorted(fields_dir.glob("*__c.field-meta.xml")):
        root = ET.parse(path).getroot()
        api_name = root.findtext("sf:fullName", default="", namespaces=NS) or path.stem.replace(
            ".field-meta", ""
        )
        if api_name not in CUSTOM_FIELD_MAP:
            continue
        logical, dv_type, display = CUSTOM_FIELD_MAP[api_name]
        if not logical.startswith(f"{publisher_prefix}_"):
            raise ValueError(f"Custom field {api_name} logical name must use prefix {publisher_prefix}_")
        label = root.findtext("sf:label", default=display, namespaces=NS) or display
        sf_type = root.findtext("sf:type", default="", namespaces=NS) or dv_type
        required_text = root.findtext("sf:required", default="false", namespaces=NS) or "false"
        entry = {
            "salesforceApiName": api_name,
            "dataverseLogicalName": logical,
            "displayName": label,
            "salesforceType": sf_type,
            "dataverseType": dv_type,
            "required": required_text.lower() == "true",
        }
        if sf_type == "Picklist":
            entry["picklistValues"] = _parse_picklist_values(root)
        if sf_type == "Checkbox":
            default = root.findtext("sf:defaultValue", default="false", namespaces=NS)
            entry["defaultValue"] = default.lower() == "true"
        fields.append(entry)
    return fields


def parse_layout(layout_path: Path) -> list[dict]:
    root = ET.parse(layout_path).getroot()
    sections = []
    for section in root.findall("sf:layoutSections", NS):
        label = section.findtext("sf:label", default="", namespaces=NS) or ""
        items = []
        for item in section.findall(".//sf:layoutItems", NS):
            field = item.findtext("sf:field", default="", namespaces=NS)
            if not field:
                continue
            behavior = item.findtext("sf:behavior", default="Edit", namespaces=NS) or "Edit"
            if field in STANDARD_FIELD_MAP:
                dv_field = STANDARD_FIELD_MAP[field]
                kind = "standard"
            elif field in CUSTOM_FIELD_MAP:
                dv_field = CUSTOM_FIELD_MAP[field][0]
                kind = "custom"
            else:
                continue
            items.append(
                {
                    "salesforceField": field,
                    "dataverseField": dv_field,
                    "kind": kind,
                    "behavior": behavior,
                }
            )
        if items:
            sections.append({"label": label, "fields": items})
    return sections


def build_field_map(repo_root: Path, registry: dict, entity_package: str) -> dict:
    entry = get_entity_entry(registry, entity_package)
    if entity_package != "Account":
        raise NotImplementedError(
            f"Parser for '{entity_package}' not configured. Add maps in lib/ and registry entry."
        )

    publisher_prefix = registry["publisherPrefix"]
    fields_dir, layout_path, source = _account_paths(repo_root, entry)
    custom_fields = parse_custom_fields(fields_dir, publisher_prefix)

    picklist_enums = {}
    for field in custom_fields:
        if field.get("picklistValues"):
            picklist_enums[field["salesforceApiName"]] = {
                name: 100000000 + idx for idx, name in enumerate(field["picklistValues"])
            }

    return {
        "entityPackage": entity_package,
        "salesforceObject": entry["salesforceObject"],
        "sourcePath": entry["sourcePath"],
        "publisherPrefix": publisher_prefix,
        "solutionName": registry["solutionName"],
        "targetEntity": entry["targetTable"],
        "targetTableKind": entry.get("targetTableKind", "standard"),
        "formDisplayName": entry["formDisplayName"],
        "standardFieldMap": STANDARD_FIELD_MAP,
        "customFields": custom_fields,
        "picklistOptionValues": picklist_enums,
        "formSections": parse_layout(layout_path),
    }


def write_field_map(repo_root: Path, registry_path: Path, entity_package: str) -> Path:
    registry = load_registry(registry_path)
    entry = get_entity_entry(registry, entity_package)
    data = build_field_map(repo_root, registry, entity_package)
    out_path = field_map_path(repo_root, entry)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return out_path
