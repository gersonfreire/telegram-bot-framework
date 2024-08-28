#!/usr/bin/env python
# -*- coding: utf-8 -*-

version = '0.0.2 - validate token against Telegram servers'

# TODOs:
# - Create a filter for admin commands

# ------------------------------------------

from telegram import Bot
from __init__ import *

import dotenv

import translations.translations

class TlgBotFwk(Application):
    
    # ------------------------------------------
    
    def get_command_handlers(self, *args, **kwargs):
        
        command_dict = {}
            
        try:
            for handler_group in self.application.handlers.values():                    
                    for handler in handler_group:
                        if isinstance(handler, CommandHandler):
                            command_name = list(handler.commands)[0]
                            command_description = handler.callback.__doc__.split("\n")[0] if handler.callback.__doc__ else command_name
                            command_filter = handler.filters
                            user_allowed = list(command_filter.user_ids)[0] if isinstance(command_filter, filters.User) else None
                            is_admin = True if isinstance(command_filter, filters.User) else False
                            command_dict[command_name] = {'command_description': command_description, 'is_admin': is_admin, 'user_allowed': user_allowed}
                            
                            # yield handler
        
        except Exception as e:
            logger.error(f"Error getting command description: {e}")
            return f'Sorry, we have a problem getting the command description: {e}'
        
        return command_dict
    
    async def get_help_text(self, user_language_code = 'en', current_user_id = None, *args, **kwargs):
        
        try:
            self.current_commands = await self.application.bot.get_my_commands(scope=BotCommandScopeDefault())
            
            self.help_text = translations.translations.get_translated_message(user_language_code, 'help_message', 'en', self.application.bot.name)            
            
            for command in self.current_commands:
                self.help_text += f"/{command.command} - {command.description}{os.linesep}"
                
            # get a dictionary of command handlers
            command_dict = self.get_command_handlers()
            
            # convert the commands dictionary into help text
            for command_name, command_data in command_dict.items():
                if command_name not in [bot_command.command for bot_command in self.current_commands]:
                    if command_data['is_admin']:
                        if command_data['user_allowed'] == current_user_id: # self.bot_owner:
                            self.help_text += f"/{command_name} - {command_data['command_description']}{os.linesep}"
                    else:
                        command_description = command_data['command_description']
                        self.help_text += f"/{command_name} - {command_description}{os.linesep}" 
                
            return self.help_text
        
        except Exception as e:
            logger.error(f"Error getting commands: {e}")
            return f'Sorry, we have a problem getting the commands: {e}'
    
    def validate_token(self, token: str = None, quit_if_error = False, run_sync = False):
        
        self.token_validated = False
        self.bot_info = None
        
        try:
            bot = Bot(token=token)
            loop = asyncio.get_event_loop()                
            self.bot_info = loop.run_until_complete(bot.get_me())
            # loop.close() 
            self.token_validated = True            
        
        except Exception as e:
            logger.error(f"Error validating token: {e}")
            if quit_if_error:
                input_with_timeout("Enter to close: ", 10)
                quit()
            return None
    
    # ------------------------------------------

    async def post_init(self, application: Application) -> None:   

        try:
            # get the name of current bot
            bot_name = application.bot.username
            
            host_alias = hostname   
            
            start_message = f"""*{application.bot.username} Started!*
_Version:_   `{bot_version}`
_Host:_     `{hostname}`
_Host Alias:_    `{host_alias}`
_CWD:_ `{os.getcwd()}`
_Path:_
`{main_script_path}`"""    
            logger.info(f"{start_message}")  

            current_commands = await application.bot.get_my_commands(scope=BotCommandScopeAllPrivateChats())
            logger.info(f"Get Current commands: {current_commands}")    
            current_commands = await application.bot.get_my_commands(scope=BotCommandScopeDefault())
            logger.info(f"Get Current commands: {current_commands}") 
            
            await application.bot.send_message(chat_id=self.bot_owner, text=f"{start_message}", parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Error: {e}")

    async def post_shutdown(self, application: Application) -> None:
        
        try:
            stop_message = f"_STOPPING bot_ {os.linesep}`{hostname}`{os.linesep}`{__file__}` {bot_version}..."
            logger.info(stop_message)
            await application.bot.send_message(chat_id=self.bot_owner, text=f"{stop_message}", parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logger.error(f"Error: {e}")
                
        sys.exit(0)

    # ------------------------------------------    
    
    def __init__(self, token: str = None, env_file: str = None, bot_name: str = None, bot_owner: str = None, bots_json_file: str = None, bot_defaults_build = None, **kwargs):
        
        try:
            
            dotenv.load_dotenv(env_file)
                
            bot_defaults_build = bot_defaults_build if bot_defaults_build else Defaults(parse_mode=ParseMode.MARKDOWN) 
            
            self.token = token if token else os.environ.get('DEFAULT_BOT_TOKEN', None)            
            self.validate_token(self.token, quit_if_error=True, run_sync=True)
            
            self.bot_name = os.environ.get('DEFAULT_BOT_NAME', None)
            self.bot_owner = int(os.environ.get('DEFAULT_BOT_OWNER', None))
            self.bots_json_file = os.environ.get('DEFAULT_BOTS_JSON_FILE', None)
            self.bot_defaults_build = bot_defaults_build
            
            # Create an Application instance using the builder pattern            
            self.application = Application.builder().defaults(bot_defaults_build).token(self.token).post_init(self.post_init).post_shutdown(self.post_shutdown).build()            
            
            self.logger = logger
            
            self.show_default_start_message = True
            
            self.language_code = None
            
            self.initialize_handlers()
            
        except Exception as e:
            logger.error(f"Error initializing bot: {e}")
            input_with_timeout("Enter to close: ", 10)
            quit()

    def initialize_handlers(self):
        
        # handles global errors
        self.application.add_error_handler(self.error_handler)
        
        # Adding a simple command handler for the /start command
        start_handler = CommandHandler('start', self.default_start_handler)
        self.application.add_handler(start_handler)
          
        help_handler = CommandHandler('help', self.default_help_handler)
        self.application.add_handler(help_handler) 
        
        # Adding a simple command handler for the /set_language_code command
        set_language_code_handler = CommandHandler('lang', self.set_language_code, filters=filters.User(user_id=self.bot_owner))
        self.application.add_handler(set_language_code_handler)
        
        self.application.add_handler(MessageHandler(filters.COMMAND, self.default_unknown_command))
      
    # -------- Default command handlers --------      
        
    @with_writing_action
    @with_log_admin 
    async def set_language_code(self, update: Update, context: CallbackContext, *args, **kwargs):
        """Set the language code for the bot

        Args:
            update (Update): _description_
            context (CallbackContext): _description_
        """
        
        if len(update.message.text.split(' ')) > 1:
            self.language_code = update.message.text.split(' ')[1].lower()
            
        await update.message.reply_text(f"_Language code set to:_ `{self.language_code}`")
                
    @with_writing_action
    @with_log_admin     
    async def error_handler(self, update: Update, context: CallbackContext) -> None:
        self.logger.error(context.error)
        await self.application.bot.send_message(chat_id=self.bot_owner, text=str(context.error))        

    @with_writing_action
    @with_log_admin        
    async def default_unknown_command(self, update: Update, context: CallbackContext, *args, **kwargs):
        
        self.logger.info(f"Unknown command received from {update.effective_user.name}")
        
        user_language_code = self.language_code.split('-')[0] 
        reply_message = translations.translations.get_translated_message(user_language_code, 'command_not_implemented', 'en', update.message.text)   
        
        await update.message.reply_text(reply_message)

    @with_writing_action
    @with_log_admin
    async def default_start_handler(self, update: Update, context: CallbackContext, *args, **kwargs):
        
        try:
            self.current_commands = await self.application.bot.get_my_commands()
            
            if self.show_default_start_message: 
                
                if self.language_code is None:
                    self.language_code = update.effective_user.language_code
                
                # Get the default current user´s language code
                user_language_code = self.language_code.split('-')[0] 
                           
                self.default_start_message = translations.translations.get_translated_message(user_language_code, 'start_message', 'en', update.effective_user.full_name, self.application.bot.name, self.application.bot.first_name)
                
                if self.bot_owner and update.effective_user.id == self.bot_owner: 
                         
                    if user_language_code in translations.translations.start_message:
                         
                        self.default_start_message += f"{os.linesep}{os.linesep}_You are the bot Owner:_` {self.bot_owner}`"
                        self.default_start_message += f"{os.linesep}_Language code:_ `{self.language_code}`"
                   
                    self.default_start_message += f"{os.linesep}{await self.get_help_text(current_user_id=update.effective_user.id)}"
                    
                await update.message.reply_text(self.default_start_message.format(update.effective_user.first_name))
                
        except Exception as e:
            logger.error(f"Error in default_start_handler: {e}")
            await update.message.reply_text(f"Sorry, we encountered an error: {e}")

    @with_writing_action
    @with_log_admin            
    async def default_help_handler(self, update: Update, context: CallbackContext, *args, **kwargs):
        
        if self.language_code is None:
            self.language_code = update.effective_user.language_code
        user_language_code = self.language_code.split('-')[0]
        
        self.help_text = await self.get_help_text(user_language_code=user_language_code, current_user_id=update.effective_user.id)
        
        self.logger.info(f"Help command received from {update.effective_user.name}")
        
        # A simple start command response
        await update.message.reply_text(self.help_text)                        

    def run(self):
        # Run the bot using the run_polling method
        self.application.run_polling()

if __name__ == '__main__':
    
    app = TlgBotFwk()
    
    app.run()