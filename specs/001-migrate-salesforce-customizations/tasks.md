# Tasks: Migrate Salesforce Entity Metadata to Dataverse

**Input**: Design documents from `/specs/001-migrate-salesforce-customizations/`  
**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/d365-migration-artifact-contract.md](./contracts/d365-migration-artifact-contract.md)

**Tests**: Not requested in spec — validation via `migration/validate_migration.py` and manual form saves per [quickstart.md](./quickstart.md).

**Organization**: Tasks grouped by user story (P1 fields → P2 forms → P3 validation). Account is the pilot under `src/Entity/Account/`; foundational work enables future folders under `src/Entity/`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Parallelizable (different files, no incomplete dependencies)
- **[US1/US2/US3]**: Maps to spec user stories

## Path Conventions

- **Source**: `src/Entity/{EntityPackage}/`
- **Tooling**: `migration/`, `migration/lib/`, `migration/maps/`
- **Plugins**: `.github/plugins/dataverse/skills/`, `.github/plugins/dataverse/.env`
- **Solution output**: `solutions/AccountMigration/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Environment, directories, and documentation paths for multi-entity migration.

- [x] T001 Confirm Dataverse plugin init per dv-connect (`.github/plugins/dataverse/.env`, `scripts/auth.py`) and document vars in `migration/README.md`
- [x] T002 [P] Create `migration/maps/` directory for per-entity field-map JSON per `specs/001-migrate-salesforce-customizations/contracts/d365-migration-artifact-contract.md`
- [x] T003 [P] Add `migration/lib/__init__.py` package scaffold for shared parse/apply/validate modules
- [x] T004 [P] Verify `migration/common.py` loads plugin `.env` and exposes `SOLUTION_NAME`, `PUBLISHER_PREFIX` for all scripts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Multi-entity registry, discovery, and shared pipeline — **must complete before user story apply work on new entities**. Account pilot can use interim wrappers until T006–T010 land.

**⚠️ CRITICAL**: US1–US3 apply tasks assume solution exists and registry is authoritative.

- [x] T005 Implement `discover_entity_packages()` in `migration/lib/discovery.py` (scan `src/Entity/*/objects` + `layouts`)
- [x] T006 Implement `validate_registry_vs_disk()` in `migration/lib/discovery.py` (fail if folder missing from `migration/entity-registry.json`)
- [x] T007 [P] Align `migration/entity-registry.json` fields with contract v1.1 (`fieldMapPath` → `migration/maps/account-field-map.json`)
- [x] T008 Extract Salesforce XML parsing into `migration/lib/parse_entity.py` (parameter: `entityPackage`, reads registry)
- [x] T009 [P] Extract column apply logic into `migration/lib/apply_metadata.py` (idempotent; `MSCRM.SolutionUniqueName`; dv-metadata patterns)
- [x] T010 [P] Extract form apply logic into `migration/lib/apply_form.py` (Web API systemforms + PublishXml per `.github/plugins/dataverse/skills/dv-metadata/references/forms-and-views.md`)
- [x] T011 Extract validation into `migration/lib/validate_entity.py` (columns + main form per registry `formDisplayName`)
- [x] T012 Create `migration/migrate_entity.py` CLI with `--entity Account` and `--entity all` driven by `migration/entity-registry.json`
- [x] T013 Refactor `migration/parse_sf_account.py` to thin wrapper calling `migration/lib/parse_entity.py` for Account
- [ ] T014 Run `migration/setup_solution.py` once to ensure **AccountMigration** solution and `crcc0` publisher exist (dv-solution)

**Checkpoint**: Registry + shared lib + CLI ready; Account wrappers call lib.

---

## Phase 3: User Story 1 — Recreate custom fields (Priority: P1) 🎯 MVP

**Goal**: Every in-scope custom field under `src/Entity/Account` exists as a Dataverse column on `account` with documented mapping.

**Independent Test**: For each `*__c.field-meta.xml` under `src/Entity/Account/objects/Account/fields/`, verify column exists on `account` with correct label, type, and picklist options per `migration/maps/account-field-map.json`.

### Implementation for User Story 1

- [x] T015 [US1] Extend `migration/lib/parse_entity.py` to emit full `customFields` + `standardFieldMap` for Account from `src/Entity/Account/`
- [x] T016 [US1] Run parse for Account → write `migration/maps/account-field-map.json` (include `entityPackage`, `picklistOptionValues` per contract)
- [x] T017 [US1] Implement picklist/memo/date column payloads in `migration/lib/apply_metadata.py` following `migration/apply_account_metadata.py` Web API patterns
- [ ] T018 [P] [US1] Implement simple types via SDK `client.tables.add_columns()` in `migration/lib/apply_metadata.py` where dv-metadata allows
- [ ] T019 [US1] Apply Account custom columns to environment via `python migration/migrate_entity.py --entity Account` (metadata step only)
- [ ] T020 [US1] Run `migration/env_inventory.py` and confirm all `customFields` logical names exist on `account`
- [x] T021 [US1] Update Account exception log in `specs/001-migrate-salesforce-customizations/data-model.md` for unmapped SF fields (FR-003, FR-007)

**Checkpoint**: SC-001 met for Account — 100% custom fields migrated or documented as exceptions.

---

## Phase 4: User Story 2 — Reproduce form layout (Priority: P2)

**Goal**: Main form **Account - Salesforce Layout** mirrors Salesforce sections, field order, and read-only behaviors from `src/Entity/Account/layouts/Account-Account Layout.layout-meta.xml`.

**Independent Test**: Open main form on `account` in target environment; compare sections/fields to source layout and `formSections` in `migration/maps/account-field-map.json`.

**Depends on**: US1 columns exist (T019).

### Implementation for User Story 2

- [x] T022 [US2] Build FormXML from `formSections` in `migration/lib/apply_form.py` (section labels, 1- vs 2-column rows)
- [x] T023 [US2] Map layout `Readonly` behavior to control `disabled="true"` in `migration/lib/apply_form.py`
- [ ] T024 [US2] Create or PATCH main form `Account - Salesforce Layout` on `account` via `migration/migrate_entity.py --entity Account` (form step)
- [ ] T025 [US2] Call `POST /api/data/v9.2/PublishXml` for `account` after form create/update in `migration/lib/apply_form.py`
- [ ] T026 [US2] Export/unpack interim check: `pac solution export` → `solutions/AccountMigration/` and verify `Entities/Account/FormXml/main/*.xml` contains migrated sections
- [x] T027 [US2] Document layout field exclusions (web links, related lists) in `specs/001-migrate-salesforce-customizations/data-model.md` (FR-004)

**Checkpoint**: SC-002 target for Account — layout parity reviewable against mapping doc.

---

## Phase 5: User Story 3 — Preserve validation intent (Priority: P3)

**Goal**: Required constraints from field metadata and layout `Required` behaviors are enforced on save in Dataverse.

**Independent Test**: Attempt save on Account form without required fields (e.g. Name); confirm block with clear message per spec acceptance scenarios.

**Depends on**: US2 form published (T024–T025).

### Implementation for User Story 3

- [x] T028 [US3] Set column `RequiredLevel` from SF field `<required>true</required>` in `migration/lib/apply_metadata.py`
- [x] T029 [US3] Implement layout `behavior=Required` → control `required="true"` in `migration/lib/apply_form.py` (close plan gap)
- [x] T030 [US3] Extend `migration/lib/validate_entity.py` to assert RequiredLevel for fields marked required in `migration/maps/account-field-map.json`
- [ ] T031 [US3] Run `python migration/lib/validate_entity.py` or `migration/validate_migration.py` for Account after validation changes
- [x] T032 [US3] Record validation mapping table (field vs layout rules) in `specs/001-migrate-salesforce-customizations/data-model.md` under Account section
- [ ] T033 [US3] Manual save test on Account form per `specs/001-migrate-salesforce-customizations/quickstart.md` (SC-003, SC-005)

**Checkpoint**: SC-003 met for Account — required rules enforced or documented as deferrals.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: ALM, multi-entity readiness, and documentation for IT adding folders under `src/Entity/`.

- [ ] T034 [P] Final `pac solution export` + `unpack` to `solutions/AccountMigration/` per dv-solution; remove zip after unpack
- [ ] T035 [P] Run `pac solution list-components --solutionUniqueName AccountMigration` and verify Account table, columns, main form listed
- [x] T036 Create `migration/onboard_entity.md` checklist for new `src/Entity/{Package}/` (registry row, constitution, maps, data-model section)
- [x] T037 Implement `migration/validate_all.py` invoking `validate_entity` for each `migration/entity-registry.json` entry with `status` active/pilot
- [x] T038 [P] Update `migration/README.md` with multi-entity run order (`migrate_entity.py --entity all`) and plugin skill references
- [x] T039 [P] Update `specs/001-migrate-salesforce-customizations/quickstart.md` if paths changed to `migration/maps/`
- [ ] T040 Stakeholder mapping review: walk `migration/maps/account-field-map.json` + `data-model.md` for Account (SC-004)

---

## Phase 7: Future Entity Packages (When IT Adds Folders)

**Purpose**: Repeatable onboarding — **do not start until a new folder exists under `src/Entity/`**.

- [ ] T041 Add registry row + constitution notes in `migration/entity-registry.json` for new `src/Entity/{Package}/`
- [ ] T042 Add `{Package}` field maps and `CUSTOM_FIELD_MAP` config in `migration/lib/parse_entity.py`
- [ ] T043 Add `specs/001-migrate-salesforce-customizations/data-model.md` section for new entity
- [ ] T044 Run `python migration/migrate_entity.py --entity {Package}` and validate + export solution

---

## Dependencies & Execution Order

### Phase Dependencies

```text
Phase 1 (Setup) → Phase 2 (Foundational) → Phase 3 (US1) → Phase 4 (US2) → Phase 5 (US3) → Phase 6 (Polish)
Phase 7 triggers when new src/Entity/{Package}/ appears
```

### User Story Dependencies

| Story | Depends on | Independent test |
|-------|------------|------------------|
| US1 (P1) | Phase 2 complete | Column inventory vs field-map JSON |
| US2 (P2) | US1 columns on `account` | Form sections vs layout XML |
| US3 (P3) | US2 form published | Save rejected without required values |

US2 and US3 are sequentially dependent on US1 for Account; foundational lib (Phase 2) blocks clean multi-entity expansion.

### Parallel Opportunities

- **Phase 1**: T002, T003, T004 in parallel after T001
- **Phase 2**: T009 ∥ T010; T007 ∥ T008 after T005–T006
- **Phase 3**: T018 ∥ T017 after T016
- **Phase 6**: T034 ∥ T035 ∥ T038 ∥ T039

---

## Parallel Example: User Story 1

```bash
# After T016, in parallel:
# T018 — SDK column path in migration/lib/apply_metadata.py
# T017 — Web API picklist/memo path in migration/lib/apply_metadata.py

# Then serial:
python migration/migrate_entity.py --entity Account
python migration/env_inventory.py
```

---

## Parallel Example: Foundational Phase

```bash
# After T008 parse_entity.py exists:
# Developer A: T009 apply_metadata.py
# Developer B: T010 apply_form.py
# Merge → T011 validate_entity.py → T012 migrate_entity.py
```

---

## Implementation Strategy

### MVP First (User Story 1 only)

1. Complete Phase 1 + Phase 2 (minimum: T005–T014, T008–T012)
2. Complete Phase 3 (Account columns)
3. **STOP and VALIDATE**: `env_inventory` + field-map review
4. Optional: export solution (subset of T034)

### Incremental Delivery

1. US1 → columns on `account` (MVP)
2. US2 → main form layout
3. US3 → required/readonly enforcement
4. Phase 6 → ALM commit + onboarding docs
5. Phase 7 → each new IT drop under `src/Entity/`

### Suggested MVP Scope

**Through T021 (US1 complete)** — custom Account fields in Dataverse with mapping documentation.

---

## Notes

- Follow **dv-overview** env confirmation (`pac org who`) before T019+ apply tasks
- Never fork per-entity scripts; extend `migration/lib/` and registry only
- List views / `migration/apply_account_views.py` remain out of scope per spec
- All tasks use checklist format: `- [ ] T### [P?] [US?] Description with file path`
