using Microsoft.Xrm.Sdk;

namespace D365Migration.Plugin
{
    public static class Logging
    {
        public static void Trace(ITracingService tracingService, string message)
        {
            tracingService?.Trace(message);
        }
    }
}
