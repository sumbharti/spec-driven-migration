# Salesforce Account → Dataverse Migration

Scripts migrate Account metadata from [`src/Entity/Account`](../src/Entity/Account) into the **AccountMigration** Dataverse solution (`crcc0_` publisher prefix).

## Prerequisites

- Python 3.10+
- `pip install PowerPlatform-Dataverse-Client azure-identity`
- [`.github/plugins/dataverse/.env`](../.github/plugins/dataverse/.env) with `DATAVERSE_URL`, `TENANT_ID`, `CLIENT_ID`, `CLIENT_SECRET`, `SOLUTION_NAME=AccountMigration`, `PUBLISHER_PREFIX=crcc0`
- PAC CLI authenticated to the target environment (`pac auth list`)

## Run order

From this directory:

```powershell
python parse_sf_account.py
python setup_solution.py
python env_inventory.py
python apply_account_metadata.py
python apply_account_form.py
python apply_account_views.py
python validate_migration.py
```

Export to source control (from repo root):

```powershell
pac solution export --name AccountMigration --path solutions/AccountMigration.zip --managed false --overwrite
pac solution unpack --zipfile solutions/AccountMigration.zip --folder solutions/AccountMigration
```

## Artifacts

| File | Purpose |
|------|---------|
| `account-field-map.json` | Generated SF → Dataverse mapping contract |
| `env-inventory.json` | Environment column/form inventory snapshot |
| `solutions/AccountMigration/` | Unpacked solution (after `pac solution unpack`) |
