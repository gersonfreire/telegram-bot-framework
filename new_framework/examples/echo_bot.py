"""
Simple Echo Bot Example

This example demonstrates the basic usage of the Telegram Bot Framework.
The bot echoes back any message it receives and provides basic commands.
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env.test
env_file = Path(__file__).parent.parent / ".env.test"
if env_file.exists():
    load_dotenv(env_file)
    print(f"✅ Loaded config from {env_file}")
else:
    print("⚠️ .env.test not found, using system environment variables")

# Add the src directory to the path so we can import the framework
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tlgfwk import TelegramBotFramework, command
from telegram import Update
from telegram.ext import ContextTypes


class EchoBot(TelegramBotFramework):
    """Simple echo bot that responds to messages."""
    
    def __init__(self):
        # Initialize with basic configuration
        # Load config from environment variables using from_env method
        from tlgfwk.core.config import Config
        config = Config.from_env()
        super().__init__(custom_config=config)
    
    def setup_handlers(self):
        """Set up custom message handlers."""
        super().setup_handlers()
        
        # Add echo handler for non-command messages
        from telegram.ext import MessageHandler, filters
        if self.application:
            self.application.add_handler(
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.echo_message)
            )
    
    @command(name="echo", description="Echo back your message")
    async def echo_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Echo command handler."""
        if context.args:
            message = " ".join(context.args)
            await update.message.reply_text(f"🔊 Echo: {message}")
        else:
            await update.message.reply_text("Please provide a message to echo!")
    
    @command(name="reverse", description="Reverse your message")
    async def reverse_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Reverse message command."""
        if context.args:
            message = " ".join(context.args)
            reversed_message = message[::-1]
            await update.message.reply_text(f"🔄 Reversed: {reversed_message}")
        else:
            await update.message.reply_text("Please provide a message to reverse!")
    
    @command(name="count", description="Count words in your message")
    async def count_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Count words in message."""
        if context.args:
            message = " ".join(context.args)
            word_count = len(message.split())
            char_count = len(message)
            await update.message.reply_text(
                f"📊 Statistics:\n"
                f"Words: {word_count}\n"
                f"Characters: {char_count}"
            )
        else:
            await update.message.reply_text("Please provide a message to count!")
    
    async def echo_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Echo non-command messages."""
        if update.message and update.message.text:
            await update.message.reply_text(f"🤖 You said: {update.message.text}")


def main():
    """Main function to run the bot."""
    # Check for required environment variables
    if not os.getenv("BOT_TOKEN"):
        print("Error: BOT_TOKEN environment variable is required")
        print("Please set it in your .env file or environment")
        return
    
    if not os.getenv("OWNER_USER_ID"):
        print("Error: OWNER_USER_ID environment variable is required")
        print("Please set it in your .env file or environment")
        return
    
    if not os.getenv("ADMIN_USER_IDS"):
        print("Warning: ADMIN_USER_IDS not set. Admin commands may not work.")
    
    # Create and run the bot
    print("Starting Echo Bot...")
    bot = EchoBot()
    
    # Setup handlers
    bot.setup_handlers()
    
    try:
        # Run the bot
        bot.run()
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Error running bot: {e}")


if __name__ == "__main__":
    main()
