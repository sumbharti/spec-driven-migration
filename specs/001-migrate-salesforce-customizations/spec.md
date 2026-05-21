# Feature Specification: Migrate Salesforce Customizations to D365

**Feature Branch**: `001-migrate-salesforce-customizations`

**Created**: 2026-05-21

**Status**: Draft

**Input**: User description: "Implement the feature specification based on the updated constitution. I want to migrate the salesforce customizations my IT has shared with me in src folder in the workspace to D365 / Power platform. src would contains entity defintion, form layout, validations which i want to create in d365 as entities, forms. for apex classes and triggers i want to conver them in .net classes for performing crud in d365 and plugins for any trigger based logics."

## Clarifications

### Session 2026-05-21

- Q: Should converted Apex CRUD logic be implemented as plugin helper assemblies or standalone service libraries? → A: A - Implement all converted Apex CRUD logic as .NET plugin service classes in the same plugin project.
- Q: Should the feature include plugin deployment automation or only manual deployment validation? → A: A - Manual validation only; plugin deployment is not required.

## User Scenarios & Testing

### User Story 1 - Migrate Salesforce metadata into D365 entities and forms (Priority: P1)

Business users need the Salesforce customizations shared in the workspace `src` folder to be re-created in Dynamics 365 so that the migrated solution reflects the same business entities, forms, and validation intent.

**Why this priority**: This is the core deliverable. Without the entity and form migration, the D365 target solution cannot represent the source business workflows.

**Independent Test**: Verify that each source entity definition, form layout, and validation rule in `src` is mapped to a D365 entity, form, or equivalent platform rule.

**Acceptance Scenarios**:

1. **Given** the `src` folder contains Salesforce entity definitions and form metadata, **when** the migration design is reviewed, **then** there is a mapped D365 entity and form for each source entity with a documented business rationale.
2. **Given** a Salesforce validation rule or layout directive in `src`, **when** the D365 artifacts are inspected, **then** the solution includes equivalent field definitions, form properties, business rules, or plugin validations that preserve the business intent.

---

### User Story 2 - Convert Apex CRUD logic into .NET plugin service classes in the same plugin project (Priority: P2)

Developers need Salesforce Apex classes that support CRUD flows to be translated into .NET plugin service classes in the same plugin project for D365 data operations.

**Why this priority**: Data access and business logic must be preserved after migration; the .NET conversion into plugin service classes in the same plugin project enables integration with Dynamics data operations and event handling.

**Independent Test**: Confirm that each Apex class with create/read/update/delete semantics has a corresponding .NET plugin service class in the same plugin project and that CRUD operations are documented for D365 execution.

**Acceptance Scenarios**:

1. **Given** an Apex class in `src` that performs Salesforce CRUD, **when** migration artifacts are reviewed, **then** there is a plugin service class in the same plugin project with the same business operation intent and D365 data handling approach.

---

### User Story 3 - Convert Salesforce triggers into D365 plugins or event automation (Priority: P3)

Operations teams need Salesforce trigger logic to run in Dynamics 365 via plugins or supported event-driven automation so that business rules fire correctly in the target platform.

**Why this priority**: Trigger semantics are essential for preserving business automation and data integrity during and after migration.

**Independent Test**: Verify that each Salesforce trigger in `src` is represented by a D365 plugin or automation design and that event conditions are mapped to create/update/delete actions.

**Acceptance Scenarios**:

1. **Given** a Salesforce trigger definition in `src`, **when** the migration design is reviewed, **then** there is a D365 plugin or automation rule that executes equivalent logic for the same entity event.

---

### Edge Cases

- What happens when a source entity or field uses a Salesforce construct that has no direct Dataverse equivalent?
- How does the migration handle validation logic that depends on Salesforce-specific triggers or workflow rules?
- How are naming collisions handled when similar entity names already exist in the D365 environment?

## Requirements

### Functional Requirements

- **FR-001**: The migration process MUST analyze the `src` folder and identify Salesforce custom entities, form layouts, validation rules, Apex classes, and triggers.
- **FR-002**: The migration process MUST produce D365 entity definitions and form designs that represent the business intent of the Salesforce metadata.
- **FR-003**: The migration process MUST map Salesforce validation and layout logic to D365-friendly equivalents such as field definitions, business rules, form scripting, or plugin validation.
- **FR-004**: The migration process MUST convert Salesforce Apex CRUD classes into .NET plugin service classes in the same plugin project designed for D365 data operations.
- **FR-005**: The migration process MUST convert Salesforce trigger logic into D365 plugins or other platform-supported event automation constructs.
- **FR-006**: The migration process MUST apply consistent naming, publisher prefix, solution boundary, and lifecycle ownership conventions to all D365 artifacts.
- **FR-007**: The migration process MUST document the mapping rationale for each migrated entity, form, validation, Apex class, and trigger.
- **FR-008**: The migration process MUST ensure all created D365 artifacts are deployable within a standard Dataverse solution.
- **FR-009**: The migration process MUST treat standard D365 tables and features as preferred targets and only introduce custom entities when justified by business value.
- **FR-010**: The migration process MUST exclude Salesforce metadata elements that cannot be migrated without a clear target-platform equivalent and document those exceptions.
- **FR-011**: The migration process MUST produce D365 artifacts and plugin components that are ready for manual deployment validation; automated deployment is not required by this feature.

### Key Entities

- **Salesforce Customization Package**: The set of metadata in the `src` folder, including entity definitions, forms, validation rules, Apex classes, and triggers.
- **D365 Entity Definition**: The Dataverse table and field model that represents a migrated Salesforce object or business concept.
- **D365 Form Layout**: The Dynamics 365 form design that captures the source form layout and field interaction requirements.
- **.NET CRUD Class**: The converted server-side class designed to perform D365 create/read/update/delete operations with source business logic preserved.
- **D365 Plugin Implementation**: The Dynamics 365 plugin or event automation design that enforces trigger-based business logic during entity events.

## Success Criteria

### Measurable Outcomes

- **SC-001**: At least 90% of source objects with clear business value are represented as D365 entities or documented exceptions.
- **SC-002**: At least 95% of source validation rules and form behaviors are captured in D365 forms, business rules, or plugin logic.
- **SC-003**: All Apex classes and trigger-based automations with direct CRUD or event behavior are converted to .NET or plugin assets with documented mapping.
- **SC-004**: The migrated artifacts deploy successfully into a Dataverse solution without unresolved metadata or packaging errors.
- **SC-005**: Stakeholders can review the migration mapping documentation and confirm that each shared `src` artifact has a corresponding D365 target or an approved exception.

## Assumptions

- The `src` folder contains Salesforce customization metadata in a form that can be parsed and mapped to D365 concepts.
- The target D365 solution will support custom entities, forms, business rules, plugins, and Dataverse solution packaging.
- Data migration of record values is out of scope; this feature focuses on metadata and customization migration only.
- Salesforce security constructs (profiles, permission sets) are not migrated literally; the existing D365 security model will be used instead.
- Standard D365 tables and platform capabilities are preferred; custom entities are only created when source business value cannot be mapped to existing D365 tables.
- Detailed implementation technology choices beyond .NET and D365 plugin patterns are not defined at this specification stage.




