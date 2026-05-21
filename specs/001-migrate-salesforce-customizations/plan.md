# Implementation Plan: Migrate Salesforce Customizations to D365

**Branch**: `001-migrate-salesforce-customizations` | **Date**: 2026-05-21 | **Spec**: specs/001-migrate-salesforce-customizations/spec.md

**Input**: Feature specification from `specs/001-migrate-salesforce-customizations/spec.md`

## Summary

Migrate Salesforce custom entity definitions, form layouts, and validation logic from the `src/Entity` schema into a Dataverse/D365 solution design. Prioritize source entity metadata and form creation from `src/Entity` first, then convert Apex CRUD and trigger logic into .NET Framework 4.6.2 plugin service classes in the same plugin project.

## Technical Context

**Language/Version**: .NET Framework 4.6.2 for plugin service classes; PowerShell for repository and metadata workflow scripts.

**Primary Dependencies**: Microsoft.CrmSdk.CoreAssemblies, Dynamics 365 / Dataverse plugin tooling, Visual Studio, Dataverse solution authoring tools.

**Storage**: Dataverse solution artifacts, model-driven form definitions, custom entity metadata, and source metadata in `src/Entity`.

**Testing**: Manual validation in a Dataverse sandbox, plugin trace logging, Visual Studio build verification, and documented artifact reviews.

**Target Platform**: Microsoft Dataverse / Dynamics 365.

**Project Type**: Metadata migration and plugin integration project with a dedicated Visual Studio solution.

**Performance Goals**: Preserve source business intent with minimal custom entity footprint and maintain deployability through standard Dataverse solution packaging.

**Constraints**: No secrets or connection strings stored in source; prefer standard Dataverse tables before creating custom entities; complete entity/form migration before Apex/plugin conversion.

**Scale/Scope**: Salesforce metadata under `src/Entity` and related Apex/trigger code in `src`; excludes data value migration and Salesforce security artifacts.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Pass. The plan focuses on Dataverse-first migration, prioritizes platform-native entity/form design, and keeps Apex/plugin conversion as a secondary implementation layer.

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
└── D365Migration.Plugin/
    ├── D365Migration.Plugin.csproj
    ├── Plugin.cs
    ├── PluginService.cs
    ├── CrmService.cs
    ├── Logging.cs
    └── app.config
```

**Structure Decision**: Use a dedicated Visual Studio solution for D365 plugin migration, keeping Dataverse entity/form design documentation in `specs/001-migrate-salesforce-customizations/` and code artifacts in `d365-migration/`.

## Complexity Tracking

No constitution violations identified that require special justification. The design uses standard Dataverse migration and plugin patterns.
