
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------

"""
This is a sample bot using this Telegram Bot Framwork that 
overloads the initialize_handlers method to add a help command handler.
"""

import __init__

from tlgfwk import *

from util.util_telegram import *
from handlers import *

__version__ = '0.0.1'

class SampleBot(TlgBotFwk):
    
    async def help(self, update: Update, context: CallbackContext):
    
        self.logger.info(f"Help command received from {update.effective_user.name}")
        
        # A simple start command response
        await update.message.reply_text(f'Hello {update.effective_user.name}! Welcome to My Telegram Bot.')    
    
    def __init__(self, token: str = None, env_file: str = None,bot_owner: str = None):
        
        super().__init__(token=token, env_file=env_file, bot_owner=bot_owner)

    def initialize_handlers(self):
        
        super().initialize_handlers()
        
        # Adding a simple command handler for the /start command
        help_handler = CommandHandler('help', self.help)
        self.application.add_handler(help_handler, group=-1) 
        
        external_start_handler = CommandHandler('start', overloaded_echo_function)
        self.application.add_handler(external_start_handler, group=-1) 
        
        # self.show_default_start_message = False           

if __name__ == '__main__':
    
    app = SampleBot()
    
    app.run()