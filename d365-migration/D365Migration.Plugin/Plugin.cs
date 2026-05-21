using System;
using Microsoft.Xrm.Sdk;

namespace D365Migration.Plugin
{
    public class Plugin : IPlugin
    {
        public void Execute(IServiceProvider serviceProvider)
        {
            var pluginService = new PluginService(serviceProvider);
            pluginService.Execute();
        }
    }
}
