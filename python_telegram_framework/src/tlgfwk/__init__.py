"""
Python Telegram Framework (tlgfwk)

A comprehensive framework for building Telegram bots.
"""

__version__ = "0.1.0"

from .core.framework import TelegramBotFramework
from .core.config import Config, ConfigError
from .core.user_manager import UserManager
from .core.persistence_manager import PersistenceManager
from .utils.logger import get_logger

__all__ = [
    "TelegramBotFramework",
    "Config",
    "ConfigError",
    "UserManager",
    "PersistenceManager",
    "get_logger",
]