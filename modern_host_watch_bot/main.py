#!/usr/bin/env python3
"""
Modern Host Watch Bot - Main Entry Point

A modern Telegram bot for monitoring hosts and services with clean architecture.
"""

import asyncio
import signal
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.bot import ModernHostWatchBot
from src.config.settings import settings

logger = logging.getLogger(__name__)


class BotRunner:
    """Bot runner with graceful shutdown."""
    
    def __init__(self):
        self.bot: ModernHostWatchBot = None
        self.shutdown_event = asyncio.Event()
    
    async def start(self):
        """Start the bot."""
        try:
            logger.info("Starting Modern Host Watch Bot...")
            
            # Create bot instance
            self.bot = ModernHostWatchBot()
            
            # Setup signal handlers
            self._setup_signal_handlers()
            
            # Start bot
            await self.bot.start()
            
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            raise
        finally:
            await self.shutdown()
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}")
            self.shutdown_event.set()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def shutdown(self):
        """Shutdown the bot gracefully."""
        try:
            logger.info("Shutting down bot...")
            
            if self.bot:
                await self.bot.stop()
            
            logger.info("Bot shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


def main():
    """Main entry point."""
    try:
        # Validate settings
        if not settings.bot_token:
            logger.error("Bot token not provided. Please set BOT_TOKEN environment variable.")
            sys.exit(1)
        
        if not settings.bot_owner_id:
            logger.error("Bot owner ID not provided. Please set BOT_OWNER_ID environment variable.")
            sys.exit(1)
        
        if not settings.encryption_key:
            logger.error("Encryption key not provided. Please set ENCRYPTION_KEY environment variable.")
            sys.exit(1)
        
        # Create and run bot
        runner = BotRunner()
        
        # Run bot
        asyncio.run(runner.start())
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 