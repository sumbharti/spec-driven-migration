# Research: D365 Migration Strategy for Salesforce Customizations

## Decision

Use a Dataverse-first migration strategy for Salesforce metadata in the `src` folder.
The migration will translate Salesforce custom entities, forms, and validation rules into Dataverse entity definitions, form layouts, business rules, and plugin-based validation.
A dedicated Visual Studio solution targeting .NET Framework 4.6.2 will host plugin/helper assemblies for CRUD and trigger logic.

## Rationale

- Salesforce metadata must be reinterpreted through the Dataverse/D365 platform model, not copied literally.
- D365 plugins are the most reliable way to preserve Salesforce trigger semantics and enforce event-driven business logic.
- Visual Studio and .NET Framework 4.6.2 are required by the user for debugging and plugin compatibility.
- Trace logging should be implemented via the Dataverse plugin execution context and helper logging classes.
- Secrets and connection details must not be stored in source; use environment variables or secure configuration services.

## Alternatives Considered

- Full Power Automate / workflow automation for trigger logic:
  - Pros: Low-code, easier to author for simple automations.
  - Cons: Less precise mapping for Salesforce triggers; harder to maintain with custom code and Visual Studio debugging.

- Hybrid plugin + Power Automate approach:
  - Pros: Good for some lightweight automation.
  - Cons: Adds additional operational patterns and may split logic across tools.

- External .NET service for CRUD and trigger handling:
  - Pros: Centralized business logic outside Dataverse.
  - Cons: Less aligned with D365 plugin deployment, debugging, and platform security patterns.

## Chosen Approach

- Standard D365 tables are preferred before creating custom entities.
- Salesforce custom objects and metadata will be represented by D365 custom tables only when business value demands it.
- Apex CRUD logic will be converted into .NET Framework 4.6.2 plugin helper assemblies that execute against Dataverse.
- Salesforce trigger logic will be converted into D365 plugin classes registered on the equivalent Dataverse entity events.
- Connection strings and secrets will be excluded from source code and managed through secure configuration.

## Observations

- The `src` folder requires discovery and parsing of Salesforce entity metadata, form layouts, validations, Apex classes, and triggers.
- This plan does not include data migration of existing Salesforce record values.
- The implementation must enforce publisher prefix discipline and solution boundaries for Dataverse packaging.
