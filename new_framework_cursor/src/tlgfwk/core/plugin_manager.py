"""
Plugin management for the Telegram Bot Framework.
"""

from typing import Optional, Dict, Any, List
import os
import importlib.util
import inspect
from pathlib import Path

from ..plugins.base import PluginBase


class PluginManager:
    """Plugin management system."""
    
    def __init__(self, plugins_dir: str, framework):
        self.plugins_dir = plugins_dir
        self.framework = framework
        self._plugins: Dict[str, PluginBase] = {}
    
    def _log(self, message: str, level: str = "info"):
        """Log a message."""
        if hasattr(self.framework, f'log_{level}'):
            getattr(self.framework, f'log_{level}')(message)
        else:
            print(f"[PluginManager] {message}")
    
    async def load_all_plugins(self):
        """Load all plugins from the plugins directory."""
        if not os.path.exists(self.plugins_dir):
            self._log(f"Plugins directory does not exist: {self.plugins_dir}", "warning")
            return
        
        # Find all Python files in the plugins directory
        plugin_files = []
        for file_path in Path(self.plugins_dir).glob("*.py"):
            if file_path.name.startswith("__"):
                continue
            plugin_files.append(file_path)
        
        self._log(f"Found {len(plugin_files)} potential plugin files")
        
        for plugin_file in plugin_files:
            try:
                await self.load_plugin_from_file(plugin_file)
            except Exception as e:
                self._log(f"Failed to load plugin from {plugin_file.name}: {e}", "error")
    
    async def load_plugin_from_file(self, plugin_file: Path):
        """Load a plugin from a specific file."""
        try:
            # Import the module
            spec = importlib.util.spec_from_file_location(
                plugin_file.stem, 
                plugin_file
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find plugin classes in the module
            plugin_classes = []
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, PluginBase) and 
                    obj != PluginBase):
                    plugin_classes.append(obj)
            
            if not plugin_classes:
                self._log(f"No plugin classes found in {plugin_file.name}", "warning")
                return
            
            # Instantiate and load plugins
            for plugin_class in plugin_classes:
                try:
                    plugin = plugin_class()
                    await self.load_plugin_instance(plugin)
                except Exception as e:
                    self._log(f"Failed to instantiate plugin {plugin_class.__name__}: {e}", "error")
                    
        except Exception as e:
            self._log(f"Failed to load plugin from {plugin_file.name}: {e}", "error")
    
    async def load_plugin_instance(self, plugin: PluginBase):
        """Load a specific plugin instance."""
        try:
            # Set framework reference
            plugin.set_framework(self.framework)
            
            # Call on_load
            await plugin.on_load()
            
            # Register plugin
            self._plugins[plugin.name] = plugin
            
            # Register commands
            for command_name, command_info in plugin.get_commands().items():
                self._register_plugin_command(plugin, command_name, command_info)
            
            self._log(f"Loaded plugin: {plugin.name} v{plugin.version}")
            
        except Exception as e:
            self._log(f"Failed to load plugin {plugin.name}: {e}", "error")
    
    def _register_plugin_command(self, plugin: PluginBase, command_name: str, command_info: Dict[str, Any]):
        """Register a command from a plugin."""
        try:
            from telegram.ext import CommandHandler
            
            # Create wrapper that includes plugin context
            async def command_wrapper(update, context):
                if not plugin.is_enabled():
                    await update.message.reply_text("❌ Este comando está temporariamente desabilitado.")
                    return
                
                try:
                    return await command_info["handler"](update, context)
                except Exception as e:
                    self._log(f"Error in plugin command {command_name}: {e}", "error")
                    await update.message.reply_text("❌ Ocorreu um erro ao executar o comando.")
            
            # Register with framework
            self.framework.application.add_handler(
                CommandHandler(command_name, command_wrapper)
            )
            
            self._log(f"Registered plugin command: /{command_name} from {plugin.name}")
            
        except Exception as e:
            self._log(f"Failed to register plugin command {command_name}: {e}", "error")
    
    async def load_plugin(self, plugin_name: str):
        """Load a specific plugin by name."""
        plugin_file = Path(self.plugins_dir) / f"{plugin_name}.py"
        if plugin_file.exists():
            await self.load_plugin_from_file(plugin_file)
        else:
            self._log(f"Plugin file not found: {plugin_file}", "error")
    
    async def unload_plugin(self, plugin_name: str):
        """Unload a plugin."""
        if plugin_name in self._plugins:
            plugin = self._plugins[plugin_name]
            try:
                await plugin.on_unload()
                del self._plugins[plugin_name]
                self._log(f"Unloaded plugin: {plugin_name}")
            except Exception as e:
                self._log(f"Failed to unload plugin {plugin_name}: {e}", "error")
    
    def get_loaded_plugins(self) -> List[str]:
        """Get list of loaded plugins."""
        return list(self._plugins.keys())
    
    def get_plugin(self, plugin_name: str) -> Optional[PluginBase]:
        """Get a specific plugin by name."""
        return self._plugins.get(plugin_name)
    
    def get_all_plugins(self) -> Dict[str, PluginBase]:
        """Get all loaded plugins."""
        return self._plugins.copy()
    
    async def enable_plugin(self, plugin_name: str):
        """Enable a plugin."""
        plugin = self.get_plugin(plugin_name)
        if plugin:
            plugin.enable()
            self._log(f"Enabled plugin: {plugin_name}")
        else:
            self._log(f"Plugin not found: {plugin_name}", "error")
    
    async def disable_plugin(self, plugin_name: str):
        """Disable a plugin."""
        plugin = self.get_plugin(plugin_name)
        if plugin:
            plugin.disable()
            self._log(f"Disabled plugin: {plugin_name}")
        else:
            self._log(f"Plugin not found: {plugin_name}", "error") 