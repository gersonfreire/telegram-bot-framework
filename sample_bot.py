
import tlgfwk as tlgfwk

from util.util_telegram import *
from handlers import *

class SampleBot(tlgfwk.TlgBotFwk):
    
    async def help(self, update: Update, context: CallbackContext):
    
        self.logger.info(f"Help command received from {update.effective_user.name}")
        
        # A simple start command response
        await update.message.reply_text(f'Hello {update.effective_user.name}! Welcome to My Telegram Bot.')    
    
    def __init__(self, token: str = None, env_file: str = None, bot_name: str = None, bot_owner: str = None, bots_json_file: str = None, bot_defaults_build = None, **kwargs):
        
        super().__init__(token, env_file, bot_name, bot_owner, bots_json_file, bot_defaults_build, **kwargs)

    def initialize_handlers(self):
        
        super().initialize_handlers()
        
        # Adding a simple command handler for the /start command
        help_handler = CommandHandler('help', self.help)
        self.application.add_handler(help_handler, group=-1) 
        
        external_start_handler = CommandHandler('start', external_start)
        self.application.add_handler(external_start_handler, group=-1) 
        
        # self.show_default_start_message = False           

if __name__ == '__main__':
    
    # app = tlgfwk.TlgBotFwk() 
    app = SampleBot()
    
    app.run()