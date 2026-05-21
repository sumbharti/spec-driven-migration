<!--
Sync Impact Report
Version change: uninitialized template -> 1.0.0
Modified principles:
- [PRINCIPLE_1_NAME] -> Model for Dataverse / D365 First
- [PRINCIPLE_2_NAME] -> Business Value and Lifecycle Ownership
- [PRINCIPLE_3_NAME] -> Deployable ALM and Solution Discipline
- [PRINCIPLE_4_NAME] -> Security and Automation Aligned to Platform Patterns
- [PRINCIPLE_5_NAME] -> Minimal Replication, Platform-Native Redesign
Added sections:
- Migration Constraints
- Review & Delivery Process
Templates requiring review:
- .specify/templates/plan-template.md ✅ reviewed
- .specify/templates/spec-template.md ✅ reviewed
- .specify/templates/tasks-template.md ✅ reviewed
Follow-up TODOs: none
-->

# D365 Migration Constitution

## Core Principles

### Model for Dataverse / D365 First
Design the target solution around Dataverse and Dynamics 365 semantics, not Salesforce object structure.
Tables, fields, relationships, forms, security, and automation must be modeled for the target platform’s capabilities,
performance, and lifecycle rather than copied literally from Salesforce metadata.

### Business Value and Lifecycle Ownership
Create only entities, fields, and automation that have clear business value, ownership, and maintainable lifecycle.
Avoid over-customizing or preserving Salesforce shape when the feature can be implemented with standard D365 tables,
fields, or configuration.

### Deployable ALM and Solution Discipline
Keep naming, publisher prefix, solution boundaries, and ALM conventions strict so the platform remains deployable,
upgradeable, and understandable across environments.
Solution design must preserve managed/unmanaged portability, clear component ownership, and predictable solution
import/export behavior.

### Security and Automation Aligned to Platform Patterns
Implement security and automation using D365 platform patterns, not Salesforce idioms.
Use Dataverse security roles, teams, field-level security, business rules, workflows, Power Automate, and plug-ins where
appropriate, and validate that each control behaves as intended in the Dynamics 365 security model.

### Minimal Replication, Platform-Native Redesign
Translate business outcomes, not Salesforce object nuance.
When migrating, preserve intent and behavior while redesigning for D365-native constructs; avoid replicating Salesforce
objects, custom fields, or processes that do not map to platform-native lifecycle and supportability.

## Migration Constraints

- Do not create tables, columns, or automation solely to mirror Salesforce metadata.
- Prefer standard D365 tables before introducing custom entities.
- Every custom table and field must have a documented owner, retention expectation, and operational purpose.
- Maintain a consistent publisher prefix and solution layering strategy across all customizations.
- Changes must fit within the Dataverse ALM model and avoid cross-solution scavenging of unmanaged artifacts.

## Review & Delivery Process

- Every migration design requires review for data model fit, solution packaging, security, and automation pattern.
- Document the rationale for table/field decisions, why a custom entity is required, and why a standard table cannot be used.
- Validate PRs against this constitution: D365-first modeling, business-value minimization, ALM discipline, and platform-aligned
  security/automation.
- Exceptions to these principles must be explicitly documented, reviewed, and approved before implementation.

## Governance

This constitution is the baseline for Salesforce-to-Dynamics 365 migration decisions in this repository.
Any design or implementation that conflicts with these principles must be justified in writing and approved by the team.

- Amendments require a documented rationale, team review, and an update to this constitution file.
- Versioning policy:
  - MAJOR: restructures principles or changes core migration governance.
  - MINOR: adds new principles, constraints, or delivery requirements.
  - PATCH: clarifications, wording improvements, and non-semantic refinements.
- Compliance expectation: every PR must reference the constitution and show how proposed changes preserve D365 behavior,
  ALM discipline, and lifecycle ownership.

**Version**: 1.0.0 | **Ratified**: 2026-05-21 | **Last Amended**: 2026-05-21
