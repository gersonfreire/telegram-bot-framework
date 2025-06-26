"""
Main bot application class.
"""
import logging
import asyncio
from typing import Optional

from telegram import Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.constants import ParseMode

from ..config.settings import settings
from ..services.monitoring import MonitoringService
from ..services.persistence import db_manager
from ..handlers.command_handlers import CommandHandlers
from ..handlers.admin_handlers import AdminHandlers

logger = logging.getLogger(__name__)


class ModernHostWatchBot:
    """Main bot application class."""
    
    def __init__(self):
        self.application: Optional[Application] = None
        self.monitoring_service: Optional[MonitoringService] = None
        self.command_handlers: Optional[CommandHandlers] = None
        self.admin_handlers: Optional[AdminHandlers] = None
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=getattr(logging, settings.log_level.upper()),
            handlers=[
                logging.FileHandler(settings.log_file),
                logging.StreamHandler()
            ]
        )
    
    async def initialize(self):
        """Initialize the bot application."""
        try:
            logger.info("Initializing Modern Host Watch Bot...")
            
            # Create application
            self.application = Application.builder().token(settings.bot_token).build()
            
            # Initialize services
            self.monitoring_service = MonitoringService(
                bot=self.application.bot,
                job_queue=self.application.job_queue
            )
            
            # Initialize handlers
            self.command_handlers = CommandHandlers(self.monitoring_service)
            self.admin_handlers = AdminHandlers()
            
            # Setup handlers
            await self._setup_handlers()
            
            # Load existing jobs
            await self.monitoring_service.load_all_jobs()
            
            # Send startup message
            await self._send_startup_message()
            
            logger.info("Bot initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing bot: {e}")
            raise
    
    async def _setup_handlers(self):
        """Setup command handlers."""
        if not self.application:
            raise RuntimeError("Application not initialized")
        
        # Basic commands
        self.application.add_handler(
            CommandHandler("start", self.command_handlers.start_command)
        )
        self.application.add_handler(
            CommandHandler("help", self.command_handlers.help_command)
        )
        
        # Host monitoring commands
        self.application.add_handler(
            CommandHandler("pingadd", self.command_handlers.pingadd_command)
        )
        self.application.add_handler(
            CommandHandler("pingdelete", self.command_handlers.pingdelete_command)
        )
        self.application.add_handler(
            CommandHandler("pinglist", self.command_handlers.pinglist_command)
        )
        self.application.add_handler(
            CommandHandler("pinghost", self.command_handlers.pinghost_command)
        )
        self.application.add_handler(
            CommandHandler("pinghostport", self.command_handlers.pinghostport_command)
        )
        self.application.add_handler(
            CommandHandler("listfailures", self.command_handlers.listfailures_command)
        )
        self.application.add_handler(
            CommandHandler("pinglog", self.command_handlers.pinglog_command)
        )
        
        # Configuration commands
        self.application.add_handler(
            CommandHandler("pinginterval", self.admin_handlers.pinginterval_command)
        )
        self.application.add_handler(
            CommandHandler("changepingport", self.admin_handlers.changepingport_command)
        )
        self.application.add_handler(
            CommandHandler("storecredentials", self.admin_handlers.storecredentials_command)
        )
        
        # Admin commands
        self.application.add_handler(
            CommandHandler("exec", self.admin_handlers.exec_command)
        )
        self.application.add_handler(
            CommandHandler("ssh", self.admin_handlers.ssh_command)
        )
        
        # Error handler
        self.application.add_error_handler(self._error_handler)
        
        logger.info("Command handlers setup completed")
    
    async def _send_startup_message(self):
        """Send startup message to bot owner."""
        try:
            startup_message = f"""
🤖 *Modern Host Watch Bot Started!*

*Version:* `1.0.0`
*Status:* Ready
*Active Jobs:* {len(self.monitoring_service.active_jobs)}
*Database:* Connected

Bot is now monitoring your hosts! 🎉
            """
            
            await self.application.bot.send_message(
                chat_id=settings.bot_owner_id,
                text=startup_message,
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            logger.error(f"Error sending startup message: {e}")
    
    async def _error_handler(self, update, context):
        """Handle errors in bot updates."""
        logger.error(f"Exception while handling an update: {context.error}")
        
        # Send error message to user if possible
        if update and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "❌ *Error:* An unexpected error occurred. Please try again later.",
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                logger.error(f"Error sending error message: {e}")
    
    async def start(self):
        """Start the bot."""
        try:
            logger.info("Starting Modern Host Watch Bot...")
            
            # Initialize bot
            await self.initialize()
            
            # Start polling
            await self.application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
            
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            raise
    
    async def stop(self):
        """Stop the bot."""
        try:
            logger.info("Stopping Modern Host Watch Bot...")
            
            if self.application:
                await self.application.stop()
                await self.application.shutdown()
            
            logger.info("Bot stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")
            raise 