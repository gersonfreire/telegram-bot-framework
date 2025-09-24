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
        self.data['telegram.token'] = bot_token  # For compatibility
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
        if not self.data.get('telegram.token'):
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
        
        # Check for required environment variables
        bot_token = os.getenv('BOT_TOKEN')
        if not bot_token:
            raise ConfigError("BOT_TOKEN environment variable is required")
        
        owner_user_id_str = os.getenv('OWNER_USER_ID')
        if not owner_user_id_str:
            raise ConfigError("OWNER_USER_ID environment variable is required")
        
        try:
            owner_user_id = int(owner_user_id_str)
        except ValueError:
            raise ConfigError(f"OWNER_USER_ID must be an integer: {owner_user_id_str}")
        
        # Parse admin user IDs if available
        admin_user_ids = []
        admin_ids_str = os.getenv('ADMIN_USER_IDS')
        if admin_ids_str and admin_ids_str.strip():
            try:
                admin_user_ids = [int(x.strip()) for x in admin_ids_str.split(',') if x.strip()]
            except ValueError:
                raise ConfigError("ADMIN_USER_IDS must be comma-separated integers")
        
        # Parse log chat ID if available
        log_chat_id = None
        log_chat_id_str = os.getenv('LOG_CHAT_ID')
        if log_chat_id_str and log_chat_id_str.strip():
            try:
                log_chat_id = int(log_chat_id_str)
            except ValueError:
                raise ConfigError(f"LOG_CHAT_ID must be an integer: {log_chat_id_str}")
        
        # Parse boolean values
        debug = cls._parse_env_bool('DEBUG', default=True)
        reuse_connections = cls._parse_env_bool('REUSE_CONNECTIONS', default=True)
        use_async = cls._parse_env_bool('USE_ASYNC', default=True)
        
        # Parse integer values
        max_workers = cls._parse_env_int('MAX_WORKERS', default=4)
        
        # Parse string values
        instance_name = os.getenv('INSTANCE_NAME', 'TelegramBot')
        
        # Create and return config instance - don't add owner to admin list automatically
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
    def _parse_env_bool(key: str, default: bool = False) -> bool:
        """Parse boolean environment variable."""
        value = os.getenv(key)
        if value is None:
            return default
        return value.lower() in ('true', '1', 'yes', 'on', 't', 'y')
    
    @staticmethod
    def _parse_env_int(key: str, default: int = 0) -> int:
        """Parse integer environment variable."""
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            return default
    
    def to_dict(self, include_sensitive: bool = True) -> Dict[str, Any]:
        """
        Convert config to dictionary.
        
        Args:
            include_sensitive: Whether to include sensitive data like tokens
            
        Returns:
            Dictionary representation of the config
        """
        result = {
            'bot_token': self.bot_token,
            'owner_user_id': self.owner_user_id,
            'admin_user_ids': self.admin_user_ids,
            'log_chat_id': self.log_chat_id,
            'debug': self.debug,
            'reuse_connections': self.reuse_connections,
            'use_async': self.use_async,
            'max_workers': self.max_workers,
            'instance_name': self.instance_name
        }
        
        if not include_sensitive:
            # Remove sensitive keys
            result.pop('bot_token', None)
        
        return result
    
    def create_env_file(self, file_path: str) -> None:
        """
        Create an .env file from this configuration.
        
        Args:
            file_path: Path to write .env file to
        """
        lines = []
        
        # Add basic configuration
        lines.append("# Telegram Bot Framework Configuration")
        lines.append(f"BOT_TOKEN={self.bot_token}")
        lines.append(f"OWNER_USER_ID={self.owner_user_id}")
        
        if self.admin_user_ids:
            lines.append(f"ADMIN_USER_IDS={','.join(str(uid) for uid in self.admin_user_ids)}")
        
        if self.log_chat_id:
            lines.append(f"LOG_CHAT_ID={self.log_chat_id}")
        
        lines.append(f"DEBUG={str(self.debug).lower()}")
        lines.append(f"REUSE_CONNECTIONS={str(self.reuse_connections).lower()}")
        lines.append(f"USE_ASYNC={str(self.use_async).lower()}")
        lines.append(f"MAX_WORKERS={self.max_workers}")
        lines.append(f"INSTANCE_NAME={self.instance_name}")
        
        # Write the file
        with open(file_path, 'w') as f:
            f.write('\n'.join(lines))
    
    # Property getters
    @property
    def bot_token(self) -> str:
        """Get the bot token."""
        return self.data.get('telegram.token', '')
    
    @property
    def owner_user_id(self) -> int:
        """Get the owner user ID."""
        return self.data.get('owner_user_id', 0)
    
    @property
    def admin_user_ids(self) -> List[int]:
        """Get the admin user IDs."""
        return self.data.get('admin_user_ids', [])
    
    @property
    def admin_ids(self) -> List[int]:
        """Get the admin user IDs (alias for admin_user_ids)."""
        return self.admin_user_ids
    
    @property
    def log_chat_id(self) -> Optional[int]:
        """Get the log chat ID."""
        return self.data.get('log_chat_id')
    
    @property
    def debug(self) -> bool:
        """Get the debug mode flag."""
        return self.data.get('debug', True)
    
    @property
    def reuse_connections(self) -> bool:
        """Get the reuse connections flag."""
        return self.data.get('reuse_connections', True)
    
    @property
    def use_async(self) -> bool:
        """Get the use async flag."""
        return self.data.get('use_async', True)
    
    @property
    def max_workers(self) -> int:
        """Get the maximum number of workers."""
        return self.data.get('max_workers', 4)
    
    @property
    def instance_name(self) -> str:
        """Get the instance name."""
        return self.data.get('instance_name', 'TelegramBot')
    
    @property
    def telegram_bot_token(self):
        return self.bot_token
    
    @property
    def connection_pool_size(self):
        return self.data.get('connection_pool_size', 20)
    
    @property
    def persistence_backend(self):
        return self.data.get('persistence_backend', 'none')
    
    @property
    def plugins_dir(self):
        return self.data.get('plugins_dir', 'plugins')
    
    @property
    def auto_load_plugins(self):
        return self.data.get('auto_load_plugins', True)
    
    @property
    def traceback_chat_id(self):
        return self.data.get('traceback_chat_id')
    
    # Property setters
    @debug.setter
    def debug(self, value: bool):
        """Set the debug mode flag."""
        self.data['debug'] = value
    
    @reuse_connections.setter
    def reuse_connections(self, value: bool):
        """Set the reuse connections flag."""
        self.data['reuse_connections'] = value
    
    @use_async.setter
    def use_async(self, value: bool):
        """Set the use async flag."""
        self.data['use_async'] = value
    
    @max_workers.setter
    def max_workers(self, value: int):
        """Set the maximum number of workers."""
        if value <= 0:
            raise ConfigError("max_workers must be positive")
        self.data['max_workers'] = value
    
    @instance_name.setter
    def instance_name(self, value: str):
        """Set the instance name."""
        self.data['instance_name'] = value or "TelegramBot"
    
    # Update method
    def update(self, **kwargs) -> None:
        """
        Update multiple configuration values.
        
        Args:
            **kwargs: Configuration values to update
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
