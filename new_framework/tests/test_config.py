"""
Test Configuration Module

Tests for the configuration management system.
"""

import os
import tempfile
import pytest
from unittest.mock import patch, mock_open

# Add src to path for testing
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tlgfwk.core.config import Config, ConfigError


class TestConfig:
    """Test cases for the Config class."""
    
    def test_config_creation_with_required_params(self):
        """Test creating config with minimum required parameters."""
        config = Config(
            bot_token="test_token",
            owner_user_id=123456789
        )
        
        assert config.bot_token == "test_token"
        assert config.owner_user_id == 123456789
        assert config.admin_user_ids == []
        assert config.debug is True  # Default value
    
    def test_config_creation_with_all_params(self):
        """Test creating config with all parameters."""
        config = Config(
            bot_token="test_token",
            owner_user_id=123456789,
            admin_user_ids=[111, 222, 333],
            log_chat_id=987654321,
            debug=False,
            reuse_connections=False,
            use_async=False,
            max_workers=8,
            instance_name="TestBot"
        )
        
        assert config.bot_token == "test_token"
        assert config.owner_user_id == 123456789
        assert config.admin_user_ids == [111, 222, 333]
        assert config.log_chat_id == 987654321
        assert config.debug is False
        assert config.reuse_connections is False
        assert config.use_async is False
        assert config.max_workers == 8
        assert config.instance_name == "TestBot"
    
    def test_config_validation_missing_token(self):
        """Test validation with missing bot token."""
        with pytest.raises(ConfigError, match="Bot token is required"):
            Config(bot_token="", owner_user_id=123456789)
        
        with pytest.raises(ConfigError, match="Bot token is required"):
            Config(bot_token=None, owner_user_id=123456789)
    
    def test_config_validation_missing_owner(self):
        """Test validation with missing owner user ID."""
        with pytest.raises(ConfigError, match="Owner user ID is required"):
            Config(bot_token="test_token", owner_user_id=0)
        
        with pytest.raises(ConfigError, match="Owner user ID is required"):
            Config(bot_token="test_token", owner_user_id=None)
    
    def test_config_validation_invalid_max_workers(self):
        """Test validation with invalid max_workers."""
        with pytest.raises(ConfigError, match="max_workers must be positive"):
            Config(
                bot_token="test_token",
                owner_user_id=123456789,
                max_workers=0
            )
        
        with pytest.raises(ConfigError, match="max_workers must be positive"):
            Config(
                bot_token="test_token",
                owner_user_id=123456789,
                max_workers=-1
            )
    
    @patch.dict(os.environ, {
        'BOT_TOKEN': 'env_test_token',
        'OWNER_USER_ID': '123456789',
        'ADMIN_USER_IDS': '111,222,333',
        'LOG_CHAT_ID': '987654321',
        'DEBUG': 'false',
        'REUSE_CONNECTIONS': 'false',
        'USE_ASYNC': 'false',
        'MAX_WORKERS': '8',
        'INSTANCE_NAME': 'EnvTestBot'
    })
    def test_config_from_env(self):
        """Test creating config from environment variables."""
        config = Config.from_env()
        
        assert config.bot_token == "env_test_token"
        assert config.owner_user_id == 123456789
        assert config.admin_user_ids == [111, 222, 333]
        assert config.log_chat_id == 987654321
        assert config.debug is False
        assert config.reuse_connections is False
        assert config.use_async is False
        assert config.max_workers == 8
        assert config.instance_name == "EnvTestBot"
    
    @patch.dict(os.environ, {
        'BOT_TOKEN': 'env_test_token',
        'OWNER_USER_ID': '123456789'
    })
    def test_config_from_env_minimal(self):
        """Test creating config from minimal environment variables."""
        config = Config.from_env()
        
        assert config.bot_token == "env_test_token"
        assert config.owner_user_id == 123456789
        assert config.admin_user_ids == []
        assert config.log_chat_id is None
        assert config.debug is True  # Default
    
    def test_config_from_env_missing_required(self):
        """Test creating config from env with missing required vars."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ConfigError, match="BOT_TOKEN environment variable is required"):
                Config.from_env()
        
        with patch.dict(os.environ, {'BOT_TOKEN': 'test'}, clear=True):
            with pytest.raises(ConfigError, match="OWNER_USER_ID environment variable is required"):
                Config.from_env()
    
    def test_config_to_dict(self):
        """Test converting config to dictionary."""
        config = Config(
            bot_token="test_token",
            owner_user_id=123456789,
            admin_user_ids=[111, 222],
            debug=False
        )
        
        config_dict = config.to_dict()
        
        assert config_dict['bot_token'] == "test_token"
        assert config_dict['owner_user_id'] == 123456789
        assert config_dict['admin_user_ids'] == [111, 222]
        assert config_dict['debug'] is False
    
    def test_config_to_dict_exclude_sensitive(self):
        """Test converting config to dict excluding sensitive data."""
        config = Config(
            bot_token="test_token",
            owner_user_id=123456789
        )
        
        config_dict = config.to_dict(include_sensitive=False)
        
        assert 'bot_token' not in config_dict
        assert config_dict['owner_user_id'] == 123456789
    
    def test_config_create_env_file(self):
        """Test creating .env file from config."""
        config = Config(
            bot_token="test_token",
            owner_user_id=123456789,
            admin_user_ids=[111, 222],
            debug=False
        )
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            config.create_env_file(temp_path)
            
            # Read and verify the file
            with open(temp_path, 'r') as f:
                content = f.read()
            
            assert "BOT_TOKEN=test_token" in content
            assert "OWNER_USER_ID=123456789" in content
            assert "ADMIN_USER_IDS=111,222" in content
            assert "DEBUG=false" in content
            
        finally:
            os.unlink(temp_path)
    
    def test_config_validate_token_format(self):
        """Test token format validation."""
        # Valid token format (roughly)
        valid_token = "123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijk"
        config = Config(bot_token=valid_token, owner_user_id=123456789)
        assert config.bot_token == valid_token
        
        # Invalid token format should still work (let Telegram API validate)
        invalid_token = "invalid_token"
        config = Config(bot_token=invalid_token, owner_user_id=123456789)
        assert config.bot_token == invalid_token
    
    def test_config_admin_user_ids_deduplication(self):
        """Test that admin user IDs are deduplicated."""
        config = Config(
            bot_token="test_token",
            owner_user_id=123456789,
            admin_user_ids=[111, 222, 111, 333, 222]  # Duplicates
        )
        
        # Should remove duplicates but preserve order
        assert config.admin_user_ids == [111, 222, 333]
    
    def test_config_owner_in_admin_list(self):
        """Test that owner can be manually added to admin list."""
        # We need to manually add owner to admin list
        admin_list = [111, 222, 123456789]  # Added owner here
        config = Config(
            bot_token="test_token",
            owner_user_id=123456789,
            admin_user_ids=admin_list
        )
        
        # Owner should be in admin list
        assert 123456789 in config.admin_user_ids
        assert config.admin_user_ids == [111, 222, 123456789]
    
    def test_config_update(self):
        """Test updating config values."""
        config = Config(
            bot_token="test_token",
            owner_user_id=123456789
        )
        
        # Update values
        config.debug = False
        config.max_workers = 8
        config.instance_name = "UpdatedBot"
        
        assert config.debug is False
        assert config.max_workers == 8
        assert config.instance_name == "UpdatedBot"
    
    def test_config_copy(self):
        """Test copying config."""
        original = Config(
            bot_token="test_token",
            owner_user_id=123456789,
            admin_user_ids=[111, 222],
            debug=False
        )
        
        # Create copy
        copy = Config(
            bot_token=original.bot_token,
            owner_user_id=original.owner_user_id,
            admin_user_ids=original.admin_user_ids.copy(),
            debug=original.debug
        )
        
        # Verify copy
        assert copy.bot_token == original.bot_token
        assert copy.owner_user_id == original.owner_user_id
        assert copy.admin_user_ids == original.admin_user_ids
        assert copy.debug == original.debug
        
        # Verify independence
        copy.admin_user_ids.append(333)
        assert 333 not in original.admin_user_ids
