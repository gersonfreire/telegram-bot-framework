"""
Plugin Management System

This module provides the plugin management functionality for the Telegram Bot Framework.
It handles plugin loading, unloading, dependency management, and hot-reloading.
"""

import os
import sys
import asyncio
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Type, Any, Set
import traceback
import logging
from dataclasses import dataclass
from enum import Enum

from ..plugins.base import PluginBase
from ..utils.logger import Logger


class PluginStatus(Enum):
    """Plugin status enumeration."""
    LOADED = "loaded"
    UNLOADED = "unloaded"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass
class PluginInfo:
    """Plugin information container."""
    name: str
    version: str
    description: str
    author: str
    dependencies: List[str]
    status: PluginStatus
    instance: Optional[PluginBase] = None
    error_message: Optional[str] = None
    file_path: Optional[str] = None


class PluginManager:
    """
    Plugin Manager for the Telegram Bot Framework.

    Handles loading, unloading, and managing plugins with dependency resolution.
    """

    def __init__(self, bot_instance=None, plugin_dir: str = "plugins"):
        """
        Initialize the plugin manager.

        Args:
            bot_instance: The main bot framework instance
            plugin_dir: Directory containing plugins
        """
        self.bot = bot_instance
        self.plugin_dir = Path(plugin_dir)
        self.logger = Logger(__name__)

        # Plugin registry
        self.plugins: Dict[str, PluginInfo] = {}
        self.loaded_plugins = []  # List of loaded plugin names for compatibility with tests
        self.available_plugins = []  # List of available plugin names
        self.loaded_plugin_instances: Dict[str, PluginBase] = {}
        self.plugin_modules: Dict[str, Any] = {}

        # Dependency graph
        self.dependency_graph: Dict[str, Set[str]] = {}
        self.reverse_dependencies: Dict[str, Set[str]] = {}

        # Configuration
        self.auto_reload = False
        self.disabled_plugins: Set[str] = set()

        # File watching for hot reload
        self._file_timestamps: Dict[str, float] = {}

        self.logger.info(f"Plugin manager initialized with plugin directory: {self.plugin_dir}")

    def discover_plugins(self) -> List[str]:
        """
        Discover all available plugins in the plugin directory.

        Returns:
            List of discovered plugin names
        """
        discovered = []

        if not self.plugin_dir.exists():
            self.logger.warning(f"Plugin directory does not exist: {self.plugin_dir}")
            self.available_plugins = []
            return discovered

        for item in self.plugin_dir.iterdir():
            if item.is_file() and item.suffix == '.py' and not item.name.startswith('_'):
                plugin_name = item.stem
                discovered.append(plugin_name)
                self.logger.debug(f"Discovered plugin: {plugin_name}")
            elif item.is_dir() and not item.name.startswith('_'):
                init_file = item / '__init__.py'
                if init_file.exists():
                    plugin_name = item.name
                    discovered.append(plugin_name)
                    self.logger.debug(f"Discovered plugin package: {plugin_name}")

        self.available_plugins = discovered
        self.logger.info(f"Discovered {len(discovered)} plugins: {discovered}")
        return discovered

    async def load_plugin(self, plugin_name: str, bot_instance=None, config=None) -> bool:
        """
        Load a specific plugin.

        Args:
            plugin_name: Name of the plugin to load
            bot_instance: Bot instance (optional, uses self.bot if not provided)
            config: Plugin configuration (optional)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if plugin is registered
            if plugin_name not in self.plugins:
                self.logger.error(f"Plugin {plugin_name} is not registered")
                return False

            # Check if already loaded
            if plugin_name in self.loaded_plugins:
                self.logger.warning(f"Plugin {plugin_name} is already loaded")
                return True

            plugin_info = self.plugins[plugin_name]
            plugin_instance = plugin_info.instance

            if not plugin_instance:
                self.logger.error(f"Plugin {plugin_name} has no instance")
                return False

            # Use provided bot instance or fallback to self.bot
            bot = bot_instance or self.bot

            # Initialize plugin
            try:
                if hasattr(plugin_instance, 'initialize') and callable(plugin_instance.initialize):
                    if config:
                        await plugin_instance.initialize(bot, config)
                    else:
                        await plugin_instance.initialize(bot)
                else:
                    # Fallback for plugins without async initialize
                    if hasattr(plugin_instance, 'bot_instance'):
                        plugin_instance.bot_instance = bot
            except Exception as e:
                self.logger.error(f"Failed to initialize plugin {plugin_name}: {e}")
                plugin_info.status = PluginStatus.ERROR
                plugin_info.error_message = str(e)
                return False

            # Start plugin lifecycle
            try:
                if hasattr(plugin_instance, 'start') and callable(plugin_instance.start):
                    if asyncio.iscoroutinefunction(plugin_instance.start):
                        await plugin_instance.start()
                    else:
                        plugin_instance.start()
            except Exception as e:
                self.logger.warning(f"Failed to start plugin {plugin_name}: {e}")

            # Register commands with bot if available
            if self.bot and hasattr(self.bot, 'add_command_handler') and hasattr(plugin_instance, 'get_commands'):
                try:
                    commands = plugin_instance.get_commands()
                    self.logger.info(f"Plugin {plugin_name} returned commands: {commands}")
                    if commands:
                        # Handle both list of dicts and dict formats
                        if isinstance(commands, list):
                            for command_info in commands:
                                if isinstance(command_info, dict):
                                    command_name = command_info.get('name')
                                    command_handler = command_info.get('handler')
                                    self.logger.info(f"Processing command: {command_name} with handler: {command_handler}")
                                    if command_name and command_handler:
                                        self.bot.add_command_handler(command_name, command_handler)
                                        self.logger.info(f"Successfully registered command '{command_name}' from plugin {plugin_name}")
                                    else:
                                        self.logger.warning(f"Invalid command info: {command_info}")
                        elif isinstance(commands, dict):
                            for command_name, command_handler in commands.items():
                                self.bot.add_command_handler(command_name, command_handler)
                                self.logger.info(f"Registered command '{command_name}' from plugin {plugin_name}")
                    else:
                        self.logger.warning(f"Plugin {plugin_name} returned no commands")
                except Exception as e:
                    self.logger.warning(f"Failed to register commands for plugin {plugin_name}: {e}")
                    import traceback
                    self.logger.warning(f"Traceback: {traceback.format_exc()}")

            # Add to loaded plugins
            self.loaded_plugins.append(plugin_name)
            plugin_info.status = PluginStatus.LOADED

            self.logger.info(f"Plugin {plugin_name} loaded successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to load plugin {plugin_name}: {e}")
            if plugin_name in self.plugins:
                self.plugins[plugin_name].status = PluginStatus.ERROR
                self.plugins[plugin_name].error_message = str(e)
            return False

    async def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a specific plugin.

        Args:
            plugin_name: Name of the plugin to unload

        Returns:
            True if successful, False otherwise
        """
        try:
            if plugin_name not in self.loaded_plugins:
                self.logger.warning(f"Plugin {plugin_name} is not loaded")
                return True

            plugin_info = self.plugins.get(plugin_name)
            if plugin_info and plugin_info.instance:
                # Cleanup plugin
                try:
                    if hasattr(plugin_info.instance, 'cleanup') and callable(plugin_info.instance.cleanup):
                        await plugin_info.instance.cleanup()
                except Exception as e:
                    self.logger.warning(f"Error during plugin {plugin_name} cleanup: {e}")

            # Remove from loaded plugins list
            self.loaded_plugins.remove(plugin_name)

            # Update status
            if plugin_info:
                plugin_info.status = PluginStatus.UNLOADED

            self.logger.info(f"Plugin {plugin_name} unloaded successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to unload plugin {plugin_name}: {e}")
            self.logger.debug(traceback.format_exc())
            return False

    def reload_plugin(self, plugin_name: str) -> bool:
        """
        Reload a specific plugin.

        Args:
            plugin_name: Name of the plugin to reload

        Returns:
            True if successful, False otherwise
        """
        self.logger.info(f"Reloading plugin {plugin_name}")

        # Store current status
        was_loaded = plugin_name in self.loaded_plugins

        if was_loaded:
            if not self.unload_plugin(plugin_name):
                return False

        return self.load_plugin(plugin_name)

    def load_all_plugins(self) -> Dict[str, bool]:
        """
        Load all discovered plugins in dependency order.

        Returns:
            Dictionary of plugin names and their load status
        """
        discovered = self.discover_plugins()
        results = {}

        # Sort by dependencies (basic implementation)
        # TODO: Implement proper topological sort for complex dependencies
        for plugin_name in discovered:
            # Use the async method with asyncio.run for each plugin
            import asyncio
            try:
                # Create a new event loop for each plugin if needed
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                results[plugin_name] = loop.run_until_complete(self.load_plugin(plugin_name))
                loop.close()
            except Exception as e:
                self.logger.error(f"Failed to load plugin {plugin_name}: {e}")
                results[plugin_name] = False

        loaded_count = sum(1 for success in results.values() if success)
        self.logger.info(f"Loaded {loaded_count}/{len(discovered)} plugins")

        return results

    async def load_all_plugins(self, bot_instance=None, config=None) -> Dict[str, bool]:
        """
        Load all registered plugins.

        Args:
            bot_instance: Bot instance (optional)
            config: Configuration for plugins (optional)

        Returns:
            Dictionary of plugin names and their load status
        """
        results = {}

        for plugin_name in self.plugins.keys():
            results[plugin_name] = await self.load_plugin(plugin_name, bot_instance, config)

        loaded_count = sum(1 for success in results.values() if success)
        self.logger.info(f"Loaded {loaded_count} out of {len(self.plugins)} plugins")
        return results

    async def unload_all_plugins(self) -> Dict[str, bool]:
        """
        Unload all loaded plugins.

        Returns:
            Dictionary of plugin names and their unload status
        """
        results = {}

        # Create a copy of the list to avoid modification during iteration
        plugins_to_unload = list(self.loaded_plugins)

        for plugin_name in plugins_to_unload:
            results[plugin_name] = await self.unload_plugin(plugin_name)

        unloaded_count = sum(1 for success in results.values() if success)
        self.logger.info(f"Unloaded {unloaded_count} plugins")
        return results

    async def register_plugin(self, plugin_name: str, plugin_instance: PluginBase) -> bool:
        """
        Register a plugin instance.

        Args:
            plugin_name: Name of the plugin
            plugin_instance: Plugin instance to register

        Returns:
            True if successful, False otherwise
        """
        try:
            if plugin_name in self.plugins:
                self.logger.warning(f"Plugin {plugin_name} is already registered")
                return False

            plugin_info = PluginInfo(
                name=plugin_name,
                version=getattr(plugin_instance, 'version', '1.0.0'),
                description=getattr(plugin_instance, 'description', ''),
                author=getattr(plugin_instance, 'author', ''),
                dependencies=getattr(plugin_instance, 'dependencies', []),
                status=PluginStatus.UNLOADED,
                instance=plugin_instance
            )

            self.plugins[plugin_name] = plugin_info
            self.loaded_plugin_instances[plugin_name] = plugin_instance

            self.logger.info(f"Plugin {plugin_name} registered successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to register plugin {plugin_name}: {e}")
            return False

    def load_plugin_instance(self, plugin_instance: PluginBase) -> bool:
        """
        Load a plugin instance directly.

        Args:
            plugin_instance: Plugin instance to load

        Returns:
            True if successful, False otherwise
        """
        try:
            plugin_name = getattr(plugin_instance, 'name', plugin_instance.__class__.__name__)

            # Register the plugin if not already registered
            if plugin_name not in self.plugins:
                plugin_info = PluginInfo(
                    name=plugin_name,
                    version=getattr(plugin_instance, 'version', '1.0.0'),
                    description=getattr(plugin_instance, 'description', ''),
                    author=getattr(plugin_instance, 'author', ''),
                    dependencies=getattr(plugin_instance, 'dependencies', []),
                    status=PluginStatus.LOADED,
                    instance=plugin_instance
                )
                self.plugins[plugin_name] = plugin_info
                self.loaded_plugin_instances[plugin_name] = plugin_instance

            # Add to loaded plugins list
            if plugin_name not in self.loaded_plugins:
                self.loaded_plugins.append(plugin_name)

            # Register commands with bot if available
            if self.bot and hasattr(self.bot, 'add_command_handler') and hasattr(plugin_instance, 'get_commands'):
                try:
                    commands = plugin_instance.get_commands()
                    self.logger.info(f"Plugin {plugin_name} returned commands: {commands}")
                    if commands:
                        # Handle both list of dicts and dict formats
                        if isinstance(commands, list):
                            for command_info in commands:
                                if isinstance(command_info, dict):
                                    command_name = command_info.get('name')
                                    command_handler = command_info.get('handler')
                                    self.logger.info(f"Processing command: {command_name} with handler: {command_handler}")
                                    if command_name and command_handler:
                                        self.bot.add_command_handler(command_name, command_handler)
                                        self.logger.info(f"Successfully registered command '{command_name}' from plugin {plugin_name}")
                                    else:
                                        self.logger.warning(f"Invalid command info: {command_info}")
                        elif isinstance(commands, dict):
                            for command_name, command_handler in commands.items():
                                self.bot.add_command_handler(command_name, command_handler)
                                self.logger.info(f"Registered command '{command_name}' from plugin {plugin_name}")
                    else:
                        self.logger.warning(f"Plugin {plugin_name} returned no commands")
                except Exception as e:
                    self.logger.warning(f"Failed to register commands for plugin {plugin_name}: {e}")
                    import traceback
                    self.logger.warning(f"Traceback: {traceback.format_exc()}")

            self.logger.info(f"Plugin instance {plugin_name} loaded successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to load plugin instance {plugin_name}: {e}")
            return False

    async def unregister_plugin(self, plugin_name: str) -> bool:
        """
        Unregister a plugin.

        Args:
            plugin_name: Name of the plugin to unregister

        Returns:
            True if successful, False if not found
        """
        if plugin_name not in self.plugins:
            self.logger.warning(f"Plugin {plugin_name} is not registered")
            return False

        # Unload if loaded
        if plugin_name in self.loaded_plugins:
            await self.unload_plugin(plugin_name)

        # Remove from registry
        del self.plugins[plugin_name]
        self.logger.info(f"Plugin {plugin_name} unregistered successfully")
        return True

    def get_loaded_plugins(self) -> List[str]:
        """
        Get list of loaded plugin names.

        Returns:
            List of loaded plugin names
        """
        return list(self.loaded_plugins)

    def get_registered_plugins(self) -> List[str]:
        """
        Get list of registered plugin names.

        Returns:
            List of registered plugin names
        """
        return list(self.plugins.keys())

    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a plugin.

        Args:
            plugin_name: Name of the plugin

        Returns:
            Plugin information dict or None if not found
        """
        if plugin_name not in self.plugins:
            return None

        plugin_info = self.plugins[plugin_name]
        return {
            'name': plugin_info.name,
            'version': plugin_info.version,
            'description': plugin_info.description,
            'author': plugin_info.author,
            'dependencies': plugin_info.dependencies,
            'status': plugin_info.status.value,
            'loaded': plugin_name in self.loaded_plugins
        }

    def list_plugins(self, status_filter: Optional[PluginStatus] = None) -> List[PluginInfo]:
        """
        List all plugins with optional status filter.

        Args:
            status_filter: Optional status to filter by

        Returns:
            List of PluginInfo objects
        """
        plugins = list(self.plugins.values())

        if status_filter:
            plugins = [p for p in plugins if p.status == status_filter]

        return plugins

    def enable_plugin(self, plugin_name: str) -> bool:
        """
        Enable a disabled plugin.

        Args:
            plugin_name: Name of the plugin to enable

        Returns:
            True if successful
        """
        if plugin_name in self.disabled_plugins:
            self.disabled_plugins.remove(plugin_name)
            self.logger.info(f"Plugin {plugin_name} enabled")
            return True
        return False

    def disable_plugin(self, plugin_name: str) -> bool:
        """
        Disable a plugin (unload if loaded).

        Args:
            plugin_name: Name of the plugin to disable

        Returns:
            True if successful
        """
        # Unload if currently loaded
        if plugin_name in self.loaded_plugins:
            if not self.unload_plugin(plugin_name):
                return False

        # Add to disabled list
        self.disabled_plugins.add(plugin_name)

        # Update status
        if plugin_name in self.plugins:
            self.plugins[plugin_name].status = PluginStatus.DISABLED

        self.logger.info(f"Plugin {plugin_name} disabled")
        return True

    def check_for_updates(self) -> List[str]:
        """
        Check for plugin file updates (for hot reload).

        Returns:
            List of plugin names that have been updated
        """
        updated = []

        for plugin_name, plugin_info in self.plugins.items():
            if plugin_info.file_path and plugin_info.status == PluginStatus.LOADED:
                file_path = Path(plugin_info.file_path)
                if file_path.exists():
                    current_time = file_path.stat().st_mtime
                    stored_time = self._file_timestamps.get(str(file_path), 0)

                    if current_time > stored_time:
                        updated.append(plugin_name)
                        self._file_timestamps[str(file_path)] = current_time

        return updated

    def auto_reload_check(self):
        """Check for updates and reload changed plugins if auto-reload is enabled."""
        if not self.auto_reload:
            return

        updated = self.check_for_updates()
        for plugin_name in updated:
            self.logger.info(f"Auto-reloading updated plugin: {plugin_name}")
            self.reload_plugin(plugin_name)

    def _find_plugin_path(self, plugin_name: str) -> Optional[Path]:
        """Find the file path for a plugin."""
        # Try as a Python file
        plugin_file = self.plugin_dir / f"{plugin_name}.py"
        if plugin_file.exists():
            return plugin_file

        # Try as a package
        plugin_package = self.plugin_dir / plugin_name / "__init__.py"
        if plugin_package.exists():
            return plugin_package.parent

        return None

    def _load_plugin_module(self, plugin_name: str, plugin_path: Path):
        """Load a plugin module from file."""
        try:
            if plugin_path.is_file():
                # Load from file
                spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            else:
                # Load from package
                spec = importlib.util.spec_from_file_location(
                    plugin_name, plugin_path / "__init__.py"
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

            return module

        except Exception as e:
            self.logger.error(f"Failed to load module for plugin {plugin_name}: {e}")
            return None

    def _find_plugin_class(self, module, plugin_name: str) -> Optional[Type[PluginBase]]:
        """Find the plugin class in a module."""
        # Look for classes that inherit from PluginBase
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and                issubclass(attr, PluginBase) and
                attr != PluginBase):
                return attr

        self.logger.error(f"No PluginBase subclass found in plugin {plugin_name}")
        return None

    def _validate_dependencies(self, plugin: PluginBase) -> bool:
        """Validate that all plugin dependencies are loaded."""
        for dep in plugin.dependencies:
            if dep not in self.loaded_plugins:
                self.logger.error(
                    f"Plugin {plugin.name} requires dependency {dep} which is not loaded"
                )
                return False
        return True

    def _update_dependency_graph(self, plugin_name: str, dependencies: List[str]):
        """Update the dependency graph."""
        self.dependency_graph[plugin_name] = set(dependencies)

        # Update reverse dependencies
        for dep in dependencies:
            if dep not in self.reverse_dependencies:
                self.reverse_dependencies[dep] = set()
            self.reverse_dependencies[dep].add(plugin_name)

    def _remove_from_dependency_graph(self, plugin_name: str):
        """Remove plugin from dependency graph."""
        # Remove from dependency graph
        if plugin_name in self.dependency_graph:
            dependencies = self.dependency_graph[plugin_name]
            del self.dependency_graph[plugin_name]

            # Update reverse dependencies
            for dep in dependencies:
                if dep in self.reverse_dependencies:
                    self.reverse_dependencies[dep].discard(plugin_name)

        # Remove from reverse dependencies
        if plugin_name in self.reverse_dependencies:
            del self.reverse_dependencies[plugin_name]

    def _update_plugin_status(self, plugin_name: str, status: PluginStatus, error_msg: str = None):
        """Update plugin status in registry."""
        if plugin_name not in self.plugins:
            self.plugins[plugin_name] = PluginInfo(
                name=plugin_name,
                version="unknown",
                description="",
                author="",
                dependencies=[],
                status=status,
                error_message=error_msg
            )
        else:
            self.plugins[plugin_name].status = status
            self.plugins[plugin_name].error_message = error_msg
