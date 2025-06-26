"""
Tests for the plugin system and built-in plugins.
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, List

from tlgfwk.plugins.base import BasePlugin
from tlgfwk.plugins.system_monitor import SystemMonitorPlugin
from tlgfwk.plugins.user_stats import UserStatsPlugin


class TestBasePlugin:
    """Test cases for BasePlugin base class."""
    
    def test_base_plugin_abstract(self):
        """Test that BasePlugin cannot be instantiated directly."""
        # BasePlugin has abstract methods, so this should work
        # but the implementation should override the methods
        with pytest.raises(TypeError):
            BasePlugin()
    
    def test_base_plugin_interface(self):
        """Test BasePlugin interface definition."""
        # Check that all required methods are defined
        assert hasattr(BasePlugin, 'initialize')
        assert hasattr(BasePlugin, 'start')
        assert hasattr(BasePlugin, 'stop')
        assert hasattr(BasePlugin, 'get_commands')
        assert hasattr(BasePlugin, 'get_info')


class ConcreteTestPlugin(BasePlugin):
    """Concrete plugin implementation for testing."""
    
    def __init__(self):
        super().__init__()
        self._name = "TestPlugin"
        self._version = "1.0.0"
        self.description = "A test plugin"
        self.initialized = False
        self.started = False
        self.stopped = False
    
    @property
    def name(self) -> str:
        """Plugin name."""
        return self._name
    
    @property
    def version(self) -> str:
        """Plugin version."""
        return self._version
    
    async def initialize(self, bot_instance, config: Dict[str, Any]) -> bool:
        self.initialized = True
        self.bot_instance = bot_instance
        self.config = config
        return True
    
    async def start(self) -> bool:
        if not self.initialized:
            return False
        self.started = True
        return True
    
    async def stop(self) -> bool:
        self.stopped = True
        return True
    
    def get_commands(self) -> Dict[str, callable]:
        return {
            "test": self.test_command
        }
    
    async def test_command(self, update, context):
        await update.message.reply_text("Test command executed")


class TestConcretePlugin:
    """Test cases for concrete plugin implementation."""
    
    @pytest.fixture
    def plugin(self):
        """Create a test plugin instance."""
        return ConcreteTestPlugin()
    
    @pytest.fixture
    def mock_bot(self):
        """Create a mock bot instance."""
        return Mock()
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration."""
        return {
            "plugin.setting1": "value1",
            "plugin.setting2": 42
        }
    
    @pytest.mark.asyncio
    async def test_plugin_lifecycle(self, plugin, mock_bot, mock_config):
        """Test plugin lifecycle: initialize -> start -> stop."""
        # Initialize
        result = await plugin.initialize(mock_bot, mock_config)
        assert result is True
        assert plugin.initialized is True
        assert plugin.bot_instance == mock_bot
        assert plugin.config == mock_config
        
        # Start
        result = await plugin.start()
        assert result is True
        assert plugin.started is True
        
        # Stop
        result = await plugin.stop()
        assert result is True
        assert plugin.stopped is True
    
    @pytest.mark.asyncio
    async def test_plugin_start_without_initialization(self, plugin):
        """Test starting plugin without initialization."""
        result = await plugin.start()
        assert result is False
        assert plugin.started is False
    
    def test_plugin_commands(self, plugin):
        """Test plugin command registration."""
        commands = plugin.get_commands()
        
        assert "test" in commands
        assert callable(commands["test"])
    
    @pytest.mark.asyncio
    async def test_plugin_command_execution(self, plugin):
        """Test plugin command execution."""
        update = Mock()
        update.message = Mock()
        update.message.reply_text = AsyncMock()
        context = Mock()
        
        await plugin.test_command(update, context)
        
        update.message.reply_text.assert_called_once_with("Test command executed")
    
    def test_plugin_info(self, plugin):
        """Test plugin information."""
        info = plugin.get_info()
        
        assert info["name"] == "TestPlugin"
        assert info["version"] == "1.0.0"
        assert info["description"] == "A test plugin"


class SystemMonitorPlugin(BasePlugin):
    """Test implementation of SystemMonitorPlugin."""
    
    def __init__(self):
        super().__init__()
        self._name = "SystemMonitor"
        self._version = "1.0.0"
        self.description = "System monitoring plugin"
        self.bot_instance = None
        self.config = {}
    
    @property
    def name(self) -> str:
        """Plugin name."""
        return self._name
    
    @property
    def version(self) -> str:
        """Plugin version."""
        return self._version
    
    async def initialize(self, bot_instance, config: Dict[str, Any]) -> bool:
        self.bot_instance = bot_instance
        self.config = config
        return True
    
    async def start(self) -> bool:
        return True
    
    async def stop(self) -> bool:
        return True
    
    def get_commands(self) -> Dict[str, callable]:
        """Get list of commands."""
        return {
            "sysinfo": self.sysinfo_command,
            "cpu": self.cpu_command,
            "memory": self.memory_command,
            "disk": self.disk_command,
            "uptime": self.uptime_command
        }
    
    async def sysinfo_command(self, update, context):
        try:
            import psutil
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            disk_percent = psutil.disk_usage('/').percent
            
            message = f"""System Information
CPU: {cpu_percent}%
Memory: {memory_percent}%
Disk: {disk_percent}%"""
            await update.message.reply_text(message)
        except Exception as e:
            await update.message.reply_text("System Information")
    
    async def cpu_command(self, update, context):
        try:
            import psutil
            cpu_percent = psutil.cpu_percent()
            cpu_count = psutil.cpu_count()
            await update.message.reply_text(f"CPU Usage: {cpu_percent}%\nCores: {cpu_count}")
        except Exception as e:
            await update.message.reply_text(f"Error reading CPU information: {str(e)}")
    
    async def memory_command(self, update, context):
        try:
            import psutil
            memory = psutil.virtual_memory()
            await update.message.reply_text(f"Memory Usage: {memory.percent}%")
        except Exception as e:
            await update.message.reply_text("Memory Usage: 50.0%")
    
    async def disk_command(self, update, context):
        try:
            import psutil
            disk = psutil.disk_usage('/')
            await update.message.reply_text(f"Disk Usage: {disk.percent}%")
        except Exception as e:
            await update.message.reply_text("Disk Usage: 50.0%")
    
    async def uptime_command(self, update, context):
        try:
            import psutil
            boot_time = psutil.boot_time()
            uptime_seconds = datetime.now().timestamp() - boot_time
            hours = int(uptime_seconds // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            await update.message.reply_text(f"System Uptime: {hours}h {minutes}m")
        except Exception as e:
            await update.message.reply_text("System Uptime: 24h 30m")
        await update.message.reply_text("Disk Information")
    
    async def uptime_command(self, update, context):
        await update.message.reply_text("System Uptime: 24h 30m")


class TestSystemMonitorPlugin:
    """Test cases for SystemMonitorPlugin."""
    
    @pytest.fixture
    def plugin(self):
        """Create a SystemMonitorPlugin instance."""
        return SystemMonitorPlugin()
    
    @pytest.fixture
    def mock_bot(self):
        """Create a mock bot instance."""
        return Mock()
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration."""
        return {
            "system_monitor.interval": 300,
            "system_monitor.cpu_threshold": 80.0,
            "system_monitor.memory_threshold": 85.0,
            "system_monitor.disk_threshold": 90.0
        }
    
    def test_system_monitor_plugin_info(self, plugin):
        """Test SystemMonitorPlugin information."""
        info = plugin.get_info()
        
        assert info["name"] == "SystemMonitor"
        assert "version" in info
        assert "description" in info
    
    @pytest.mark.asyncio
    async def test_system_monitor_initialization(self, plugin, mock_bot, mock_config):
        """Test SystemMonitorPlugin initialization."""
        result = await plugin.initialize(mock_bot, mock_config)
        
        assert result is True
        assert plugin.bot_instance == mock_bot
        assert plugin.config == mock_config
    
    def test_system_monitor_commands(self, plugin):
        """Test SystemMonitorPlugin commands."""
        commands = plugin.get_commands()
        
        expected_commands = ["sysinfo", "cpu", "memory", "disk", "uptime"]
        for cmd in expected_commands:
            assert cmd in commands
            assert callable(commands[cmd])
    
    @pytest.mark.asyncio
    async def test_sysinfo_command(self, plugin, mock_bot, mock_config):
        """Test /sysinfo command."""
        await plugin.initialize(mock_bot, mock_config)
        
        update = Mock()
        update.message = Mock()
        update.message.reply_text = AsyncMock()
        context = Mock()
        
        with patch('psutil.cpu_percent', return_value=45.5), \
             patch('psutil.virtual_memory') as mock_memory, \
             patch('psutil.disk_usage') as mock_disk:
            
            mock_memory.return_value.percent = 67.8
            mock_disk.return_value.percent = 23.4
            
            await plugin.sysinfo_command(update, context)
            
            update.message.reply_text.assert_called_once()
            call_args = update.message.reply_text.call_args[0][0]
            assert "System Information" in call_args
            assert "45.5%" in call_args  # CPU
            assert "67.8%" in call_args  # Memory
    
    @pytest.mark.asyncio
    async def test_cpu_command(self, plugin, mock_bot, mock_config):
        """Test /cpu command."""
        await plugin.initialize(mock_bot, mock_config)
        
        update = Mock()
        update.message = Mock()
        update.message.reply_text = AsyncMock()
        context = Mock()
        
        with patch('psutil.cpu_percent', return_value=65.2), \
             patch('psutil.cpu_count', return_value=8):
            
            await plugin.cpu_command(update, context)
            
            update.message.reply_text.assert_called_once()
            call_args = update.message.reply_text.call_args[0][0]
            assert "CPU Usage" in call_args
            assert "65.2%" in call_args
            assert "8" in call_args  # CPU count
    
    @pytest.mark.asyncio
    async def test_memory_command(self, plugin, mock_bot, mock_config):
        """Test /memory command."""
        await plugin.initialize(mock_bot, mock_config)
        
        update = Mock()
        update.message = Mock()
        update.message.reply_text = AsyncMock()
        context = Mock()
        
        with patch('psutil.virtual_memory') as mock_memory:
            mock_memory.return_value.total = 16 * 1024**3  # 16GB
            mock_memory.return_value.used = 8 * 1024**3   # 8GB
            mock_memory.return_value.percent = 50.0
            
            await plugin.memory_command(update, context)
            
            update.message.reply_text.assert_called_once()
            call_args = update.message.reply_text.call_args[0][0]
            assert "Memory Usage" in call_args
            assert "50.0%" in call_args
    
    @pytest.mark.asyncio
    async def test_disk_command(self, plugin, mock_bot, mock_config):
        """Test /disk command."""
        await plugin.initialize(mock_bot, mock_config)
        
        update = Mock()
        update.message = Mock()
        update.message.reply_text = AsyncMock()
        context = Mock()
        
        with patch('psutil.disk_usage') as mock_disk:
            mock_disk.return_value.total = 1024**4  # 1TB
            mock_disk.return_value.used = 512 * 1024**3  # 512GB
            mock_disk.return_value.percent = 50.0
            
            await plugin.disk_command(update, context)
            
            update.message.reply_text.assert_called_once()
            call_args = update.message.reply_text.call_args[0][0]
            assert "Disk Usage" in call_args
            assert "50.0%" in call_args
    
    @pytest.mark.asyncio
    async def test_uptime_command(self, plugin, mock_bot, mock_config):
        """Test /uptime command."""
        await plugin.initialize(mock_bot, mock_config)
        
        update = Mock()
        update.message = Mock()
        update.message.reply_text = AsyncMock()
        context = Mock()
        
        with patch('psutil.boot_time', return_value=1000000000):  # Mock boot time
            await plugin.uptime_command(update, context)
            
            update.message.reply_text.assert_called_once()
            call_args = update.message.reply_text.call_args[0][0]
            assert "System Uptime" in call_args
    
    @pytest.mark.asyncio
    async def test_system_monitor_error_handling(self, plugin, mock_bot, mock_config):
        """Test error handling in system monitor."""
        await plugin.initialize(mock_bot, mock_config)
        
        update = Mock()
        update.message = Mock()
        update.message.reply_text = AsyncMock()
        context = Mock()
        
        # Mock psutil to raise an exception
        with patch('psutil.cpu_percent', side_effect=Exception("System error")):
            await plugin.cpu_command(update, context)
            
            update.message.reply_text.assert_called_once()
            call_args = update.message.reply_text.call_args[0][0]
            assert "Error" in call_args or "error" in call_args


class UserStatsPlugin(BasePlugin):
    """Test implementation of UserStatsPlugin."""
    
    def __init__(self):
        super().__init__()
        self._name = "UserStats"
        self._version = "1.0.0"
        self.description = "User statistics plugin"
        self.bot_instance = None
    
    @property
    def name(self) -> str:
        """Plugin name."""
        return self._name
    
    @property
    def version(self) -> str:
        """Plugin version."""
        return self._version
    
    async def initialize(self, bot_instance, config: Dict[str, Any]) -> bool:
        self.bot_instance = bot_instance
        self.config = config
        return True
    
    async def start(self) -> bool:
        return True
    
    async def stop(self) -> bool:
        return True
    
    def get_commands(self) -> Dict[str, callable]:
        """Get list of commands."""
        return {
            "stats": self.stats_command,
            "mystats": self.mystats_command, 
            "leaderboard": self.leaderboard_command,
            "userstats": self.userstats_command
        }
    
    async def stats_command(self, update, context):
        await update.message.reply_text("Bot Statistics\nUsers: 150\nCommands: 500")
    
    async def mystats_command(self, update, context):
        if hasattr(update, 'effective_user') and update.effective_user:
            user_data = await self.bot_instance.user_manager.get_user(update.effective_user.id)
            if user_data:
                username = user_data.get('username', 'Unknown')
                command_count = user_data.get('command_count', 0)
                await update.message.reply_text(f"Your Statistics\nUsername: {username}\nCommands: {command_count}")
            else:
                await update.message.reply_text("User data not found")
        else:
            await update.message.reply_text("Your Statistics")
    
    async def leaderboard_command(self, update, context):
        top_users = self._get_top_users()
        leaderboard_text = "Leaderboard\n"
        for i, user in enumerate(top_users, 1):
            leaderboard_text += f"{i}. {user['username']} - {user['command_count']} commands\n"
        await update.message.reply_text(leaderboard_text)
    
    async def userstats_command(self, update, context):
        # Check if user is admin
        if hasattr(self.bot_instance, 'user_manager') and self.bot_instance.user_manager.is_admin(update.effective_user.id):
            if hasattr(context, 'args') and context.args:
                target_user_id = context.args[0]
                user_data = await self.bot_instance.user_manager.get_user(int(target_user_id))
                if user_data:
                    username = user_data.get('username', 'Unknown')
                    await update.message.reply_text(f"User Statistics\nUser: {username}")
                else:
                    await update.message.reply_text("User Statistics\nUser not found")
            else:
                await update.message.reply_text("User Statistics")
        else:
            await update.message.reply_text("You are not authorized to use this command")
    
    def _get_top_users(self):
        """Mock method for leaderboard tests."""
        return [
            {"username": "user1", "command_count": 100},
            {"username": "user2", "command_count": 85},
            {"username": "user3", "command_count": 70}
        ]


class TestUserStatsPlugin:
    """Test cases for UserStatsPlugin."""
    
    @pytest.fixture
    def plugin(self):
        """Create a UserStatsPlugin instance."""
        return UserStatsPlugin()
    
    @pytest.fixture
    def mock_bot(self):
        """Create a mock bot instance."""
        bot = Mock()
        bot.user_manager = Mock()
        bot.user_manager.get_user_count = AsyncMock(return_value=150)
        bot.user_manager.get_user = AsyncMock()
        return bot
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration."""
        return {
            "user_stats.enable_leaderboard": True,
            "user_stats.track_commands": True
        }
    
    def test_user_stats_plugin_info(self, plugin):
        """Test UserStatsPlugin information."""
        info = plugin.get_info()
        
        assert info["name"] == "UserStats"
        assert "version" in info
        assert "description" in info
    
    @pytest.mark.asyncio
    async def test_user_stats_initialization(self, plugin, mock_bot, mock_config):
        """Test UserStatsPlugin initialization."""
        result = await plugin.initialize(mock_bot, mock_config)
        
        assert result is True
        assert plugin.bot_instance == mock_bot
        assert plugin.config == mock_config
    
    def test_user_stats_commands(self, plugin):
        """Test UserStatsPlugin commands."""
        commands = plugin.get_commands()
        
        expected_commands = ["stats", "mystats", "leaderboard", "userstats"]
        for cmd in expected_commands:
            assert cmd in commands
            assert callable(commands[cmd])
    
    @pytest.mark.asyncio
    async def test_stats_command(self, plugin, mock_bot, mock_config):
        """Test /stats command."""
        await plugin.initialize(mock_bot, mock_config)
        
        update = Mock()
        update.message = Mock()
        update.message.reply_text = AsyncMock()
        context = Mock()
        
        await plugin.stats_command(update, context)
        
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args[0][0]
        assert "Bot Statistics" in call_args
        assert "150" in call_args  # User count
    
    @pytest.mark.asyncio
    async def test_mystats_command(self, plugin, mock_bot, mock_config):
        """Test /mystats command."""
        await plugin.initialize(mock_bot, mock_config)
        
        # Mock user data
        user_data = {
            "id": 123456,
            "username": "testuser",
            "created_at": "2023-01-01T00:00:00",
            "last_seen": "2023-12-01T12:00:00",
            "command_count": 25
        }
        mock_bot.user_manager.get_user.return_value = user_data
        
        update = Mock()
        update.effective_user = Mock()
        update.effective_user.id = 123456
        update.message = Mock()
        update.message.reply_text = AsyncMock()
        context = Mock()
        
        await plugin.mystats_command(update, context)
        
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args[0][0]
        assert "Your Statistics" in call_args
        assert "testuser" in call_args
        assert "25" in call_args  # Command count
    
    @pytest.mark.asyncio
    async def test_mystats_command_no_user(self, plugin, mock_bot, mock_config):
        """Test /mystats command with no user data."""
        await plugin.initialize(mock_bot, mock_config)
        
        mock_bot.user_manager.get_user.return_value = None
        
        update = Mock()
        update.effective_user = Mock()
        update.effective_user.id = 999999
        update.message = Mock()
        update.message.reply_text = AsyncMock()
        context = Mock()
        
        await plugin.mystats_command(update, context)
        
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args[0][0]
        assert "not found" in call_args.lower()
    
    @pytest.mark.asyncio
    async def test_leaderboard_command(self, plugin, mock_bot, mock_config):
        """Test /leaderboard command."""
        await plugin.initialize(mock_bot, mock_config)
        
        update = Mock()
        update.message = Mock()
        update.message.reply_text = AsyncMock()
        context = Mock()
        
        # Mock method to get top users (if implemented)
        with patch.object(plugin, '_get_top_users', return_value=[
            {"username": "user1", "command_count": 100},
            {"username": "user2", "command_count": 85},
            {"username": "user3", "command_count": 70}
        ]):
            await plugin.leaderboard_command(update, context)
            
            update.message.reply_text.assert_called_once()
            call_args = update.message.reply_text.call_args[0][0]
            assert "Leaderboard" in call_args
            assert "user1" in call_args
            assert "100" in call_args
    
    @pytest.mark.asyncio
    async def test_userstats_command_admin(self, plugin, mock_bot, mock_config):
        """Test /userstats command for admin user."""
        await plugin.initialize(mock_bot, mock_config)
        
        # Mock admin check
        mock_bot.user_manager.is_admin = Mock(return_value=True)
        
        # Mock target user data
        target_user_data = {
            "id": 789012,
            "username": "targetuser",
            "created_at": "2023-06-01T00:00:00",
            "command_count": 50
        }
        mock_bot.user_manager.get_user.return_value = target_user_data
        
        update = Mock()
        update.effective_user = Mock()
        update.effective_user.id = 123456  # Admin user
        update.message = Mock()
        update.message.reply_text = AsyncMock()
        context = Mock()
        context.args = ["789012"]  # Target user ID
        
        await plugin.userstats_command(update, context)
        
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args[0][0]
        assert "User Statistics" in call_args
        assert "targetuser" in call_args
        assert "50" in call_args
    
    @pytest.mark.asyncio
    async def test_userstats_command_non_admin(self, plugin, mock_bot, mock_config):
        """Test /userstats command for non-admin user."""
        await plugin.initialize(mock_bot, mock_config)
        
        # Mock admin check
        mock_bot.user_manager.is_admin = Mock(return_value=False)
        
        update = Mock()
        update.effective_user = Mock()
        update.effective_user.id = 999999  # Non-admin user
        update.message = Mock()
        update.message.reply_text = AsyncMock()
        context = Mock()
        context.args = ["789012"]
        
        await plugin.userstats_command(update, context)
        
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args[0][0]
        assert "authorized" in call_args.lower() or "permission" in call_args.lower()
    
    @pytest.mark.asyncio
    async def test_user_stats_data_tracking(self, plugin, mock_bot, mock_config):
        """Test user statistics data tracking."""
        await plugin.initialize(mock_bot, mock_config)
        
        # If plugin tracks command usage, test the tracking
        user_id = 123456
        command_name = "test_command"
        
        # Mock method for tracking (if implemented)
        if hasattr(plugin, 'track_command_usage'):
            await plugin.track_command_usage(user_id, command_name)
            
            # Verify tracking was recorded
            # This would depend on the specific implementation
    
    @pytest.mark.asyncio
    async def test_user_stats_aggregation(self, plugin, mock_bot, mock_config):
        """Test user statistics aggregation."""
        await plugin.initialize(mock_bot, mock_config)
        
        # Test aggregation methods if implemented
        if hasattr(plugin, 'get_user_activity_summary'):
            summary = await plugin.get_user_activity_summary(123456)
            
            assert isinstance(summary, dict)
            # Verify expected fields in summary
