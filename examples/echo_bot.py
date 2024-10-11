
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

class EchoBot(TlgBotFwk):  
    
    def __init__(self, token: str = None, env_file: str = None,bot_owner: str = None):        
        super().__init__(token=token, env_file=env_file, bot_owner=bot_owner)
            
    async def cmd_echo_super_class(self, update: Update, context: CallbackContext):
        if len(update.message.text.split(" ")) >= 1:
            await update.message.reply_text(f'Echo: {update.message.text.split(" ", 1)[1:]}')    
        else:    
            await update.message.reply_text('Usage: /echo <message>') 

    def initialize_handlers(self):        
        super().initialize_handlers()
        
        echo_handler_super_class = CommandHandler('echo', self.cmd_echo_super_class)
        self.application.add_handler(echo_handler_super_class, group=-1)      

if __name__ == '__main__':
    
    app = EchoBot()    
    app.run()