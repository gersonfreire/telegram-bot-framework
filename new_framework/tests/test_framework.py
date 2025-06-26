"""
Tests for the main TelegramBotFramework class.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from telegram import Update, Message, User, Chat
from telegram.ext import Application

from tlgfwk.core.framework import TelegramBotFramework
from tlgfwk.core.config import Config


class TestTelegramBotFramework:
    """Test cases for TelegramBotFramework."""
    
    @pytest.fixture
    async def mock_config(self):
        """Create a mock config for testing."""
        config = Mock(spec=Config)
        config.get.side_effect = lambda key, default=None: {
            'telegram.token': 'test_token',
            'app.name': 'TestBot',
            'app.admin_user_ids': [123456],
            'logging.level': 'INFO',
            'logging.format': '%(levelname)s - %(message)s',
            'features.enable_persistence': True,
            'features.enable_plugins': True,
            'features.enable_payments': False,
            'features.enable_scheduling': True,
            'plugins.plugin_dir': 'plugins'
        }.get(key, default)
        # Add direct property access
        config.plugins_dir = 'plugins'
        config.instance_name = 'TestBot'
        return config
    
    @pytest.fixture
    async def framework(self, mock_config):
        """Create a framework instance for testing."""
        with patch('tlgfwk.core.framework.Application.builder') as mock_builder:
            mock_app = Mock(spec=Application)
            mock_builder.return_value.token.return_value.build.return_value = mock_app
            
            fw = TelegramBotFramework(custom_config=mock_config)
            fw.application = mock_app
            return fw
    
    def test_initialization(self, mock_config):
        """Test framework initialization."""
        with patch('tlgfwk.core.framework.Application.builder') as mock_builder:
            mock_app = Mock()
            mock_app_builder = Mock()
            mock_app_builder.token.return_value = mock_app_builder  # Return self for chaining
            mock_app_builder.build.return_value = mock_app
            mock_builder.return_value = mock_app_builder
            
            fw = TelegramBotFramework(custom_config=mock_config)
            
            assert fw.config == mock_config
            assert fw.application == mock_app
            assert fw.user_manager is not None
            assert fw.persistence_manager is None  # Not initialized in constructor
            assert fw.plugin_manager is not None
            assert fw.scheduler is not None
    
    @pytest.mark.asyncio
    async def test_start_command(self, framework):
        """Test /start command handler."""
        update = Mock(spec=Update)
        context = Mock()
        update.effective_user = Mock(spec=User)
        update.effective_user.id = 123456
        update.effective_user.username = "testuser"
        update.effective_chat = Mock(spec=Chat)
        update.effective_chat.id = 123456
        update.message = Mock(spec=Message)
        update.message.reply_text = AsyncMock()
        
        # Mock user manager
        framework.user_manager.register_user = AsyncMock()
        framework.user_manager.is_admin = Mock(return_value=True)
        
        await framework._handle_start(update, context)
        
        framework.user_manager.register_user.assert_called_once()
        update.message.reply_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_help_command(self, framework):
        """Test /help command handler."""
        update = Mock(spec=Update)
        context = Mock()
        update.message = Mock(spec=Message)
        update.message.reply_text = AsyncMock()
        
        await framework._handle_help(update, context)
        
        update.message.reply_text.assert_called_once()
        args, kwargs = update.message.reply_text.call_args
        assert "Available commands:" in args[0]
    
    @pytest.mark.asyncio
    async def test_admin_command_authorized(self, framework):
        """Test /admin command with authorized user."""
        update = Mock(spec=Update)
        context = Mock()
        update.effective_user = Mock(spec=User)
        update.effective_user.id = 123456  # Admin user
        update.message = Mock(spec=Message)
        update.message.reply_text = AsyncMock()
        
        framework.user_manager.is_admin = Mock(return_value=True)
        
        await framework._handle_admin(update, context)
        
        update.message.reply_text.assert_called_once()
        args, kwargs = update.message.reply_text.call_args
        assert "Admin Panel" in args[0]
    
    @pytest.mark.asyncio
    async def test_admin_command_unauthorized(self, framework):
        """Test /admin command with unauthorized user."""
        update = Mock(spec=Update)
        context = Mock()
        update.effective_user = Mock(spec=User)
        update.effective_user.id = 999999  # Non-admin user
        update.message = Mock(spec=Message)
        update.message.reply_text = AsyncMock()
        
        framework.user_manager.is_admin = Mock(return_value=False)
        
        await framework._handle_admin(update, context)
        
        update.message.reply_text.assert_called_once()
        args, kwargs = update.message.reply_text.call_args
        assert "not authorized" in args[0].lower()
    
    @pytest.mark.asyncio
    async def test_status_command(self, framework):
        """Test /status command."""
        update = Mock(spec=Update)
        context = Mock()
        update.message = Mock(spec=Message)
        update.message.reply_text = AsyncMock()
        
        framework.user_manager.get_user_count = AsyncMock(return_value=10)
        framework.plugin_manager.get_loaded_plugins = Mock(return_value=['plugin1', 'plugin2'])
        
        await framework._handle_status(update, context)
        
        update.message.reply_text.assert_called_once()
        args, kwargs = update.message.reply_text.call_args
        assert "Status" in args[0]
        assert "10" in args[0]  # User count
    
    @pytest.mark.asyncio
    async def test_error_handler(self, framework):
        """Test error handling."""
        update = Mock(spec=Update)
        context = Mock()
        context.error = Exception("Test error")
        update.message = Mock(spec=Message)
        update.message.reply_text = AsyncMock()
        
        with patch.object(framework, 'logger') as mock_logger:
            await framework._handle_error(update, context)
            mock_logger.error.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_run_method(self, framework):
        """Test the run method."""
        framework.application.run_polling = AsyncMock()
        framework.scheduler.start = AsyncMock()
        framework.logger = Mock()
        
        await framework.run()
        
        framework.scheduler.start.assert_called_once()
        framework.application.run_polling.assert_called_once()
    
    def test_add_command_handler(self, framework):
        """Test adding custom command handlers."""
        mock_handler = Mock()
        framework.application.add_handler = Mock()
        
        framework.add_command_handler("test", mock_handler)
        
        framework.application.add_handler.assert_called_once()
    
    def test_register_decorator(self, framework):
        """Test command registration via decorator."""
        framework.application.add_handler = Mock()
        
        @framework.command("test")
        async def test_command(update, context):
            pass
        
        framework.application.add_handler.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_shutdown(self, framework):
        """Test framework shutdown."""
        framework.application.stop = AsyncMock()
        framework.application.shutdown = AsyncMock()
        framework.scheduler.shutdown = AsyncMock()
        framework.persistence_manager.close = AsyncMock()
        framework.logger = Mock()
        
        await framework.shutdown()
        
        framework.scheduler.shutdown.assert_called_once()
        framework.persistence_manager.close.assert_called_once()
        framework.application.stop.assert_called_once()
        framework.application.shutdown.assert_called_once()
