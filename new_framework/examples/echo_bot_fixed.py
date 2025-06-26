"""
Simple Echo Bot Example - Framework Compatibility Version

This example demonstrates the basic usage of the Telegram Bot Framework.
The bot echoes back any message it receives and provides basic commands.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the path so we can import the framework
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tlgfwk import TelegramBotFramework, command
from telegram import Update
from telegram.ext import ContextTypes


class EchoBot(TelegramBotFramework):
    """Simple echo bot that responds to messages."""
    
    def __init__(self):
        # Initialize with basic configuration
        # The framework will automatically load config from environment variables
        super().__init__()
        self.logger.info("EchoBot inicializado!")
    
    def setup_handlers(self):
        """Set up custom message handlers."""
        super().setup_handlers()
        
        # Add echo handler for non-command messages
        from telegram.ext import MessageHandler, filters
        if self.application:
            self.application.add_handler(
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.echo_message)
            )
            self.logger.info("Handlers de echo configurados!")
    
    @command(name="echo", description="Echo back your message")
    async def echo_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Echo command handler."""
        try:
            if context.args:
                message = " ".join(context.args)
                await update.message.reply_text(f"🔊 Echo: {message}")
                self.logger.info(f"Echo command executed: {message}")
            else:
                await update.message.reply_text("Please provide a message to echo!")
        except Exception as e:
            self.logger.error(f"Error in echo_command: {e}")
    
    @command(name="reverse", description="Reverse your message")
    async def reverse_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Reverse message command."""
        try:
            if context.args:
                message = " ".join(context.args)
                reversed_message = message[::-1]
                await update.message.reply_text(f"🔄 Reversed: {reversed_message}")
                self.logger.info(f"Reverse command executed: {message} -> {reversed_message}")
            else:
                await update.message.reply_text("Please provide a message to reverse!")
        except Exception as e:
            self.logger.error(f"Error in reverse_command: {e}")
    
    @command(name="count", description="Count words in your message")
    async def count_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Count words in message."""
        try:
            if context.args:
                message = " ".join(context.args)
                word_count = len(message.split())
                char_count = len(message)
                await update.message.reply_text(
                    f"📊 Statistics:\n"
                    f"Words: {word_count}\n"
                    f"Characters: {char_count}"
                )
                self.logger.info(f"Count command executed: {word_count} words, {char_count} chars")
            else:
                await update.message.reply_text("Please provide a message to count!")
        except Exception as e:
            self.logger.error(f"Error in count_command: {e}")
    
    async def echo_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Echo non-command messages."""
        try:
            if update.message and update.message.text:
                await update.message.reply_text(f"🤖 You said: {update.message.text}")
                self.logger.info(f"Echoed message: {update.message.text}")
        except Exception as e:
            self.logger.error(f"Error in echo_message: {e}")


def check_environment():
    """Check if required environment variables are set."""
    missing_vars = []
    
    if not os.getenv("BOT_TOKEN"):
        missing_vars.append("BOT_TOKEN")
    
    if not os.getenv("OWNER_USER_ID"):
        missing_vars.append("OWNER_USER_ID")
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Solutions:")
        print("1. Create a .env file based on .env.example")
        print("2. Set environment variables manually")
        print("3. Get a bot token from @BotFather on Telegram")
        return False
    
    return True


def main():
    """Main function to run the bot."""
    print("🤖 Starting Echo Bot...")
    
    # Check environment
    if not check_environment():
        return 1
    
    try:
        # Create and run the bot
        bot = EchoBot()
        
        print("✅ Bot configuration loaded!")
        print(f"🆔 Owner ID: {bot.config.owner_user_id}")
        print(f"👥 Admin IDs: {bot.config.admin_user_ids}")
        print(f"🔧 Debug mode: {bot.config.debug}")
        
        # Setup handlers
        bot.setup_handlers()
        
        # Run the bot
        print("🚀 Starting bot polling...")
        bot.run()
        
    except KeyboardInterrupt:
        print("\n⏹️  Bot stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Error running bot: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
