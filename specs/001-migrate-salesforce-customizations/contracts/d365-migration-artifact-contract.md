# D365 Migration Artifact Contract

## Purpose

Define the expected deliverables and artifact boundaries for migrating Salesforce customizations from `src` into a Dataverse/D365 solution and supporting .NET plugin components.

## Artifact Types

### Dataverse Artifacts

- **Entity definitions**: Dataverse tables representing migrated Salesforce custom objects.
- **Fields**: Dataverse columns matching migrated Salesforce field semantics.
- **Relationships**: Dataverse lookup, 1:N, N:1, and N:N relationships mapping Salesforce associations.
- **Forms**: Dataverse model-driven forms that capture migrated layout and data entry behavior.
- **Business rules**: Dataverse business rules for validation and conditional form behavior.
- **Plugins**: Dataverse plugin registrations for event-driven automation and validation.

### .NET Artifacts

- **Visual Studio solution**: `d365-migration/D365Migration.sln`
- **Plugin project**: `d365-migration/D365Migration.Plugin` targeting .NET Framework 4.6.2.
- **Plugin project: `d365-migration/D365Migration.Plugin` for Dataverse CRUD patterns, logging, and plugin service classes.
- **Optional tests**: `d365-migration/D365Migration.Tests` for shared logic validation.

## Contract Rules

- All plugin assemblies must be built against .NET Framework 4.6.2.
- Plugin and shared code must not contain connection strings or secrets.
- Configuration values should be loaded from environment variables, secure files outside source control, or secure vaults.
- All Dataverse artifacts must be packaged in a deployable solution with a consistent publisher prefix.
- Custom entities are allowed only when standard Dataverse tables cannot support the business requirement.

## Delivery Expectations

- The deliverable includes a Dataverse solution that imports cleanly and a Visual Studio solution that opens and builds with no missing project references.
- Plugin assemblies must be deployable via the Dataverse plugin registration tool.
- Trace logging must be available for plugin execution and error investigation.

## Developer Contract

- Developers must review this artifact contract before implementing migration logic.
- Changes to the migration artifact scope require updating this contract and the implementation plan.


