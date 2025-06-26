#!/usr/bin/env python3
"""
Simple echo bot example using the NEW Telegram Bot Framework (new_framework_cursor).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tlgfwk.core import TelegramBotFramework, command
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
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
        bot = EchoBot(config_file=env_path)
        print("Starting Echo Bot...")
        print("Press Ctrl+C to stop")
        bot.run()
        print("DEBUG: bot.run() terminou, entrando no keep alive")
        # --- MANTÉM O SCRIPT VIVO EM AMBIENTES COM EVENT LOOP JÁ ATIVO ---
        import asyncio, time
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            print("DEBUG: Loop já está rodando, mantendo o script vivo...")
            while True:
                time.sleep(3600)
        else:
            print("DEBUG: Loop não está rodando, script termina normalmente.")
    except KeyboardInterrupt:
        print("Bot stopped by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 