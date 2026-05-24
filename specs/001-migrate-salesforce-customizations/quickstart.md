# Quickstart: Migrate `src/Entity` to Dataverse

**Feature**: 001-migrate-salesforce-customizations  
**Branch**: `001-migrate-salesforce-customizations`

`src/Entity/` is a **multi-entity catalog**. **Account** is the first package; additional folders will be added by IT as sibling directories.

## Prerequisites

1. Python 3.10+
2. PAC CLI authenticated (`pac auth list`)
3. Dataverse plugin per **dv-connect**:
   - `.github/plugins/dataverse/.env` — `DATAVERSE_URL`, credentials, `SOLUTION_NAME`, `PUBLISHER_PREFIX`
   - `scripts/auth.py`

```powershell
pip install PowerPlatform-Dataverse-Client azure-identity
```

## Confirm environment

```powershell
pac auth list
pac org who
```

## Migrate one entity (Account pilot)

```powershell
python migration/setup_solution.py
python migration/migrate_entity.py --entity Account --steps parse,metadata,form,validate
```

Contract output: `migration/maps/account-field-map.json`

Legacy wrappers (`parse_sf_account.py`, `apply_account_*`, `validate_migration.py`) call the same `migration/lib/` code.

## Migrate all entities

```powershell
python migration/migrate_entity.py --entity all --steps parse,metadata,form,validate
python migration/validate_all.py
```

Driven by `entity-registry.json` and folders under `src/Entity/`.

## Onboard a new entity package

When IT adds `src/Entity/{NewPackage}/`:

1. Verify structure: `objects/{SfObject}/fields/`, `layouts/*.layout-meta.xml`
2. Add entry to `migration/entity-registry.json` (constitution: standard vs custom table)
3. Add field mapping config for that object (explicit maps in parser)
4. Add section to `specs/.../data-model.md`
5. Run `python migrate_entity.py --entity {NewPackage}`
6. Run validate for that entity
7. Export/unpack solution (once; includes all entities)

## Pull to repo (ALM)

```powershell
pac solution export --name AccountMigration --path solutions/AccountMigration.zip --managed false --overwrite
pac solution unpack --zipfile solutions/AccountMigration.zip --folder solutions/AccountMigration --packagetype Unmanaged
Remove-Item solutions/AccountMigration.zip
pac solution list-components --solutionUniqueName AccountMigration
```

Commit `solutions/AccountMigration/`, `migration/entity-registry.json`, and `migration/maps/*.json`.

## Skills (`.github/plugins/dataverse`)

| Step | Skill |
|------|-------|
| Connect | dv-connect |
| Solution / export | dv-solution |
| Columns / tables | dv-metadata |
| Forms | dv-metadata → forms-and-views.md |
| Verify | dv-query |

## Out of scope

- List views, web links, `src/Apex`, record data
