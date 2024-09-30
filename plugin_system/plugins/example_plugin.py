# Example plugin (plugins/example_plugin.py)

try:
    from plugin_base import Plugin
except ImportError:
    print("Error importing Plugin from plugin_base")
    try:
        from ...plugin_system.plugin_base import Plugin
    except ImportError:
        print("Error importing Plugin from plugin_base")
        from plugin_system.plugin_base import Plugin

# class example_plugin(Plugin):
class ExamplePlugin(Plugin):
    def execute(self):
        print("Example Plugin Executed")
        
    # create the above function in the plugin_sample.py file
    def execute_message(self, message):
        print(message)    