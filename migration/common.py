"""Shared paths and environment helpers for Salesforce entity migration."""

import json
import os
import sys
from pathlib import Path

MIGRATION_DIR = Path(__file__).resolve().parent
REPO_ROOT = MIGRATION_DIR.parent
ENTITY_SRC_ROOT = REPO_ROOT / "src" / "Entity"
REGISTRY_PATH = MIGRATION_DIR / "entity-registry.json"
MAPS_DIR = MIGRATION_DIR / "maps"
INVENTORY_PATH = MIGRATION_DIR / "env-inventory.json"

# Legacy paths (Account pilot)
SF_ACCOUNT_ROOT = ENTITY_SRC_ROOT / "Account"
SF_FIELDS_DIR = SF_ACCOUNT_ROOT / "objects" / "Account" / "fields"
SF_LAYOUT_PATH = SF_ACCOUNT_ROOT / "layouts" / "Account-Account Layout.layout-meta.xml"
SF_LIST_VIEWS_DIR = SF_ACCOUNT_ROOT / "objects" / "Account" / "listViews"
FIELD_MAP_PATH = MAPS_DIR / "account-field-map.json"

DV_PLUGIN_DIR = REPO_ROOT / ".github" / "plugins" / "dataverse"
SOLUTION_NAME = os.environ.get("SOLUTION_NAME", "AccountMigration")
PUBLISHER_PREFIX = os.environ.get("PUBLISHER_PREFIX", "crcc0")


def ensure_migration_on_path():
    migration_dir = str(MIGRATION_DIR)
    if migration_dir not in sys.path:
        sys.path.insert(0, migration_dir)


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


def load_registry() -> dict:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
