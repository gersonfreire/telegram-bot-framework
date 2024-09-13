
# plugin_manager.py
import importlib
import os
import sys

from plugin_base import Plugin

class PluginManager:
    def __init__(self, plugin_dir):
        self.plugin_dir = plugin_dir
        self.plugins = []

    def load_plugins(self):
        sys.path.insert(0, self.plugin_dir)
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = filename[:-3]
                module = importlib.import_module(module_name)
                for attr in dir(module):
                    cls = getattr(module, attr)
                    if isinstance(cls, type) and issubclass(cls, Plugin) and cls is not Plugin:
                        self.plugins.append(cls())

    def execute_plugins(self):
        for plugin in self.plugins:
            plugin.execute()
