"""
User management for the Telegram Bot Framework.
"""

import asyncio
from typing import Optional, List, Dict, Any
from telegram import User
from datetime import datetime


class UserData:
    """User data model."""
    
    def __init__(self, user_id: int, username: str = None, first_name: str = None, 
                 last_name: str = None, is_admin: bool = False, is_owner: bool = False):
        self.user_id = user_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.is_admin = is_admin
        self.is_owner = is_owner
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.data = {}
    
    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = datetime.now()


class UserManager:
    """User management system."""
    
    def __init__(self, config, persistence_manager=None):
        self.config = config
        self.persistence_manager = persistence_manager
        self._users: Dict[int, UserData] = {}
        self._load_users()
    
    def _load_users(self):
        """Load users from persistence or create default."""
        # Create owner user
        owner_id = self.config.owner_user_id
        if owner_id:
            self._users[owner_id] = UserData(
                user_id=owner_id,
                username="owner",
                first_name="Owner",
                is_owner=True
            )
        
        # Add admin users
        for admin_id in self.config.admin_user_ids:
            if admin_id not in self._users:
                self._users[admin_id] = UserData(
                    user_id=admin_id,
                    username="admin",
                    first_name="Admin",
                    is_admin=True
                )
    
    async def register_user(self, user: User) -> UserData:
        """Register a new user."""
        user_id = user.id
        
        if user_id not in self._users:
            # Check if user should be admin/owner
            is_admin = user_id in self.config.admin_user_ids
            is_owner = user_id == self.config.owner_user_id
            
            user_data = UserData(
                user_id=user_id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                is_admin=is_admin,
                is_owner=is_owner
            )
            
            self._users[user_id] = user_data
        
        else:
            # Update existing user
            user_data = self._users[user_id]
            user_data.username = user.username
            user_data.first_name = user.first_name
            user_data.last_name = user.last_name
            user_data.update_activity()
        
        return self._users[user_id]
    
    async def get_user(self, user_id: int) -> Optional[UserData]:
        """Get user by ID."""
        return self._users.get(user_id)
    
    async def get_all_users(self) -> List[UserData]:
        """Get all registered users."""
        return list(self._users.values())
    
    async def is_admin(self, user_id: int) -> bool:
        """Check if user is admin."""
        # Checa diretamente na config
        return user_id in self.config.admin_user_ids
    
    async def is_owner(self, user_id: int) -> bool:
        """Check if user is owner."""
        # Checa diretamente na config
        return user_id == self.config.owner_user_id 