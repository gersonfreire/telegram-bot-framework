
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------

"""
This is an example of an echo bot using this Telegram Bot Framework.
"""

import __init__

from tlgfwk import *

class EchoBot(TlgBotFwk):
    def __init__(self, token):
        super().__init__(token)

    def setup_handlers(self):
        # Add handlers
        self.add_handler(CommandHandler("start", self.start))
        self.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.echo))

    async def start(self, update: Update, context: CallbackContext) -> None:
        await update.message.reply_text('Hello! I am an echo bot. Send me any message and I will echo it back!')

    async def echo(self, update: Update, context: CallbackContext) -> None:
        await update.message.reply_text(update.message.text)

def main():
    # Replace with your bot token
    BOT_TOKEN = 'YOUR_BOT_TOKEN'
    
    # Initialize and start the bot
    bot = EchoBot(BOT_TOKEN)
    bot.run()

if __name__ == '__main__':
    main()