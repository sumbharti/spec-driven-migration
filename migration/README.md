# Salesforce Entity → Dataverse Migration

`src/Entity/` is a **multi-entity catalog** (Account is first; IT adds more folders over time). See `entity-registry.json` for each package’s target table and status.

**Pilot**: Account — custom **fields**, main **form layout**, and **validation** from `src/Entity/Account/` into **AccountMigration** (`crcc0_` prefix).

## Prerequisites

- Python 3.10+
- `pip install PowerPlatform-Dataverse-Client azure-identity`
- [`.github/plugins/dataverse/.env`](../.github/plugins/dataverse/.env):
  - `DATAVERSE_URL`, `TENANT_ID`, `CLIENT_ID`, `CLIENT_SECRET`
  - `SOLUTION_NAME=AccountMigration`, `PUBLISHER_PREFIX=crcc0`
- PAC CLI: `pac auth list` / `pac org who` (confirm target environment before apply)

Plugin skills: **dv-connect**, **dv-metadata**, **dv-solution**, **dv-query**, **dv-overview** under `.github/plugins/dataverse/skills/`.

## Run order (Account or `--entity all`)

From repository root:

```powershell
python migration/migrate_entity.py --entity Account --steps parse,metadata,form,validate
```

Or legacy wrappers:

```powershell
cd migration
python parse_sf_account.py
python setup_solution.py
python apply_account_metadata.py
python apply_account_form.py
python validate_migration.py
```

Validate all registry entities:

```powershell
python migration/validate_all.py
```

## Artifacts

| File | Purpose |
|------|---------|
| `entity-registry.json` | Catalog of `src/Entity/{Package}/` → Dataverse target |
| `maps/{entity}-field-map.json` | Generated contract per entity |
| `lib/` | Shared parse, apply metadata/form, validate |
| `solutions/AccountMigration/` | Unpacked solution (after `pac solution unpack`) |

## Export to source control

```powershell
pac solution export --name AccountMigration --path solutions/AccountMigration.zip --managed false --overwrite
pac solution unpack --zipfile solutions/AccountMigration.zip --folder solutions/AccountMigration --packagetype Unmanaged
```

New entity packages: see [onboard_entity.md](./onboard_entity.md).
