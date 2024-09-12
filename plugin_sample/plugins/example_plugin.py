# Example plugin (plugins/example_plugin.py)
from plugin_base import Plugin

class ExamplePlugin(Plugin):
    def execute(self):
        print("Example Plugin Executed")