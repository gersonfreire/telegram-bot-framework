#!/usr/bin/env python3
"""
Simple echo bot example using the Telegram Bot Framework.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tlgfwk import TelegramBotFramework
from tlgfwk.core import command
from telegram import Update
from telegram.ext import ContextTypes


class EchoBot(TelegramBotFramework):
    """Simple echo bot example."""
    
    @command(name="echo", description="Echo back your message")
    async def echo_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Echo back the user's message."""
        if context.args:
            message = " ".join(context.args)
            await update.message.reply_text(f"Echo: {message}")
        else:
            await update.message.reply_text("Usage: /echo <message>")
    
    @command(name="hello", description="Say hello")
    async def hello_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Say hello to the user."""
        user = update.effective_user
        await update.message.reply_text(f"Hello, {user.first_name}! 👋")


def main():
    """Main function."""
    try:
        # Create and run the bot
        bot = EchoBot()
        print("🤖 Starting Echo Bot...")
        print("Press Ctrl+C to stop")
        bot.run()
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 