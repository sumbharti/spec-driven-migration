# Implementation Plan: Migrate Salesforce Entity Metadata to Dataverse

**Branch**: `001-migrate-salesforce-customizations` | **Date**: 2026-05-23 | **Spec**: [spec.md](./spec.md)

**Input**: Migrate fields, form layout, and validation from Salesforce `src/Entity` to Dataverse using `.github/plugins/dataverse` skills. **Account** is the first entity package; additional entities will be added as sibling folders under `src/Entity/`.

## Summary

Discover every entity package under `src/Entity/{EntityPackage}/`, parse each into a shared JSON contract, apply **fields**, **form layout**, and **validation** per entity in a target Dataverse environment inside one solution, validate, then export/unpack to `solutions/`. **Account** (`src/Entity/Account` → standard `account`) is the **pilot**; new IT drops add folders (e.g. `src/Entity/Contact/`) and registry rows—no pipeline fork after shared libraries exist. Plugin skills: **dv-connect**, **dv-metadata**, **dv-solution**, **dv-query**, **dv-overview**.

## In-scope metadata per entity package

| Salesforce source | Dataverse target | Plugin skill |
|-------------------|------------------|--------------|
| `objects/*/fields/*__c.field-meta.xml` | Custom columns (`{prefix}_*`) | **dv-metadata** |
| Field `required` in metadata | Column `RequiredLevel` | **dv-metadata** |
| `layouts/*.layout-meta.xml` | Main form + sections | **dv-metadata** → `forms-and-views.md` (Web API) |
| Layout `Required` / `Readonly` | Control `required` / `disabled` + publish | **dv-metadata** |
| Standard fields on layout | Mapped standard columns | Contract + registry |
| Packaging | Unmanaged solution in git | **dv-solution** |
| Environment / auth | `.env`, `scripts/auth.py` | **dv-connect**, **dv-overview** |

**Out of scope**: `src/Apex`, web links, list views, record data, security profiles.

## Multi-entity source model

```text
src/Entity/
├── Account/                    # Pilot (exists)
│   ├── objects/Account/fields/
│   └── layouts/
└── {FuturePackage}/           # Added by IT
    ├── objects/{SfObject}/
    └── layouts/
```

**Discovery**: Child of `src/Entity/` with both `objects/` and `layouts/` = entity package.

**Registry**: `migration/entity-registry.json` — one row per package (`targetTable`, `targetTableKind`, `formDisplayName`, `status`).

**Solution**: Single umbrella **AccountMigration** (`crcc0_` prefix) for all packages unless ALM requires split later.

## Technical Context

**Language/Version**: Python 3.10+  
**Primary Dependencies**: `PowerPlatform-Dataverse-Client`, `azure-identity`; PAC CLI; `.github/plugins/dataverse/scripts/auth.py`  
**Storage**: Dataverse; `migration/entity-registry.json`, `migration/maps/*-field-map.json`, `solutions/AccountMigration/`  
**Testing**: `validate_migration.py` (Account); future `validate_all.py`  
**Target Platform**: Microsoft Dataverse / Dynamics 365  
**Project Type**: Multi-entity metadata migration + solution ALM  
**Performance Goals**: Idempotent per-entity runs; 5–30s waits between metadata bursts  
**Constraints**: Constitution standard-table-first; environment-first authoring; solution-bound components  
**Scale/Scope**: 1 package today (Account); N packages under `src/Entity/`  

## Constitution Check

*GATE: Per entity before apply.*

| Principle | Account pilot | Multi-entity rule |
|-----------|---------------|-------------------|
| D365 First | Standard `account` | Prefer standard DV table per SF object |
| Business value | Layout-referenced fields | Same per package |
| ALM discipline | AccountMigration + `crcc0_` | One export covers all entities in solution |
| Minimal replication | No custom Account table | Custom table only with documented approval |

**Status**: PASS for Account; each new registry entry requires constitution notes before apply.

## Project Structure

### Documentation

```text
specs/001-migrate-salesforce-customizations/
├── plan.md, research.md, data-model.md, quickstart.md
├── contracts/d365-migration-artifact-contract.md
└── tasks.md                    # /speckit-tasks
```

### Repository

```text
src/Entity/{EntityPackage}/       # Multi-entity catalog
migration/
├── entity-registry.json          # Catalog (Account pilot)
├── account-field-map.json        # Pilot contract (→ maps/ when lib exists)
├── parse_sf_account.py           # Pilot; → lib/parse_entity.py
├── apply_account_metadata.py     # Fields + validation (columns)
├── apply_account_form.py         # Form layout
├── validate_migration.py
└── setup_solution.py
.github/plugins/dataverse/skills/ # dv-metadata, dv-solution, dv-connect, dv-query
solutions/AccountMigration/
```

## Implementation Phases

### Phase 0 — Registry & discovery

| Step | Deliverable |
|------|-------------|
| Maintain `entity-registry.json` | Account row; discover new folders |
| Fail if disk has package not in registry | Prevents silent skips |

### Phase 1 — Shared pipeline (before entity #2)

| Step | Deliverable |
|------|-------------|
| `lib/parse_entity.py`, `lib/apply_metadata.py`, `lib/apply_form.py` | Parameterized by `entityPackage` |
| `migrate_entity.py --entity Account\|all` | Single entry point |
| Contracts under `migration/maps/{package}-field-map.json` | Per contract v1.1 |

### Phase 2 — Account pilot (fields, form, validation)

| Step | Skill | FR |
|------|-------|-----|
| Parse Account XML → field-map JSON | — | FR-001, FR-007 |
| Create custom columns on `account` | dv-metadata | FR-002 |
| Set column RequiredLevel from field XML | dv-metadata | FR-006 |
| Build main form from layout sections | dv-metadata (Web API) | FR-004, FR-005 |
| Layout Required on controls (gap) | dv-metadata | FR-005 |
| PublishXml for `account` | dv-metadata | — |
| `validate_migration.py` | dv-query | SC-001–003 |

### Phase 3 — Onboard additional `src/Entity/{Package}/`

Repeat Phase 2 per registry row: constitution gate → maps → apply → validate → update `data-model.md`.

### Phase 4 — ALM

`pac solution export` + `unpack` → commit `solutions/AccountMigration/` (dv-solution).

## Plugin skill matrix

| Intent | Skill | Rule |
|--------|-------|------|
| Init / auth | dv-connect | Python only; use plugin `auth.py` |
| Columns / tables | dv-metadata | SDK first; Web API for picklist/memo |
| Forms / publish | dv-metadata | Web API; unique GUIDs; PublishXml |
| Export to git | dv-solution | Unmanaged export → unpack |
| Confirm env | dv-overview | `pac org who` before mutate |

**Anti-patterns**: Hand-write new Entity.xml; npm tooling; metadata outside solution; fork scripts per entity.

## Per-entity onboarding checklist

1. Add `src/Entity/{Package}/` (IT drop).  
2. Add registry row + constitution review.  
3. Define explicit field maps (no blind type inference).  
4. `migrate_entity.py --entity {Package}`.  
5. Section in `data-model.md`.  
6. Validate + export solution.

## Complexity Tracking

| Item | Justification |
|------|----------------|
| Web API for forms | SDK does not support systemforms |
| Account-only scripts (interim) | Pilot until Phase 1 lib extraction |

## Readiness

| Artifact | Path |
|----------|------|
| Plan | [plan.md](./plan.md) |
| Research | [research.md](./research.md) |
| Data model | [data-model.md](./data-model.md) |
| Contract | [contracts/d365-migration-artifact-contract.md](./contracts/d365-migration-artifact-contract.md) |
| Quickstart | [quickstart.md](./quickstart.md) |
| Registry | `migration/entity-registry.json` |

**Next**: `/speckit-tasks` for Phase 0–2 work items.  
**Gaps**: Shared `migration/lib/`; form `Required` on controls in `apply_account_form.py`.
