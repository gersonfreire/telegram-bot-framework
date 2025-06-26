"""
Tests for decorators module.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from telegram import Update, Message, User, Chat

from tlgfwk.core.decorators import (
    command, admin_required, user_required, rate_limit,
    log_execution, validate_args, permission_required
)


class TestCommandDecorator:
    """Test cases for @command decorator."""
    
    @pytest.fixture
    def mock_framework(self):
        """Create a mock framework instance."""
        framework = Mock()
        framework.add_command_handler = Mock()
        return framework
    
    def test_command_decorator_basic(self, mock_framework):
        """Test basic command decorator functionality."""
        @command("test", framework=mock_framework)
        async def test_command(update, context):
            return "executed"
        
        # Should register the command with the framework
        mock_framework.add_command_handler.assert_called_once()
        call_args = mock_framework.add_command_handler.call_args
        assert call_args[0][0] == "test"  # Command name
    
    def test_command_decorator_with_description(self, mock_framework):
        """Test command decorator with description."""
        @command("test", description="A test command", framework=mock_framework)
        async def test_command(update, context):
            return "executed"
        
        mock_framework.add_command_handler.assert_called_once()
        # Description might be stored in the handler or metadata
    
    def test_command_decorator_aliases(self, mock_framework):
        """Test command decorator with aliases."""
        @command(["test", "t"], framework=mock_framework)
        async def test_command(update, context):
            return "executed"
        
        # Should register multiple commands
        assert mock_framework.add_command_handler.call_count >= 1


class TestAdminRequired:
    """Test cases for @admin_required decorator."""
    
    @pytest.fixture
    def mock_user_manager(self):
        """Create a mock user manager."""
        user_manager = Mock()
        user_manager.is_admin = Mock()
        return user_manager
    
    @pytest.mark.asyncio
    async def test_admin_required_authorized(self, mock_user_manager):
        """Test admin_required with authorized user."""
        mock_user_manager.is_admin.return_value = True
        
        @admin_required(mock_user_manager)
        async def admin_function(update, context):
            return "admin_executed"
        
        # Mock update object
        update = Mock(spec=Update)
        update.effective_user = Mock(spec=User)
        update.effective_user.id = 123456
        context = Mock()
        
        result = await admin_function(update, context)
        
        assert result == "admin_executed"
        mock_user_manager.is_admin.assert_called_once_with(123456)
    
    @pytest.mark.asyncio
    async def test_admin_required_unauthorized(self, mock_user_manager):
        """Test admin_required with unauthorized user."""
        mock_user_manager.is_admin.return_value = False
        
        @admin_required(mock_user_manager)
        async def admin_function(update, context):
            return "admin_executed"
        
        update = Mock(spec=Update)
        update.effective_user = Mock(spec=User)
        update.effective_user.id = 999999
        update.message = Mock(spec=Message)
        update.message.reply_text = AsyncMock()
        context = Mock()
        
        result = await admin_function(update, context)
        
        # Should send unauthorized message
        update.message.reply_text.assert_called_once()
        mock_user_manager.is_admin.assert_called_once_with(999999)
        assert result is None  # Should not execute original function
    
    @pytest.mark.asyncio
    async def test_admin_required_no_user(self, mock_user_manager):
        """Test admin_required with no user in update."""
        @admin_required(mock_user_manager)
        async def admin_function(update, context):
            return "admin_executed"
        
        update = Mock(spec=Update)
        update.effective_user = None
        update.message = Mock(spec=Message)
        update.message.reply_text = AsyncMock()
        context = Mock()
        
        result = await admin_function(update, context)
        
        # Should handle gracefully
        update.message.reply_text.assert_called_once()
        assert result is None


class TestUserRequired:
    """Test cases for @user_required decorator."""
    
    @pytest.fixture
    def mock_user_manager(self):
        """Create a mock user manager."""
        user_manager = Mock()
        user_manager.is_banned = AsyncMock()
        user_manager.register_user = AsyncMock()
        user_manager.update_user_activity = AsyncMock()
        return user_manager
    
    @pytest.mark.asyncio
    async def test_user_required_valid_user(self, mock_user_manager):
        """Test user_required with valid user."""
        mock_user_manager.is_banned.return_value = False
        
        @user_required(mock_user_manager)
        async def user_function(update, context):
            return "user_executed"
        
        update = Mock(spec=Update)
        update.effective_user = Mock(spec=User)
        update.effective_user.id = 123456
        update.effective_user.username = "testuser"
        update.effective_user.first_name = "Test"
        update.effective_user.last_name = "User"
        context = Mock()
        
        result = await user_function(update, context)
        
        assert result == "user_executed"
        mock_user_manager.is_banned.assert_called_once_with(123456)
        mock_user_manager.register_user.assert_called_once()
        mock_user_manager.update_user_activity.assert_called_once_with(123456)
    
    @pytest.mark.asyncio
    async def test_user_required_banned_user(self, mock_user_manager):
        """Test user_required with banned user."""
        mock_user_manager.is_banned.return_value = True
        
        @user_required(mock_user_manager)
        async def user_function(update, context):
            return "user_executed"
        
        update = Mock(spec=Update)
        update.effective_user = Mock(spec=User)
        update.effective_user.id = 123456
        update.message = Mock(spec=Message)
        update.message.reply_text = AsyncMock()
        context = Mock()
        
        result = await user_function(update, context)
        
        # Should send banned message
        update.message.reply_text.assert_called_once()
        assert result is None


class TestRateLimit:
    """Test cases for @rate_limit decorator."""
    
    @pytest.mark.asyncio
    async def test_rate_limit_within_limit(self):
        """Test rate limit within allowed calls."""
        call_count = {"count": 0}
        
        @rate_limit(max_calls=3, window=60)
        async def limited_function(update, context):
            call_count["count"] += 1
            return "executed"
        
        update = Mock(spec=Update)
        update.effective_user = Mock(spec=User)
        update.effective_user.id = 123456
        context = Mock()
        
        # First call should succeed
        result = await limited_function(update, context)
        assert result == "executed"
        assert call_count["count"] == 1
    
    @pytest.mark.asyncio
    async def test_rate_limit_exceeded(self):
        """Test rate limit when exceeded."""
        @rate_limit(max_calls=1, window=60)
        async def limited_function(update, context):
            return "executed"
        
        update = Mock(spec=Update)
        update.effective_user = Mock(spec=User)
        update.effective_user.id = 123456
        update.message = Mock(spec=Message)
        update.message.reply_text = AsyncMock()
        context = Mock()
        
        # First call should succeed
        result1 = await limited_function(update, context)
        assert result1 == "executed"
        
        # Second call should be rate limited
        result2 = await limited_function(update, context)
        assert result2 is None
        update.message.reply_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_rate_limit_different_users(self):
        """Test rate limit with different users."""
        @rate_limit(max_calls=1, window=60)
        async def limited_function(update, context):
            return "executed"
        
        # User 1
        update1 = Mock(spec=Update)
        update1.effective_user = Mock(spec=User)
        update1.effective_user.id = 123456
        context1 = Mock()
        
        # User 2
        update2 = Mock(spec=Update)
        update2.effective_user = Mock(spec=User)
        update2.effective_user.id = 789012
        context2 = Mock()
        
        # Both should succeed (different users)
        result1 = await limited_function(update1, context1)
        result2 = await limited_function(update2, context2)
        
        assert result1 == "executed"
        assert result2 == "executed"


class TestLogExecution:
    """Test cases for @log_execution decorator."""
    
    @pytest.mark.asyncio
    async def test_log_execution_success(self):
        """Test log_execution with successful execution."""
        mock_logger = Mock()
        
        @log_execution(mock_logger)
        async def logged_function(update, context):
            return "success"
        
        update = Mock(spec=Update)
        update.effective_user = Mock(spec=User)
        update.effective_user.id = 123456
        context = Mock()
        
        result = await logged_function(update, context)
        
        assert result == "success"
        # Should log start and completion
        assert mock_logger.info.call_count >= 2
    
    @pytest.mark.asyncio
    async def test_log_execution_exception(self):
        """Test log_execution with exception."""
        mock_logger = Mock()
        
        @log_execution(mock_logger)
        async def failing_function(update, context):
            raise ValueError("Test error")
        
        update = Mock(spec=Update)
        update.effective_user = Mock(spec=User)
        update.effective_user.id = 123456
        context = Mock()
        
        with pytest.raises(ValueError):
            await failing_function(update, context)
        
        # Should log error
        mock_logger.error.assert_called_once()


class TestValidateArgs:
    """Test cases for @validate_args decorator."""
    
    @pytest.mark.asyncio
    async def test_validate_args_success(self):
        """Test validate_args with valid arguments."""
        def validator(args):
            return len(args) >= 2 and args[0].isdigit()
        
        @validate_args(validator, "Usage: /command <number> <text>")
        async def validated_function(update, context):
            return "valid"
        
        update = Mock(spec=Update)
        update.message = Mock(spec=Message)
        context = Mock()
        context.args = ["123", "test"]
        
        result = await validated_function(update, context)
        
        assert result == "valid"
    
    @pytest.mark.asyncio
    async def test_validate_args_failure(self):
        """Test validate_args with invalid arguments."""
        def validator(args):
            return len(args) >= 2 and args[0].isdigit()
        
        @validate_args(validator, "Usage: /command <number> <text>")
        async def validated_function(update, context):
            return "valid"
        
        update = Mock(spec=Update)
        update.message = Mock(spec=Message)
        update.message.reply_text = AsyncMock()
        context = Mock()
        context.args = ["invalid"]
        
        result = await validated_function(update, context)
        
        assert result is None
        update.message.reply_text.assert_called_once()


class TestPermissionRequired:
    """Test cases for @permission_required decorator."""
    
    @pytest.fixture
    def mock_user_manager(self):
        """Create a mock user manager."""
        user_manager = Mock()
        user_manager.has_permission = AsyncMock()
        return user_manager
    
    @pytest.mark.asyncio
    async def test_permission_required_granted(self, mock_user_manager):
        """Test permission_required with granted permission."""
        mock_user_manager.has_permission.return_value = True
        
        @permission_required("premium", mock_user_manager)
        async def premium_function(update, context):
            return "premium_executed"
        
        update = Mock(spec=Update)
        update.effective_user = Mock(spec=User)
        update.effective_user.id = 123456
        context = Mock()
        
        result = await premium_function(update, context)
        
        assert result == "premium_executed"
        mock_user_manager.has_permission.assert_called_once_with(123456, "premium")
    
    @pytest.mark.asyncio
    async def test_permission_required_denied(self, mock_user_manager):
        """Test permission_required with denied permission."""
        mock_user_manager.has_permission.return_value = False
        
        @permission_required("premium", mock_user_manager)
        async def premium_function(update, context):
            return "premium_executed"
        
        update = Mock(spec=Update)
        update.effective_user = Mock(spec=User)
        update.effective_user.id = 123456
        update.message = Mock(spec=Message)
        update.message.reply_text = AsyncMock()
        context = Mock()
        
        result = await premium_function(update, context)
        
        assert result is None
        update.message.reply_text.assert_called_once()
        mock_user_manager.has_permission.assert_called_once_with(123456, "premium")


class TestDecoratorChaining:
    """Test cases for combining multiple decorators."""
    
    @pytest.fixture
    def mock_user_manager(self):
        """Create a mock user manager."""
        user_manager = Mock()
        user_manager.is_admin = Mock(return_value=True)
        user_manager.is_banned = AsyncMock(return_value=False)
        user_manager.register_user = AsyncMock()
        user_manager.update_user_activity = AsyncMock()
        user_manager.has_permission = AsyncMock(return_value=True)
        return user_manager
    
    @pytest.mark.asyncio
    async def test_multiple_decorators(self, mock_user_manager):
        """Test combining multiple decorators."""
        mock_logger = Mock()
        
        @log_execution(mock_logger)
        @admin_required(mock_user_manager)
        @user_required(mock_user_manager)
        async def multi_decorated_function(update, context):
            return "all_checks_passed"
        
        update = Mock(spec=Update)
        update.effective_user = Mock(spec=User)
        update.effective_user.id = 123456
        update.effective_user.username = "admin"
        update.effective_user.first_name = "Admin"
        update.effective_user.last_name = "User"
        context = Mock()
        
        result = await multi_decorated_function(update, context)
        
        assert result == "all_checks_passed"
        
        # All checks should have been performed
        mock_user_manager.is_admin.assert_called_once()
        mock_user_manager.is_banned.assert_called_once()
        mock_logger.info.assert_called()
    
    @pytest.mark.asyncio
    async def test_decorator_order_matters(self, mock_user_manager):
        """Test that decorator order affects execution."""
        # If admin check fails first, user check shouldn't be called
        mock_user_manager.is_admin.return_value = False
        
        @admin_required(mock_user_manager)
        @user_required(mock_user_manager)
        async def ordered_function(update, context):
            return "should_not_execute"
        
        update = Mock(spec=Update)
        update.effective_user = Mock(spec=User)
        update.effective_user.id = 999999
        update.message = Mock(spec=Message)
        update.message.reply_text = AsyncMock()
        context = Mock()
        
        result = await ordered_function(update, context)
        
        assert result is None
        mock_user_manager.is_admin.assert_called_once()
        # user_required decorators shouldn't be called due to admin failure
        mock_user_manager.is_banned.assert_not_called()
