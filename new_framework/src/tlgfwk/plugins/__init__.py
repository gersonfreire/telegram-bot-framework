"""
Plugins Module

This module contains the plugin system and built-in plugins for the Telegram Bot Framework.
"""

from .base import PluginBase
from .system_monitor import SystemMonitorPlugin
from .user_stats import UserStatsPlugin

__all__ = [
    'PluginBase',
    'SystemMonitorPlugin',
    'UserStatsPlugin'
]
