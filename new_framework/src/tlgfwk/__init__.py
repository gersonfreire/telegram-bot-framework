"""
Telegram Bot Framework (tlgfwk)

Uma framework abrangente para desenvolvimento de bots Telegram com funcionalidades
integradas de gerenciamento de usuários, persistência, plugins e muito mais.
"""

__version__ = "1.0.0"
__author__ = "Telegram Bot Framework Contributors"
__email__ = "contact@tlgfwk.dev"

from .core.framework import TelegramBotFramework
from .core.config import Config, ConfigError
from .core.user_manager import UserManager
from .core.persistence_manager import PersistenceManager
from .core.plugin_manager import PluginManager
from .core.payment_manager import PaymentManager
from .core.scheduler import JobScheduler
from .core.decorators import (
    command, admin_required, admin_required_simple, user_required, owner_required,
    rate_limit, validate_args, typing_action, log_command, typing_indicator
)
from .plugins.base import PluginBase
from .plugins.system_monitor import SystemMonitorPlugin
from .plugins.user_stats import UserStatsPlugin
from .utils.logger import get_logger, setup_logging, TelegramLogHandler, PerformanceLogger
from .utils.crypto import CryptoUtils, EnvCrypto, generate_encryption_key, create_secure_token

__all__ = [
    # Core framework
    "TelegramBotFramework",

    # Configuration
    "Config",
    "ConfigError",

    # Managers
    "UserManager",
    "PersistenceManager",
    "PluginManager",
    "PaymentManager",
    "JobScheduler",

    # Decorators
    "command",
    "admin_required",
    "admin_required_simple",
    "user_required",
    "owner_required",
    "rate_limit",
    "validate_args",
    "typing_action",
    "log_command",
    "typing_indicator",

    # Plugin system
    "PluginBase",
    "SystemMonitorPlugin",
    "UserStatsPlugin",

    # Utilities
    "get_logger",
    "setup_logging",
    "TelegramLogHandler",
    "PerformanceLogger",
    "CryptoUtils",
    "EnvCrypto",
    "generate_encryption_key",
    "create_secure_token",
]
