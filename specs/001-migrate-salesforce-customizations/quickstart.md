# Quickstart: Migrate Salesforce Customizations to D365

## 1. Review the migration plan

- Open `specs/001-migrate-salesforce-customizations/spec.md` and `specs/001-migrate-salesforce-customizations/plan.md`.
- Confirm the migration scope: metadata-only migration from `src`, not data value migration.

## 2. Inspect Salesforce metadata in `src`

- Identify Salesforce custom entities, field definitions, form layouts, validation rules, Apex classes, and triggers.
- Document which Salesforce objects map to standard Dataverse tables and which require custom Dataverse tables.

## 3. Create the Dataverse solution

- Create a new solution in Dataverse for the migrated artifacts.
- Add custom entities, fields, relationships, forms, business rules, and plugin assembly references as needed.
- Follow strict publisher prefix and solution layering discipline.

## 4. Create the Visual Studio migration solution

- Create `d365-migration/D365Migration.sln` at the repository root.
- Add a .NET Framework 4.6.2 plugin project: `D365Migration.Plugin`.
- Create a single plugin project: `D365Migration.Plugin`.
- (Optional) Add `D365Migration.Tests` for unit tests of shared helper logic.

## 5. Implement .NET plugin architecture

- Implement trigger and CRUD behavior as Dataverse plugin classes in `D365Migration.Plugin`.
- Factor reusable Dataverse data access into `D365Migration.Plugin`.
- Add trace logging through the Dataverse plugin tracing service and shared logging helpers.
- Do not store connection strings or secrets in source code; use environment configuration or secure key storage.

## 6. Debug and validate in Visual Studio

- Build the solution in Visual Studio.
- Use the plugin registration tool to deploy the plugin assembly to your Dataverse environment.
- Attach the debugger to the Dataverse process or use Visual Studio debugging support for plugin execution.

## 7. Validate deployment and artifacts

- Import the Dataverse solution and verify entity, form, and plugin registration deployment.
- Test migrated business rules and event logic against the target entities.
- Confirm that trace logging is available and that no secrets are committed to source code.

## 8. Next step: generate tasks

- After the plan is validated, run `/speckit.tasks` to turn this design into executable implementation tasks.


