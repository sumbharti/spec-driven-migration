#!/usr/bin/env python3
"""Create or update Account main form matching Salesforce layout sections."""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
import xml.sax.saxutils as xml_escape

from common import FIELD_MAP_PATH, SOLUTION_NAME, load_dataverse_env

load_dataverse_env()

from auth import get_token  # noqa: E402

FORM_NAME = "Account - Salesforce Layout"

CONTROL_CLASSIDS = {
    "text": "{4273EDBD-AC1D-40d3-9FB2-095C621B552D}",
    "picklist": "{3EF39988-22BB-4f0b-BBBE-64B5A3748AEE}",
    "lookup": "{270BD3DB-D9AF-4782-9025-509E298DEC0A}",
    "datetime": "{5B773807-9FB2-42db-97C3-7A91EFF8ADFF}",
    "int": "{C6D124CA-7EDA-4a60-AEA9-7FB8D318B68F}",
    "money": "{533B9108-5A8B-42cb-BD37-52D1B8E7C741}",
    "toggle": "{67FAC785-CD58-4f9f-ABB3-4B7DDC6ED5ED}",
    "memo": "{E0DECE4B-6FC8-4a8f-A065-082708572369}",
    "address": "{7189F4CA-8E32-11DB-BEFD-00104B2EF995}",
}

FIELD_CONTROL = {
    "name": ("text", "Account Name"),
    "ownerid": ("lookup", "Owner"),
    "parentaccountid": ("lookup", "Parent Account"),
    "telephone1": ("text", "Main Phone"),
    "fax": ("text", "Fax"),
    "websiteurl": ("text", "Website"),
    "customertypecode": ("picklist", "Relationship Type"),
    "industrycode": ("picklist", "Industry"),
    "numberofemployees": ("int", "Number of Employees"),
    "revenue": ("money", "Annual Revenue"),
    "description": ("memo", "Description"),
    "address1_composite": ("address", "Address 1"),
    "address2_composite": ("address", "Address 2"),
    "createdby": ("lookup", "Created By"),
    "modifiedby": ("lookup", "Modified By"),
    "crcc0_readyforai": ("toggle", "Ready for AI"),
    "crcc0_active": ("toggle", "Active"),
    "crcc0_aisummary": ("memo", "AI Summary"),
    "crcc0_upsellopportunity": ("picklist", "Upsell Opportunity"),
    "crcc0_customerpriority": ("picklist", "Customer Priority"),
    "crcc0_sla": ("picklist", "SLA"),
    "crcc0_slaexpirationdate": ("datetime", "SLA Expiration Date"),
    "crcc0_slaserialnumber": ("text", "SLA Serial Number"),
    "crcc0_numberoflocations": ("int", "Number of Locations"),
}


def new_guid() -> str:
    return str(uuid.uuid4()).upper()


def api_request(method: str, path: str, body: dict | None = None, extra_headers: dict | None = None):
    env = os.environ["DATAVERSE_URL"].rstrip("/")
    token = get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
        "Accept": "application/json",
        "MSCRM.SolutionUniqueName": SOLUTION_NAME,
    }
    if extra_headers:
        headers.update(extra_headers)
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode()
    if "?" in path:
        base, query = path.split("?", 1)
        path = f"{base}?{urllib.parse.quote(query, safe='=$&(),')}"
    req = urllib.request.Request(f"{env}/api/data/v9.2/{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read()
            return json.loads(raw) if raw else {}, resp.headers
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        raise RuntimeError(f"{method} {path} failed ({e.code}): {err_body}") from e


def find_form_by_name(name: str) -> dict | None:
    encoded = name.replace("'", "''")
    data, _ = api_request(
        "GET",
        f"systemforms?$filter=objecttypecode eq 'account' and name eq '{encoded}'&$select=formid,name,formxml,type",
    )
    values = data.get("value", [])
    return values[0] if values else None


def _cell_inner(field: str, behavior: str) -> str:
    ctrl_type, default_label = FIELD_CONTROL.get(field, ("text", field))
    classid = CONTROL_CLASSIDS[ctrl_type]
    cell_id = "{" + new_guid() + "}"
    disabled_attr = ' disabled="true"' if behavior == "Readonly" else ""
    label_text = xml_escape.escape(default_label)
    return f"""                      <cell id="{cell_id}">
                        <labels><label description="{label_text}" languagecode="1033" /></labels>
                        <control id="{field}" classid="{classid}" datafieldname="{field}"{disabled_attr} />
                      </cell>"""


def _rows_xml(fields: list[dict], columns: int) -> str:
    rows = []
    if columns == 1:
        for f in fields:
            rows.append(f"                    <row>\n{_cell_inner(f['dataverseField'], f['behavior'])}\n                    </row>")
    else:
        for i in range(0, len(fields), 2):
            left = fields[i]
            right = fields[i + 1] if i + 1 < len(fields) else None
            if right:
                rows.append(
                    f"                    <row>\n{_cell_inner(left['dataverseField'], left['behavior'])}\n"
                    f"{_cell_inner(right['dataverseField'], right['behavior'])}\n                    </row>"
                )
            else:
                rows.append(f"                    <row>\n{_cell_inner(left['dataverseField'], left['behavior'])}\n                    </row>")
    return "\n".join(rows)


def section_xml(label: str, fields: list[dict], columns: int = 2) -> str:
    sec_id = "{" + new_guid() + "}"
    col_attr = "11" if columns == 2 else "1"
    safe_label = xml_escape.escape(label)
    rows_xml = _rows_xml(fields, columns)
    showlabel = "true" if label not in ("Description Information",) else "false"
    return f"""                <section showlabel="{showlabel}" showbar="false" IsUserDefined="0" id="{sec_id}" columns="{col_attr}">
                  <labels><label description="{safe_label}" languagecode="1033" /></labels>
                  <rows>
{rows_xml}
                  </rows>
                </section>"""


def build_form_xml(sections: list[dict]) -> str:
    tab_id = "{" + new_guid() + "}"
    section_blocks = []
    for sec in sections:
        label = sec["label"]
        fields = sec["fields"]
        cols = 1 if label == "Description Information" else 2
        section_blocks.append(section_xml(label, fields, columns=cols))

    sections_joined = "\n".join(section_blocks)
    return f"""<form><tabs><tab verticallayout="true" id="{tab_id}" IsUserDefined="1"><labels><label description="Summary" languagecode="1033" /></labels><columns><column width="100%"><sections>
{sections_joined}
              </sections></column></columns></tab></tabs></form>"""


def publish_account():
    body = {
        "ParameterXml": "<importexportxml><entities><entity>account</entity></entities></importexportxml>"
    }
    api_request("POST", "PublishXml", body)


def main():
    field_map = json.loads(FIELD_MAP_PATH.read_text(encoding="utf-8"))
    form_xml = build_form_xml(field_map["formSections"])

    existing = find_form_by_name(FORM_NAME)
    if existing:
        form_id = existing["formid"]
        print(f"Updating form: {FORM_NAME} ({form_id})")
        api_request("PATCH", f"systemforms({form_id})", {"formxml": form_xml})
    else:
        print(f"Creating form: {FORM_NAME}")
        _, headers = api_request(
            "POST",
            "systemforms",
            {
                "name": FORM_NAME,
                "objecttypecode": "account",
                "type": 2,
                "formxml": form_xml,
                "iscustomizable": {"Value": True},
            },
        )
        print(f"  Created: {headers.get('OData-EntityId')}")

    print("Publishing account entity...")
    publish_account()
    print("Form published.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
