# Data Model: Salesforce → D365 Migration Mapping

## Conceptual Entities

The migration is driven by the Salesforce metadata inside `src`.
Each Salesforce custom object or entity definition should be evaluated against Dataverse platform capabilities and mapped to one of these target constructs:

- **Standard Dataverse table**: Use when Salesforce business intent matches an existing Dataverse table.
- **Custom Dataverse table**: Use only when business value cannot be represented by standard tables.
- **Lookup relationships**: Map Salesforce lookup/master-detail to Dataverse lookup fields and 1:N / N:1 relationships.
- **Choices / picklists**: Map Salesforce picklists to Dataverse option sets or global choice sets.
- **Form layout and validations**: Map Salesforce page layouts and validation rules to Dataverse forms, business rules, and plugin validations.

## Entity Pattern

Each migrated Salesforce entity should be represented as one of:

- `new_<prefix>_<logicalname>` for a custom Dataverse table
- `new_<prefix>_<entity>_<field>` for custom fields where needed

Every custom artifact must have:

- a clear business rationale
- an owning team or owner
- a retention/maintenance expectation
- an ALM-friendly publisher prefix and solution layer

## Field Mapping Guidelines

- Salesforce `Text` → Dataverse `Single Line of Text`
- Salesforce `LongTextArea` / `RichTextArea` → Dataverse `Multiple Lines of Text`
- Salesforce `Checkbox` → Dataverse `Two Options`
- Salesforce `Picklist` → Dataverse `Choice` / global option set
- Salesforce `Date` / `DateTime` → Dataverse `Date` / `Date and Time`
- Salesforce `Lookup` / `Master-Detail` → Dataverse `Lookup`
- Salesforce `Number` / `Currency` / `Percent` → Dataverse numeric field types

## Relationship Modeling

- Preserve one-to-many relationships using Dataverse 1:N / N:1 relationship metadata.
- Preserve many-to-many relationships using Dataverse N:N relationships or intersect tables.
- Map Salesforce parent-child ownership semantics to Dataverse ownership models.

## Validation and Form Behavior

- Keep form-level field visibility and requiredness where business intent requires it.
- Implement inline validation with Dataverse business rules when possible.
- Use plugin validation only when platform rules do not support the required logic or when validation depends on complex event sequencing.
- Keep form layouts aligned to the source entity’s key data entry patterns while using Dataverse form sections and tabs.

## Entity Discovery

The first implementation step is to scan `src` for Salesforce entity definitions, layout metadata, Apex classes, and triggers.
The discovered objects will be mapped into the above constructs and documented in the migration design.

## Notes

- This is a migration model template; exact entity names and fields will be determined during discovery of `src` metadata.
- The plan assumes that Salesforce metadata is complete enough to infer forms and validation intent.
