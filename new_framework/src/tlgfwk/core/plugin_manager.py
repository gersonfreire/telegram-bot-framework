"""
Plugin Management System

This module provides the plugin management functionality for the Telegram Bot Framework.
It handles plugin loading, unloading, dependency management, and hot-reloading.
"""

import os
import sys
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Type, Any, Set
import traceback
import logging
from dataclasses import dataclass
from enum import Enum

from ..plugins.base import PluginBase
from ..utils.logger import get_logger


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
    
    def __init__(self, bot_instance, plugin_dir: str = "plugins"):
        """
        Initialize the plugin manager.
        
        Args:
            bot_instance: The main bot framework instance
            plugin_dir: Directory containing plugins
        """
        self.bot = bot_instance
        self.plugin_dir = Path(plugin_dir)
        self.logger = get_logger(__name__)
        
        # Plugin registry
        self.plugins: Dict[str, PluginInfo] = {}
        self.loaded_plugins: Dict[str, PluginBase] = {}
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
        
        self.logger.info(f"Discovered {len(discovered)} plugins: {discovered}")
        return discovered
    
    def load_plugin(self, plugin_name: str, force_reload: bool = False) -> bool:
        """
        Load a specific plugin.
        
        Args:
            plugin_name: Name of the plugin to load
            force_reload: Force reload if already loaded
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if already loaded
            if plugin_name in self.loaded_plugins and not force_reload:
                self.logger.warning(f"Plugin {plugin_name} is already loaded")
                return True
            
            # Check if disabled
            if plugin_name in self.disabled_plugins:
                self.logger.info(f"Plugin {plugin_name} is disabled, skipping load")
                return False
            
            # Find plugin file
            plugin_path = self._find_plugin_path(plugin_name)
            if not plugin_path:
                self.logger.error(f"Plugin {plugin_name} not found")
                return False
            
            # Load module
            module = self._load_plugin_module(plugin_name, plugin_path)
            if not module:
                return False
            
            # Find plugin class
            plugin_class = self._find_plugin_class(module, plugin_name)
            if not plugin_class:
                return False
            
            # Create plugin instance
            plugin_instance = plugin_class(self.bot)
            
            # Validate dependencies
            if not self._validate_dependencies(plugin_instance):
                return False
            
            # Initialize plugin
            try:
                plugin_instance.initialize()
            except Exception as e:
                self.logger.error(f"Failed to initialize plugin {plugin_name}: {e}")
                self._update_plugin_status(plugin_name, PluginStatus.ERROR, str(e))
                return False
            
            # Register plugin
            self.loaded_plugins[plugin_name] = plugin_instance
            self.plugin_modules[plugin_name] = module
            
            # Update plugin info
            plugin_info = PluginInfo(
                name=plugin_instance.name,
                version=plugin_instance.version,
                description=plugin_instance.description,
                author=plugin_instance.author,
                dependencies=plugin_instance.dependencies,
                status=PluginStatus.LOADED,
                instance=plugin_instance,
                file_path=str(plugin_path)
            )
            self.plugins[plugin_name] = plugin_info
            
            # Update dependency graph
            self._update_dependency_graph(plugin_name, plugin_instance.dependencies)
            
            # Store file timestamp for hot reload
            if plugin_path.is_file():
                self._file_timestamps[str(plugin_path)] = plugin_path.stat().st_mtime
            
            self.logger.info(f"Plugin {plugin_name} loaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load plugin {plugin_name}: {e}")
            self.logger.debug(traceback.format_exc())
            self._update_plugin_status(plugin_name, PluginStatus.ERROR, str(e))
            return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
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
            
            # Check for dependent plugins
            dependents = self.reverse_dependencies.get(plugin_name, set())
            if dependents:
                loaded_dependents = [dep for dep in dependents if dep in self.loaded_plugins]
                if loaded_dependents:
                    self.logger.error(
                        f"Cannot unload plugin {plugin_name}: "
                        f"plugins {loaded_dependents} depend on it"
                    )
                    return False
            
            # Get plugin instance
            plugin_instance = self.loaded_plugins[plugin_name]
            
            # Cleanup plugin
            try:
                plugin_instance.cleanup()
            except Exception as e:
                self.logger.warning(f"Error during plugin {plugin_name} cleanup: {e}")
            
            # Remove from registry
            del self.loaded_plugins[plugin_name]
            
            # Remove module from cache
            if plugin_name in self.plugin_modules:
                module = self.plugin_modules[plugin_name]
                if hasattr(module, '__file__') and module.__file__:
                    module_name = module.__name__
                    if module_name in sys.modules:
                        del sys.modules[module_name]
                del self.plugin_modules[plugin_name]
            
            # Update status
            if plugin_name in self.plugins:
                self.plugins[plugin_name].status = PluginStatus.UNLOADED
                self.plugins[plugin_name].instance = None
            
            # Clean up dependency graph
            self._remove_from_dependency_graph(plugin_name)
            
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
            results[plugin_name] = self.load_plugin(plugin_name)
        
        loaded_count = sum(1 for success in results.values() if success)
        self.logger.info(f"Loaded {loaded_count}/{len(discovered)} plugins")
        
        return results
    
    def unload_all_plugins(self) -> Dict[str, bool]:
        """
        Unload all loaded plugins.
        
        Returns:
            Dictionary of plugin names and their unload status
        """
        results = {}
        
        # Unload in reverse dependency order
        for plugin_name in list(self.loaded_plugins.keys()):
            results[plugin_name] = self.unload_plugin(plugin_name)
        
        return results
    
    def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """
        Get information about a specific plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            PluginInfo object or None if not found
        """
        return self.plugins.get(plugin_name)
    
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
            if (isinstance(attr, type) and 
                issubclass(attr, PluginBase) and 
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
