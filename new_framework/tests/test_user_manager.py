"""
Tests for the UserManager class.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from tlgfwk.core.user_manager import UserManager
from tlgfwk.core.persistence_manager import PersistenceManager


class TestUserManager:
    """Test cases for UserManager."""
    
    @pytest.fixture
    def mock_persistence(self):
        """Create a mock persistence manager."""
        persistence = Mock(spec=PersistenceManager)
        persistence.get = AsyncMock()
        persistence.set = AsyncMock()
        persistence.delete = AsyncMock()
        persistence.exists = AsyncMock()
        return persistence
    
    @pytest.fixture
    def user_manager(self, mock_persistence):
        """Create a UserManager instance for testing."""
        admin_ids = [123456, 789012]
        return UserManager(admin_ids, mock_persistence)
    
    @pytest.mark.asyncio
    async def test_register_user_new(self, user_manager, mock_persistence):
        """Test registering a new user."""
        mock_persistence.exists.return_value = False
        
        user_id = 123456
        username = "testuser"
        first_name = "Test"
        last_name = "User"
        
        await user_manager.register_user(user_id, username, first_name, last_name)
        
        # Check that user was stored
        mock_persistence.set.assert_called_once()
        call_args = mock_persistence.set.call_args
        assert call_args[0][0] == f"user:{user_id}"
        
        user_data = call_args[0][1]
        assert user_data['id'] == user_id
        assert user_data['username'] == username
        assert user_data['first_name'] == first_name
        assert user_data['last_name'] == last_name
        assert 'created_at' in user_data
        assert 'last_seen' in user_data
    
    @pytest.mark.asyncio
    async def test_register_user_existing(self, user_manager, mock_persistence):
        """Test registering an existing user (should update last_seen)."""
        existing_user = {
            'id': 123456,
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'created_at': '2023-01-01T00:00:00',
            'last_seen': '2023-01-01T00:00:00'
        }
        
        mock_persistence.exists.return_value = True
        mock_persistence.get.return_value = existing_user
        
        await user_manager.register_user(123456, "testuser", "Test", "User")
        
        # Should update the existing user
        mock_persistence.set.assert_called_once()
        call_args = mock_persistence.set.call_args
        user_data = call_args[0][1]
        assert user_data['last_seen'] != existing_user['last_seen']
    
    @pytest.mark.asyncio
    async def test_get_user_existing(self, user_manager, mock_persistence):
        """Test getting an existing user."""
        user_data = {
            'id': 123456,
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        mock_persistence.get.return_value = user_data
        
        result = await user_manager.get_user(123456)
        
        assert result == user_data
        mock_persistence.get.assert_called_once_with("user:123456")
    
    @pytest.mark.asyncio
    async def test_get_user_nonexistent(self, user_manager, mock_persistence):
        """Test getting a non-existent user."""
        mock_persistence.get.return_value = None
        
        result = await user_manager.get_user(999999)
        
        assert result is None
    
    def test_is_admin_true(self, user_manager):
        """Test is_admin for admin user."""
        assert user_manager.is_admin(123456) is True
        assert user_manager.is_admin(789012) is True
    
    def test_is_admin_false(self, user_manager):
        """Test is_admin for non-admin user."""
        assert user_manager.is_admin(999999) is False
    
    @pytest.mark.asyncio
    async def test_ban_user(self, user_manager, mock_persistence):
        """Test banning a user."""
        user_data = {
            'id': 123456,
            'username': 'testuser',
            'banned': False
        }
        
        mock_persistence.get.return_value = user_data
        
        await user_manager.ban_user(123456)
        
        mock_persistence.set.assert_called_once()
        call_args = mock_persistence.set.call_args
        updated_user = call_args[0][1]
        assert updated_user['banned'] is True
    
    @pytest.mark.asyncio
    async def test_unban_user(self, user_manager, mock_persistence):
        """Test unbanning a user."""
        user_data = {
            'id': 123456,
            'username': 'testuser',
            'banned': True
        }
        
        mock_persistence.get.return_value = user_data
        
        await user_manager.unban_user(123456)
        
        mock_persistence.set.assert_called_once()
        call_args = mock_persistence.set.call_args
        updated_user = call_args[0][1]
        assert updated_user['banned'] is False
    
    @pytest.mark.asyncio
    async def test_is_banned_true(self, user_manager, mock_persistence):
        """Test is_banned for banned user."""
        user_data = {'banned': True}
        mock_persistence.get.return_value = user_data
        
        result = await user_manager.is_banned(123456)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_is_banned_false(self, user_manager, mock_persistence):
        """Test is_banned for non-banned user."""
        user_data = {'banned': False}
        mock_persistence.get.return_value = user_data
        
        result = await user_manager.is_banned(123456)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_is_banned_no_field(self, user_manager, mock_persistence):
        """Test is_banned for user without banned field."""
        user_data = {'id': 123456}
        mock_persistence.get.return_value = user_data
        
        result = await user_manager.is_banned(123456)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_is_banned_no_user(self, user_manager, mock_persistence):
        """Test is_banned for non-existent user."""
        mock_persistence.get.return_value = None
        
        result = await user_manager.is_banned(999999)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_user_count(self, user_manager, mock_persistence):
        """Test getting user count."""
        # Mock the persistence manager to return a count
        with patch.object(user_manager, '_count_users') as mock_count:
            mock_count.return_value = 42
            
            result = await user_manager.get_user_count()
            
            assert result == 42
    
    @pytest.mark.asyncio
    async def test_update_user_activity(self, user_manager, mock_persistence):
        """Test updating user activity."""
        user_data = {
            'id': 123456,
            'last_seen': '2023-01-01T00:00:00'
        }
        
        mock_persistence.get.return_value = user_data
        
        # Mock datetime.now() to return a fixed date different from the one in user_data
        with patch('tlgfwk.core.user_manager.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2023, 1, 2, 12, 0, 0)
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            await user_manager.update_user_activity(123456)
            
            mock_persistence.set.assert_called_once()
            call_args = mock_persistence.set.call_args
            updated_user = call_args[0][1]
            assert updated_user['last_seen'] != user_data['last_seen']
            assert updated_user['last_seen'] == '2023-01-02T12:00:00'
    
    @pytest.mark.asyncio
    async def test_update_user_activity_no_user(self, user_manager, mock_persistence):
        """Test updating activity for non-existent user."""
        mock_persistence.get.return_value = None
        
        # Should not raise an exception
        await user_manager.update_user_activity(999999)
        
        # Should not attempt to set anything
        mock_persistence.set.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_set_user_permission(self, user_manager, mock_persistence):
        """Test setting user permissions."""
        user_data = {
            'id': 123456,
            'permissions': []
        }
        
        mock_persistence.get.return_value = user_data
        
        await user_manager.set_user_permission(123456, "premium", True)
        
        mock_persistence.set.assert_called_once()
        call_args = mock_persistence.set.call_args
        updated_user = call_args[0][1]
        assert "premium" in updated_user['permissions']
    
    @pytest.mark.asyncio
    async def test_has_permission_true(self, user_manager, mock_persistence):
        """Test has_permission for user with permission."""
        user_data = {
            'permissions': ["premium", "beta"]
        }
        
        mock_persistence.get.return_value = user_data
        
        result = await user_manager.has_permission(123456, "premium")
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_has_permission_false(self, user_manager, mock_persistence):
        """Test has_permission for user without permission."""
        user_data = {
            'permissions': ["beta"]
        }
        
        mock_persistence.get.return_value = user_data
        
        result = await user_manager.has_permission(123456, "premium")
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_has_permission_admin_override(self, user_manager, mock_persistence):
        """Test has_permission for admin user (should always return True)."""
        user_data = {
            'permissions': []
        }
        
        mock_persistence.get.return_value = user_data
        
        # 123456 is an admin user
        result = await user_manager.has_permission(123456, "premium")
        
        assert result is True
