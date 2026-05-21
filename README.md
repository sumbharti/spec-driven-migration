Added readme.

Connect your dataverse mcp server with Copilot CLI: https://learn.microsoft.com/en-us/power-apps/maker/data-platform/data-platform-mcp-vscode 

Install plugin for Dataverse:
https://learn.microsoft.com/en-us/power-apps/maker/data-platform/data-platform-mcp-vscode#option-2-use-the-dataverse-plugin-from-the-awesome-copilot-marketplace

constitution:

declare principles to move salesforce customizations into d365. Remember to Model the target around Dataverse/D365 behavior, not Salesforce object structure alone; fields, relationships, forms, security, and automation should be redesigned where needed rather than copied literally.

Avoid over-customizing to mimic every Salesforce object nuance; only create tables and columns that have clear business value and lifecycle ownership

Keep naming, publisher prefix, solution boundaries, and ALM conventions strict so the platform stays deployable and understandable across environments.


Specification

Implement the feature specification based on the updated constitution. I want to migrate the I want to migrate salesforce customizations my IT has shared with me in src folder in the workspace to D365 / Power platform. src would contains entity defintion, form layout, validations which i want to create in d365 as entities, forms. for apex classes and triggers i want to conver them in .net classes for performing crud in d365 and plugins for any trigger based logics.