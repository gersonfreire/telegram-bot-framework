import asyncio
import inspect
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from .config import Config, ConfigError
from .persistence_manager import PersistenceManager
from .user_manager import UserManager
from .plugin_manager import PluginManager
from .scheduler import JobScheduler
from .decorators import command
from ..utils.logger import setup_logging, get_logger

class TelegramBotFramework:
    """
    The main class for the Telegram Bot Framework.

    This class orchestrates all the components of the framework, including:
    - Configuration loading (`Config`)
    - Logging (`setup_logging`)
    - Data persistence (`PersistenceManager`)
    - User management (`UserManager`)
    - Plugin management (`PluginManager`)
    - Job scheduling (`JobScheduler`)
    - Command registration and handling

    It initializes the `python-telegram-bot` Application and registers
    both built-in and plugin-provided command handlers.

    Attributes:
        config (Config): The configuration object.
        logger (logging.Logger): The logger instance for the framework.
        persistence_manager (PersistenceManager): The manager for data persistence.
        user_manager (UserManager): The manager for user data.
        plugin_manager (PluginManager): The manager for plugins.
        scheduler (JobScheduler): The manager for scheduled jobs.
        application (Application): The `python-telegram-bot` Application instance.
        commands (dict): A dictionary of registered commands and their metadata.
    """
    def __init__(self, env_file='.env', key_file='secret.key'):
        """
        Initializes the TelegramBotFramework.

        Args:
            env_file (str): Path to the .env file.
            key_file (str): Path to the encryption key file.
        """
        try:
            self.config = Config(env_file=env_file, key_file=key_file)
            setup_logging(self.config)
            self.logger = get_logger(__name__)

            self.persistence_manager = PersistenceManager()
            self.user_manager = UserManager(self.persistence_manager, self.config)
            
            self.plugin_manager = PluginManager(self, plugin_dir='python_telegram_framework/src/tlgfwk/plugins')
            
            self.scheduler = JobScheduler(self.persistence_manager)
            
            self.application = Application.builder().token(self.config.bot_token).build()
            self.commands = {}
            self._register_commands()
            self.plugin_manager.load_plugins()
            self.application.add_handler(MessageHandler(filters.COMMAND, self.unknown_command))

        except ConfigError as e:
            print(f"Configuration Error: {e}")
            # In a real application, you might want to exit or handle this more gracefully
            exit(1)
        except Exception as e:
            print(f"An unexpected error occurred during initialization: {e}")
            exit(1)

    def _register_commands(self):
        """Registers all methods decorated with @command."""
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if hasattr(method, '_command_metadata'):
                metadata = method._command_metadata
                self.commands[metadata['name']] = metadata
                self.application.add_handler(CommandHandler(metadata['name'], method))
                self.logger.info(f"Registered command: /{metadata['name']}")

    @command("start", "Starts the bot and registers the user.")
    async def start(self, update, context):
        """Handler for the /start command."""
        user = update.effective_user
        self.user_manager.add_or_update_user(user)
        self.user_manager.record_interaction(user.id, '/start')

        await update.message.reply_html(
            rf"Hi {user.mention_html()}!",
            reply_markup=None,
        )
        self.logger.info(f"User {user.id} ({user.username}) started the bot.")

    @command("help", "Shows this help message.")
    async def help_command(self, update, context):
        """Handler for the /help command."""
        self.user_manager.record_interaction(update.effective_user.id, '/help')
        
        is_admin = self.user_manager.is_admin(update.effective_user.id)
        
        help_text = "Available commands:\n\n"
        sorted_commands = sorted(self.commands.items())

        for name, metadata in sorted_commands:
            if metadata.get('owner_only') and not self.user_manager.is_owner(update.effective_user.id):
                continue
            if metadata.get('admin_only') and not is_admin:
                continue
            
            help_text += f"/{name} - {metadata['description']}"
            if metadata.get('admin_only') or metadata.get('owner_only'):
                help_text += " (Admin)"
            help_text += "\n"

        await update.message.reply_text(help_text)
        self.logger.info(f"User {update.effective_user.id} requested help.")

    async def unknown_command(self, update, context):
        """Handler for unrecognized commands."""
        self.user_manager.record_interaction(update.effective_user.id, update.message.text)
        await update.message.reply_text("Sorry, I didn't understand that command.")
        self.logger.warning(f"User {update.effective_user.id} sent an unknown command: {update.message.text}")

    def run(self):
        """Starts the bot."""
        self.logger.info("Starting bot...")
        self.scheduler.start()
        try:
            self.application.run_polling()
        finally:
            self.scheduler.shutdown()
            self.logger.info("Bot has been stopped.")

if __name__ == '__main__':
    # This allows running the framework directly for testing purposes.
    # In a real application, you would import and instantiate TelegramBotFramework.
    try:
        bot = TelegramBotFramework()
        bot.run()
    except Exception as e:
        print(f"Failed to run the bot: {e}")