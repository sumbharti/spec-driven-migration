#!/usr/bin/env python3
"""Create Dataverse saved queries from Salesforce Account list views."""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

from common import FIELD_MAP_PATH, SOLUTION_NAME, load_dataverse_env

load_dataverse_env()

from auth import get_token  # noqa: E402


def api_request(method: str, path: str, body: dict | None = None):
    env = os.environ["DATAVERSE_URL"].rstrip("/")
    token = get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
        "Accept": "application/json",
        "MSCRM.SolutionUniqueName": SOLUTION_NAME,
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


def view_exists(name: str) -> bool:
    encoded = name.replace("'", "''")
    data, _ = api_request(
        "GET",
        f"savedqueries?$filter=returnedtypecode eq 'account' and name eq '{encoded}'&$select=savedqueryid,name",
    )
    return bool(data.get("value"))


def dv_columns(view: dict) -> list[str]:
    cols = []
    for col in view.get("columns", []):
        dv = col.get("dataverse")
        if dv:
            cols.append(dv)
    if not cols:
        cols = ["name", "telephone1", "address1_stateorprovince"]
    return cols


def build_fetch(view: dict) -> str:
    attrs = dv_columns(view)
    attr_xml = "\n".join(f'    <attribute name="{a}" />' for a in attrs)
    conditions = ['    <condition attribute="statecode" operator="eq" value="0" />']

    scope = view.get("filterScope", "Everything")
    if scope == "Mine":
        conditions.append('    <condition attribute="ownerid" operator="eq-userid" />')

    api = view.get("salesforceApiName", "")
    for filt in view.get("filters", []):
        sf_field = filt.get("field", "")
        value = filt.get("value", "")
        if sf_field == "ACCOUNT.CREATED_DATE" and value == "THIS_WEEK":
            start = datetime.now(timezone.utc).date()
            start = start - timedelta(days=start.weekday())
            conditions.append(
                f'    <condition attribute="createdon" operator="on-or-after" value="{start.isoformat()}" />'
            )
        elif sf_field == "ACCOUNT.CREATED_DATE" and value == "LAST_WEEK":
            end = datetime.now(timezone.utc).date()
            end = end - timedelta(days=end.weekday())
            start = end - timedelta(days=7)
            conditions.append(
                f'    <condition attribute="createdon" operator="on-or-after" value="{start.isoformat()}" />'
            )
            conditions.append(
                f'    <condition attribute="createdon" operator="on-or-before" value="{end.isoformat()}" />'
            )

    if api == "PlatinumandGoldSLACustomers":
        conditions.append('    <condition attribute="crcc0_sla" operator="in">')
        conditions.append('      <value>100000002</value>')  # Platinum
        conditions.append('      <value>100000000</value>')  # Gold
        conditions.append("    </condition>")

    cond_block = "\n".join(conditions)
    return f"""<fetch version="1.0" output-format="xml-platform" mapping="logical" distinct="false">
  <entity name="account">
{attr_xml}
    <order attribute="name" descending="false" />
    <filter type="and">
{cond_block}
    </filter>
  </entity>
</fetch>"""


def build_layout(attrs: list[str]) -> str:
    cells = "\n".join(f'    <cell name="{a}" width="150" />' for a in attrs)
    return f"""<grid name="resultset" object="1" jump="name" select="1" icon="1" preview="1">
  <row name="result" id="accountid">
{cells}
  </row>
</grid>"""


def publish_account():
    body = {
        "ParameterXml": "<importexportxml><entities><entity>account</entity></entities></importexportxml>"
    }
    api_request("POST", "PublishXml", body)


def main():
    field_map = json.loads(FIELD_MAP_PATH.read_text(encoding="utf-8"))
    created = 0
    skipped = 0

    for view in field_map["listViews"]:
        name = view["dataverseName"]
        if view_exists(name):
            print(f"  Skip (exists): {name}")
            skipped += 1
            continue

        attrs = dv_columns(view)
        fetch = build_fetch(view)
        layout = build_layout(attrs)
        print(f"  Creating view: {name}")
        api_request(
            "POST",
            "savedqueries",
            {
                "name": name,
                "returnedtypecode": "account",
                "querytype": 0,
                "fetchxml": fetch,
                "layoutxml": layout,
                "isdefault": False,
                "isprivate": False,
                "isquickfindquery": False,
            },
        )
        created += 1

    if created:
        print("Publishing account views...")
        publish_account()

    print(f"Done. Created: {created}, Skipped: {skipped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
