# Contract: Salesforce → Dataverse Migration Artifacts

**Version**: 1.1.0  
**Feature**: 001-migrate-salesforce-customizations  
**Consumer**: `migration/lib/parse_entity.py`, `migration/migrate_entity.py`, apply/validate scripts

## Purpose

Defines the JSON contract produced by parsing one entity package under `src/Entity/{EntityPackage}/` and consumed by shared apply/validate code. **One file per entity package** in `migration/maps/`.

**Reference implementation**: `migration/account-field-map.json` (pilot; may move to `migration/maps/account-field-map.json`)

## Root object

```json
{
  "entityPackage": "string (folder name under src/Entity, e.g. Account)",
  "salesforceObject": "string (e.g. Account)",
  "sourcePath": "string (e.g. src/Entity/Account)",
  "publisherPrefix": "string (e.g. crcc0)",
  "solutionName": "string (e.g. AccountMigration)",
  "targetEntity": "string (logical name, e.g. account)",
  "targetTableKind": "standard | custom",
  "formDisplayName": "string (e.g. Account - Salesforce Layout)",
  "standardFieldMap": { "SalesforceApiName": "dataverseLogicalName" },
  "customFields": [ "CustomFieldEntry" ],
  "picklistOptionValues": { "SalesforceApiName": { "Label": 100000000 } },
  "formSections": [ "FormSection" ],
  "listViews": [ "ListView (optional, out of spec scope)" ]
}
```

## CustomFieldEntry

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| salesforceApiName | string | yes | SF API name (e.g. `CustomerPriority__c`) |
| dataverseLogicalName | string | yes | Lowercase logical name with prefix |
| displayName | string | yes | User-facing label |
| salesforceType | string | yes | SF metadata type |
| dataverseType | string | yes | `bool`, `picklist`, `string`, `int`, `date`, `memo` |
| picklistValues | string[] | no | Ordered labels when SF type is Picklist |
| defaultValue | boolean | no | For Checkbox fields |

## FormSection

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| label | string | yes | Section title from layout XML |
| fields | FormField[] | yes | Ordered fields in section |

## FormField

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| salesforceField | string | yes | SF field API name |
| dataverseField | string | yes | Target column logical name |
| kind | string | yes | `standard` or `custom` |
| behavior | string | yes | `Edit`, `Required`, or `Readonly` from layout |

### Behavior → apply rules

| behavior | Column apply | Form apply |
|----------|--------------|------------|
| Edit | Per field metadata | Control enabled |
| Required | Set RequiredLevel if field metadata also required; Name uses platform default | Control `required="true"` |
| Readonly | — | Control `disabled="true"` |

## Entity registry (catalog-level)

Separate file: `migration/entity-registry.json`

```json
{
  "solutionName": "AccountMigration",
  "publisherPrefix": "crcc0",
  "entities": [
    {
      "entityPackage": "Account",
      "salesforceObject": "Account",
      "targetTable": "account",
      "targetTableKind": "standard",
      "mainLayoutGlob": "Account-Account Layout.layout-meta.xml",
      "formDisplayName": "Account - Salesforce Layout",
      "status": "pilot"
    }
  ]
}
```

Every discovered folder under `src/Entity/` with `objects/` + `layouts/` MUST have a registry entry before apply.

## Validation rules (contract-level)

1. Every `customFields[].dataverseLogicalName` MUST start with `{publisherPrefix}_`.
2. Every `formSections[].fields[].dataverseField` MUST exist in `standardFieldMap` values or `customFields[].dataverseLogicalName`.
3. For `dataverseType: picklist`, `picklistValues` MUST be non-empty and `picklistOptionValues` MUST contain integer codes for each label.
4. `solutionName` MUST match `MSCRM.SolutionUniqueName` header on all apply API calls.
5. `entityPackage` MUST match the folder name under `src/Entity/`.

## Environment variables (apply phase)

Loaded from `.github/plugins/dataverse/.env` via `migration/common.py`:

| Variable | Purpose |
|----------|---------|
| DATAVERSE_URL | Target environment |
| TENANT_ID, CLIENT_ID, CLIENT_SECRET | Auth |
| SOLUTION_NAME | Solution unique name |
| PUBLISHER_PREFIX | Column prefix |

## Validate script expectations

`validate_migration.py` MUST verify:

- All `customFields[].dataverseLogicalName` exist on `targetEntity`
- Main form named per apply script convention exists (e.g. `Account - Salesforce Layout`)
- Optional: per-field RequiredLevel for fields marked required in contract

## Versioning

- **MINOR**: Add optional properties backward-compatible for apply scripts
- **MAJOR**: Rename required properties or change behavior enum values
