import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from .config import Config, ConfigError
from .persistence_manager import PersistenceManager
from .user_manager import UserManager
from ..utils.logger import setup_logging, get_logger

class TelegramBotFramework:
    """
    The main class for the Telegram Bot Framework.
    It initializes the bot, sets up handlers, and runs the application.
    """
    def __init__(self, env_file='.env', key_file='secret.key'):
        try:
            self.config = Config(env_file=env_file, key_file=key_file)
            setup_logging(self.config)
            self.logger = get_logger(__name__)

            self.persistence_manager = PersistenceManager()
            self.user_manager = UserManager(self.persistence_manager, self.config)
            
            self.application = Application.builder().token(self.config.bot_token).build()
            self._register_default_handlers()

        except ConfigError as e:
            print(f"Configuration Error: {e}")
            # In a real application, you might want to exit or handle this more gracefully
            exit(1)
        except Exception as e:
            print(f"An unexpected error occurred during initialization: {e}")
            exit(1)

    def _register_default_handlers(self):
        """Registers the default command and message handlers."""
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(MessageHandler(filters.COMMAND, self.unknown_command))

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

    async def help_command(self, update, context):
        """Handler for the /help command."""
        self.user_manager.record_interaction(update.effective_user.id, '/help')
        # This will be expanded later to list all registered commands.
        await update.message.reply_text("This is a placeholder for the help command.")
        self.logger.info(f"User {update.effective_user.id} requested help.")

    async def unknown_command(self, update, context):
        """Handler for unrecognized commands."""
        self.user_manager.record_interaction(update.effective_user.id, update.message.text)
        await update.message.reply_text("Sorry, I didn't understand that command.")
        self.logger.warning(f"User {update.effective_user.id} sent an unknown command: {update.message.text}")

    def run(self):
        """Starts the bot."""
        self.logger.info("Starting bot...")
        self.application.run_polling()
        self.logger.info("Bot has been stopped.")

if __name__ == '__main__':
    # This allows running the framework directly for testing purposes.
    # In a real application, you would import and instantiate TelegramBotFramework.
    try:
        bot = TelegramBotFramework()
        bot.run()
    except Exception as e:
        print(f"Failed to run the bot: {e}")