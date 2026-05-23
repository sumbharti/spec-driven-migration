"""Shared paths and environment helpers for Salesforce Account migration."""

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SF_ACCOUNT_ROOT = REPO_ROOT / "src" / "Entity" / "Account"
SF_FIELDS_DIR = SF_ACCOUNT_ROOT / "objects" / "Account" / "fields"
SF_LAYOUT_PATH = SF_ACCOUNT_ROOT / "layouts" / "Account-Account Layout.layout-meta.xml"
SF_LIST_VIEWS_DIR = SF_ACCOUNT_ROOT / "objects" / "Account" / "listViews"
FIELD_MAP_PATH = Path(__file__).resolve().parent / "account-field-map.json"
INVENTORY_PATH = Path(__file__).resolve().parent / "env-inventory.json"

DV_PLUGIN_DIR = REPO_ROOT / ".github" / "plugins" / "dataverse"
SOLUTION_NAME = os.environ.get("SOLUTION_NAME", "AccountMigration")
PUBLISHER_PREFIX = os.environ.get("PUBLISHER_PREFIX", "crcc0")


def ensure_dataverse_scripts_on_path():
    scripts_dir = str(DV_PLUGIN_DIR / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)


def load_dataverse_env():
    ensure_dataverse_scripts_on_path()
    os.chdir(DV_PLUGIN_DIR)
    from auth import load_env

    load_env()
    os.environ.setdefault("SOLUTION_NAME", SOLUTION_NAME)
    os.environ.setdefault("PUBLISHER_PREFIX", PUBLISHER_PREFIX)
