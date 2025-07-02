from functools import wraps
from telegram import Update
from telegram.ext import CallbackContext
from .user_manager import UserManager

def command(name, description, admin_only=False, owner_only=False):
    """
    Decorator to register a command with metadata.

    This decorator attaches metadata to a command handler function,
    which is later used by the framework to register the command,
    generate help messages, and enforce permissions.

    Args:
        name (str): The name of the command (e.g., "start").
        description (str): A brief description of the command.
        admin_only (bool): If True, restricts the command to admins.
        owner_only (bool): If True, restricts the command to the owner.

    Returns:
        function: The decorated function.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, update: Update, context: CallbackContext, *args, **kwargs):
            user_id = update.effective_user.id
            
            if owner_only and not self.user_manager.is_owner(user_id):
                await update.message.reply_text("This command is for the bot owner only.")
                return
            
            if admin_only and not self.user_manager.is_admin(user_id):
                await update.message.reply_text("This command is for admins only.")
                return

            return await func(self, update, context, *args, **kwargs)
        
        # Store metadata in the function object
        wrapper._command_metadata = {
            'name': name,
            'description': description,
            'admin_only': admin_only,
            'owner_only': owner_only
        }
        return wrapper
    return decorator

def admin_required(func):
    """
    Decorator to restrict a command to admin users.
    """
    @wraps(func)
    async def wrapper(self, update: Update, context: CallbackContext, *args, **kwargs):
        user_id = update.effective_user.id
        if not self.user_manager.is_admin(user_id):
            await update.message.reply_text("Sorry, this command is for admins only.")
            return
        return await func(self, update, context, *args, **kwargs)
    return wrapper

def owner_required(func):
    """
    Decorator to restrict a command to the bot owner.
    """
    @wraps(func)
    async def wrapper(self, update: Update, context: CallbackContext, *args, **kwargs):
        user_id = update.effective_user.id
        if not self.user_manager.is_owner(user_id):
            await update.message.reply_text("Sorry, this command is for the bot owner only.")
            return
        return await func(self, update, context, *args, **kwargs)
    return wrapper