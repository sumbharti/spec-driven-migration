using System;
using System.Collections.Generic;
using Microsoft.Xrm.Sdk;
using Microsoft.Xrm.Sdk.Query;

namespace D365Migration.Plugin
{
    public class PluginService
    {
        private readonly IOrganizationService _organizationService;
        private readonly ITracingService _tracing;
        private readonly IPluginExecutionContext _context;
        private readonly CrmService _crmService;

        public PluginService(IServiceProvider serviceProvider)
        {
            if (serviceProvider == null) throw new ArgumentNullException(nameof(serviceProvider));

            _tracing = (ITracingService)serviceProvider.GetService(typeof(ITracingService));
            var serviceFactory = (IOrganizationServiceFactory)serviceProvider.GetService(typeof(IOrganizationServiceFactory));
            _context = (IPluginExecutionContext)serviceProvider.GetService(typeof(IPluginExecutionContext));
            _organizationService = serviceFactory?.CreateOrganizationService(_context?.UserId);
            _crmService = new CrmService(_organizationService, _tracing);
        }

        public void Execute()
        {
            Logging.Trace(_tracing, "D365Migration.Plugin execution started.");

            if (_context?.InputParameters.Contains("Target") == true && _context.InputParameters["Target"] is Entity targetEntity)
            {
                Logging.Trace(_tracing, $"Processing entity: {targetEntity.LogicalName}, Message: {_context.MessageName}");

                if (string.Equals(_context.MessageName, "Create", StringComparison.OrdinalIgnoreCase)
                    && _context.Stage == 20)
                {
                    ValidateDuplicatePhoneOnCreate(targetEntity);
                }
                else
                {
                    Logging.Trace(_tracing, "No custom event handling defined for this plugin registration.");
                }
            }
            else
            {
                Logging.Trace(_tracing, "No target entity provided in plugin context.");
            }
        }

        public Guid CreateEntity(Entity entity)
        {
            return _crmService.Create(entity);
        }

        public Entity Retrieve(string logicalName, Guid id, ColumnSet columns)
        {
            return _crmService.Retrieve(logicalName, id, columns);
        }

        public void Update(Entity entity)
        {
            _crmService.Update(entity);
        }

        public void Delete(string logicalName, Guid id)
        {
            _crmService.Delete(logicalName, id);
        }

        public Guid CreateAccount(string name, string billingStreet, string billingCity,
            string billingState, string billingPostalCode, string billingCountry, string phone, string accountType)
        {
            if (string.IsNullOrWhiteSpace(name))
            {
                throw new InvalidPluginExecutionException("Account Name is required.");
            }

            var account = new Entity("account");
            account["name"] = name;
            account["address1_line1"] = billingStreet;
            account["address1_city"] = billingCity;
            account["address1_stateorprovince"] = billingState;
            account["address1_postalcode"] = billingPostalCode;
            account["address1_country"] = billingCountry;

            if (!string.IsNullOrWhiteSpace(phone))
            {
                account["telephone1"] = phone;
            }

            if (!string.IsNullOrWhiteSpace(accountType))
            {
                account["accountcategorycode"] = new OptionSetValue(GetAccountTypeOptionSetValue(accountType));
            }

            return _crmService.Create(account);
        }

        public Guid CreateAccountFromWrapper(AccountWrapper accountWrapper)
        {
            if (accountWrapper == null || string.IsNullOrWhiteSpace(accountWrapper.Name))
            {
                throw new InvalidPluginExecutionException("Account Name is required.");
            }

            return CreateAccount(
                accountWrapper.Name,
                accountWrapper.BillingStreet,
                accountWrapper.BillingCity,
                accountWrapper.BillingState,
                accountWrapper.BillingPostalCode,
                accountWrapper.BillingCountry,
                accountWrapper.Phone,
                accountWrapper.AccountType);
        }

        public EntityCollection GetContactsByAccountNumber(string accountNumber)
        {
            if (string.IsNullOrWhiteSpace(accountNumber))
            {
                throw new InvalidPluginExecutionException("Account Number is required.");
            }

            var accountQuery = new QueryExpression("account")
            {
                ColumnSet = new ColumnSet("accountid", "name", "accountnumber"),
                Criteria = new FilterExpression
                {
                    Conditions =
                    {
                        new ConditionExpression("accountnumber", ConditionOperator.Equal, accountNumber)
                    }
                },
                TopCount = 1
            };

            var accounts = _organizationService.RetrieveMultiple(accountQuery);
            if (accounts.Entities.Count == 0)
            {
                return new EntityCollection();
            }

            var accountId = accounts.Entities[0].Id;
            return QueryContactsByAccountId(accountId);
        }

        public EntityCollection GetContactsByAccountId(Guid accountId)
        {
            if (accountId == Guid.Empty)
            {
                throw new InvalidPluginExecutionException("Account Id is required.");
            }

            return QueryContactsByAccountId(accountId);
        }

        private EntityCollection QueryContactsByAccountId(Guid accountId)
        {
            var contactQuery = new QueryExpression("contact")
            {
                ColumnSet = new ColumnSet("contactid", "firstname", "lastname", "email", "telephone1", "jobtitle", "department", "fullname"),
                Criteria = new FilterExpression
                {
                    Conditions =
                    {
                        new ConditionExpression("parentcustomerid", ConditionOperator.Equal, accountId)
                    }
                },
                Orders =
                {
                    new OrderExpression("fullname", OrderType.Ascending)
                }
            };

            return _organizationService.RetrieveMultiple(contactQuery);
        }

        private void ValidateDuplicatePhoneOnCreate(Entity account)
        {
            if (account.LogicalName != "account" || !account.Attributes.Contains("telephone1"))
            {
                return;
            }

            var phone = account.GetAttributeValue<string>("telephone1");
            if (string.IsNullOrWhiteSpace(phone))
            {
                return;
            }

            var query = new QueryExpression("account")
            {
                ColumnSet = new ColumnSet("accountid", "name", "telephone1"),
                Criteria = new FilterExpression
                {
                    Conditions =
                    {
                        new ConditionExpression("telephone1", ConditionOperator.Equal, phone)
                    }
                }
            };

            var result = _organizationService.RetrieveMultiple(query);
            if (result.Entities.Count > 0)
            {
                var duplicate = result.Entities[0];
                var duplicateName = duplicate.GetAttributeValue<string>("name");
                throw new InvalidPluginExecutionException($"Duplicate Account found! An Account with Phone number '{phone}' already exists: {duplicateName} (Id: {duplicate.Id}).");
            }
        }

        private int GetAccountTypeOptionSetValue(string accountType)
        {
            switch (accountType?.Trim().ToLowerInvariant())
            {
                case "customer":
                    return 1;
                case "partner":
                    return 2;
                case "competitor":
                    return 3;
                default:
                    return 0;
            }
        }

        public class AccountWrapper
        {
            public string Name { get; set; }
            public string BillingStreet { get; set; }
            public string BillingCity { get; set; }
            public string BillingState { get; set; }
            public string BillingPostalCode { get; set; }
            public string BillingCountry { get; set; }
            public string Phone { get; set; }
            public string AccountType { get; set; }
        }
    }
}
