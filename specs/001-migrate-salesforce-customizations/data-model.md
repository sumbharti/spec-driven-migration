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

## Account Entity Mapping Example

The source Salesforce `Account` metadata in `src/Entity/Account` is mapped to the Dataverse standard `account` table with a small set of custom attributes for business-specific fields that are not already represented by the platform.

Key source artifacts:

- `src/Entity/Account/objects/Account/Account.object-meta.xml`
- `src/Entity/Account/objects/Account/fields/*.field-meta.xml`
- `src/Entity/Account/layouts/Account-Account Layout.layout-meta.xml`
- `src/Apex/classes/AccountSFMigration.cls`
- `src/Apex/triggers/AccountDuplicatePhoneTrigger.trigger`

Target design principles:

- Use standard `account` table fields for Name, Phone, Fax, Website, Type, Industry, NumberOfEmployees, AnnualRevenue, BillingAddress, ShippingAddress, and ownership.
- Add custom fields only when business logic requires a Salesforce-specific field, including:
  - `new_ready_for_ai` for `Ready_for_AI__c`
  - `new_upsell_opportunity` for `UpsellOpportunity__c`
  - `new_sla` for `SLA__c`, `new_sla_expiration_date` for `SLAExpirationDate__c`, and `new_sla_serial_number` for `SLASerialNumber__c`
  - `new_number_of_locations` for `NumberofLocations__c`
  - `new_customer_priority` for `CustomerPriority__c`
- Preserve lookup relationships such as parent account via the existing `parentaccountid` lookup.

Form design mapping:

- Map the Salesforce `Account Information` section to a D365 Account main form section with required Name and editable Owner, Parent Account, and AI readiness fields.
- Map `Additional Information` to a D365 section containing Type, Industry, NumberOfEmployees, and AnnualRevenue.
- Map `Description Information` to a D365 description section using `description` and a new multiline text field for `AI_Summary__c`.
- Map `Address Information` to D365 billing/shipping address sections using the built-in address controls.
- Keep system fields readonly on the form, and add custom links via D365 form navigation or command bar actions rather than Salesforce custom links.

Validation mapping:

- Enforce required Name on the D365 account main form.
- Enforce duplicate Phone detection as a pre-create plugin on the Account entity.
- Preserve business rule equivalent validations using Dataverse business rules when possible, and reserve plugin validation for duplicate detection and other event-specific checks.

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
