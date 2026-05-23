#!/usr/bin/env python3
"""Create or verify AccountMigration solution and crcc0 publisher."""

import os
import sys

from common import PUBLISHER_PREFIX, SOLUTION_NAME, load_dataverse_env

load_dataverse_env()

from auth import get_credential  # noqa: E402
from PowerPlatform.Dataverse.client import DataverseClient  # noqa: E402


def find_publisher(client: DataverseClient):
    pages = client.records.get(
        "publisher",
        filter=f"customizationprefix eq '{PUBLISHER_PREFIX}'",
        select=["publisherid", "uniquename", "friendlyname", "customizationprefix"],
        top=5,
    )
    for page in pages:
        for pub in page:
            return pub
    return None


def find_solution(client: DataverseClient):
    pages = client.records.get(
        "solution",
        filter=f"uniquename eq '{SOLUTION_NAME}'",
        select=["solutionid", "uniquename", "friendlyname", "version"],
        top=1,
    )
    for page in pages:
        for sol in page:
            return sol
    return None


def main():
    url = os.environ["DATAVERSE_URL"]
    client = DataverseClient(url, get_credential())

    publisher = find_publisher(client)
    if publisher:
        publisher_id = publisher["publisherid"]
        print(f"Using publisher: {publisher['uniquename']} (prefix: {publisher['customizationprefix']}_)")
    else:
        publisher_id = client.records.create(
            "publisher",
            {
                "uniquename": f"{PUBLISHER_PREFIX}publisher",
                "friendlyname": f"{PUBLISHER_PREFIX.upper()} Publisher",
                "customizationprefix": PUBLISHER_PREFIX,
                "description": "Publisher for Salesforce Account migration",
            },
        )
        print(f"Created publisher with prefix {PUBLISHER_PREFIX}_")

    solution = find_solution(client)
    if solution:
        print(f"Solution already exists: {solution['uniquename']} v{solution.get('version')}")
        return 0

    solution_id = client.records.create(
        "solution",
        {
            "uniquename": SOLUTION_NAME,
            "friendlyname": "Salesforce Account Migration",
            "version": "1.0.0.0",
            "description": "Account custom fields, forms, and views migrated from Salesforce metadata",
            "publisherid@odata.bind": f"/publishers({publisher_id})",
        },
    )
    print(f"Created solution {SOLUTION_NAME} ({solution_id})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
