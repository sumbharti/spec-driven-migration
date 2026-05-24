# Data Model: Salesforce Entity Packages → Dataverse

**Feature**: 001-migrate-salesforce-customizations  
**Source catalog**: `src/Entity/` (multi-entity; grows as IT adds folders)  
**Solution**: **AccountMigration** (umbrella; prefix `crcc0_`)  
**Registry**: `migration/entity-registry.json` (planned)

## Entity package index

| Entity package (`src/Entity/…`) | SF object | DV table | Kind | Status | Section |
|---------------------------------|-----------|----------|------|--------|---------|
| Account | Account | account | standard | pilot | [Account](#account) |
| _{Future}_ | _TBD_ | _TBD_ | _TBD_ | planned | Add section when folder exists |

When onboarding a new package: add a registry row, a section below, and `migration/maps/{package}-field-map.json`.

---

## Account

**Source**: `src/Entity/Account`  
**Target**: Standard table `account`

## Target platform entity

| Concept | Salesforce | Dataverse |
|---------|------------|-----------|
| Business object | Account | account (standard) |
| Primary name | Name | name |
| Ownership | OwnerId | ownerid |
| Parent hierarchy | ParentId | parentaccountid |

## Custom columns (in scope)

All custom fields use publisher prefix `crcc0_` and are packaged in **AccountMigration**.

| Display name | SF API name | DV logical name | SF type | DV type | Required (field meta) | Picklist values |
|--------------|-------------|-----------------|---------|---------|----------------------|-----------------|
| Ready for AI | Ready_for_AI__c | crcc0_readyforai | Checkbox | Boolean | No | — |
| Active | Active__c | crcc0_active | Picklist | Boolean* | No | No, Yes |
| AI Summary | AI_Summary__c | crcc0_aisummary | Html | Memo | No | — |
| Upsell Opportunity | UpsellOpportunity__c | crcc0_upsellopportunity | Picklist | Choice | No | Maybe, No, Yes |
| Customer Priority | CustomerPriority__c | crcc0_customerpriority | Picklist | Choice | No | High, Low, Medium |
| SLA | SLA__c | crcc0_sla | Picklist | Choice | No | Gold, Silver, Platinum, Bronze |
| SLA Expiration Date | SLAExpirationDate__c | crcc0_slaexpirationdate | Date | DateTime | No | — |
| SLA Serial Number | SLASerialNumber__c | crcc0_slaserialnumber | Text | String | No | — |
| Number of Locations | NumberofLocations__c | crcc0_numberoflocations | Number | Whole Number | No | — |

\* **Active** is a documented transformation: Salesforce picklist → Dataverse boolean for simplified UX (see research.md).

## Standard column mappings (referenced in layout)

| SF field | DV logical name | Layout notes |
|----------|-----------------|--------------|
| Name | name | Required on layout |
| OwnerId | ownerid | |
| ParentId | parentaccountid | |
| Phone | telephone1 | |
| Fax | fax | |
| Website | websiteurl | |
| Type | customertypecode | |
| Industry | industrycode | |
| NumberOfEmployees | numberofemployees | |
| AnnualRevenue | revenue | |
| Description | description | |
| BillingAddress | address1_composite | |
| ShippingAddress | address2_composite | |
| CreatedById | createdby | System section |
| LastModifiedById | modifiedby | System section |

Standard fields without DV equivalent in layout (e.g., D&B, channel program fields) are **excluded** from v1 form; listed in exception log when encountered in layout XML.

## Form layout mapping

**Source file**: `src/Entity/Account/layouts/Account-Account Layout.layout-meta.xml`  
**Target**: Main form `Account - Salesforce Layout` (form type 2) on `account`

| SF section label | DV form section | Column layout |
|------------------|-----------------|---------------|
| Account Information | Account Information | 2 columns |
| Additional Information | Additional Information | 2 columns |
| Address Information | Address Information | 2 columns |
| Description Information | Description Information | 1 column |
| System Information | System Information | 2 columns |

Field order and `behavior` per section are captured in `migration/maps/account-field-map.json` → `formSections[]`.

### Layout exclusions (FR-004)

| Excluded from main form | Reason |
|-------------------------|--------|
| Related lists, custom links | Salesforce-only UI; out of spec |
| `webLinks/*.webLink-meta.xml` | Out of spec |
| Standard fields in object folder but not on layout | No layout placement (e.g. D&B, channel program fields) |

## Validation mapping

| Source | Rule | DV enforcement | Status |
|--------|------|----------------|--------|
| Layout: Name `Required` | Account name mandatory on edit | Platform `name` + form control `required="true"` via `migration/lib/apply_form.py` | Implemented in code |
| Field metadata: custom `required=false` | No column-level required | `RequiredLevel: None` in `migration/lib/apply_metadata.py` | Implemented |
| Field metadata: `required=true` (if added) | Column required on save | `RequiredLevel: ApplicationRequired` | Implemented in code |
| Layout: `Readonly` | Display-only on form | `disabled="true"` on control | Implemented |
| Layout: `Required` (non-Name fields) | Form-level required | `required="true"` on control | Implemented in code |
| SF ValidationRule files | — | N/A | Not in source |

## Relationships

- **Parent account**: `parentaccountid` lookup to `account` (standard 1:N).
- No new custom relationships required for Account v1.

## Migration exception log (v1)

| Source artifact | Reason excluded |
|-----------------|-----------------|
| `webLinks/*.webLink-meta.xml` | Out of spec (UI integrations) |
| `listViews/*.listView-meta.xml` | Out of spec (views) |
| SF fields in object folder not in layout/custom set | No business mapping yet — e.g. `DandbCompanyId`, `DunsNumber`, `NaicsCode`, `ChannelProgramName`, `OperatingHoursId`, `Tier`, `Rating`, `CleanStatus`, `Jigsaw`, `Site`, `Tradestyle`, `YearStarted`, `Sic`, `SicDesc`, `AccountSource`, `IsPartner`, `IsCustomerPortal`, `AccountNumber` |
| `src/Apex/**` | Out of spec (code migration) |

## Template: new entity package section

Copy when `src/Entity/{EntityPackage}/` is added:

1. **Target platform entity** — SF object → DV table (standard vs custom)
2. **Custom columns** — table of `*__c` fields
3. **Standard column mappings** — layout-referenced fields
4. **Form layout mapping** — sections from main layout XML
5. **Validation mapping** — field + layout rules
6. **Relationships** — lookups created or reused
7. **Migration exception log** — web links, list views, unmapped SF fields
