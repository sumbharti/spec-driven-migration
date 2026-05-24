# Research: Salesforce `src/Entity` → Dataverse Metadata Migration

**Feature**: 001-migrate-salesforce-customizations  
**Date**: 2026-05-23

## Decision 1: Environment-first metadata authoring

**Decision**: Create and modify columns, forms, and validation in the target Dataverse environment via API, then export/unpack into `solutions/` with PAC CLI.

**Rationale**: The `dv-metadata` skill states that the environment validates metadata more reliably than hand-written solution XML. Exported XML from `pac solution unpack` is always schema-valid. The repo already follows this pattern (`migration/` scripts → `solutions/AccountMigration/`).

**Alternatives considered**:
- Hand-author `Entity.xml` / `FormXml` only in repo — rejected due to fragile GUIDs, classids, and opaque import failures.
- Maker portal only, no repo — rejected; violates ALM and constitution deployable-solution discipline.

## Decision 2: Standard table first (Account on `account`)

**Decision**: Map Salesforce **Account** to the standard Dataverse **account** table; add custom columns with publisher prefix `crcc0_` inside the **AccountMigration** solution.

**Rationale**: Constitution principle *Model for Dataverse / D365 First* and *Minimal Replication* require preferring standard tables. Account is a standard object in both platforms; only custom fields (`*__c`) need new columns.

**Alternatives considered**:
- Custom table `crcc0_account` mirroring Salesforce — rejected; duplicates platform capability and increases lifecycle cost.

## Decision 3: Three-phase migration pipeline (parse → apply → validate → export)

**Decision**: Use a Python pipeline under `migration/`:

1. **Parse** — `parse_sf_account.py` reads `src/Entity/Account` XML and emits `account-field-map.json` (contract).
2. **Apply** — idempotent scripts create columns (`apply_account_metadata.py`), main form (`apply_account_form.py`); views script exists but is **out of spec scope**.
3. **Validate** — `validate_migration.py` checks columns and main form presence.
4. **Export** — `pac solution export` + `unpack` per `dv-solution` pull-to-repo workflow.

**Rationale**: Separates deterministic parsing from environment mutation; supports re-runs and constitution-compliant ALM.

**Alternatives considered**:
- Single monolithic script — rejected; harder to test and extend per entity package.

## Decision 4: Tool routing per `.github/plugins/dataverse` skills

**Decision**:

| Task | Skill / tool |
|------|----------------|
| Auth, env confirm | `dv-connect`, `scripts/auth.py`, `.github/plugins/dataverse/.env` |
| Publisher + solution | `dv-solution` (`setup_solution.py` / SDK) |
| Custom columns (simple types) | `dv-metadata` — prefer `client.tables.add_columns()` where types match |
| Picklist, memo, date columns | Web API attribute POST with `MSCRM.SolutionUniqueName` (SDK gap) — `apply_account_metadata.py` pattern |
| Main forms | Web API `systemforms` + `PublishXml` — `dv-metadata` / `forms-and-views.md` |
| Layout `Required` / `Readonly` | Form control attributes + column `RequiredLevel` where applicable |
| Post-change ALM | `dv-solution` export/unpack/commit |
| Inventory / validation queries | `dv-query` patterns in `env_inventory.py`, `validate_migration.py` |

**Rationale**: Plugin hard rules: MCP → SDK → Web API. Forms and some attribute types are Web API-only per skill boundaries.

**Alternatives considered**:
- PAC-only for forms — no reliable `pac` form-create command; Web API is documented standard.

## Decision 5: Salesforce type → Dataverse column mapping

**Decision**: Use explicit mapping table in parser (not automatic inference) for custom fields:

| Salesforce type | Dataverse attribute | Notes |
|-------------------|---------------------|-------|
| Checkbox | Boolean | `Active__c` picklist-as-bool mapped separately where needed |
| Picklist | Local choice (OptionSet) | Option values assigned stable ints in `picklistOptionValues` |
| Text | String | Max length from SF metadata when present |
| Number | Whole Number | |
| Date | DateTime (date-only usage) | |
| Html | Memo | Rich text not replicated; plain memo for AI Summary |

**Rationale**: Type mismatches (e.g., SF Picklist stored as DV Boolean for Active) are business decisions requiring documentation, not blind automation.

**Alternatives considered**:
- Fully automatic type inference — rejected; risks silent semantic loss (constitution business-value principle).

## Decision 6: Validation enforcement strategy

**Decision**:

1. **Field metadata `required=true`** → column `RequiredLevel` = `ApplicationRequired` or `BusinessRequired` on create.
2. **Layout `behavior=Required`** (e.g., Name) → enforced on form via control `required="true"` (form-level) in addition to column rules where supported.
3. **Layout `behavior=Readonly`** → control `disabled="true"` on form (existing pattern).
4. **Explicit SF ValidationRule XML** — none in current `src/Entity`; defer to future spec if added.

**Rationale**: Matches spec FR-006 and available source artifacts. Form-only required fields need form XML, not column metadata alone.

**Alternatives considered**:
- Business Rules for all required fields — rejected for v1; portal/XAML complexity per `dv-metadata` guidance.

## Decision 7: Multi-entity catalog under `src/Entity/`

**Decision**: Treat `src/Entity/` as a **catalog of entity packages**—one subdirectory per Salesforce object IT shares (Account first; more folders added over time). Use `migration/entity-registry.json` to map each package to its Dataverse target table, form name, and constitution status. Discover packages by scanning for `objects/` + `layouts/` under each child folder.

**Rationale**: Spec assumes additional entity packages (edge case in spec.md). A registry avoids hard-coding Account-only paths and prevents duplicate apply scripts per entity.

**Alternatives considered**:
- One mega-parser file per new entity — rejected; does not scale.
- Single combined JSON for all entities — rejected; harder to validate and review per business object.

## Decision 8: Contract file as integration boundary

**Decision**: One machine-readable contract per entity package: `migration/maps/{entityPackage}-field-map.json` (e.g. `account-field-map.json`). Shared schema in [d365-migration-artifact-contract.md](./contracts/d365-migration-artifact-contract.md). Human-readable mapping: `data-model.md` section per entity.

**Rationale**: Enables per-entity validate/apply and stakeholder review sessions (SC-004) without re-parsing XML.

## Decision 9: Out-of-scope artifacts

**Decision**: Do not migrate in this feature: `src/Apex`, web links, list views (scripts may remain for reference), record data, security profiles.

**Rationale**: Aligns with updated `spec.md` scope.

## Open items (implementation)

- Add `migration/entity-registry.json` and `migrate_entity.py --entity all` (Phase 0–1 in plan).
- Refactor Account scripts into `migration/lib/` before second entity package lands.
- Extend form apply to set `required="true"` where layout behavior is `Required`.
