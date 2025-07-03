import importlib
import inspect
import os
from telegram.ext import CommandHandler
from ..utils.logger import get_logger
from .plugin_manager import BasePlugin

class PluginManager:
    """
    Manages the loading and registration of plugins, allowing them to
    override framework commands.
    """
    def __init__(self, framework, plugin_dir='plugins/'):
        self.framework = framework
        self.plugin_dir = plugin_dir
        self.logger = get_logger(__name__)
        self.loaded_plugins = {}

    def load_plugins(self):
        """Loads all plugins from the plugin directory."""
        if not os.path.exists(self.plugin_dir):
            self.logger.warning(f"Plugin directory not found: {self.plugin_dir}")
            return

        for filename in os.listdir(self.plugin_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                module_name = filename[:-3]
                try:
                    self.load_plugin(module_name)
                except Exception as e:
                    self.logger.error(f"Failed to load plugin {module_name}: {e}", exc_info=True)

    def load_plugin(self, module_name):
        """Loads a single plugin and registers its commands."""
        try:
            module_path = f"tlgfwk.plugins.{module_name}"
            module = importlib.import_module(module_path)
            importlib.reload(module)  # For hot-reloading

            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BasePlugin) and obj is not BasePlugin:
                    plugin_instance = obj(self.framework)
                    self.loaded_plugins[module_name] = plugin_instance
                    self._register_plugin_commands(plugin_instance)
                    self.logger.info(f"Loaded plugin: {name}")
        except ImportError as e:
            self.logger.error(f"Could not import plugin {module_name}: {e}")

    def _register_plugin_commands(self, plugin_instance):
        """Registers all commands from a plugin, allowing overrides."""
        for _, method in inspect.getmembers(plugin_instance, predicate=inspect.ismethod):
            if hasattr(method, '_command_metadata'):
                metadata = method._command_metadata
                command_name = metadata['name']

                # If command exists, remove the old one before adding the new one
                if command_name in self.framework.commands:
                    self.logger.warning(
                        f"Plugin is overriding framework command: /{command_name}"
                    )
                    # Remove existing handler
                    current_handlers = self.framework.application.handlers.get(0, [])
                    self.framework.application.handlers[0] = [
                        h for h in current_handlers
                        if not (isinstance(h, CommandHandler) and command_name in h.commands)
                    ]

                # Add the new or overriding command
                self.framework.commands[command_name] = metadata
                handler = CommandHandler(command_name, method)
                self.framework.application.add_handler(handler)
                self.logger.info(f"Registered command: /{command_name}")