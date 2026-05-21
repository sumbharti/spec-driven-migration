# Implementation Plan: Migrate Salesforce Customizations to D365

**Branch**: `001-migrate-salesforce-customizations` | **Date**: 2026-05-21 | **Spec**: specs/001-migrate-salesforce-customizations/spec.md

**Input**: Feature specification from `specs/001-migrate-salesforce-customizations/spec.md`

This plan organizes the migration of Salesforce metadata from the `src` folder into a Dataverse/D365 solution and associated .NET Framework 4.6.2 plugin service classes in the same plugin project.

## Summary

Migrate Salesforce custom entity definitions, form layouts, and validation logic from the workspace `src` folder into a Dataverse solution. Use Dataverse-first modeling and standard platform constructs wherever possible, while implementing Apex CRUD and trigger behavior as .NET Framework 4.6.2 plugin service classes in the same plugin project. Ensure the result is deployable as a Dataverse solution and debuggable in Visual Studio, with trace logging and secure configuration patterns that do not store secrets in source code.

## Technical Context

**Language/Version**: .NET Framework 4.6.2 for plugin service classes in the same plugin project; PowerShell for metadata discovery and authoring workflows.

**Primary Dependencies**: Dataverse SDK/CRM SDK tooling, Dynamics 365 Plugin Registration Tool, Visual Studio, Dataverse MCP VS Code extensions, PowerShell.

**Storage**: Dataverse tables and solution packages for migrated metadata; source metadata remains in `src` as migration input.

**Testing\*\*:\ Manual\ verification\ in\ a\ Dataverse\ sandbox,\ plugin\ trace\ logging,\ and\ solution\ import\ validation\.\ No\ unit,\ integration,\ or\ end-to-end\ tests\ will\ be\ written\ for\ this\ feature\.

**Target Platform**: Microsoft Dataverse / Dynamics 365 with support for .NET Framework 4.6.2 plugins.

**Project Type**: Metadata migration and integration project, with a Visual Studio solution containing plugin service classes in a single plugin project.

**Performance Goals**: Preserve business intent, minimize custom entity footprint, maintain Dataverse deployability, and support reliable Visual Studio debugging of plugin logic.

**Constraints**: Do not store connection strings or secrets in source code. Prefer standard Dataverse entities before creating custom tables. Maintain strict publisher prefix and solution boundary discipline.

**Scale/Scope**: Salesforce customization metadata in `src`; excludes data value migration and Salesforce security profile conversion.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Pass. This plan follows the constitution by modeling around Dataverse/D365 behavior instead of copying Salesforce metadata literally.
- It prioritizes platform-native D365 tables, forms, business rules, and plugin patterns.
- It enforces solution/package discipline and avoids storing secrets in source code.

## Project Structure

### Documentation (this feature)
```text
specs/001-migrate-salesforce-customizations/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── d365-migration-artifact-contract.md
└── tasks.md
```

### Source Code (repository root)
```text
d365-migration/
├── D365Migration.sln
├── D365Migration.Plugin/
│   ├── D365Migration.Plugin.csproj
│   ├── Plugin.cs
│   ├── PluginService.cs
│   └── app.config
└── D365Migration.Tests/  # optional future unit tests
```

**Structure Decision**: Create a dedicated Visual Studio solution for the D365 plugin migration implementation. This keeps Salesforce metadata extraction separate from the plugin/solution delivery model and supports Visual Studio debugging.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Dedicated Visual Studio solution | Required for .NET Framework 4.6.2 plugin development and debugging | Embedding plugin code directly in the existing workspace would mix source metadata with runtime assemblies and reduce maintainability |





