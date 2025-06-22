"""
Tests for data models.
"""
import pytest
from datetime import datetime
from src.models.host import HostConfig, HostStatus, HostJob
from src.models.user import User, UserPreferences


class TestHostConfig:
    """Test HostConfig model."""
    
    def test_valid_host_config(self):
        """Test creating valid host config."""
        config = HostConfig(
            host_address="192.168.1.1",
            interval_seconds=300,
            port=80
        )
        
        assert config.host_address == "192.168.1.1"
        assert config.interval_seconds == 300
        assert config.port == 80
        assert config.ssh_port == 22  # default
    
    def test_valid_domain_name(self):
        """Test host config with domain name."""
        config = HostConfig(
            host_address="example.com",
            interval_seconds=300
        )
        
        assert config.host_address == "example.com"
    
    def test_invalid_host_address(self):
        """Test invalid host address."""
        with pytest.raises(ValueError):
            HostConfig(
                host_address="",
                interval_seconds=300
            )
    
    def test_invalid_interval(self):
        """Test invalid interval."""
        with pytest.raises(ValueError):
            HostConfig(
                host_address="192.168.1.1",
                interval_seconds=60  # too low
            )
    
    def test_invalid_port(self):
        """Test invalid port."""
        with pytest.raises(ValueError):
            HostConfig(
                host_address="192.168.1.1",
                interval_seconds=300,
                port=70000  # invalid port
            )


class TestHostStatus:
    """Test HostStatus model."""
    
    def test_host_status_creation(self):
        """Test creating host status."""
        status = HostStatus(
            host_address="192.168.1.1",
            is_online=True,
            port_open=True,
            response_time_ms=50
        )
        
        assert status.host_address == "192.168.1.1"
        assert status.is_online is True
        assert status.port_open is True
        assert status.response_time_ms == 50
        assert status.consecutive_failures == 0
    
    def test_host_status_defaults(self):
        """Test host status defaults."""
        status = HostStatus(host_address="192.168.1.1")
        
        assert status.is_online is False
        assert status.port_open is False
        assert status.response_time_ms is None
        assert status.consecutive_failures == 0


class TestHostJob:
    """Test HostJob model."""
    
    def test_host_job_creation(self):
        """Test creating host job."""
        config = HostConfig(
            host_address="192.168.1.1",
            interval_seconds=300
        )
        status = HostStatus(host_address="192.168.1.1")
        
        job = HostJob(
            job_id="test-job-123",
            user_id=123456,
            host_config=config,
            host_status=status
        )
        
        assert job.job_id == "test-job-123"
        assert job.user_id == 123456
        assert job.host_config == config
        assert job.host_status == status
        assert job.is_active is True
    
    def test_job_name_property(self):
        """Test job name property."""
        config = HostConfig(
            host_address="192.168.1.1",
            interval_seconds=300
        )
        status = HostStatus(host_address="192.168.1.1")
        
        job = HostJob(
            job_id="test-job-123",
            user_id=123456,
            host_config=config,
            host_status=status
        )
        
        expected_name = f"ping_192.168.1.1_123456"
        assert job.job_name == expected_name
    
    def test_update_status(self):
        """Test updating job status."""
        config = HostConfig(
            host_address="192.168.1.1",
            interval_seconds=300
        )
        status = HostStatus(host_address="192.168.1.1")
        
        job = HostJob(
            job_id="test-job-123",
            user_id=123456,
            host_config=config,
            host_status=status
        )
        
        old_updated_at = job.updated_at
        
        new_status = HostStatus(
            host_address="192.168.1.1",
            is_online=True,
            port_open=True
        )
        
        job.update_status(new_status)
        
        assert job.host_status == new_status
        assert job.updated_at > old_updated_at


class TestUser:
    """Test User model."""
    
    def test_user_creation(self):
        """Test creating user."""
        preferences = UserPreferences(
            language_code="en",
            show_success_logs=True
        )
        
        user = User(
            user_id=123456,
            username="testuser",
            first_name="Test",
            last_name="User",
            is_admin=False,
            is_owner=False,
            preferences=preferences
        )
        
        assert user.user_id == 123456
        assert user.username == "testuser"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.is_admin is False
        assert user.is_owner is False
        assert user.preferences == preferences
        assert user.is_active is True
    
    def test_user_permissions(self):
        """Test user permissions."""
        # Regular user
        user = User(
            user_id=123456,
            username="testuser"
        )
        
        assert user.has_permission("admin") is False
        
        # Admin user
        admin_user = User(
            user_id=123456,
            username="admin",
            is_admin=True
        )
        
        assert admin_user.has_permission("admin") is True
        
        # Owner user
        owner_user = User(
            user_id=123456,
            username="owner",
            is_owner=True
        )
        
        assert owner_user.has_permission("admin") is True
        assert owner_user.has_permission("any_permission") is True
    
    def test_update_activity(self):
        """Test updating user activity."""
        user = User(
            user_id=123456,
            username="testuser"
        )
        
        old_activity = user.last_activity
        user.update_activity()
        
        assert user.last_activity > old_activity


class TestUserPreferences:
    """Test UserPreferences model."""
    
    def test_preferences_defaults(self):
        """Test user preferences defaults."""
        preferences = UserPreferences()
        
        assert preferences.language_code == "en"
        assert preferences.show_success_logs is False
        assert preferences.enable_notifications is True
        assert preferences.timezone == "UTC"
    
    def test_custom_preferences(self):
        """Test custom user preferences."""
        preferences = UserPreferences(
            language_code="pt",
            show_success_logs=True,
            enable_notifications=False,
            timezone="America/Sao_Paulo"
        )
        
        assert preferences.language_code == "pt"
        assert preferences.show_success_logs is True
        assert preferences.enable_notifications is False
        assert preferences.timezone == "America/Sao_Paulo" 