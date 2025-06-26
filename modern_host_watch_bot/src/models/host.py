"""
Data models for host monitoring.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator
import ipaddress


class HostConfig(BaseModel):
    """Configuration for a monitored host."""
    
    host_address: str = Field(..., description="Host IP address or domain name")
    interval_seconds: int = Field(..., description="Check interval in seconds")
    port: int = Field(default=80, description="TCP port to check")
    ssh_port: int = Field(default=22, description="SSH port")
    ssh_username: Optional[str] = Field(default=None, description="SSH username")
    ssh_password: Optional[str] = Field(default=None, description="Encrypted SSH password")
    
    @validator('host_address')
    def validate_host_address(cls, v):
        """Validate host address format."""
        try:
            # Try to parse as IP address
            ipaddress.ip_address(v)
        except ValueError:
            # If not IP, assume it's a domain name
            if not v or len(v) > 253:
                raise ValueError("Invalid host address")
        return v
    
    @validator('interval_seconds')
    def validate_interval(cls, v):
        """Validate check interval."""
        from ..config.settings import settings
        if v < settings.min_interval_seconds or v > settings.max_interval_seconds:
            raise ValueError(f"Interval must be between {settings.min_interval_seconds} and {settings.max_interval_seconds} seconds")
        return v
    
    @validator('port', 'ssh_port')
    def validate_port(cls, v):
        """Validate port number."""
        if v < 1 or v > 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v


class HostStatus(BaseModel):
    """Current status of a monitored host."""
    
    host_address: str
    is_online: bool = Field(default=False, description="Host online status")
    port_open: bool = Field(default=False, description="TCP port status")
    last_check: Optional[datetime] = Field(default=None, description="Last check timestamp")
    last_failure: Optional[datetime] = Field(default=None, description="Last failure timestamp")
    response_time_ms: Optional[int] = Field(default=None, description="Response time in milliseconds")
    consecutive_failures: int = Field(default=0, description="Consecutive failure count")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class HostJob(BaseModel):
    """Job configuration for host monitoring."""
    
    job_id: str = Field(..., description="Unique job identifier")
    user_id: int = Field(..., description="User who owns this job")
    host_config: HostConfig = Field(..., description="Host configuration")
    host_status: HostStatus = Field(..., description="Current host status")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True, description="Whether the job is active")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
    
    def update_status(self, status: HostStatus):
        """Update host status and timestamp."""
        self.host_status = status
        self.updated_at = datetime.utcnow()
    
    @property
    def job_name(self) -> str:
        """Get job name for scheduling."""
        return f"ping_{self.host_config.host_address}_{self.user_id}" 