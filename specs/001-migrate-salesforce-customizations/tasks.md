# Tasks: Migrate Salesforce Customizations to D365

**Input**: Design documents from `/specs/001-migrate-salesforce-customizations/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize the Visual Studio solution and plugin project structure required for migration implementation.

- [ ] T001 Create Visual Studio solution `d365-migration/D365Migration.sln`
- [ ] T002 Create .NET Framework 4.6.2 plugin project `d365-migration/D365Migration.Plugin/D365Migration.Plugin.csproj`
- [ ] T003 Create plugin entry file `d365-migration/D365Migration.Plugin/Plugin.cs`
- [ ] T004 Create plugin service file `d365-migration/D365Migration.Plugin/PluginService.cs`
- [ ] T005 Create Dataverse connection configuration placeholder `d365-migration/D365Migration.Plugin/app.config`
- [ ] T006 [P] Create plugin data access service file `d365-migration/D365Migration.Plugin/CrmService.cs`
- [ ] T007 [P] Create plugin tracing helper file `d365-migration/D365Migration.Plugin/Logging.cs`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the core migration design, Dataverse mapping discipline, and secure configuration conventions before story-specific work begins.

- [ ] T008 Define Dataverse entity and field mapping principles in `specs/001-migrate-salesforce-customizations/data-model.md`
- [ ] T009 Document the artifact contract and solution packaging rules in `specs/001-migrate-salesforce-customizations/contracts/d365-migration-artifact-contract.md`
- [ ] T010 [P] Capture the Salesforce `src` metadata inventory and migration scope in `specs/001-migrate-salesforce-customizations/research.md`
- [ ] T011 [P] Update `specs/001-migrate-salesforce-customizations/quickstart.md` with the Visual Studio plugin project creation and secure configuration guidance
- [ ] T012 [P] Add a secure configuration comment to `d365-migration/D365Migration.Plugin/app.config` that explicitly avoids storing connection strings or secrets in source
- [ ] T013 Configure publisher prefix and solution boundary guidance in `specs/001-migrate-salesforce-customizations/contracts/d365-migration-artifact-contract.md`

---

## Phase 3: User Story 1 - Migrate Salesforce metadata into D365 entities and forms (Priority: P1)

**Goal**: Translate Salesforce entity definitions, forms, and validation intent from `src` into target Dataverse entity, form, and business rule designs.

**Independent Test**: Confirm that source entity/form metadata from `src` is mapped into Dataverse design artifacts and that the migration set is documented.

- [ ] T014 [US1] Analyze Salesforce entity definitions in `src` and capture the target Dataverse table design in `specs/001-migrate-salesforce-customizations/data-model.md`
- [ ] T015 [US1] Analyze Salesforce form layout metadata in `src` and document the corresponding Dataverse form design and field behavior in `specs/001-migrate-salesforce-customizations/data-model.md`
- [ ] T016 [US1] Analyze Salesforce validation logic in `src` and document Dataverse validation equivalents using business rules, form behavior, or plugin validation in `specs/001-migrate-salesforce-customizations/data-model.md`
- [ ] T017 [US1] Update `specs/001-migrate-salesforce-customizations/research.md` with the concrete migration mapping rationale for each source entity and form

---

## Phase 4: User Story 2 - Convert Apex CRUD logic into .NET plugin service classes in the same plugin project (Priority: P2)

**Goal**: Translate Salesforce Apex CRUD classes into D365 plugin service class implementations in the same plugin project.

**Independent Test**: Confirm that each migrated Apex CRUD class has an equivalent plugin service class implementation and documented D365 data operation flow.

- [ ] T018 [US2] Translate Salesforce Apex CRUD semantics into `d365-migration/D365Migration.Plugin/PluginService.cs`
- [ ] T019 [US2] Implement Dataverse create/read/update/delete helper methods in `d365-migration/D365Migration.Plugin/CrmService.cs`
- [ ] T020 [US2] Add trace logging to CRUD operations in `d365-migration/D365Migration.Plugin/Logging.cs`
- [ ] T021 [US2] Document the CRUD mapping approach in `specs/001-migrate-salesforce-customizations/research.md`

---

## Phase 5: User Story 3 - Convert Salesforce triggers into D365 plugins or event automation (Priority: P3)

**Goal**: Represent Salesforce trigger behavior as D365 plugin event logic within the same plugin project.

**Independent Test**: Confirm that Salesforce trigger event conditions are mapped to D365 plugin registration points and that the plugin project contains event-handling scaffolding.

- [ ] T022 [US3] Analyze Salesforce trigger definitions in `src` and document the D365 event mapping in `specs/001-migrate-salesforce-customizations/data-model.md`
- [ ] T023 [US3] Implement plugin invocation scaffolding for mapped trigger events in `d365-migration/D365Migration.Plugin/Plugin.cs`
- [ ] T024 [US3] Implement the event-handling path for one or more trigger-based operations in `d365-migration/D365Migration.Plugin/PluginService.cs`
- [ ] T025 [US3] Update `specs/001-migrate-salesforce-customizations/research.md` with trigger mapping rationale and any platform constraints

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finalize deliverables, ensure governance compliance, and document the final migration approach.

- [ ] T026 [P] Review all generated docs in `specs/001-migrate-salesforce-customizations/` for consistency with the updated constitution and plan
- [ ] T027 [P] Verify `d365-migration/D365Migration.Plugin/app.config` contains no hard-coded secrets or connection strings
- [ ] T028 [P] Clean up `d365-migration/D365Migration.Plugin` project files and ensure the Visual Studio solution builds
- [ ] T029 [P] Confirm the final Dataverse artifact contract in `specs/001-migrate-salesforce-customizations/contracts/d365-migration-artifact-contract.md` matches the implementation approach
- [ ] T030 [P] Add a manual deployment scope note to the final documentation clarifying that plugin deployment is validated manually and not automated as part of this feature

---

## Dependencies & Execution Order

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: Depend on Foundational phase completion
- **Polish (Final Phase)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2)
- **User Story 2 (P2)**: Can start after Foundational (Phase 2)
- **User Story 3 (P3)**: Can start after Foundational (Phase 2)

### Parallel Opportunities

- `T006`, `T007`, `T010`, `T011`, `T012`, `T013`, `T018`, `T019`, `T020`, `T026`, `T027`, `T028`, and `T029` are all eligible for parallel execution where team capacity permits.
