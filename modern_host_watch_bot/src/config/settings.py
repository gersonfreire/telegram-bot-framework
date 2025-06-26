"""
Configuration settings for the Modern Host Watch Bot.
"""
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Bot Configuration
    bot_token: str = Field(..., description="Telegram Bot Token")
    bot_owner_id: int = Field(..., description="Bot owner user ID")
    admin_user_ids: List[int] = Field(default=[], description="Admin user IDs")
    
    # Database Configuration
    database_url: str = Field(default="sqlite:///./bot_data.db", description="Database URL")
    
    # Monitoring Configuration
    min_interval_seconds: int = Field(default=120, description="Minimum interval between checks")
    max_interval_seconds: int = Field(default=2400, description="Maximum interval between checks")
    default_port: int = Field(default=80, description="Default TCP port to check")
    default_ssh_port: int = Field(default=22, description="Default SSH port")
    port_check_timeout: float = Field(default=1.0, description="Port check timeout in seconds")
    max_hosts_per_user: int = Field(default=50, description="Maximum hosts per user")
    max_hosts_per_listing: int = Field(default=50, description="Maximum hosts to show in listing")
    
    # Security Configuration
    encryption_key: str = Field(..., description="Encryption key for credentials")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: str = Field(default="bot.log", description="Log file path")
    
    # Notification Configuration
    enable_notifications: bool = Field(default=True, description="Enable failure notifications")
    notification_cooldown: int = Field(default=300, description="Notification cooldown in seconds")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings() 