"""
Tests for the PluginManager class and plugin system.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any

from tlgfwk.core.plugin_manager import PluginManager
from tlgfwk.plugins.base import PluginBase


class MockPlugin(PluginBase):
    """Mock plugin for testing."""
    
    def __init__(self, name="MockPlugin", version="1.0.0"):
        super().__init__()
        self._name = name
        self._version = version
        self.description = "A mock plugin for testing"
        self.initialized = False
        self.started = False
        self.stopped = False
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def version(self) -> str:
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
            "mock": self.mock_command
        }
    
    async def mock_command(self, update, context):
        """Mock command handler."""
        await update.message.reply_text("Mock command executed")


class FailingPlugin(PluginBase):
    """Plugin that fails during operations."""
    
    def __init__(self, name="FailingPlugin", version="1.0.0"):
        super().__init__()
        self._name = name
        self._version = version
        self.description = "A plugin that fails"
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def version(self) -> str:
        return self._version
    
    async def initialize(self, bot_instance, config: Dict[str, Any]) -> bool:
        raise Exception("Initialization failed")
    
    async def start(self) -> bool:
        raise Exception("Start failed")
    
    async def stop(self) -> bool:
        raise Exception("Stop failed")


class TestPluginManager:
    """Test cases for PluginManager."""
    
    @pytest.fixture
    def plugin_manager(self):
        """Create a PluginManager instance."""
        return PluginManager()
    
    @pytest.fixture
    def mock_bot(self):
        """Create a mock bot instance."""
        bot = Mock()
        bot.add_command_handler = Mock()
        return bot
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration."""
        return {
            "plugin.enable_all": True,
            "plugin.mock_setting": "test_value"
        }
    
    def test_initialization(self, plugin_manager):
        """Test PluginManager initialization."""
        assert plugin_manager.plugins == {}
        assert plugin_manager.loaded_plugins == []
    
    @pytest.mark.asyncio
    async def test_register_plugin_success(self, plugin_manager):
        """Test successful plugin registration."""
        plugin = MockPlugin()
        
        result = await plugin_manager.register_plugin("MockPlugin", plugin)
        
        assert result is True
        assert "MockPlugin" in plugin_manager.plugins
        assert plugin_manager.plugins["MockPlugin"].instance == plugin
    
    @pytest.mark.asyncio
    async def test_register_plugin_duplicate(self, plugin_manager):
        """Test registering duplicate plugin."""
        plugin1 = MockPlugin()
        plugin2 = MockPlugin()
        
        await plugin_manager.register_plugin("MockPlugin", plugin1)
        result = await plugin_manager.register_plugin("MockPlugin", plugin2)
        
        assert result is False
        assert plugin_manager.plugins["MockPlugin"].instance == plugin1  # Original should remain
    
    @pytest.mark.asyncio
    async def test_unregister_plugin_success(self, plugin_manager):
        """Test successful plugin unregistration."""
        plugin = MockPlugin()
        await plugin_manager.register_plugin("MockPlugin", plugin)
        
        result = await plugin_manager.unregister_plugin("MockPlugin")
        
        assert result is True
        assert "MockPlugin" not in plugin_manager.plugins
    
    @pytest.mark.asyncio
    async def test_unregister_plugin_not_found(self, plugin_manager):
        """Test unregistering non-existent plugin."""
        result = await plugin_manager.unregister_plugin("NonExistentPlugin")
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_load_plugin_success(self, plugin_manager, mock_bot, mock_config):
        """Test successful plugin loading."""
        plugin = MockPlugin()
        await plugin_manager.register_plugin("MockPlugin", plugin)
        
        result = await plugin_manager.load_plugin("MockPlugin", mock_bot, mock_config)
        
        assert result is True
        assert "MockPlugin" in plugin_manager.loaded_plugins
        assert plugin.initialized is True
    
    @pytest.mark.asyncio
    async def test_load_plugin_not_registered(self, plugin_manager, mock_bot, mock_config):
        """Test loading non-registered plugin."""
        result = await plugin_manager.load_plugin("NonExistentPlugin", mock_bot, mock_config)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_load_plugin_initialization_failure(self, plugin_manager, mock_bot, mock_config):
        """Test loading plugin that fails initialization."""
        plugin = FailingPlugin()
        await plugin_manager.register_plugin("FailingPlugin", plugin)
        
        result = await plugin_manager.load_plugin("FailingPlugin", mock_bot, mock_config)
        
        assert result is False
        assert "FailingPlugin" not in plugin_manager.loaded_plugins
    
    @pytest.mark.asyncio
    async def test_unload_plugin_success(self, plugin_manager, mock_bot, mock_config):
        """Test successful plugin unloading."""
        plugin = MockPlugin()
        await plugin_manager.register_plugin("MockPlugin", plugin)
        await plugin_manager.load_plugin("MockPlugin", mock_bot, mock_config)
        
        result = await plugin_manager.unload_plugin("MockPlugin")
        
        assert result is True
        assert "MockPlugin" not in plugin_manager.loaded_plugins
    
    @pytest.mark.asyncio
    async def test_unload_plugin_not_loaded(self, plugin_manager):
        """Test unloading non-loaded plugin."""
        plugin = MockPlugin()
        await plugin_manager.register_plugin("MockPlugin", plugin)
        
        result = await plugin_manager.unload_plugin("MockPlugin")
        
        assert result is True  # Unloading non-loaded plugin is considered successful
    
    @pytest.mark.asyncio
    async def test_load_all_plugins(self, plugin_manager, mock_bot, mock_config):
        """Test loading all registered plugins."""
        plugin1 = MockPlugin(name="Plugin1")
        plugin2 = MockPlugin(name="Plugin2")
        
        await plugin_manager.register_plugin("Plugin1", plugin1)
        await plugin_manager.register_plugin("Plugin2", plugin2)
        
        results = await plugin_manager.load_all_plugins(mock_bot, mock_config)
        
        assert len(results) == 2
        assert all(results.values())
        assert "Plugin1" in plugin_manager.loaded_plugins
        assert "Plugin2" in plugin_manager.loaded_plugins
    
    @pytest.mark.asyncio
    async def test_unload_all_plugins(self, plugin_manager, mock_bot, mock_config):
        """Test unloading all loaded plugins."""
        plugin1 = MockPlugin(name="Plugin1")
        plugin2 = MockPlugin(name="Plugin2")
        
        await plugin_manager.register_plugin("Plugin1", plugin1)
        await plugin_manager.register_plugin("Plugin2", plugin2)
        await plugin_manager.load_plugin("Plugin1", mock_bot, mock_config)
        await plugin_manager.load_plugin("Plugin2", mock_bot, mock_config)
        
        results = await plugin_manager.unload_all_plugins()
        
        assert len(results) == 2
        assert all(results.values())
        assert len(plugin_manager.loaded_plugins) == 0
    
    def test_get_loaded_plugins(self, plugin_manager):
        """Test getting list of loaded plugins."""
        plugin_manager.loaded_plugins = ["Plugin1", "Plugin2"]
        
        result = plugin_manager.get_loaded_plugins()
        
        assert result == ["Plugin1", "Plugin2"]
    
    def test_get_registered_plugins(self, plugin_manager):
        """Test getting list of registered plugins."""
        plugin1 = MockPlugin(name="Plugin1")
        plugin2 = MockPlugin(name="Plugin2")
        
        plugin_manager.plugins["Plugin1"] = plugin1
        plugin_manager.plugins["Plugin2"] = plugin2
        
        result = plugin_manager.get_registered_plugins()
        
        assert "Plugin1" in result
        assert "Plugin2" in result
    
    @pytest.mark.asyncio
    async def test_get_plugin_info(self, plugin_manager):
        """Test getting plugin information."""
        plugin = MockPlugin()
        await plugin_manager.register_plugin("MockPlugin", plugin)
        
        info = plugin_manager.get_plugin_info("MockPlugin")
        
        assert info is not None
        assert info["name"] == "MockPlugin"
        assert info["version"] == "1.0.0"
        assert info["description"] == "A mock plugin for testing"
        assert info["status"] == "unloaded"
    
    @pytest.mark.asyncio
    async def test_get_plugin_info_loaded(self, plugin_manager, mock_bot, mock_config):
        """Test getting info for loaded plugin."""
        plugin = MockPlugin()
        await plugin_manager.register_plugin("MockPlugin", plugin)
        await plugin_manager.load_plugin("MockPlugin", mock_bot, mock_config)
        
        info = plugin_manager.get_plugin_info("MockPlugin")
        
        assert info["status"] == "loaded"
    
    @pytest.mark.asyncio
    async def test_get_plugin_info_not_found(self, plugin_manager):
        """Test getting info for non-existent plugin."""
        info = plugin_manager.get_plugin_info("NonExistentPlugin")
        
        assert info is None
    
    @pytest.mark.asyncio
    async def test_plugin_command_registration(self, plugin_manager, mock_bot, mock_config):
        """Test that plugin commands are registered with the bot."""
        plugin = MockPlugin()
        await plugin_manager.register_plugin("MockPlugin", plugin)
        await plugin_manager.load_plugin("MockPlugin", mock_bot, mock_config)
        
        # Should have registered the mock command
        mock_bot.add_command_handler.assert_called()
    
    @pytest.mark.asyncio
    async def test_plugin_error_handling(self, plugin_manager, mock_bot, mock_config):
        """Test error handling during plugin operations."""
        plugin = FailingPlugin()
        await plugin_manager.register_plugin("FailingPlugin", plugin)
        
        # Should handle initialization failure gracefully
        result = await plugin_manager.load_plugin("FailingPlugin", mock_bot, mock_config)
        assert result is False
        
        # Plugin should not be in loaded list
        assert "FailingPlugin" not in plugin_manager.loaded_plugins
    
    @pytest.mark.asyncio
    async def test_plugin_dependencies(self, plugin_manager):
        """Test plugin dependency handling (if implemented)."""
        # This test would verify dependency resolution
        # For now, it's a placeholder for future dependency system
        
        plugin = MockPlugin()
        await plugin_manager.register_plugin("MockPlugin", plugin)
        
        # Could test that dependencies are loaded first
        # assert plugin_manager.resolve_dependencies("MockPlugin") == []
    
    @pytest.mark.asyncio
    async def test_plugin_config_isolation(self, plugin_manager, mock_bot):
        """Test that plugins receive isolated configuration."""
        plugin = MockPlugin()
        await plugin_manager.register_plugin("MockPlugin", plugin)
        
        config = {
            "plugin.mock_setting": "plugin_value",
            "global.setting": "global_value"
        }
        
        await plugin_manager.load_plugin("MockPlugin", mock_bot, config)
        
        # Plugin should receive the full config
        assert plugin.config == config
    
    @pytest.mark.asyncio
    async def test_plugin_lifecycle_events(self, plugin_manager, mock_bot, mock_config):
        """Test plugin lifecycle events."""
        plugin = MockPlugin()
        await plugin_manager.register_plugin("MockPlugin", plugin)
        
        # Test initialization
        await plugin_manager.load_plugin("MockPlugin", mock_bot, mock_config)
        assert plugin.initialized is True
        assert plugin.started is True
        
        # Test shutdown
        await plugin_manager.unload_plugin("MockPlugin")
        assert plugin.stopped is True
    
    @pytest.mark.asyncio
    async def test_concurrent_plugin_operations(self, plugin_manager, mock_bot, mock_config):
        """Test concurrent plugin loading/unloading."""
        plugins = []
        for i in range(5):
            plugin = MockPlugin(name=f"Plugin{i}")
            plugins.append(plugin)
            await plugin_manager.register_plugin(f"Plugin{i}", plugin)
        
        # Load all plugins concurrently
        load_tasks = [
            plugin_manager.load_plugin(f"Plugin{i}", mock_bot, mock_config)
            for i in range(5)
        ]
        
        results = await asyncio.gather(*load_tasks)
        
        assert all(results)
        assert len(plugin_manager.loaded_plugins) == 5
        
        # Unload all plugins concurrently
        unload_tasks = [
            plugin_manager.unload_plugin(f"Plugin{i}")
            for i in range(5)
        ]
        
        results = await asyncio.gather(*unload_tasks)
        
        assert all(results)
        assert len(plugin_manager.loaded_plugins) == 0
