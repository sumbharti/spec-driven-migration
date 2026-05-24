"""Account entity: explicit SF → Dataverse field and form control maps."""

STANDARD_FIELD_MAP = {
    "Name": "name",
    "OwnerId": "ownerid",
    "ParentId": "parentaccountid",
    "Phone": "telephone1",
    "Fax": "fax",
    "Website": "websiteurl",
    "Type": "customertypecode",
    "Industry": "industrycode",
    "NumberOfEmployees": "numberofemployees",
    "AnnualRevenue": "revenue",
    "Description": "description",
    "BillingAddress": "address1_composite",
    "ShippingAddress": "address2_composite",
    "CreatedById": "createdby",
    "LastModifiedById": "modifiedby",
}

# api_name -> (logical_name, dataverse_type, default_display)
CUSTOM_FIELD_MAP = {
    "Ready_for_AI__c": ("crcc0_readyforai", "bool", "Ready for AI"),
    "Active__c": ("crcc0_active", "bool", "Active"),
    "AI_Summary__c": ("crcc0_aisummary", "memo", "AI Summary"),
    "UpsellOpportunity__c": ("crcc0_upsellopportunity", "picklist", "Upsell Opportunity"),
    "CustomerPriority__c": ("crcc0_customerpriority", "picklist", "Customer Priority"),
    "SLA__c": ("crcc0_sla", "picklist", "SLA"),
    "SLAExpirationDate__c": ("crcc0_slaexpirationdate", "date", "SLA Expiration Date"),
    "SLASerialNumber__c": ("crcc0_slaserialnumber", "string", "SLA Serial Number"),
    "NumberofLocations__c": ("crcc0_numberoflocations", "int", "Number of Locations"),
}

FIELD_CONTROL = {
    "name": ("text", "Account Name"),
    "ownerid": ("lookup", "Owner"),
    "parentaccountid": ("lookup", "Parent Account"),
    "telephone1": ("text", "Main Phone"),
    "fax": ("text", "Fax"),
    "websiteurl": ("text", "Website"),
    "customertypecode": ("picklist", "Relationship Type"),
    "industrycode": ("picklist", "Industry"),
    "numberofemployees": ("int", "Number of Employees"),
    "revenue": ("money", "Annual Revenue"),
    "description": ("memo", "Description"),
    "address1_composite": ("address", "Address 1"),
    "address2_composite": ("address", "Address 2"),
    "createdby": ("lookup", "Created By"),
    "modifiedby": ("lookup", "Modified By"),
    "crcc0_readyforai": ("toggle", "Ready for AI"),
    "crcc0_active": ("toggle", "Active"),
    "crcc0_aisummary": ("memo", "AI Summary"),
    "crcc0_upsellopportunity": ("picklist", "Upsell Opportunity"),
    "crcc0_customerpriority": ("picklist", "Customer Priority"),
    "crcc0_sla": ("picklist", "SLA"),
    "crcc0_slaexpirationdate": ("datetime", "SLA Expiration Date"),
    "crcc0_slaserialnumber": ("text", "SLA Serial Number"),
    "crcc0_numberoflocations": ("int", "Number of Locations"),
}
