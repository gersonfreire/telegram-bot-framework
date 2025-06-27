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
        print(f"[DEBUG] PluginBase.set_framework() chamado para {self.name}")
        self.framework = framework
        # Registrar todos os comandos já registrados
        print(f"[DEBUG] Registrando {len(self._commands)} comandos no framework")
        for command_info in self._commands.values():
            self._register_with_framework(command_info)
    
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
        print(f"[DEBUG] PluginBase.register_command() chamado para '{command_name}'")
        self._commands[command_name] = command_info
        self._register_with_framework(command_info)
    
    def _register_with_framework(self, command_info: Dict[str, Any]):
        """Registra o comando no framework se possível."""
        command_name = command_info["name"]
        print(f"[DEBUG] _register_with_framework() para '{command_name}'")
        print(f"[DEBUG] Framework disponível: {self.framework is not None}")
        
        if self.framework and hasattr(self.framework, 'application'):
            from telegram.ext import CommandHandler
            print(f"[DEBUG] Registrando handler para '/{command_name}' no framework")
            
            async def command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
                return await command_info["handler"](update, context)
            
            self.framework.application.add_handler(
                CommandHandler(command_name, command_wrapper)
            )
            print(f"[DEBUG] Handler para '/{command_name}' registrado com sucesso")
        else:
            print(f"[DEBUG] Framework não disponível para registrar '{command_name}'")
    
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