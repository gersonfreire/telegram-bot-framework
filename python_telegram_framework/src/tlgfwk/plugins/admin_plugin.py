import logging
from telegram import Update
from telegram.ext import ContextTypes
from tlgfwk.core.decorators import command
from tlgfwk.core.plugin_manager import BasePlugin

logger = logging.getLogger(__name__)

class AdminPlugin(BasePlugin):
    """
    A plugin for administrative commands, restricted to the bot owner.
    """

    @command("config", description="View or update bot configuration.", owner_only=True)
    async def config_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handles the /config command.
        Usage: /config [KEY] [VALUE]
        """
        args = context.args
        if len(args) == 0:
            # Display current (non-sensitive) configuration
            config_data = {k: v for k, v in self.framework.config.__dict__.items() if k != 'bot_token' and not k.endswith('_key')}
            message = "Current Configuration:\n" + "\n".join(f"`{key}`: `{value}`" for key, value in config_data.items())
            await update.message.reply_text(message, parse_mode='Markdown')
        elif len(args) == 2:
            key, value = args[0].upper(), args[1]
            try:
                self.framework.config.set(key, value)
                await update.message.reply_text(f"Configuration `{key}` updated successfully.", parse_mode='Markdown')
            except Exception as e:
                await update.message.reply_text(f"Error updating configuration: {e}")
        else:
            await update.message.reply_text("Usage: `/config` or `/config KEY VALUE`", parse_mode='Markdown')

    @command("add_admin", description="Add a new administrator.", owner_only=True)
    async def add_admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handles the /add_admin command.
        Usage: /add_admin <user_id>
        """
        if not context.args or not context.args[0].isdigit():
            await update.message.reply_text("Usage: `/add_admin <user_id>`", parse_mode='Markdown')
            return

        user_id = int(context.args[0])
        if self.framework.user_manager.add_admin(user_id):
            # Persist the updated admin list to the .env file
            current_admins = self.framework.config.admin_ids
            if user_id not in current_admins:
                new_admins_str = ",".join(map(str, current_admins + [user_id]))
                self.framework.config.set('ADMIN_IDS', new_admins_str)
            await update.message.reply_text(f"User {user_id} added as an admin.")
        else:
            await update.message.reply_text(f"User {user_id} is already an admin.")

    @command("remove_admin", description="Remove an administrator.", owner_only=True)
    async def remove_admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handles the /remove_admin command.
        Usage: /remove_admin <user_id>
        """
        if not context.args or not context.args[0].isdigit():
            await update.message.reply_text("Usage: `/remove_admin <user_id>`", parse_mode='Markdown')
            return

        user_id = int(context.args[0])
        if self.framework.user_manager.remove_admin(user_id):
             # Persist the updated admin list to the .env file
            current_admins = self.framework.config.admin_ids
            if user_id in current_admins:
                current_admins.remove(user_id)
                new_admins_str = ",".join(map(str, current_admins))
                self.framework.config.set('ADMIN_IDS', new_admins_str)
            await update.message.reply_text(f"User {user_id} removed from admins.")
        else:
            await update.message.reply_text(f"User {user_id} is not an admin.")

    @command("list_users", description="List all registered users.", owner_only=True)
    async def list_users_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handles the /list_users command.
        """
        users = self.framework.user_manager.get_all_users()
        if not users:
            await update.message.reply_text("No users registered yet.")
            return

        message = "Registered Users:\n"
        for user_id, user_data in users.items():
            message += f"- ID: `{user_id}`, Name: {user_data.get('first_name', 'N/A')}, Last Command: {user_data.get('last_command', {}).get('command', 'N/A')}\n"

        # For long lists, consider pagination or sending a file
        if len(message) > 4096:
            message = message[:4090] + "\n..."
        await update.message.reply_text(message, parse_mode='Markdown')

    @command("plugins", description="List all loaded plugins.", owner_only=True)
    async def list_plugins_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handles the /plugins command.
        """
        loaded_plugins = self.framework.plugin_manager.loaded_plugins
        if not loaded_plugins:
            await update.message.reply_text("No plugins are currently loaded.")
            return

        message = "Loaded Plugins:\n"
        for name, instance in loaded_plugins.items():
            message += f"- `{name}` (`{instance.__class__.__name__}`)\n"
        
        await update.message.reply_text(message, parse_mode='Markdown')

    @command("reload", description="Reload a specific plugin.", owner_only=True)
    async def reload_plugin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handles the /reload command.
        Usage: /reload <plugin_name>
        """
        if not context.args:
            await update.message.reply_text("Usage: `/reload <plugin_name>`", parse_mode='Markdown')
            return

        plugin_name = context.args[0]
        if self.framework.plugin_manager.reload_plugin(plugin_name):
            await update.message.reply_text(f"Plugin `{plugin_name}` reloaded successfully.", parse_mode='Markdown')
            # After reloading, it's a good practice to update the command list
            await self.framework.set_bot_commands()
        else:
            await update.message.reply_text(f"Failed to reload plugin `{plugin_name}`. Check logs for details.", parse_mode='Markdown')