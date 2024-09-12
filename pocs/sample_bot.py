import os,sys
   
# ---- Add parent folder to import path ----
script_path = os.path.dirname(os.path.realpath(__file__))
parent_folder = os.path.dirname(script_path)
common_module_path = rf"{parent_folder}{os.sep}"
sys.path.append(common_module_path)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(parent_folder)
script_name = os.path.basename(sys.argv[0]).replace('.py', '')

# -----------------------------------------

import tlgfwk as tlgfwk

from util.util_telegram import *
from handlers import *

__version__ = '0.0.1'

class SampleBot(tlgfwk.TlgBotFwk):
    
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
        
        external_start_handler = CommandHandler('start', external_start)
        self.application.add_handler(external_start_handler, group=-1) 
        
        # self.show_default_start_message = False           

if __name__ == '__main__':
    
    app = SampleBot()
    
    app.run()