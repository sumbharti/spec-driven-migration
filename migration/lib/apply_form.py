"""Create or update main form from field-map formSections."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
import uuid
import xml.sax.saxutils as xml_escape
from pathlib import Path

from lib.account_config import FIELD_CONTROL
from lib.registry import field_map_path, get_entity_entry, load_registry

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


def new_guid() -> str:
    return str(uuid.uuid4()).upper()


def api_request(method: str, path: str, body: dict | None, solution_name: str, get_token):
    env = os.environ["DATAVERSE_URL"].rstrip("/")
    token = get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
        "Accept": "application/json",
        "MSCRM.SolutionUniqueName": solution_name,
    }
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
        raise RuntimeError(f"{method} {path} failed ({e.code}): {e.read().decode()}") from e


def find_form_by_name(target_entity: str, name: str, get_token, solution_name: str) -> dict | None:
    encoded = name.replace("'", "''")
    data, _ = api_request(
        "GET",
        f"systemforms?$filter=objecttypecode eq '{target_entity}' and name eq '{encoded}'&$select=formid,name,formxml,type",
        None,
        solution_name,
        get_token,
    )
    values = data.get("value", [])
    return values[0] if values else None


def _cell_inner(field: str, behavior: str) -> str:
    ctrl_type, default_label = FIELD_CONTROL.get(field, ("text", field))
    classid = CONTROL_CLASSIDS[ctrl_type]
    cell_id = "{" + new_guid() + "}"
    disabled_attr = ' disabled="true"' if behavior == "Readonly" else ""
    required_attr = ' required="true"' if behavior == "Required" else ""
    label_text = xml_escape.escape(default_label)
    return f"""                      <cell id="{cell_id}">
                        <labels><label description="{label_text}" languagecode="1033" /></labels>
                        <control id="{field}" classid="{classid}" datafieldname="{field}"{disabled_attr}{required_attr} />
                      </cell>"""


def _rows_xml(fields: list[dict], columns: int) -> str:
    rows = []
    if columns == 1:
        for f in fields:
            rows.append(
                f"                    <row>\n{_cell_inner(f['dataverseField'], f['behavior'])}\n                    </row>"
            )
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
                rows.append(
                    f"                    <row>\n{_cell_inner(left['dataverseField'], left['behavior'])}\n                    </row>"
                )
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


def publish_entity(target_entity: str, get_token):
    body = {
        "ParameterXml": f"<importexportxml><entities><entity>{target_entity}</entity></entities></importexportxml>"
    }
    env = os.environ["DATAVERSE_URL"].rstrip("/")
    token = get_token()
    req = urllib.request.Request(
        f"{env}/api/data/v9.2/PublishXml",
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        resp.read()


def apply_form(repo_root: Path, registry_path: Path, entity_package: str, get_token) -> int:
    registry = load_registry(registry_path)
    entry = get_entity_entry(registry, entity_package)
    map_path = field_map_path(repo_root, entry)
    field_map = json.loads(map_path.read_text(encoding="utf-8"))
    target = field_map["targetEntity"]
    solution = field_map["solutionName"]
    form_name = field_map.get("formDisplayName") or entry["formDisplayName"]
    form_xml = build_form_xml(field_map["formSections"])

    existing = find_form_by_name(target, form_name, get_token, solution)
    if existing:
        form_id = existing["formid"]
        print(f"Updating form: {form_name} ({form_id})")
        api_request("PATCH", f"systemforms({form_id})", {"formxml": form_xml}, solution, get_token)
    else:
        print(f"Creating form: {form_name}")
        _, headers = api_request(
            "POST",
            "systemforms",
            {
                "name": form_name,
                "objecttypecode": target,
                "type": 2,
                "formxml": form_xml,
                "iscustomizable": {"Value": True},
            },
            solution,
            get_token,
        )
        print(f"  Created: {headers.get('OData-EntityId')}")

    print(f"Publishing {target} entity...")
    publish_entity(target, get_token)
    print("Form published.")
    return 0
