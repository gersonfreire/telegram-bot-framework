"""
Core Module

This module contains the core components of the Telegram Bot Framework.
"""

from .config import Config, ConfigError
from .framework import TelegramBotFramework
from .user_manager import UserManager
from .persistence_manager import PersistenceManager
from .plugin_manager import PluginManager
from .payment_manager import PaymentManager
from .scheduler import JobScheduler
from .decorators import (
    command, admin_required, owner_required, rate_limit, 
    validate_args, typing_action, log_command
)

__all__ = [
    # Main framework
    'TelegramBotFramework',
    
    # Configuration
    'Config',
    'ConfigError',
    
    # Managers
    'UserManager',
    'PersistenceManager', 
    'PluginManager',
    'PaymentManager',
    'JobScheduler',
    
    # Decorators
    'command',
    'admin_required',
    'owner_required', 
    'rate_limit',
    'validate_args',
    'typing_action',
    'log_command'
]
