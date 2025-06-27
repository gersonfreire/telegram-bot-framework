"""
Base class for Telegram Bot Framework plugins.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable
from telegram import Update
from telegram.ext import ContextTypes


class PluginBase(ABC):
    """
    Base class for all plugins in the Telegram Bot Framework.
    
    Plugins should inherit from this class and implement the required methods.
    """
    
    name: str = "UnnamedPlugin"
    version: str = "1.0.0"
    description: str = "No description provided"
    author: str = "Unknown"
    
    def __init__(self):
        """Initialize the plugin."""
        self.framework = None
        self._commands: Dict[str, Dict[str, Any]] = {}
        self._enabled = True
    
    def set_framework(self, framework):
        """Set the framework instance."""
        self.framework = framework
    
    def register_command(self, command_info: Dict[str, Any]):
        """
        Register a command with the framework.
        
        Args:
            command_info: Dictionary with command information
                - name: Command name (without /)
                - handler: Command handler function
                - description: Command description
                - admin_only: Whether command is admin-only
        """
        command_name = command_info["name"]
        self._commands[command_name] = command_info
        
        # Register with framework if available
        if self.framework and hasattr(self.framework, 'application'):
            from telegram.ext import CommandHandler
            
            # Create wrapper to pass plugin instance
            async def command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
                return await command_info["handler"](update, context)
            
            self.framework.application.add_handler(
                CommandHandler(command_name, command_wrapper)
            )
    
    def get_commands(self) -> Dict[str, Dict[str, Any]]:
        """Get all registered commands for this plugin."""
        return self._commands.copy()
    
    def is_enabled(self) -> bool:
        """Check if plugin is enabled."""
        return self._enabled
    
    def enable(self):
        """Enable the plugin."""
        self._enabled = True
    
    def disable(self):
        """Disable the plugin."""
        self._enabled = False
    
    @abstractmethod
    async def on_load(self):
        """Called when plugin is loaded."""
        pass
    
    @abstractmethod
    async def on_unload(self):
        """Called when plugin is unloaded."""
        pass
    
    async def on_startup(self):
        """Called when framework starts up."""
        pass
    
    async def on_shutdown(self):
        """Called when framework shuts down."""
        pass 