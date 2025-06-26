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
    
    def __init__(self, config_file: Optional[str] = None, **kwargs):
        """
        Initialize configuration.
        
        Args:
            config_file: Path to .env file to load
            **kwargs: Direct configuration values
        """
        self.data: Dict[str, Any] = {}
        self._encryption_key: Optional[bytes] = None
        
        # Load from environment file if provided
        if config_file:
            load_dotenv(config_file)
        
        # Load configuration from environment and kwargs
        self._load_configuration(**kwargs)
        
        # Validate required configuration
        self._validate_configuration()
    
    def _load_configuration(self, **kwargs):
        """Load configuration from environment variables and kwargs."""
        # Telegram configuration
        self.data['telegram.token'] = kwargs.get('bot_token') or os.getenv('TELEGRAM_TOKEN', '')
        
        # App configuration
        self.data['app.name'] = kwargs.get('app_name') or os.getenv('APP_NAME', 'TelegramBot')
        
        # Admin users
        admin_ids = kwargs.get('admin_user_ids') or kwargs.get('owner_user_id')
        if admin_ids is None:
            admin_env = os.getenv('APP_ADMIN_USER_IDS', '')
            if admin_env:
                admin_ids = [int(x.strip()) for x in admin_env.split(',') if x.strip()]
            else:
                admin_ids = []
        elif isinstance(admin_ids, int):
            admin_ids = [admin_ids]
        elif isinstance(admin_ids, str):
            admin_ids = [int(x.strip()) for x in admin_ids.split(',') if x.strip()]
        
        self.data['app.admin_user_ids'] = admin_ids
        
        # Features
        self.data['features.enable_persistence'] = self._parse_bool(
            kwargs.get('enable_persistence', os.getenv('FEATURES_ENABLE_PERSISTENCE', 'true'))
        )
        self.data['features.enable_plugins'] = self._parse_bool(
            kwargs.get('enable_plugins', os.getenv('FEATURES_ENABLE_PLUGINS', 'true'))
        )
        self.data['features.enable_payments'] = self._parse_bool(
            kwargs.get('enable_payments', os.getenv('FEATURES_ENABLE_PAYMENTS', 'false'))
        )
        self.data['features.enable_scheduling'] = self._parse_bool(
            kwargs.get('enable_scheduling', os.getenv('FEATURES_ENABLE_SCHEDULING', 'true'))
        )
        
        # Logging
        self.data['logging.level'] = kwargs.get('log_level') or os.getenv('LOGGING_LEVEL', 'INFO')
        self.data['logging.file'] = kwargs.get('log_file') or os.getenv('LOGGING_FILE')
        self.data['logging.format'] = kwargs.get('log_format') or os.getenv(
            'LOGGING_FORMAT', 
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.data['logging.max_file_size'] = int(
            kwargs.get('log_max_file_size', os.getenv('LOGGING_MAX_FILE_SIZE', '10485760'))
        )  # 10MB default
        self.data['logging.backup_count'] = int(
            kwargs.get('log_backup_count', os.getenv('LOGGING_BACKUP_COUNT', '5'))
        )
        
        # Crypto
        crypto_key = kwargs.get('encryption_key') or os.getenv('CRYPTO_KEY')
        if crypto_key:
            self.data['crypto.key'] = crypto_key
            if isinstance(crypto_key, str):
                # Convert string to bytes for encryption
                if len(crypto_key) == 32:
                    self._encryption_key = crypto_key.encode()
                else:
                    # Derive key from string
                    from cryptography.hazmat.primitives import hashes
                    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
                    kdf = PBKDF2HMAC(
                        algorithm=hashes.SHA256(),
                        length=32,
                        salt=b'telegram_bot_framework',
                        iterations=100000,
                    )
                    self._encryption_key = kdf.derive(crypto_key.encode())
        
        self.data['crypto.algorithm'] = kwargs.get('crypto_algorithm') or os.getenv('CRYPTO_ALGORITHM', 'AES-256-GCM')
        
        # Persistence
        self.data['persistence.type'] = kwargs.get('persistence_type') or os.getenv('PERSISTENCE_TYPE', 'file')
        self.data['persistence.file_path'] = kwargs.get('persistence_file') or os.getenv('PERSISTENCE_FILE_PATH', 'bot_data.json')
        self.data['persistence.database_url'] = kwargs.get('database_url') or os.getenv('DATABASE_URL')
        
        # Payments
        self.data['payments.default_currency'] = kwargs.get('default_currency') or os.getenv('PAYMENTS_DEFAULT_CURRENCY', 'USD')
        self.data['payments.enable_logging'] = self._parse_bool(
            kwargs.get('payment_logging', os.getenv('PAYMENTS_ENABLE_LOGGING', 'true'))
        )
        
        # Plugins
        self.data['plugins.directory'] = kwargs.get('plugins_dir') or os.getenv('PLUGINS_DIRECTORY', 'plugins')
        self.data['plugins.auto_load'] = self._parse_bool(
            kwargs.get('auto_load_plugins', os.getenv('PLUGINS_AUTO_LOAD', 'true'))
        )
        
        # Scheduler
        self.data['scheduler.timezone'] = kwargs.get('timezone') or os.getenv('SCHEDULER_TIMEZONE', 'UTC')
        self.data['scheduler.max_workers'] = int(
            kwargs.get('scheduler_max_workers', os.getenv('SCHEDULER_MAX_WORKERS', '10'))
        )
    
    def _parse_bool(self, value: Union[str, bool]) -> bool:
        """Parse string boolean values."""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return False
    
    def _validate_configuration(self):
        """Validate required configuration values."""
        if not self.data.get('telegram.token'):
            raise ConfigError("Telegram bot token is required")
        
        if not self.data.get('app.admin_user_ids'):
            raise ConfigError("At least one admin user ID is required")
    
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
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Get all configuration as dictionary.
        
        Returns:
            Configuration dictionary
        """
        return self.data.copy()
    
    def update(self, updates: Dict[str, Any]) -> None:
        """
        Update configuration with dictionary.
        
        Args:
            updates: Dictionary of updates
        """
        self.data.update(updates)
    
    # Legacy properties for backward compatibility
    @property
    def bot_token(self) -> str:
        return self.get('telegram.token', '')
    
    @property
    def owner_user_id(self) -> int:
        admin_ids = self.get('app.admin_user_ids', [])
        return admin_ids[0] if admin_ids else 0
    
    @property
    def admin_user_ids(self) -> List[int]:
        return self.get('app.admin_user_ids', [])
    
    @property
    def app_name(self) -> str:
        return self.get('app.name', 'TelegramBot')
    
    @property
    def debug(self) -> bool:
        return self.get('logging.level', 'INFO').upper() == 'DEBUG'
    
    # Configurações de agendamento
    scheduler_timezone: str = "UTC"
    
    # Configurações de pagamento
    stripe_api_key: Optional[str] = None
    paypal_client_id: Optional[str] = None
    paypal_client_secret: Optional[str] = None
    
    # Configurações de rede
    request_timeout: int = 30
    connection_pool_size: int = 20
    
    def __post_init__(self):
        """Validação e processamento pós-inicialização."""
        self._validate_required_fields()
        self._setup_encryption()
    
    def _validate_required_fields(self):
        """Valida campos obrigatórios."""
        if not self.telegram_bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN é obrigatório")
        
        if not self.bot_owner_id:
            raise ValueError("BOT_OWNER_ID é obrigatório")
        
        if not self.admin_ids:
            self.admin_ids = [self.bot_owner_id]
        elif self.bot_owner_id not in self.admin_ids:
            self.admin_ids.append(self.bot_owner_id)
    
    def _setup_encryption(self):
        """Configura sistema de criptografia."""
        if self.encryption_enabled and not self.encryption_key:
            self.encryption_key = self._generate_encryption_key()
    
    def _generate_encryption_key(self) -> str:
        """Gera chave de criptografia."""
        key = Fernet.generate_key()
        return base64.urlsafe_b64encode(key).decode()
    
    def encrypt_value(self, value: str) -> str:
        """Criptografa um valor."""
        if not self.encryption_enabled or not self.encryption_key:
            return value
        
        try:
            key = base64.urlsafe_b64decode(self.encryption_key.encode())
            fernet = Fernet(key)
            return fernet.encrypt(value.encode()).decode()
        except Exception as e:
            logger.warning(f"Erro ao criptografar valor: {e}")
            return value
    
    def decrypt_value(self, encrypted_value: str) -> str:
        """Descriptografa um valor."""
        if not self.encryption_enabled or not self.encryption_key:
            return encrypted_value
        
        try:
            key = base64.urlsafe_b64decode(self.encryption_key.encode())
            fernet = Fernet(key)
            return fernet.decrypt(encrypted_value.encode()).decode()
        except Exception as e:
            logger.warning(f"Erro ao descriptografar valor: {e}")
            return encrypted_value
    
    @classmethod
    def from_env(cls, env_file: Optional[str] = None) -> "Config":
        """Carrega configuração de arquivo .env."""
        if env_file is None:
            env_file = ".env"
        
        # Criar arquivo .env se não existir
        env_path = Path(env_file)
        if not env_path.exists():
            cls._create_empty_env_file(env_path)
        
        # Carregar variáveis de ambiente
        load_dotenv(env_file)
        
        # Extrair configurações
        config_dict = cls._extract_config_from_env()
        
        return cls(**config_dict)
    
    @staticmethod
    def _create_empty_env_file(env_path: Path):
        """Cria arquivo .env vazio com template."""
        template = """# Configurações obrigatórias
TELEGRAM_BOT_TOKEN=
BOT_OWNER_ID=
ADMIN_IDS=

# Configurações opcionais
DEBUG=true
LOG_CHAT_ID=
TRACEBACK_CHAT_ID=
ASYNC_MODE=true
REUSE_CONNECTIONS=true
MAX_NETWORK_WORKERS=4
INSTANCE_NAME=TelegramBot

# Configurações de persistência
PERSISTENCE_BACKEND=pickle
DATABASE_URL=sqlite:///bot_data.db
PERSISTENCE_INTERVAL=5

# Configurações de criptografia
ENCRYPTION_ENABLED=true
ENCRYPTION_KEY=

# Configurações de plugins
PLUGINS_DIR=plugins
AUTO_LOAD_PLUGINS=true

# Configurações de agendamento
SCHEDULER_TIMEZONE=UTC

# Configurações de pagamento
STRIPE_API_KEY=
PAYPAL_CLIENT_ID=
PAYPAL_CLIENT_SECRET=

# Configurações de rede
REQUEST_TIMEOUT=30
CONNECTION_POOL_SIZE=20
"""
        env_path.write_text(template, encoding="utf-8")
        logger.info(f"Arquivo .env criado em {env_path}")
    
    @staticmethod
    def _extract_config_from_env() -> Dict[str, Any]:
        """Extrai configurações das variáveis de ambiente."""
        config = {}
        
        # Configurações obrigatórias
        config["telegram_bot_token"] = os.getenv("TELEGRAM_BOT_TOKEN", "")
        
        bot_owner_id = os.getenv("BOT_OWNER_ID", "0")
        config["bot_owner_id"] = int(bot_owner_id) if bot_owner_id.isdigit() else 0
        
        admin_ids_str = os.getenv("ADMIN_IDS", "")
        config["admin_ids"] = [
            int(id_.strip()) for id_ in admin_ids_str.split(",") 
            if id_.strip().isdigit()
        ]
        
        # Configurações opcionais
        log_chat_id = os.getenv("LOG_CHAT_ID")
        config["log_chat_id"] = int(log_chat_id) if log_chat_id and log_chat_id.isdigit() else None
        
        traceback_chat_id = os.getenv("TRACEBACK_CHAT_ID")
        config["traceback_chat_id"] = int(traceback_chat_id) if traceback_chat_id and traceback_chat_id.isdigit() else None
        
        config["debug"] = os.getenv("DEBUG", "true").lower() == "true"
        config["async_mode"] = os.getenv("ASYNC_MODE", "true").lower() == "true"
        config["reuse_connections"] = os.getenv("REUSE_CONNECTIONS", "true").lower() == "true"
        config["max_network_workers"] = int(os.getenv("MAX_NETWORK_WORKERS", "4"))
        config["instance_name"] = os.getenv("INSTANCE_NAME", "TelegramBot")
        
        # Configurações de persistência
        config["persistence_backend"] = os.getenv("PERSISTENCE_BACKEND", "pickle")
        config["database_url"] = os.getenv("DATABASE_URL", "sqlite:///bot_data.db")
        config["persistence_interval"] = int(os.getenv("PERSISTENCE_INTERVAL", "5"))
        
        # Configurações de criptografia
        config["encryption_enabled"] = os.getenv("ENCRYPTION_ENABLED", "true").lower() == "true"
        config["encryption_key"] = os.getenv("ENCRYPTION_KEY")
        
        # Configurações de plugins
        config["plugins_dir"] = os.getenv("PLUGINS_DIR", "plugins")
        config["auto_load_plugins"] = os.getenv("AUTO_LOAD_PLUGINS", "true").lower() == "true"
        
        # Configurações de agendamento
        config["scheduler_timezone"] = os.getenv("SCHEDULER_TIMEZONE", "UTC")
        
        # Configurações de pagamento
        config["stripe_api_key"] = os.getenv("STRIPE_API_KEY")
        config["paypal_client_id"] = os.getenv("PAYPAL_CLIENT_ID")
        config["paypal_client_secret"] = os.getenv("PAYPAL_CLIENT_SECRET")
        
        # Configurações de rede
        config["request_timeout"] = int(os.getenv("REQUEST_TIMEOUT", "30"))
        config["connection_pool_size"] = int(os.getenv("CONNECTION_POOL_SIZE", "20"))
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte configuração para dicionário."""
        return {
            "telegram_bot_token": "***HIDDEN***" if self.telegram_bot_token else "",
            "bot_owner_id": self.bot_owner_id,
            "admin_ids": self.admin_ids,
            "log_chat_id": self.log_chat_id,
            "traceback_chat_id": self.traceback_chat_id,
            "debug": self.debug,
            "async_mode": self.async_mode,
            "reuse_connections": self.reuse_connections,
            "max_network_workers": self.max_network_workers,
            "instance_name": self.instance_name,
            "persistence_backend": self.persistence_backend,
            "database_url": self.database_url,
            "persistence_interval": self.persistence_interval,
            "encryption_enabled": self.encryption_enabled,
            "encryption_key": "***HIDDEN***" if self.encryption_key else None,
            "plugins_dir": self.plugins_dir,
            "auto_load_plugins": self.auto_load_plugins,
            "scheduler_timezone": self.scheduler_timezone,
            "stripe_api_key": "***HIDDEN***" if self.stripe_api_key else None,
            "paypal_client_id": "***HIDDEN***" if self.paypal_client_id else None,
            "paypal_client_secret": "***HIDDEN***" if self.paypal_client_secret else None,
            "request_timeout": self.request_timeout,
            "connection_pool_size": self.connection_pool_size,
        }
    
    def save_to_env(self, env_file: str = ".env"):
        """Salva configuração no arquivo .env."""
        config_lines = []
        
        # Configurações obrigatórias
        config_lines.append("# Configurações obrigatórias")
        config_lines.append(f"TELEGRAM_BOT_TOKEN={self.telegram_bot_token}")
        config_lines.append(f"BOT_OWNER_ID={self.bot_owner_id}")
        config_lines.append(f"ADMIN_IDS={','.join(map(str, self.admin_ids))}")
        config_lines.append("")
        
        # Configurações opcionais
        config_lines.append("# Configurações opcionais")
        config_lines.append(f"DEBUG={str(self.debug).lower()}")
        config_lines.append(f"LOG_CHAT_ID={self.log_chat_id or ''}")
        config_lines.append(f"TRACEBACK_CHAT_ID={self.traceback_chat_id or ''}")
        config_lines.append(f"ASYNC_MODE={str(self.async_mode).lower()}")
        config_lines.append(f"REUSE_CONNECTIONS={str(self.reuse_connections).lower()}")
        config_lines.append(f"MAX_NETWORK_WORKERS={self.max_network_workers}")
        config_lines.append(f"INSTANCE_NAME={self.instance_name}")
        config_lines.append("")
        
        # Outras configurações...
        config_content = "\n".join(config_lines)
        
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(config_content)
        
        logger.info(f"Configuração salva em {env_file}")
