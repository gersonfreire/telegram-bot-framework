# Example plugin (plugins/example_plugin.py)
from plugin_base import Plugin
# from ..plugin_base import Plugin

# class example_plugin(Plugin):
class ExamplePlugin(Plugin):
    def execute(self):
        print("Example Plugin Executed")
        
    # create the above function in the plugin_sample.py file
    def execute_message(self, message):
        print(message)    