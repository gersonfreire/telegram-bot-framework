import importlib
import inspect
import os
from ..utils.logger import get_logger

class PluginManager:
    """
    Manages the loading and registration of plugins.

    This class is responsible for:
    - Discovering and loading plugin modules from a specified directory.
    - Instantiating plugin classes.
    - Registering command handlers defined within plugins.

    Attributes:
        framework (TelegramBotFramework): The main framework instance.
        plugin_dir (str): The directory where plugins are located.
        logger (logging.Logger): The logger instance.
        loaded_plugins (dict): A dictionary of loaded plugin instances.
    """
    def __init__(self, framework, plugin_dir='plugins/'):
        """
        Initializes the PluginManager.

        Args:
            framework (TelegramBotFramework): The main framework instance.
            plugin_dir (str): The directory to load plugins from.
        """
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
                    self.logger.error(f"Failed to load plugin {module_name}: {e}")

    def load_plugin(self, module_name):
        """Loads a single plugin by its module name."""
        try:
            module_path = f"{self.plugin_dir.replace('/', '.')}{module_name}"
            module = importlib.import_module(module_path)
            
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, object) and hasattr(obj, '_is_plugin') and obj._is_plugin:
                    plugin_instance = obj(self.framework)
                    self.loaded_plugins[module_name] = plugin_instance
                    self._register_plugin_commands(plugin_instance)
                    self.logger.info(f"Loaded plugin: {name}")

        except ImportError as e:
            self.logger.error(f"Could not import plugin {module_name}: {e}")

    def _register_plugin_commands(self, plugin_instance):
        """Registers all commands from a plugin instance."""
        for name, method in inspect.getmembers(plugin_instance, predicate=inspect.ismethod):
            if hasattr(method, '_command_metadata'):
                metadata = method._command_metadata
                command_name = metadata['name']
                
                # Avoid overwriting framework commands
                if command_name in self.framework.commands:
                    self.logger.warning(f"Plugin command /{command_name} conflicts with a framework command. Skipping.")
                    continue

                self.framework.commands[command_name] = metadata
                self.framework.application.add_handler(CommandHandler(command_name, method))
                self.logger.info(f"Registered plugin command: /{command_name}")