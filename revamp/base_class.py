import asyncio
import os
import sys
import logging
from telegram import Bot, Update, BotCommandScopeDefault
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, ContextTypes, PicklePersistence, JobQueue, Defaults
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

logger = logging.getLogger(__name__)

class BaseTelegramBot(Application):
    
    def validate_token(self, token: str = None, quit_if_error = True, input_token = True):
        
        self.token_validated = False
        self.bot_info = None       
        
        try:           
            
            bot = Bot(token=token)
            self.loop = asyncio.get_event_loop()                
            self.bot_info = self.loop.run_until_complete(bot.get_me())
            # loop.close() 
            self.token_validated = True  
            
            return True          
        
        except Exception as e:
            logger.error(f"Error validating token: {e}")
            
            # if input_token:
            #     token = input_with_timeout("You have 30 sec. to enter the bot token: ", 30)
            #     if self.validate_token(token, quit_if_error, False):
            #         self.token = token
            #         # self.bot_owner = int(input_with_timeout("You have 30 sec. to enter the bot owner id: ", 30))
            #         self.bot_owner = int(input_with_timeout("You have 30 sec. to enter the bot owner id: ", 30))
            #         # clear entire .env file
            #         os.remove(self.env_file)
            #         open(self.env_file, 'w').close()
            #         dotenv.set_key(self.env_file, 'DEFAULT_BOT_TOKEN', self.token)
            #         # dotenv.set_key(self.env_file, 'DEFAULT_BOT_OWNER', int(self.bot_owner)) 
            #         self.add_or_update_env_setting('DEFAULT_BOT_OWNER', self.bot_owner)
                    
            #         dotenv.load_dotenv(self.env_file)
                                       
            #         return True
                
            # if quit_if_error:
            #     input_with_timeout("Enter to close: ", 10)
            #     quit()
                
            return None    
    
    async def error_handler(self, update: Update, context: CallbackContext) -> None:
        
        try:
            error_message = f"{__file__} at line {str(sys.exc_info()[-1])}: {str(context.error)}" 
            self.logger.error(error_message) 
            await self.application.bot.send_message(chat_id=self.bot_owner, text=error_message, parse_mode=None) 
        
        except Exception as e:            
            logger.error(e)  
            await self.application.bot.send_message(chat_id=self.bot_owner, text=str(e))
       
    def __init__(self, 
                 token: str = None,
                 admin_id_list: list[int] = None,
                 disable_persistence: bool = False,
                 disable_command_not_implemented: bool = False,
                 disable_error_handler: bool = False,
                 default_language_code: str = 'en',
                 default_persistence_interval: int = 30,
                 **kwargs):
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        env_path = os.path.join(script_dir, '.env')
        if os.path.exists(env_path):
            load_dotenv(env_path, verbose=True, override=True)
        else:
            logger.error(f".env file not found at {env_path}")

        token = token or os.getenv('DEFAULT_BOT_TOKEN')
        if not token:
            logger.error("DEFAULT_BOT_TOKEN not found in environment variables")
            quit()
            
        self.token = token
        self.default_persistence_interval = default_persistence_interval
        self.admin_id_list = admin_id_list or list(map(int, os.getenv('ADMIN_ID_LIST', '').split(',')))
        self.disable_persistence = disable_persistence
        self.disable_command_not_implemented = disable_command_not_implemented
        self.disable_error_handler = disable_error_handler
        self.default_language_code = default_language_code
        self.help_text = ""
        self.default_start_message = ""
        self.common_users_commands = []
        self.admin_commands = []
        self.all_commands = []
        
        # ---------- Build the bot application ------------
        
        self.bot_info = None
        self.validate_token(self.token)  
            
        # Making bot persistant from the base class      
        # https://github.com/python-telegram-bot/python-telegram-bot/wiki/Making-your-bot-persistent
        script_path = os.path.dirname(os.path.abspath(__file__))
        persistence_file = kwargs.get('persistence_file', None)
        self.persistence_file = f"{script_path}{os.sep}{self.bot_info.username + '.pickle'}" if not persistence_file else persistence_file
        persistence = PicklePersistence(filepath=self.persistence_file, update_interval=self.default_persistence_interval) if not disable_persistence else None
        
        # Create an Application instance using the builder pattern  
        # ('To use `JobQueue`, PTB must be installed via `pip install "python-telegram-bot[job-queue]"`.',)    
        bot_defaults_build = kwargs.get('bot_defaults_build', Defaults(parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True))  # Get bot_defaults_build from kwargs or use an empty dictionary as default
        
        self.application = Application.builder().defaults(bot_defaults_build).token(self.token).post_init(self.post_init).post_stop(self.post_stop).persistence(persistence).job_queue(JobQueue()).build()
        
        # --------------------------------------------------  
                
        self.initialize_handlers()      

    def initialize_handlers(self):
        try:

            if not self.disable_error_handler:
                self.application.add_error_handler(self.error_handler)
                            
            # unschedule_function_handler = CommandHandler('unschedule', self.cmd_unschedule_function, filters=filters.User(user_id=self.admin_id_list))
            # self.add_handler(unschedule_function_handler)
            
            # if not self.disable_command_not_implemented:
            #     self.add_handler(MessageHandler(filters.COMMAND, self.default_unknown_command))
                
        except Exception as e:
            logger.error(f"Error initializing handlers: {e}")
            for admin_id in self.admin_id_list:
                try:
                    self.send_message_sync(chat_id=admin_id, message=f"Error initializing handlers: {e}")
                except Exception as e:
                    logger.error(f"Error sending warning to admin {admin_id}: {e}")

    async def get_help_text(self, language_code=None, current_user_id=None):
        try:
            help_header = "Help Text Header"
            help_text_list = ["Command 1", "Command 2"]
            self.help_text = f'{help_header}{os.linesep}{os.linesep.join(help_text_list)}'
            
            self.common_users_commands = [command for command in self.common_users_commands if command.command not in self.disable_commands_list]
            self.all_commands = [command for command in self.all_commands if command.command not in self.disable_commands_list]
            
            await self.bot.set_my_commands(self.common_users_commands)
            await self.bot.set_my_commands(self.all_commands, scope={'type': 'chat', 'chat_id': self.bot_owner})
            await self.set_admin_commands()
            
            self.common_users_commands = await self.bot.get_my_commands()
            self.all_commands = await self.bot.get_my_commands(scope={'type': 'chat', 'chat_id': self.bot_owner})
                        
            return self.help_text
        except Exception as e:
            logger.error(f"Error getting commands: {e}")
            return f'Sorry, we have a problem getting the commands: {e}'

    async def set_start_message(self, language_code: str, full_name: str, user_id: int):
        try:
            self.default_start_message = f"Welcome {full_name} to {self.bot.username}!"
            if user_id in self.admin_id_list:
                self.default_start_message += f"{os.linesep}{os.linesep}_You are one of the bot admins:_` {self.admin_id_list}`"
                self.default_start_message += f"{os.linesep}_User language code:_ `{language_code}`"
                self.default_start_message += f"{os.linesep}_Default language code:_ `{self.default_language_code}`"
                self.default_start_message += f"{os.linesep}{os.linesep}{await self.get_help_text(language_code, user_id)}"
        except Exception as e:
            logger.error(f"Error in set_start_message: {e}")
            return f'Sorry, we encountered an error: {e}'

    async def post_stop(self, application: Application) -> None:
        try:
            self.persistence.flush() if self.persistence else None
            stop_message = f"_STOPPING_ @{self.bot.username} {os.linesep}`{self.hostname}`{os.linesep}`{__file__}` {self.bot.username}..."
            logger.info(stop_message)
            await self.send_admins_message(message=stop_message)
        except Exception as e:
            logger.error(f"Error: {e}")
        sys.exit(0)

    async def stop_bot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(f"*{update._bot.username} STOPPED!*", parse_mode=ParseMode.MARKDOWN)
        os.abort()

    async def restart_bot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            await update.message.reply_text("_Restarting..._", parse_mode=ParseMode.MARKDOWN)
            args = sys.argv[:]
            args.insert(0, sys.executable)
            os.chdir(os.getcwd())
            os.execv(sys.executable, args)
        except Exception as e:
            logger.error(f"Error restarting bot: {e}")
            await update.message.reply_text(f"An error occurred while restarting the bot: {e}")

    async def error_handler(self, update: Update, context: CallbackContext) -> None:
        try:
            error_message = f"{__file__} at line {str(sys.exc_info()[-1])}: {str(context.error)}"
            logger.error(error_message)
            await self.bot.send_message(chat_id=self.bot_owner, text=error_message, parse_mode=None)
        except Exception as e:
            logger.error(e)
            await self.bot.send_message(chat_id=self.bot_owner, text=str(e))

    async def post_init(self, application: Application) -> None:
        try:
            self.bot_name = application.bot.username
            post_init_message = await self.get_init_message()
            logger.info(f"{post_init_message}")
            await self.set_start_message(self.default_language_code, 'Admin', self.admin_id_list[0])
            post_init_message += f"{os.linesep}{os.linesep}{self.default_start_message}"
            self.common_users_commands = await application.bot.get_my_commands(scope=BotCommandScopeDefault())
            logger.info(f"Get Current commands: {self.common_users_commands}")
            self.common_users_commands = [command for command in self.common_users_commands if command.command not in self.disable_commands_list]
            self.admin_commands = await application.bot.get_my_commands(scope={'type': 'chat', 'chat_id': self.admin_id_list[0]}) if self.admin_id_list else []
            self.admin_commands = [command for command in self.admin_commands if command.command not in self.disable_commands_list]
            self.all_commands = tuple(list(self.common_users_commands) + list(self.admin_commands))
            await self.send_admins_message(message=post_init_message)
        except Exception as e:
            logger.error(f"Error: {e}")

    async def get_init_message(self):
        try:
            post_init_message = f"""@{self.bot.username} *Started!*
_Version:_   `{__version__}`
_Host:_     `{self.hostname}`
_CWD:_ `{os.getcwd()}`
_Path:_
`{self.main_script_path}`"""
            logger.info(f"{post_init_message}")
            return post_init_message
        except Exception as e:
            logger.error(f"Error in get_init_message: {e}")
            return f'Sorry, we encountered an error: {e}'

    def run(self):
        self.application.run_polling()
        
if __name__ == '__main__':  

    bot = BaseTelegramBot()
    bot.run()
    