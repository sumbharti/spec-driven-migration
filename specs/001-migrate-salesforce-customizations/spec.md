# Feature Specification: Migrate Salesforce Entity Customizations to Dataverse

**Feature Branch**: `001-migrate-salesforce-customizations`

**Created**: 2026-05-23

**Status**: Draft

**Input**: User description: "add specification to migrate salesforce customizations including fields, form layout and validations in src Entity folder to dataverse"

## User Scenarios & Testing

### User Story 1 - Recreate custom fields on the target table (Priority: P1)

Solution owners need every Salesforce custom field defined under `src/Entity` to exist on the correct Dataverse table with equivalent labels, data types, and option values so users can capture the same business data after migration.

**Why this priority**: Columns are the foundation of forms and validation. Without correct field migration, layouts and rules cannot function.

**Independent Test**: For each custom field metadata file under `src/Entity`, verify a corresponding Dataverse column exists with documented mapping for type, length, precision, required flag, and picklist options.

**Acceptance Scenarios**:

1. **Given** a custom field definition in `src/Entity` (for example, a picklist or text custom field on Account), **when** the migrated solution is reviewed, **then** a Dataverse column exists on the target table with the same business label and compatible data type.
2. **Given** a picklist field with defined values in source metadata, **when** the column is inspected in the target environment, **then** all source option labels are available to users in the same intended order or with documented ordering changes.
3. **Given** a standard Salesforce field referenced in source metadata, **when** migration mapping is reviewed, **then** the field maps to the appropriate standard Dataverse column or is documented as excluded with business justification.

---

### User Story 2 - Reproduce form layout and field behavior (Priority: P2)

Business users need main record forms in Dataverse to mirror the sections, field groupings, and read-only or required behaviors defined in Salesforce layout metadata under `src/Entity`.

**Why this priority**: Forms drive day-to-day data entry. Layout parity reduces retraining and adoption risk after platform change.

**Independent Test**: Compare each source layout file under `src/Entity` to its Dataverse main form and confirm sections, included fields, and field-level behaviors match the documented mapping.

**Acceptance Scenarios**:

1. **Given** a Salesforce page layout in `src/Entity` (for example, Account layout with named sections), **when** the corresponding Dataverse main form is opened, **then** users see the same section structure and fields grouped in equivalent positions.
2. **Given** a layout item marked as required or read-only in source metadata, **when** a user edits the record on the migrated form, **then** the same field enforces equivalent required or read-only behavior on save or display.
3. **Given** a source layout field that cannot be placed on a form (unsupported or excluded mapping), **when** migration documentation is reviewed, **then** the exception is listed with an approved alternative or workaround.

---

### User Story 3 - Preserve validation intent from metadata (Priority: P3)

Administrators need field-level and form-level validation rules from Salesforce metadata to be enforced in Dataverse so invalid records cannot be saved under the same business rules as the source system.

**Why this priority**: Validation protects data quality. Losing rules during migration creates compliance and operational risk.

**Independent Test**: For each documented validation rule derived from source metadata (field `required` flags, layout `Required` behaviors, and explicit validation rule definitions if present), attempt to save invalid data on the target form and confirm rejection with a clear message.

**Acceptance Scenarios**:

1. **Given** a field marked as required in Salesforce field metadata, **when** a user saves a record without that value, **then** Dataverse blocks save and presents an understandable validation message.
2. **Given** a field marked as required only on the Salesforce layout, **when** migration artifacts are reviewed, **then** equivalent enforcement exists via form configuration or platform validation with the same business outcome.
3. **Given** source metadata with no explicit cross-field validation rules, **when** migration is complete, **then** all enforceable required and format constraints from fields and layouts are implemented and documented gaps list any rules deferred to a later phase.

---

### Edge Cases

- What happens when a Salesforce field type has no direct Dataverse equivalent (for example, certain compound or platform-specific types)?
- How are duplicate or conflicting labels and API names handled when the target environment already contains similar columns or forms?
- What happens when a layout references a field that was excluded from column migration?
- How are Salesforce-only UI elements in layout metadata (web links, related lists not in scope) treated without blocking form migration?
- How does migration proceed when `src/Entity` gains additional entity folders beyond the initial Account package?

## Requirements

### Functional Requirements

- **FR-001**: The migration MUST inventory all metadata under `src/Entity`, including object definitions, field definitions, and layout definitions, organized per source entity package.
- **FR-002**: The migration MUST create or extend Dataverse table columns for every in-scope custom field in `src/Entity`, preserving business labels, descriptions where present, data types, lengths, and picklist values.
- **FR-003**: The migration MUST map standard Salesforce fields referenced in `src/Entity` to standard Dataverse columns where equivalents exist, and MUST document exclusions where they do not.
- **FR-004**: The migration MUST produce a main form per in-scope source layout that preserves section titles, field inclusion, and column placement to the extent supported by the target platform.
- **FR-005**: The migration MUST translate layout field behaviors (such as required and read-only) into equivalent Dataverse form and column settings.
- **FR-006**: The migration MUST implement validation derived from field-level `required` settings and layout-level required behaviors found in `src/Entity`.
- **FR-007**: The migration MUST produce a field-and-layout mapping document for each source entity package, listing source name, target name, mapping type (direct, transformed, excluded), and rationale for exclusions.
- **FR-008**: The migration MUST package all created or updated metadata into a deployable Dataverse solution boundary with consistent publisher prefix and naming conventions.
- **FR-009**: The migration MUST exclude Salesforce artifacts outside this feature scope (Apex classes, triggers, web links, and record data) and MUST state those exclusions in migration documentation.
- **FR-010**: The migration MUST flag any source validation or layout rule that cannot be reproduced in Dataverse and MUST require explicit stakeholder approval before sign-off.

### Key Entities

- **Source Entity Package**: A folder under `src/Entity` containing Salesforce object, field, and layout metadata for one business object (for example, Account).
- **Field Mapping Record**: The business mapping between a Salesforce field and a Dataverse column, including type transformation and option value alignment.
- **Form Layout Mapping**: The correspondence between a Salesforce page layout and a Dataverse main form, including sections and field behaviors.
- **Validation Mapping**: The set of enforceable rules (required fields, layout-required fields, and explicit validation definitions when present) and their Dataverse enforcement mechanism.
- **Migration Exception Log**: Approved list of source elements that are not migrated, with reason and business impact.

## Success Criteria

### Measurable Outcomes

- **SC-001**: 100% of custom fields under `src/Entity` are either represented as Dataverse columns or listed as approved exceptions with business sign-off.
- **SC-002**: 95% or more of layout sections and in-scope fields from source main layouts appear on the corresponding Dataverse main forms according to the published mapping document.
- **SC-003**: 100% of required constraints discoverable from field metadata and layout required behaviors in `src/Entity` are enforced on save in Dataverse or documented as approved deferrals.
- **SC-004**: Stakeholders can complete a mapping review session for each entity package in under 60 minutes using only the migration documentation, with no undocumented source artifacts.
- **SC-005**: A pilot user group can create and edit records on migrated forms without reporting missing custom fields or blocking validation errors that contradict the source system intent.

## Assumptions

- `src/Entity` is the sole source for in-scope metadata; other workspace folders (such as Apex) are out of scope for this feature.
- The initial source content includes at least the Account entity package; the same rules apply when additional entity packages are added under `src/Entity`.
- Record data migration (bulk load of existing Salesforce rows) is out of scope; this feature covers customization metadata only.
- List views, web links, workflows, and security profiles from Salesforce are out of scope unless added by a future feature.
- Standard Dataverse tables are preferred targets for standard Salesforce objects; custom tables are used only when a standard table cannot represent the business object.
- The target environment provides a publisher prefix and solution used consistently across all migrated artifacts.
- Explicit Salesforce validation rule files are not present in the current `src/Entity` snapshot; validation scope is limited to field and layout metadata unless such files are added later.
