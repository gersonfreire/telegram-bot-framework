"""
Decorators for the Telegram Bot Framework.

This module provides decorators for command registration, permission checking,
and other framework functionality.
"""

import functools
from typing import Optional, Dict, Any, Callable
from telegram import Update
from telegram.ext import ContextTypes


class CommandRegistry:
    """Registry for command handlers."""
    
    def __init__(self):
        self._commands: Dict[str, Dict[str, Any]] = {}
    
    def register_command(self, name: str, handler: Callable, description: str = "", 
                        admin_only: bool = False, aliases: list = None):
        """Register a command handler."""
        self._commands[name] = {
            "handler": handler,
            "description": description,
            "admin_only": admin_only,
            "aliases": aliases or []
        }
    
    def get_all_commands(self) -> Dict[str, Dict[str, Any]]:
        """Get all registered commands."""
        return self._commands.copy()
    
    def get_command(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific command."""
        return self._commands.get(name)


# Global registry instance
_command_registry = CommandRegistry()


def get_command_registry() -> CommandRegistry:
    """Get the global command registry."""
    return _command_registry


def command(name: str, description: str = "", admin_only: bool = False, aliases: list = None):
    """
    Decorator to register a command handler.
    
    Args:
        name: Command name
        description: Command description
        admin_only: Whether command is admin-only
        aliases: List of command aliases
    """
    def decorator(func: Callable):
        _command_registry.register_command(name, func, description, admin_only, aliases)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def admin_required(func: Callable):
    """Decorator to require admin permissions."""
    @functools.wraps(func)
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        
        # Check if user is admin
        if hasattr(self, 'user_manager') and self.user_manager:
            is_admin = await self.user_manager.is_admin(user_id)
            if not is_admin:
                await update.message.reply_text("❌ Este comando é restrito a administradores.")
                return
        
        return await func(self, update, context, *args, **kwargs)
    
    return wrapper


def owner_required(func: Callable):
    """Decorator to require owner permissions."""
    @functools.wraps(func)
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        
        # Check if user is owner
        if hasattr(self, 'user_manager') and self.user_manager:
            is_owner = await self.user_manager.is_owner(user_id)
            if not is_owner:
                await update.message.reply_text("❌ Este comando é restrito ao proprietário do bot.")
                return
        
        return await func(self, update, context, *args, **kwargs)
    
    return wrapper 