using System;
using Microsoft.Xrm.Sdk;
using Microsoft.Xrm.Sdk.Query;

namespace D365Migration.Plugin
{
    public class CrmService
    {
        private readonly IOrganizationService _organizationService;
        private readonly ITracingService _tracing;

        public CrmService(IOrganizationService organizationService, ITracingService tracing)
        {
            _organizationService = organizationService ?? throw new ArgumentNullException(nameof(organizationService));
            _tracing = tracing;
        }

        public Guid Create(Entity entity)
        {
            _tracing?.Trace($"Creating entity: {entity?.LogicalName}");
            return _organizationService.Create(entity);
        }

        public Entity Retrieve(string logicalName, Guid id, ColumnSet columns)
        {
            _tracing?.Trace($"Retrieving entity {logicalName} with id {id}");
            return _organizationService.Retrieve(logicalName, id, columns);
        }

        public void Update(Entity entity)
        {
            _tracing?.Trace($"Updating entity: {entity?.LogicalName} id {entity?.Id}");
            _organizationService.Update(entity);
        }

        public void Delete(string logicalName, Guid id)
        {
            _tracing?.Trace($"Deleting entity: {logicalName} id {id}");
            _organizationService.Delete(logicalName, id);
        }
    }
}
