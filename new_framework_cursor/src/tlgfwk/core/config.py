"""
Configuration management for the Telegram Bot Framework.

This module handles all bot configuration including loading environment variables,
validation, and encryption of sensitive data.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import base64


logger = logging.getLogger(__name__)


class ConfigError(Exception):
    """Exception raised for configuration errors."""
    pass


class Config:
    """
    Configuration management class for the Telegram Bot Framework.
    
    Handles loading configuration from environment variables, files,
    and provides validation and encryption capabilities.
    """
    
    def __init__(self, bot_token: str = None, owner_user_id: int = None, 
                 admin_user_ids: List[int] = None, log_chat_id: int = None, 
                 debug: bool = True, reuse_connections: bool = True, 
                 use_async: bool = True, max_workers: int = 4, 
                 instance_name: str = "TelegramBot", config_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            bot_token: Telegram bot token
            owner_user_id: User ID of the bot owner
            admin_user_ids: List of admin user IDs
            log_chat_id: Chat ID for logging
            debug: Debug mode flag
            reuse_connections: Whether to reuse connections
            use_async: Whether to use async mode
            max_workers: Maximum worker threads
            instance_name: Bot instance name
            config_file: Path to .env file to load
        """
        # Set up data structure
        self.data: Dict[str, Any] = {}
        self._encryption_key: Optional[bytes] = None
        
        # Load from environment file if provided
        if config_file:
            load_dotenv(config_file)
        
        # Set the basic properties
        self.data['bot_token'] = bot_token
        self.data['telegram_bot_token'] = bot_token  # For compatibility
        if owner_user_id:
            self.data['owner_user_id'] = owner_user_id
        
        # Process admin user IDs - important: DON'T auto-add owner!
        admin_ids = admin_user_ids or []
        if not isinstance(admin_ids, list):
            if isinstance(admin_ids, int):
                admin_ids = [admin_ids]
            elif isinstance(admin_ids, str):
                admin_ids = [int(x.strip()) for x in admin_ids.split(',') if x.strip()]
            else:
                admin_ids = []
            
        # Remove duplicates while preserving order
        self.data['admin_user_ids'] = list(dict.fromkeys(admin_ids))
        
        # Set other properties
        self.data['log_chat_id'] = log_chat_id
        self.data['debug'] = debug if debug is not None else True
        self.data['reuse_connections'] = reuse_connections if reuse_connections is not None else True
        self.data['use_async'] = use_async if use_async is not None else True
        self.data['max_workers'] = max_workers if max_workers is not None else 4
        self.data['instance_name'] = instance_name or "TelegramBot"
        
        # Validate configuration
        self._validate_configuration()
    
    def _parse_bool(self, value: Union[str, bool]) -> bool:
        """Parse string boolean values."""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return False
    
    def _validate_configuration(self):
        """Validate required configuration values."""
        # Check bot token
        if not self.data.get('telegram_bot_token'):
            raise ConfigError("Bot token is required")
        
        # Check owner user ID
        if not self.data.get('owner_user_id') or self.data.get('owner_user_id') == 0:
            raise ConfigError("Owner user ID is required")
        
        # Check max_workers
        if self.data.get('max_workers', 0) <= 0:
            raise ConfigError("max_workers must be positive")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.
        
        Args:
            key: Configuration key (e.g., 'app.name')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.
        
        Args:
            key: Configuration key
            value: Value to set
        """
        self.data[key] = value
    
    def has(self, key: str) -> bool:
        """
        Check if configuration key exists.
        
        Args:
            key: Configuration key
            
        Returns:
            True if key exists
        """
        return key in self.data
    
    def encrypt_value(self, value: str) -> str:
        """
        Encrypt a configuration value.
        
        Args:
            value: Value to encrypt
            
        Returns:
            Encrypted value as base64 string
        """
        if not self._encryption_key:
            raise ConfigError("Encryption key not configured")
        
        fernet = Fernet(base64.urlsafe_b64encode(self._encryption_key))
        encrypted = fernet.encrypt(value.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt_value(self, encrypted_value: str) -> str:
        """
        Decrypt a configuration value.
        
        Args:
            encrypted_value: Encrypted value as base64 string
            
        Returns:
            Decrypted value
        """
        if not self._encryption_key:
            raise ConfigError("Encryption key not configured")
        
        fernet = Fernet(base64.urlsafe_b64encode(self._encryption_key))
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_value.encode())
        decrypted = fernet.decrypt(encrypted_bytes)
        return decrypted.decode()

    @classmethod
    def from_env(cls, env_file: Optional[str] = None) -> "Config":
        """
        Load configuration from environment variables.
        
        Args:
            env_file: Path to .env file to load
            
        Returns:
            Config instance
            
        Raises:
            ConfigError: If required environment variables are missing
        """
        if env_file:
            # Load from .env file if provided
            if not os.path.exists(env_file):
                raise ConfigError(f".env file not found: {env_file}")
            load_dotenv(env_file)
        else:
            # Try to load from default .env file
            default_env = Path(".env")
            if default_env.exists():
                load_dotenv(default_env)
        
        # Get required values from environment
        bot_token = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
        owner_user_id = cls._parse_env_int("OWNER_USER_ID")
        admin_user_ids = cls._parse_env_list("ADMIN_USER_IDS")
        log_chat_id = cls._parse_env_int("LOG_CHAT_ID", 0) or None
        debug = cls._parse_env_bool("DEBUG", True)
        reuse_connections = cls._parse_env_bool("REUSE_CONNECTIONS", True)
        use_async = cls._parse_env_bool("USE_ASYNC", True)
        max_workers = cls._parse_env_int("MAX_WORKERS", 4)
        instance_name = os.getenv("INSTANCE_NAME", "TelegramBot")
        
        # Create config instance
        return cls(
            bot_token=bot_token,
            owner_user_id=owner_user_id,
            admin_user_ids=admin_user_ids,
            log_chat_id=log_chat_id,
            debug=debug,
            reuse_connections=reuse_connections,
            use_async=use_async,
            max_workers=max_workers,
            instance_name=instance_name
        )
    
    @staticmethod
    def _parse_env_list(key: str) -> List[int]:
        """Parse comma-separated list of integers from environment."""
        value = os.getenv(key, "")
        if not value:
            return []
        
        try:
            return [int(x.strip()) for x in value.split(',') if x.strip()]
        except ValueError:
            logger.warning(f"Invalid value for {key}: {value}")
            return []
    
    @staticmethod
    def _parse_env_bool(key: str, default: bool = False) -> bool:
        """Parse boolean value from environment."""
        value = os.getenv(key)
        if value is None:
            return default
        
        return value.lower() in ('true', '1', 'yes', 'on')
    
    @staticmethod
    def _parse_env_int(key: str, default: int = 0) -> int:
        """Parse integer value from environment."""
        value = os.getenv(key)
        if value is None:
            return default
        
        try:
            return int(value)
        except ValueError:
            logger.warning(f"Invalid integer value for {key}: {value}")
            return default
    
    def to_dict(self, include_sensitive: bool = True) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Args:
            include_sensitive: Whether to include sensitive data
            
        Returns:
            Configuration dictionary
        """
        result = self.data.copy()
        
        if not include_sensitive:
            # Mask sensitive data
            if 'bot_token' in result:
                result['bot_token'] = '***' + result['bot_token'][-4:] if result['bot_token'] else None
            if 'telegram_bot_token' in result:
                result['telegram_bot_token'] = '***' + result['telegram_bot_token'][-4:] if result['telegram_bot_token'] else None
        
        return result
    
    def create_env_file(self, file_path: str) -> None:
        """
        Create a .env file with current configuration.
        
        Args:
            file_path: Path to .env file
        """
        env_content = f"""# Telegram Bot Framework Configuration

# Required
BOT_TOKEN={self.data.get('bot_token', 'your_bot_token_here')}
OWNER_USER_ID={self.data.get('owner_user_id', 'your_user_id_here')}

# Optional
ADMIN_USER_IDS={','.join(map(str, self.data.get('admin_user_ids', [])))}
LOG_CHAT_ID={self.data.get('log_chat_id', '')}
DEBUG={str(self.data.get('debug', True)).lower()}
REUSE_CONNECTIONS={str(self.data.get('reuse_connections', True)).lower()}
USE_ASYNC={str(self.data.get('use_async', True)).lower()}
MAX_WORKERS={self.data.get('max_workers', 4)}
INSTANCE_NAME={self.data.get('instance_name', 'TelegramBot')}

# Advanced
PERSISTENCE_BACKEND=sqlite
PLUGINS_DIR=plugins
AUTO_LOAD_PLUGINS=true
"""
        
        with open(file_path, 'w') as f:
            f.write(env_content)
        
        logger.info(f"Created .env file: {file_path}")
    
    @property
    def bot_token(self) -> str:
        """Get bot token."""
        return self.data.get('bot_token') or self.data.get('telegram_bot_token')
    
    @property
    def telegram_bot_token(self) -> str:
        """Get bot token (alias)."""
        return self.bot_token
    
    @property
    def owner_user_id(self) -> int:
        """Get owner user ID."""
        return self.data.get('owner_user_id', 0)
    
    @property
    def admin_user_ids(self) -> List[int]:
        """Get admin user IDs."""
        return self.data.get('admin_user_ids', [])
    
    @property
    def log_chat_id(self) -> Optional[int]:
        """Get log chat ID."""
        return self.data.get('log_chat_id')
    
    @property
    def debug(self) -> bool:
        """Get debug flag."""
        return self.data.get('debug', True)
    
    @property
    def reuse_connections(self) -> bool:
        """Get reuse connections flag."""
        return self.data.get('reuse_connections', True)
    
    @property
    def use_async(self) -> bool:
        """Get async flag."""
        return self.data.get('use_async', True)
    
    @property
    def max_workers(self) -> int:
        """Get max workers."""
        return self.data.get('max_workers', 4)
    
    @property
    def instance_name(self) -> str:
        """Get instance name."""
        return self.data.get('instance_name', 'TelegramBot')
    
    @property
    def connection_pool_size(self) -> int:
        """Get connection pool size."""
        return self.data.get('connection_pool_size', 20)
    
    @property
    def persistence_backend(self) -> str:
        """Get persistence backend."""
        return self.data.get('persistence_backend', 'sqlite')
    
    @property
    def plugins_dir(self) -> Optional[str]:
        """Get plugins directory."""
        return self.data.get('plugins_dir')
    
    @property
    def auto_load_plugins(self) -> bool:
        """Get auto load plugins flag."""
        return self.data.get('auto_load_plugins', True)
    
    @property
    def traceback_chat_id(self) -> Optional[int]:
        """Get traceback chat ID."""
        return self.data.get('traceback_chat_id')
    
    @debug.setter
    def debug(self, value: bool):
        """Set debug flag."""
        self.data['debug'] = value
    
    @reuse_connections.setter
    def reuse_connections(self, value: bool):
        """Set reuse connections flag."""
        self.data['reuse_connections'] = value
    
    @use_async.setter
    def use_async(self, value: bool):
        """Set async flag."""
        self.data['use_async'] = value
    
    @max_workers.setter
    def max_workers(self, value: int):
        """Set max workers."""
        self.data['max_workers'] = value
    
    @instance_name.setter
    def instance_name(self, value: str):
        """Set instance name."""
        self.data['instance_name'] = value
    
    def update(self, **kwargs) -> None:
        """
        Update configuration with new values.
        
        Args:
            **kwargs: Configuration values to update
        """
        for key, value in kwargs.items():
            self.data[key] = value
        
        # Re-validate after update
        self._validate_configuration() 