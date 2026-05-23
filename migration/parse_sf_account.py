#!/usr/bin/env python3
"""Parse Salesforce Account metadata from src/ into account-field-map.json."""

import json
import xml.etree.ElementTree as ET
from pathlib import Path

from common import (
    FIELD_MAP_PATH,
    PUBLISHER_PREFIX,
    SF_FIELDS_DIR,
    SF_LAYOUT_PATH,
    SF_LIST_VIEWS_DIR,
)

NS = {"sf": "http://soap.sforce.com/2006/04/metadata"}

STANDARD_FIELD_MAP = {
    "Name": "name",
    "OwnerId": "ownerid",
    "ParentId": "parentaccountid",
    "Phone": "telephone1",
    "Fax": "fax",
    "Website": "websiteurl",
    "Type": "customertypecode",
    "Industry": "industrycode",
    "NumberOfEmployees": "numberofemployees",
    "AnnualRevenue": "revenue",
    "Description": "description",
    "BillingAddress": "address1_composite",
    "ShippingAddress": "address2_composite",
    "CreatedById": "createdby",
    "LastModifiedById": "modifiedby",
}

CUSTOM_FIELD_MAP = {
    "Ready_for_AI__c": ("crcc0_readyforai", "bool", "Ready for AI"),
    "Active__c": ("crcc0_active", "bool", "Active"),
    "AI_Summary__c": ("crcc0_aisummary", "memo", "AI Summary"),
    "UpsellOpportunity__c": ("crcc0_upsellopportunity", "picklist", "Upsell Opportunity"),
    "CustomerPriority__c": ("crcc0_customerpriority", "picklist", "Customer Priority"),
    "SLA__c": ("crcc0_sla", "picklist", "SLA"),
    "SLAExpirationDate__c": ("crcc0_slaexpirationdate", "date", "SLA Expiration Date"),
    "SLASerialNumber__c": ("crcc0_slaserialnumber", "string", "SLA Serial Number"),
    "NumberofLocations__c": ("crcc0_numberoflocations", "int", "Number of Locations"),
}

SF_LIST_COLUMN_MAP = {
    "ACCOUNT.NAME": "name",
    "ACCOUNT.SITE": "address1_line1",
    "ACCOUNT.ADDRESS1_STATE": "address1_stateorprovince",
    "ACCOUNT.PHONE1": "telephone1",
    "ACCOUNT.TYPE": "customertypecode",
    "CORE.USERS.ALIAS": "ownerid",
}


def _parse_picklist_values(root: ET.Element) -> list[str]:
    values = []
    for value_el in root.findall(".//sf:value", NS):
        label_el = value_el.find("sf:label", NS)
        if label_el is not None and label_el.text:
            values.append(label_el.text.strip())
        elif value_el.find("sf:fullName", NS) is not None:
            values.append(value_el.find("sf:fullName", NS).text.strip())
    return values


def parse_custom_fields() -> list[dict]:
    fields = []
    for path in sorted(SF_FIELDS_DIR.glob("*__c.field-meta.xml")):
        root = ET.parse(path).getroot()
        api_name = root.findtext("sf:fullName", default="", namespaces=NS) or path.stem.replace(
            ".field-meta", ""
        )
        if api_name not in CUSTOM_FIELD_MAP:
            continue
        logical, dv_type, display = CUSTOM_FIELD_MAP[api_name]
        label = root.findtext("sf:label", default=display, namespaces=NS) or display
        sf_type = root.findtext("sf:type", default="", namespaces=NS) or dv_type
        entry = {
            "salesforceApiName": api_name,
            "dataverseLogicalName": logical,
            "displayName": label,
            "salesforceType": sf_type,
            "dataverseType": dv_type,
        }
        if sf_type == "Picklist":
            entry["picklistValues"] = _parse_picklist_values(root)
        if sf_type == "Checkbox":
            default = root.findtext("sf:defaultValue", default="false", namespaces=NS)
            entry["defaultValue"] = default.lower() == "true"
        fields.append(entry)
    return fields


def parse_layout() -> list[dict]:
    root = ET.parse(SF_LAYOUT_PATH).getroot()
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


def parse_list_views() -> list[dict]:
    views = []
    for path in sorted(SF_LIST_VIEWS_DIR.glob("*.listView-meta.xml")):
        root = ET.parse(path).getroot()
        api_name = root.findtext("sf:fullName", default=path.stem, namespaces=NS)
        label = root.findtext("sf:label", default=api_name, namespaces=NS)
        filter_scope = root.findtext("sf:filterScope", default="Everything", namespaces=NS)
        columns = []
        for col in root.findall("sf:columns", NS):
            if col.text:
                columns.append(
                    {
                        "salesforce": col.text.strip(),
                        "dataverse": SF_LIST_COLUMN_MAP.get(col.text.strip()),
                    }
                )
        filters = []
        for filt in root.findall("sf:filters", NS):
            filters.append(
                {
                    "field": filt.findtext("sf:field", default="", namespaces=NS),
                    "operation": filt.findtext("sf:operation", default="", namespaces=NS),
                    "value": filt.findtext("sf:value", default="", namespaces=NS),
                }
            )
        views.append(
            {
                "salesforceApiName": api_name,
                "dataverseName": f"{label} (SF)",
                "filterScope": filter_scope,
                "columns": columns,
                "filters": filters,
            }
        )
    return views


def build_field_map() -> dict:
    picklist_enums = {}
    for field in parse_custom_fields():
        if field.get("picklistValues"):
            picklist_enums[field["salesforceApiName"]] = {
                name: 100000000 + idx
                for idx, name in enumerate(field["picklistValues"])
            }

    return {
        "publisherPrefix": PUBLISHER_PREFIX,
        "targetEntity": "account",
        "solutionName": "AccountMigration",
        "standardFieldMap": STANDARD_FIELD_MAP,
        "customFields": parse_custom_fields(),
        "picklistOptionValues": picklist_enums,
        "formSections": parse_layout(),
        "listViews": parse_list_views(),
    }


def main():
    data = build_field_map()
    FIELD_MAP_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Wrote {FIELD_MAP_PATH}")
    print(f"  Custom fields: {len(data['customFields'])}")
    print(f"  Form sections: {len(data['formSections'])}")
    print(f"  List views: {len(data['listViews'])}")


if __name__ == "__main__":
    main()
