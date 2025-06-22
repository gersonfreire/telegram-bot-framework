"""
Data models for Modern Host Watch Bot.
"""

from .host import HostConfig, HostStatus, HostJob
from .user import User, UserPreferences

__all__ = [
    "HostConfig",
    "HostStatus", 
    "HostJob",
    "User",
    "UserPreferences"
] 