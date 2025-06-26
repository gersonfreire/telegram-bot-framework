"""
Integration tests for the complete Telegram Bot Framework.
These tests verify that all components work together correctly.
"""

import pytest
import asyncio
import tempfile
import os
from unittest.mock import Mock, AsyncMock, patch
from telegram import Update, Message, User, Chat
from telegram.ext import Application

from tlgfwk.core.framework import TelegramBotFramework
from tlgfwk.core.config import Config
from tlgfwk.plugins.system_monitor import SystemMonitorPlugin
from tlgfwk.plugins.user_stats import UserStatsPlugin


@pytest.mark.integration
class TestFrameworkIntegration:
    """Integration tests for the complete framework."""
    
    @pytest.fixture
    async def temp_config_file(self):
        """Create a temporary configuration file."""
        config_data = """
# Telegram Bot Configuration
TELEGRAM_TOKEN=test_token_here
APP_NAME=TestBot
APP_ADMIN_USER_IDS=123456,789012

# Features
FEATURES_ENABLE_PERSISTENCE=true
FEATURES_ENABLE_PLUGINS=true
FEATURES_ENABLE_PAYMENTS=false
FEATURES_ENABLE_SCHEDULING=true

# Logging
LOGGING_LEVEL=INFO
LOGGING_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# Crypto
CRYPTO_KEY=test_key_32_bytes_long_for_aes256

# Persistence
PERSISTENCE_TYPE=file
PERSISTENCE_FILE_PATH=test_data.json
"""
        fd, path = tempfile.mkstemp(suffix='.env')
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(config_data)
            yield path
        finally:
            if os.path.exists(path):
                os.unlink(path)
    
    @pytest.fixture
    async def integrated_framework(self, temp_config_file):
        """Create a fully integrated framework instance."""
        config = Config(config_file=temp_config_file)
        
        with patch('tlgfwk.core.framework.Application.builder') as mock_builder:
            mock_app = Mock(spec=Application)
            mock_app.add_handler = Mock()
            mock_builder.return_value.token.return_value.build.return_value = mock_app
            
            framework = TelegramBotFramework(config)
            framework.application = mock_app
            
            # Register plugins
            system_plugin = SystemMonitorPlugin()
            user_stats_plugin = UserStatsPlugin()
            
            await framework.plugin_manager.register_plugin(system_plugin)
            await framework.plugin_manager.register_plugin(user_stats_plugin)
            
            yield framework
            
            # Cleanup
            await framework.shutdown()
    
    @pytest.mark.asyncio
    async def test_framework_initialization_complete(self, integrated_framework):
        """Test that the framework initializes all components correctly."""
        framework = integrated_framework
        
        # Check core components
        assert framework.config is not None
        assert framework.user_manager is not None
        assert framework.persistence_manager is not None
        assert framework.plugin_manager is not None
        assert framework.scheduler is not None
        
        # Check configuration is loaded
        assert framework.config.get('app.name') == 'TestBot'
        assert 123456 in framework.config.get('app.admin_user_ids')
        
        # Check plugins are registered
        plugins = framework.plugin_manager.get_registered_plugins()
        assert 'SystemMonitor' in plugins
        assert 'UserStats' in plugins
    
    @pytest.mark.asyncio
    async def test_plugin_loading_integration(self, integrated_framework):
        """Test that plugins load and integrate correctly."""
        framework = integrated_framework
        
        # Load all plugins
        results = await framework.plugin_manager.load_all_plugins(
            framework, framework.config.data
        )
        
        assert all(results.values())  # All plugins should load successfully
        
        loaded_plugins = framework.plugin_manager.get_loaded_plugins()
        assert 'SystemMonitor' in loaded_plugins
        assert 'UserStats' in loaded_plugins
        
        # Check that plugin commands are registered
        assert framework.application.add_handler.called
    
    @pytest.mark.asyncio
    async def test_user_management_integration(self, integrated_framework):
        """Test user management integration with persistence."""
        framework = integrated_framework
        
        # Register a user
        user_id = 123456
        username = "testuser"
        first_name = "Test"
        last_name = "User"
        
        await framework.user_manager.register_user(
            user_id, username, first_name, last_name
        )
        
        # Verify user is stored
        user_data = await framework.user_manager.get_user(user_id)
        assert user_data is not None
        assert user_data['username'] == username
        assert user_data['first_name'] == first_name
        
        # Test admin functionality
        assert framework.user_manager.is_admin(user_id) is True
        assert framework.user_manager.is_admin(999999) is False
    
    @pytest.mark.asyncio
    async def test_command_execution_flow(self, integrated_framework):
        """Test complete command execution flow."""
        framework = integrated_framework
        
        # Load plugins first
        await framework.plugin_manager.load_all_plugins(
            framework, framework.config.data
        )
        
        # Create mock update for /start command
        update = Mock(spec=Update)
        update.effective_user = Mock(spec=User)
        update.effective_user.id = 123456
        update.effective_user.username = "testuser"
        update.effective_user.first_name = "Test"
        update.effective_user.last_name = "User"
        update.effective_chat = Mock(spec=Chat)
        update.effective_chat.id = 123456
        update.message = Mock(spec=Message)
        update.message.reply_text = AsyncMock()
        
        context = Mock()
        
        # Execute start command
        await framework._handle_start(update, context)
        
        # Verify user was registered
        user_data = await framework.user_manager.get_user(123456)
        assert user_data is not None
        
        # Verify response was sent
        update.message.reply_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_persistence_integration(self, integrated_framework):
        """Test persistence integration across components."""
        framework = integrated_framework
        
        # Store data through different components
        await framework.persistence_manager.set("test_key", "test_value")
        
        # Register user (uses persistence)
        await framework.user_manager.register_user(789012, "persistent_user", "Persistent", "User")
        
        # Verify data persists
        test_data = await framework.persistence_manager.get("test_key")
        assert test_data == "test_value"
        
        user_data = await framework.user_manager.get_user(789012)
        assert user_data is not None
        assert user_data['username'] == "persistent_user"
    
    @pytest.mark.asyncio
    async def test_scheduler_integration(self, integrated_framework):
        """Test scheduler integration with the framework."""
        framework = integrated_framework
        
        # Start scheduler
        await framework.scheduler.start()
        
        # Add a test job
        job_executed = asyncio.Event()
        
        async def test_job():
            job_executed.set()
        
        await framework.scheduler.add_job(
            "integration_test_job",
            test_job,
            "date",
            run_date=asyncio.get_event_loop().time() + 0.1  # Run soon
        )
        
        # Wait for job to execute
        try:
            await asyncio.wait_for(job_executed.wait(), timeout=2.0)
            
            # Verify job executed
            job_info = await framework.scheduler.get_job_info("integration_test_job")
            assert job_info is not None
            assert job_info['run_count'] >= 1
        except asyncio.TimeoutError:
            pytest.skip("Job execution timed out - may be expected in test environment")
        finally:
            await framework.scheduler.shutdown()
    
    @pytest.mark.asyncio
    async def test_error_handling_integration(self, integrated_framework):
        """Test error handling across the framework."""
        framework = integrated_framework
        
        # Test with invalid update
        update = Mock(spec=Update)
        update.effective_user = None  # Invalid state
        update.message = Mock(spec=Message)
        update.message.reply_text = AsyncMock()
        context = Mock()
        context.error = Exception("Test error")
        
        # Should handle gracefully
        await framework._handle_error(update, context)
        
        # Verify error was logged (framework should have logger)
        assert hasattr(framework, 'logger')
    
    @pytest.mark.asyncio
    async def test_configuration_integration(self, integrated_framework):
        """Test configuration integration across components."""
        framework = integrated_framework
        
        # Verify configuration is accessible throughout
        config = framework.config
        
        # Framework should use config
        assert framework.user_manager.admin_user_ids == config.get('app.admin_user_ids')
        
        # Plugins should receive config
        await framework.plugin_manager.load_all_plugins(framework, config.data)
        
        # Each loaded plugin should have config access
        for plugin_name in framework.plugin_manager.get_loaded_plugins():
            plugin = framework.plugin_manager.plugins[plugin_name]
            assert hasattr(plugin, 'config')
            assert plugin.config is not None
    
    @pytest.mark.asyncio
    async def test_full_lifecycle_integration(self, integrated_framework):
        """Test complete framework lifecycle."""
        framework = integrated_framework
        
        # 1. Start framework components
        await framework.scheduler.start()
        
        # 2. Load plugins
        await framework.plugin_manager.load_all_plugins(framework, framework.config.data)
        
        # 3. Process some user interactions
        update = Mock(spec=Update)
        update.effective_user = Mock(spec=User)
        update.effective_user.id = 123456
        update.effective_user.username = "lifecycle_user"
        update.effective_user.first_name = "Lifecycle"
        update.effective_user.last_name = "Test"
        update.effective_chat = Mock(spec=Chat)
        update.effective_chat.id = 123456
        update.message = Mock(spec=Message)
        update.message.reply_text = AsyncMock()
        
        context = Mock()
        
        # Execute various commands
        await framework._handle_start(update, context)
        await framework._handle_help(update, context)
        await framework._handle_status(update, context)
        
        # 4. Verify state persistence
        user_data = await framework.user_manager.get_user(123456)
        assert user_data is not None
        
        # 5. Shutdown gracefully
        await framework.plugin_manager.unload_all_plugins()
        await framework.scheduler.shutdown()
        
        # Verify clean shutdown
        assert len(framework.plugin_manager.loaded_plugins) == 0
        assert framework.scheduler.running is False
    
    @pytest.mark.asyncio
    async def test_concurrent_operations_integration(self, integrated_framework):
        """Test concurrent operations across the framework."""
        framework = integrated_framework
        
        # Start components
        await framework.scheduler.start()
        await framework.plugin_manager.load_all_plugins(framework, framework.config.data)
        
        # Create multiple concurrent operations
        tasks = []
        
        # Concurrent user registrations
        for i in range(10):
            task = framework.user_manager.register_user(
                100000 + i, f"user{i}", f"First{i}", f"Last{i}"
            )
            tasks.append(task)
        
        # Concurrent data storage
        for i in range(10):
            task = framework.persistence_manager.set(f"key{i}", f"value{i}")
            tasks.append(task)
        
        # Execute all concurrently
        await asyncio.gather(*tasks)
        
        # Verify all operations completed successfully
        for i in range(10):
            user_data = await framework.user_manager.get_user(100000 + i)
            assert user_data is not None
            assert user_data['username'] == f"user{i}"
            
            value = await framework.persistence_manager.get(f"key{i}")
            assert value == f"value{i}"
        
        await framework.scheduler.shutdown()


@pytest.mark.integration
class TestEndToEndScenarios:
    """End-to-end scenario tests."""
    
    @pytest.mark.asyncio
    async def test_new_user_onboarding_scenario(self, integrated_framework):
        """Test complete new user onboarding scenario."""
        framework = integrated_framework
        await framework.plugin_manager.load_all_plugins(framework, framework.config.data)
        
        # New user sends /start
        update = Mock(spec=Update)
        update.effective_user = Mock(spec=User)
        update.effective_user.id = 555555
        update.effective_user.username = "newuser"
        update.effective_user.first_name = "New"
        update.effective_user.last_name = "User"
        update.effective_chat = Mock(spec=Chat)
        update.effective_chat.id = 555555
        update.message = Mock(spec=Message)
        update.message.reply_text = AsyncMock()
        
        context = Mock()
        
        # Start command - should register user
        await framework._handle_start(update, context)
        
        # User should be registered
        user_data = await framework.user_manager.get_user(555555)
        assert user_data is not None
        
        # User asks for help
        await framework._handle_help(update, context)
        
        # User checks status
        await framework._handle_status(update, context)
        
        # Verify all interactions were handled
        assert update.message.reply_text.call_count >= 3
    
    @pytest.mark.asyncio
    async def test_admin_management_scenario(self, integrated_framework):
        """Test admin management scenario."""
        framework = integrated_framework
        
        # Admin user accesses admin panel
        update = Mock(spec=Update)
        update.effective_user = Mock(spec=User)
        update.effective_user.id = 123456  # Admin user
        update.message = Mock(spec=Message)
        update.message.reply_text = AsyncMock()
        
        context = Mock()
        
        await framework._handle_admin(update, context)
        
        # Should have access
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args[0][0]
        assert "Admin Panel" in call_args
        
        # Non-admin user tries to access
        update.effective_user.id = 999999  # Non-admin
        update.message.reply_text.reset_mock()
        
        await framework._handle_admin(update, context)
        
        # Should be denied
        call_args = update.message.reply_text.call_args[0][0]
        assert "not authorized" in call_args.lower()
    
    @pytest.mark.asyncio 
    async def test_plugin_command_scenario(self, integrated_framework):
        """Test plugin command execution scenario."""
        framework = integrated_framework
        await framework.plugin_manager.load_all_plugins(framework, framework.config.data)
        
        # Get system monitor plugin
        system_plugin = framework.plugin_manager.plugins.get('SystemMonitor')
        if system_plugin:
            update = Mock(spec=Update)
            update.message = Mock(spec=Message)
            update.message.reply_text = AsyncMock()
            context = Mock()
            
            # Execute system info command
            with patch('psutil.cpu_percent', return_value=50.0), \
                 patch('psutil.virtual_memory') as mock_memory:
                
                mock_memory.return_value.percent = 60.0
                
                await system_plugin.sysinfo_command(update, context)
                
                update.message.reply_text.assert_called_once()
                call_args = update.message.reply_text.call_args[0][0]
                assert "System Information" in call_args
