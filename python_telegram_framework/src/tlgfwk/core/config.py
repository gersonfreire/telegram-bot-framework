import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet, InvalidToken
import logging

# Configure logging
logger = logging.getLogger(__name__)

class ConfigError(Exception):
    """Custom exception for configuration errors."""
    pass

class Config:
    """
    Manages bot configuration, loading from .env files, handling encryption,
    and validating necessary parameters.

    This class is responsible for:
    - Loading environment variables from a specified .env file.
    - Generating and managing an encryption key for sensitive data.
    - Automatically creating a default .env file if one doesn't exist.
    - Decrypting sensitive values like the bot token.
    - Validating that all required configuration parameters are present.

    Attributes:
        env_file (str): The path to the .env file.
        key_file (str): The path to the file storing the encryption key.
        cipher_suite (Fernet): The Fernet instance for encryption/decryption.
        bot_token (str): The Telegram bot token.
        owner_id (int): The Telegram user ID of the bot owner.
        admin_ids (list[int]): A list of Telegram user IDs for bot administrators.
        log_chat_id (int, optional): The chat ID for sending general logs.
        traceback_chat_id (int, optional): The chat ID for sending error tracebacks.
        debug_mode (bool): A flag to enable or disable debug mode.
    """
    def __init__(self, env_file='.env', key_file='secret.key'):
        """
        Initializes the Config object.

        Args:
            env_file (str): The path to the .env file. Defaults to '.env'.
            key_file (str): The path to the encryption key file. Defaults to 'secret.key'.
        """
        self.env_file = env_file
        self.key_file = key_file
        self.cipher_suite = self._load_key()
        self._create_env_if_not_exists()
        load_dotenv(dotenv_path=self.env_file)
        self._load_config()

    def _load_key(self):
        """Loads the encryption key or generates a new one."""
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
        return Fernet(key)

    def _create_env_if_not_exists(self):
        """Creates an empty .env file if it doesn't exist."""
        if not os.path.exists(self.env_file):
            with open(self.env_file, 'w') as f:
                f.write("# Telegram Bot Configuration\n")
                f.write("BOT_TOKEN=\n")
                f.write("OWNER_ID=\n")
                f.write("ADMIN_IDS=\n")
                f.write("LOG_CHAT_ID=\n")
                f.write("TRACEBACK_CHAT_ID=\n")
            logger.info(f"Created a new .env file at {self.env_file}")

    def _load_config(self):
        """Loads and validates configuration from environment variables."""
        self.bot_token = self._get_decrypted('BOT_TOKEN')
        self.owner_id = self._get_int('OWNER_ID')
        self.admin_ids = self._get_int_list('ADMIN_IDS')
        self.log_chat_id = self._get_int('LOG_CHAT_ID', required=False)
        self.traceback_chat_id = self._get_int('TRACEBACK_CHAT_ID', required=False)
        self.debug_mode = self._get_bool('DEBUG_MODE', default=True)
        self.use_https = self._get_bool('USE_HTTPS', default=True)
        self.num_workers = self._get_int('NUM_WORKERS', default=4)
        self.instance_name = os.getenv('INSTANCE_NAME', 'default-instance')

        if not self.bot_token:
            raise ConfigError("BOT_TOKEN is a required configuration.")
        if not self.owner_id:
            raise ConfigError("OWNER_ID is a required configuration.")

    def _get_decrypted(self, key, required=True):
        """Gets a value from .env and decrypts it."""
        value = os.getenv(key)
        if not value:
            if required:
                raise ConfigError(f"{key} is a required configuration.")
            return None
        try:
            return self.cipher_suite.decrypt(value.encode()).decode()
        except (InvalidToken, TypeError):
            # Assume it's not encrypted if decryption fails
            return value

    def _get_int(self, key, required=True, default=None):
        """Gets an integer value from .env."""
        value = os.getenv(key)
        if not value:
            if required:
                raise ConfigError(f"{key} is a required configuration.")
            return default
        try:
            return int(value)
        except ValueError:
            raise ConfigError(f"Configuration {key} must be an integer.")

    def _get_int_list(self, key, required=True, default=None):
        """Gets a comma-separated list of integers from .env."""
        value = os.getenv(key)
        if not value:
            if required:
                return default or []
            return default or []
        try:
            return [int(item.strip()) for item in value.split(',')]
        except ValueError:
            raise ConfigError(f"Configuration {key} must be a comma-separated list of integers.")

    def _get_bool(self, key, default=False):
        """Gets a boolean value from .env."""
        value = os.getenv(key, str(default)).lower()
        return value in ['true', '1', 't', 'y', 'yes']

    def set(self, key, value):
        """Sets a configuration value and saves it to the .env file."""
        # For simplicity, this example doesn't write back to the .env file.
        # A more robust implementation would update the file.
        setattr(self, key.lower(), value)
        logger.info(f"Configuration {key} set to {value} in memory.")

    def encrypt_and_save(self, key, plain_text):
        """Encrypts a value and suggests how to save it to .env."""
        encrypted_value = self.cipher_suite.encrypt(plain_text.encode()).decode()
        logger.info(f"Add this to your .env file: {key}={encrypted_value}")
        return encrypted_value