"""
Data models for user management.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class UserPreferences(BaseModel):
    """User preferences and settings."""
    
    language_code: str = Field(default="en", description="User language preference")
    show_success_logs: bool = Field(default=False, description="Show success notifications")
    enable_notifications: bool = Field(default=True, description="Enable failure notifications")
    timezone: str = Field(default="UTC", description="User timezone")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class User(BaseModel):
    """User model for the bot."""
    
    user_id: int = Field(..., description="Telegram user ID")
    username: Optional[str] = Field(default=None, description="Telegram username")
    first_name: Optional[str] = Field(default=None, description="User first name")
    last_name: Optional[str] = Field(default=None, description="User last name")
    is_admin: bool = Field(default=False, description="Whether user is admin")
    is_owner: bool = Field(default=False, description="Whether user is bot owner")
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True, description="Whether user is active")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
    
    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = datetime.utcnow()
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission."""
        if self.is_owner:
            return True
        if permission == "admin" and self.is_admin:
            return True
        return False 