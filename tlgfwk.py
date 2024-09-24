#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------

__version__ = """
TODO´s:
0.6.3 Load just a specified plugin
0.6.4 Show to admin user which commands is common or admin
0.6.5 Add a command to show the bot configuration settings
0.6.7 Improve command handler to show the commands available to the user and admin
0.6.8 Show 👑 on the user list for the admin users
0.6.9 Show 👑 on the command help list for the admin commands
0.7.0 Add a command to show user´s balance
"""

from __init__ import *

class TlgBotFwk(Application):
    
    # ------------- util functions ------------------
     
    async def force_persistence(self, update: Update, context: CallbackContext):
        """Force the bot to save the persistence file

        Args:
            update (Update): _description_
            context (CallbackContext): _description_
        """
        
        try:
            # if the dictionary of users does not exist on bot_data, create it
            if 'user_dict' not in context.bot_data:
                context.bot_data['user_dict'] = {}
                
            # Insert or update user on the bot_data dictionary
            context.bot_data['user_dict'][update.effective_user.id] = update.effective_user
            
            # force persistence of the bot_data dictionary
            self.application.persistence.update_bot_data(context.bot_data) if self.application.persistence else None
                      
            # set effective language code
            language_code = context.user_data['language_code'] if 'language_code' in context.user_data else update.effective_user.language_code
            
            # force persistence update of the user data
            self.application.persistence.update_user_data(update.effective_user.id, context.user_data) if self.application.persistence else None          
            
            # get user data from persistence
            user_data = await self.application.persistence.get_user_data() if self.application.persistence else None
            
        except Exception as e:
            logger.error(f"Error: {e}")
            await update.message.reply_text(f"An error occurred: {e}")
    
    async def get_init_message(self): 
        try:
            post_init_message = f"""@{self.bot_name} *Started!*
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
    
    async def set_start_message(self, language_code:str, full_name:str, user_id:int): #, update, context):
        
        try:
                                      
            self.default_start_message = translations.get_translated_message(language_code, 'start_message', 'en', full_name, self.application.bot.name, self.application.bot.first_name)
            
            # if self.bot_owner and user_id == self.bot_owner:                          
            if user_id in self.admins_owner:                          
                self.default_start_message += f"{os.linesep}{os.linesep}_You are one of the bot admins:_` {self.admins_owner}`"
                self.default_start_message += f"{os.linesep}_User language code:_ `{language_code}`"
                self.default_start_message += f"{os.linesep}_Default language code:_ `{self.default_language_code}`"
            
                # language_code = context.user_data.get('language_code', update.effective_user.language_code)
                self.default_start_message += f"{os.linesep}{os.linesep}{await self.get_help_text(language_code, user_id)}"
        
        except Exception as e:
            logger.error(f"Error in set_start_message: {e}")
            return f'Sorry, we encountered an error: {e}'            
    
    async def set_admin_commands(self):
        """Set the admin commands to the bot menu

        Args:
            bot (_type_): _description_
            admin_id_list (_type_): _description_
            admin_commands (_type_): _description_
        """
        
        try:
            # for all admin users set the scope of the commands to chat_id
            for admin_id in self.admins_owner:
                await self.application.bot.set_my_commands(self.all_commands, scope={'type': 'chat', 'chat_id': admin_id})
                
        except Exception as e:
            logger.error(f"Error setting admin commands: {e}")
            return f'Sorry, we have a problem setting admin commands: {e}'
    
    async def send_admins_message(self, message: str, *args, **kwargs):
        """Send a message to all admin users

        Args:
            message (str): _description_
        """
        
        try:
            # send message to all admin users
            for admin_id in self.admins_owner:
                await self.application.bot.send_message(chat_id=admin_id, text=message)
            
        except Exception as e:
            logger.error(f"Error sending message to admin users: {e}")
            return f'Sorry, we have a problem sending message to admin users: {e}'
    
    async def cmd_show_config(self, update: Update, context: CallbackContext, *args, **kwargs):
        """Show the bot configuration settings

        Args:
            update (Update): _description_
            context (CallbackContext): _description_
        """
        
        try:           
            
            self.links_string = os.environ.get('USEFUL_LINKS', '')
            self.links_list = self.links_string.split(',') if self.links_string else []          
             
            self.show_config_message = f"""*Bot Configuration Settings*{os.linesep}
_Bot Name:_ `{self.bot_name}`
_Bot Owner:_ `{self.bot_owner}`
_Bot Admins:_ `{self.admin_id_string if self.admin_id_string else ''}`
_Default Language Code:_ `{self.default_language_code}`
_Decrypted Token:_ `{self.token}`
_Links:_ 
{self.links_string.replace(',', os.linesep)}"""

            await update.message.reply_text(self.show_config_message, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Error in cmd_show_config: {e}")
            await update.message.reply_text(f"Sorry, we encountered an error: {e}")
    
    async def cmd_show_env(self, update: Update, context: CallbackContext, *args, **kwargs):
        """Show the bot environment settings

        Args:
            update (Update): _description_
            context (CallbackContext): _description_
        """
        
        try:
            # Load the .env file into a dictionary
            env_vars = dotenv.dotenv_values(self.env_file)
            
            # convert dictionary to string
            env_vars_str = os.linesep.join([f"`{key}`=`{value}`" for key, value in env_vars.items()])
            
            self.show_env_message = f"""*Bot Environment Settings*{os.linesep}
{env_vars_str}
{self.links_string.replace(',', os.linesep)}"""

            await update.message.reply_text(self.show_env_message, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Error in cmd_show_env: {e}")
            await update.message.reply_text(f"Sorry, we encountered an error: {e}")
    
    def add_or_update_env_setting(self, key, value):
        """Function to add or update a setting in the .env file

        Args:
            key (_type_): _description_
            value (_type_): _description_
        """
        
        # Read the existing .env file
        if os.path.exists(self.env_file):
            with open(self.env_file, 'r') as file:
                lines = file.readlines()
        else:
            lines = []

        # Check if the key already exists
        key_exists = False
        for i, line in enumerate(lines):
            if line.startswith(f"{key}="):
                lines[i] = f"{key}={value}\n"
                key_exists = True
                break

        # If the key does not exist, add it
        if not key_exists:
            lines.append(f"{key}={value}\n")

        # Write the updated content back to the .env file
        with open(self.env_file, 'w') as file:
            file.writelines(lines)    
    
    def get_command_handlers(self, *args, **kwargs):
        
        command_dict = {}
            
        try:
            for handler_group in self.application.handlers.values():                    
                    for handler in handler_group:
                        try:
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
                            continue
        
        except Exception as e:
            logger.error(f"Error getting command description: {e}")
            return f'Sorry, we have a problem getting the command description: {e}'
        
        return command_dict
    
    async def get_help_text(self, language_code = None, current_user_id = None):
        """Generates a help text from bot commands already set and the command handlers

        Args:
            language_code (_type_, optional): _description_. Defaults to None.
            current_user_id (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        
        try: 
            # set admin commands        
            await self.set_admin_commands()
                
            # get all commands from bot commands menu scope=BotCommandScopeDefault()
            self.common_users_commands = await self.application.bot.get_my_commands()
            self.admin_commands = await self.application.bot.get_my_commands(scope={'type': 'chat', 'chat_id': self.admins_owner[0]}) if self.admins_owner else []
            
            self.all_commands = tuple(list(self.common_users_commands) + list(self.admin_commands))
            
            language_code = self.default_language_code if not language_code else language_code
            
            self.help_text = translations.get_translated_message(language_code, 'help_message', self.default_language_code, self.application.bot.name)           
            
            for command in self.common_users_commands:
                self.help_text += f"/{command.command} - {command.description}{os.linesep}"
                
            # get a dictionary of command handlers
            command_dict = self.get_command_handlers()
            
            # convert the commands dictionary into help text and update command menu
            for command_name, command_data in command_dict.items():
                flag_admin = '👑' if command_data['is_admin'] else ' '
                try:
                    if command_name not in [bot_command.command for bot_command in self.common_users_commands]:
                        if command_data['is_admin']:
                            if current_user_id in self.admins_owner:
                                self.help_text += f"/{command_name} {flag_admin} - {command_data['command_description']}{os.linesep}"
                                
                                # add command got from command handler to telegram menu commands only to specific admin user
                                admin_commands_list = list(self.admin_commands)
                                admin_commands_list.append(BotCommand(command_name, command_data['command_description']))
                                self.admin_commands = tuple(admin_commands_list)
                                
                        else:
                            command_description = command_data['command_description']
                            self.help_text += f"/{command_name} {flag_admin} - {command_description}{os.linesep}" 
                            
                            # Add command got from command handler to telegram menu commands
                            users_commands_list = list(self.common_users_commands)
                            users_commands_list.append(BotCommand(command_name, command_description))
                            self.common_users_commands = tuple(users_commands_list)
                        
                        self.all_commands = tuple(list(self.common_users_commands) + list(self.admin_commands)) 

                except Exception as e:
                    logger.error(f"Error adding command to menu: {e}")
                    continue
                               
            # if sort is enabled, convert help text to a list of strings and order list by command name
            if self.sort_commands: 
                help_header = self.help_text.split(os.linesep)[0]
                help_text_list = self.help_text.split(os.linesep)[1:]
                help_text_list = sorted(help_text_list)
                self.help_text = f'{help_header}{os.linesep}{os.linesep.join(help_text_list)}'            
                
            # set new commands to telegram bot menu
            await self.application.bot.set_my_commands(self.common_users_commands)
            
            # concatenate tuples of admin and user commands                       
            await self.application.bot.set_my_commands(self.all_commands, scope={'type': 'chat', 'chat_id': self.bot_owner})
            
            # for all admin users set the scope of the commands to chat_id
            await self.set_admin_commands()
            
            # double check
            self.common_users_commands = await self.application.bot.get_my_commands()
            self.all_commands = await self.application.bot.get_my_commands(scope={'type': 'chat', 'chat_id': self.bot_owner})
                        
            return self.help_text
        
        except Exception as e:
            logger.error(f"Error getting commands: {e}")
            return f'Sorry, we have a problem getting the commands: {e}'
    
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
            
            if input_token:
                token = input_with_timeout("You have 30 sec. to enter the bot token: ", 30)
                if self.validate_token(token, quit_if_error, False):
                    self.token = token
                    # self.bot_owner = int(input_with_timeout("You have 30 sec. to enter the bot owner id: ", 30))
                    self.bot_owner = int(input_with_timeout("You have 30 sec. to enter the bot owner id: ", 30))
                    # clear entire .env file
                    os.remove(self.env_file)
                    open(self.env_file, 'w').close()
                    dotenv.set_key(self.env_file, 'DEFAULT_BOT_TOKEN', self.token)
                    # dotenv.set_key(self.env_file, 'DEFAULT_BOT_OWNER', int(self.bot_owner)) 
                    self.add_or_update_env_setting('DEFAULT_BOT_OWNER', self.bot_owner)
                    
                    dotenv.load_dotenv(self.env_file)
                                       
                    return True
                
            if quit_if_error:
                input_with_timeout("Enter to close: ", 10)
                quit()
                
            return None
    
    def check_encrypt(self, decrypted_token: str = None, decrypted_bot_owner: str = None, decrypt_key = None, encrypted_token: str = None, encrypted_bot_owner: str = None):             
            
        def decrypt(encrypted_token, key):
            f = Fernet(key)
            # key = base64.urlsafe_b64decode(key.encode()).decode()
            # key = key.encode()
            # # Decrypt the string
            # decrypted_string = fernet.decrypt(encrypted_string).decode()
            # decrypted_token = f.decrypt(token.encode()).decode()
            decrypted_token = f.decrypt(encrypted_token).decode()
            return decrypted_token
        
        # encrypt the token and store it in the .env file
        def encrypt(decrypted_token, key):           
            f = Fernet(key)
            # Fernet key must be 32 url-safe base64-encoded bytes.
            # key = base64.urlsafe_b64decode(key.encode())
            # # Encrypt the string
            # encrypted_string = fernet.encrypt(original_string.encode()) 
            # encrypted_token = f.encrypt(decrypted_token.encode()).decode()
            encrypted_token = f.encrypt(decrypted_token.encode())
            return encrypted_token
        
        self.encrypt_ascii_key = os.environ.get('ENCRYPT_KEY', None) if not decrypt_key else decrypt_key 
            
        # First time, if there is not a crypto key yet, generate it and encrypt the token and save back to the .env file
        if not self.encrypt_ascii_key:
            
            # Define a literal string
            literal_string = "mysecretpassword1234567890123456"  # Must be 32 characters

            # Convert the literal string to bytes
            key_bytes = literal_string.encode()

            # Encode the byte string in URL-safe base64 format
            key = base64.urlsafe_b64encode(key_bytes)
                        
            # Convert key_bytes back to string literal
            key_string_literal = key_bytes.decode('utf-8')            

            # Encrypt a string
            fernet = Fernet(key) 
            
            # ------------------------------           
            
            self.token = os.environ.get('DEFAULT_BOT_TOKEN', None) if not decrypted_token else decrypted_token
            self.bot_owner = int(os.environ.get('DEFAULT_BOT_OWNER', None)) if not decrypted_bot_owner else int(decrypted_bot_owner)
                        
            self.encrypt_byte_key = key # Fernet.generate_key() # key 
            self.encrypt_ascii_key =  base64.urlsafe_b64encode(self.encrypt_byte_key).decode()     
            
            # update the .env file with the encrypted token
            self.encrypted_token = encrypt(self.token, self.encrypt_byte_key).decode()
            dotenv.set_key(self.env_file, 'ENCRYPTED_BOT_TOKEN', self.encrypted_token) 
            
            # update the .env file with the encrypted bot owner and the key
            self.encrypted_bot_owner = encrypt(str(self.bot_owner), self.encrypt_byte_key).decode()
            dotenv.set_key(self.env_file, 'ENCRYPTED_BOT_OWNER', self.encrypted_bot_owner) 
            
            # save the new encryption key to the .env file
            dotenv.set_key(self.env_file, 'ENCRYPT_KEY', self.encrypt_ascii_key) 
            
            # remove the decrypted token and the bot owner from the .env file
            dotenv.unset_key(self.env_file, 'DEFAULT_BOT_TOKEN')
            dotenv.unset_key(self.env_file, 'DEFAULT_BOT_OWNER')  
            
        else: 
            
            self.encrypted_token = os.environ.get('ENCRYPTED_BOT_TOKEN', None) if not encrypted_token else encrypted_token
            self.encrypted_bot_owner = os.environ.get('ENCRYPTED_BOT_OWNER', None) if not encrypted_bot_owner else int(decrypted_bot_owner)              
            
            self.encrypt_byte_key = base64.urlsafe_b64decode(self.encrypt_ascii_key.encode())
            
            # key_string_literal = key_bytes.decode('utf-8')  
            
            # Decrypt the token got from the .env file
            self.token = decrypt(self.encrypted_token, self.encrypt_byte_key)
            self.bot_owner = int(decrypt(str(self.encrypted_bot_owner), self.encrypt_byte_key)) 
    
    # --------------- Init stop bot event handlers--------------------

    async def post_init(self, application: Application) -> None:   

        try:
            self.bot_name = application.bot.username
            
            post_init_message = await self.get_init_message() 
            logger.info(f"{post_init_message}") 
            
            await self.set_start_message(self.default_language_code, 'Admin', self.admins_owner[0])
            
            post_init_message += f"{os.linesep}{os.linesep}{self.default_start_message}"
             
            self.common_users_commands = await application.bot.get_my_commands(scope=BotCommandScopeDefault())            
            logger.info(f"Get Current commands: {self.common_users_commands}")
            
            self.admin_commands = await application.bot.get_my_commands(scope={'type': 'chat', 'chat_id': self.admins_owner[0]}) if self.admins_owner else []
            
            self.all_commands = tuple(list(self.common_users_commands) + list(self.admin_commands))
            
            # for all admin users set the scope of the commands to chat_id
            await self.send_admins_message(message=post_init_message)
            
        except Exception as e:
            logger.error(f"Error: {e}")

    async def post_stop(self, application: Application) -> None:
        
        try:            
            # force persistence of all bot data
            self.application.persistence.flush() if self.application.persistence else None
            
            stop_message = f"_STOPPING_ @{self.bot_name} {os.linesep}`{self.hostname}`{os.linesep}`{__file__}` {self.bot_name}..."
            logger.info(stop_message)
                     
            await self.send_admins_message(message=stop_message)
            
        except Exception as e:
            logger.error(f"Error: {e}")
                
        sys.exit(0)

    # --------------- Payment handlers --------------------
    
    # after (optional) shipping, it's the pre-checkout
    async def precheckout_callback(update: Update, context: CallbackContext) -> None:
        try:
            query = update.pre_checkout_query
            # check the payload, is this from your bot?
            if query.invoice_payload != 'Custom-Payload':
            # answer False pre_checkout_query
                await query.answer(ok=False, error_message="Erro no processamento do pagamento!")
            else:
                await query.answer(ok=True)
            
        except Exception as e:
            logger.error(f"Error in precheckout_callback: {e}")
            await query.answer(ok=False, error_message="An unexpected error occurred during payment processing.")
       
    # ---------------- Bot constructor and initializers -------    
    
    def __init__(self, 
        token: str = None,
        validate_token = True,
        quit_if_error = True,
        env_file: str = '.env', 
        bot_owner: str = None, 
        bot_defaults_build = Defaults(parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True), 
        disable_default_handlers = False,
        default_language_code = None,
        decrypt_key = None,
        disable_encryption = True,
        admin_id_list: list[int] = None,
        links: list[str] = [],
        persistence_file: str = None,
        disable_persistence = False,
        default_persistence_interval = 10,
        logger = logger,
        sort_commands = False,
        enable_plugins = False,
        ):
        
        try: 
            self.hostname = socket.getfqdn()
            self.main_script_path = sys.argv[0]
            self.bot_name = None
             
            self.env_file = env_file if env_file else '.env'
            self.logger = logger 
            self.token = token if token else ''
            self.bot_owner = bot_owner if bot_owner else ''
            
            # self.admin_id_string = [int(admin_id) for admin_id in os.environ.get('ADMIN_ID_LIST', '').split(',')]  
            self.admin_id_string = admin_id_list if admin_id_list else os.environ.get('ADMIN_ID_LIST', '')
            
            self.all_commands = []            
            self.sort_commands = sort_commands
            
            self.default_persistence_interval = default_persistence_interval

            # Create an empty .env file at run time if it does not exist
            if self.env_file and not os.path.exists(self.env_file):
                open(self.env_file, 'w').close() 
                # and add en empty line with token and bot owner
                dotenv.set_key(self.env_file, 'DEFAULT_BOT_TOKEN',self.token)
                # dotenv.set_key(self.env_file, 'DEFAULT_BOT_OWNER',self.bot_owner)            
            
            dotenv.load_dotenv(self.env_file)
            self.token = os.environ.get('DEFAULT_BOT_TOKEN', None) if not self.token else self.token
            self.bot_owner = int(os.environ.get('DEFAULT_BOT_OWNER', 999999)) if not self.bot_owner else self.bot_owner 
                 
            # read list of admin users from the .env file
            default_list = [self.bot_owner] + [int(admin_id) for admin_id in (self.admin_id_string.split(',') if self.admin_id_string else [])]
            default_str = ','.join(map(str, default_list))
            self.admins_owner = [int(admin_id) for admin_id in os.environ.get('ADMIN_ID_LIST', default_str).split(',')]
            
            if validate_token:            
                self.validate_token(self.token, quit_if_error)  
            
            if not disable_encryption:
                # If there is a crypto key, decrypt the token and the bot_owner got from the .env file
                self.check_encrypt(token, bot_owner, decrypt_key)
            else:
                self.token = os.environ.get('DEFAULT_BOT_TOKEN', None) if not self.token else self.token
                self.bot_owner = int(os.environ.get('DEFAULT_BOT_OWNER', None)) if not self.bot_owner else int(self.bot_owner)
                               
            self.default_language_code = os.environ.get('DEFAULT_LANGUAGE_CODE', 'en-US') if not default_language_code else default_language_code
            
            self.disable_default_handlers = os.environ.get('DISABLE_DEFAULT_HANDLERS', False) if not disable_default_handlers else disable_default_handlers
            
            self.links_string=os.linesep.join(links) if links else os.environ.get('USEFUL_LINKS', '') 
            self.links_list = self.links_string.split(',') if self.links_string else [] 
            dotenv.set_key(dotenv_path=self.env_file, key_to_set='USEFUL_LINKS', value_to_set=self.links_string)
            
            self.bot_defaults_build = bot_defaults_build 
            
            # ---------- Build the bot application ------------
              
            # Making bot persistant from the base class      
            # https://github.com/python-telegram-bot/python-telegram-bot/wiki/Making-your-bot-persistent
            self.persistence_file = f"{script_path}{os.sep}{self.bot_info.username + '.pickle'}" if not persistence_file else persistence_file
            persistence = PicklePersistence(filepath=self.persistence_file, update_interval=self.default_persistence_interval) if not disable_persistence else None
            
            # Create an Application instance using the builder pattern            
            self.application = Application.builder().defaults(bot_defaults_build).token(self.token).post_init(self.post_init).post_stop(self.post_stop).persistence(persistence).build() 
            
            # --------------------------------------------------
            
            # save botname to .env file
            dotenv.set_key(self.env_file, 'BOT_NAME', self.bot_info.username)                      
            
            self.initialize_handlers()
            
            # -------------------------------------------  
            
            self.enable_plugins = enable_plugins          
             
            if enable_plugins:
                try:                    
                    # self.plugin_manager = PluginManager(plugins_dir)
                    self.plugin_manager = PluginManager()
                    self.plugin_manager.load_plugins()     
                    
                except Exception as e:
                    logger.error(f"Error in plugin manager: {e}") 
            # -------------------------------------------
            
        except Exception as e:
            logger.error(f"Error initializing bot: {e}")
            input_with_timeout("Enter to close: ", 10)
            quit()

    def initialize_handlers(self):
        
        try:
            # handles global errors
            self.application.add_error_handler(self.error_handler)
            
            if not self.disable_default_handlers:
                self.logger.info("Default handlers enabled")
            
                # Adding a simple command handler for the /start command
                start_handler = CommandHandler('start', self.default_start_handler)
                self.application.add_handler(start_handler)
                
                help_handler = CommandHandler('help', self.default_help_handler)
                self.application.add_handler(help_handler) 
            
            else:
                self.logger.info("Default handlers disabled")
            
            # handler for the /lang command to set the default language code
            set_language_code_handler = CommandHandler('lang', self.set_default_language, filters=filters.User(user_id=self.admins_owner))
            self.application.add_handler(set_language_code_handler)
            
            # add handler for the /userlang command to set the user language code
            set_user_language_handler = CommandHandler('userlang', self.set_user_language)
            self.application.add_handler(set_user_language_handler)
            
            # add handler for the /git command to update the bot's code from a git repository
            git_handler = CommandHandler('git', self.cmd_git, filters=filters.User(user_id=self.admins_owner))
            self.application.add_handler(git_handler)
            
            # add handler for the /restart command to restart the bot
            restart_handler = CommandHandler('restart', self.restart_bot, filters=filters.User(user_id=self.admins_owner))
            self.application.add_handler(restart_handler)
            
            # add handler for the /stop command to stop the bot
            stop_handler = CommandHandler('stop', self.stop_bot, filters=filters.User(user_id=self.admins_owner))
            self.application.add_handler(stop_handler)
            
            # add handler for the /showconfig command to show the bot configuration settings
            show_config_handler = CommandHandler('showconfig', self.cmd_show_config, filters=filters.User(user_id=self.admins_owner))
            self.application.add_handler(show_config_handler)
            
            # add version command handler
            version_handler = CommandHandler('version', self.cmd_version_handler, filters=filters.User(user_id=self.admins_owner))
            self.application.add_handler(version_handler)
            
            # add admin manage command handler
            admin_manage_handler = CommandHandler('admin', self.cmd_manage_admin, filters=filters.User(user_id=self.admins_owner))
            self.application.add_handler(admin_manage_handler)
            
            # add useful links command handler
            useful_links_handler = CommandHandler('links', self.cmd_manage_links)
            self.application.add_handler(useful_links_handler)
            
            # add show env command handler
            show_env_handler = CommandHandler('showenv', self.cmd_show_env, filters=filters.User(user_id=self.admins_owner))
            self.application.add_handler(show_env_handler)
            
            # add show pickle command handler
            show_pickle_handler = CommandHandler('showpickle', self.cmd_show_pickle, filters=filters.User(user_id=self.admins_owner))
            self.application.add_handler(show_pickle_handler)
            
            # add force persistence command handler
            force_persistence_handler = CommandHandler('forcepersistence', self.cmd_force_persistence, filters=filters.User(user_id=self.admins_owner))
            self.application.add_handler(force_persistence_handler)
            
            # Add admin command to show users from persistence file
            show_users_handler = CommandHandler('showusers', self.cmd_show_users, filters=filters.User(user_id=self.admins_owner))
            self.application.add_handler(show_users_handler)
            
            self.application.add_handler(CommandHandler("payment", self.cmd_payment)) 
            
            # add handler for the /loadplugin command to load a plugin dynamically
            load_plugin_handler = CommandHandler('loadplugin', self.cmd_load_plugin, filters=filters.User(user_id=self.admins_owner))
            self.application.add_handler(load_plugin_handler)
            
            # Add handler for the /showcommands command to show the commands available to the user and admin
            show_commands_handler = CommandHandler('showcommands', self.cmd_show_commands, filters=filters.User(user_id=self.admins_owner))
            self.application.add_handler(show_commands_handler)
            
            # Add handler for the /showbalance command to show the current user's balance
            show_balance_handler = CommandHandler('showbalance', self.cmd_show_balance)
            self.application.add_handler(show_balance_handler)
            
            # Pre-checkout handler to final check
            self.application.add_handler(PreCheckoutQueryHandler(precheckout_callback))            
            
            self.application.add_handler(MessageHandler(filters.COMMAND, self.default_unknown_command))
            
        except Exception as e:
            logger.error(f"Error initializing handlers: {e}")
            for admin_id in self.admins_owner:
                try:
                    self.send_message_sync(chat_id=admin_id, message=f"Error initializing handlers: {e}")
                except Exception as e:
                    logger.error(f"Error sending warning to admin {admin_id}: {e}")
            return f'Sorry, we have a problem initializing handlers: {e}'
    
    @with_writing_action_sync
    def send_message_sync(self, chat_id: int, message: str):
        """Send a message synchronously

        Args:
            chat_id (int): _description_
            message (str): _description_
        """
        
        try:
            try:
                result = self.loop.run_until_complete(self.application.bot.send_message(chat_id=chat_id, text=message))
            except Exception as e:
                logger.error(f"Error sending message with markdown: {e}")
                result = self.loop.run_until_complete(self.application.bot.send_message(chat_id=chat_id, text=message, parse_mode=None))
                        
            return result
        
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return f'Sorry, we have a problem sending message: {e}'
       
    # -------- Default command handlers --------
    
    @with_writing_action
    @with_log_admin
    async def cmd_show_balance(self, update: Update, context: CallbackContext):
        """Show the current user's balance

        Args:
            update (Update): The update object
            context (CallbackContext): The callback context
        """
        try:
            user_id = update.effective_user.id
            
            # Get user data from persistence
            user_data = await self.application.persistence.get_user_data() if self.application.persistence else None
            bot_data = await self.application.persistence.get_bot_data() if self.application.persistence else None
            
            # Then get the balance from the user data
            balance = user_data.get('balance', 0) if user_data else 0

            message = f"_Your current balance is: _`${balance:,.2f}`"
            await update.message.reply_text(message)
            
        except Exception as e:
            logger.error(f"Error showing balance: {e}")
            await update.message.reply_text(f"Sorry, we encountered an error: {e}")
    
    @with_writing_action
    @with_log_admin
    async def cmd_show_commands(self, update: Update, context: CallbackContext):
        """Show the commands available to the user and admin

        Args:
            update (Update): The update object
            context (CallbackContext): The callback context
        """
        
        def get_command_line(command):
            return f"/{command.command} - {command.description}"
        
        try:
            user_id = update.effective_user.id
            is_admin = user_id in self.admins_owner

            common_commands = [get_command_line(cmd) for cmd in self.common_users_commands]
            admin_commands = [get_command_line(cmd) for cmd in self.admin_commands if cmd not in self.common_users_commands]
            
            # order by name
            common_commands.sort()
            admin_commands.sort()
            
            message = f"_User Commands:_{os.linesep}{os.linesep.join(common_commands)}"
            
            if is_admin:
                message += f"{os.linesep}{os.linesep}_Admin Commands:_{os.linesep}{os.linesep.join(admin_commands)}"

            await update.message.reply_text(message)
            
        except Exception as e:
            logger.error(f"Error showing commands: {e}")
            await update.message.reply_text(f"Sorry, we encountered an error: {e}")
    
    @with_writing_action
    @with_log_admin
    async def cmd_load_plugin(self, update: Update, context: CallbackContext):
        """Load a plugin dynamically

        Args:
            update (Update): _description_
            context (CallbackContext): _description_
        """
        
        try:
            if not context.args:
                self.plugin_manager.load_plugins() 
                await update.message.reply_text("_All plugins loaded!_.")
                return
            
            plugin_name = context.args[0]
            self.plugin_manager.load_plugin(plugin_name)
            
            message = f"Plugin {plugin_name} loaded successfully."
            await update.message.reply_text(message)
            
        except Exception as e:
            logger.error(f"Error loading plugin: {e}")
            await update.message.reply_text(f"Sorry, we encountered an error: {e}")

    @with_writing_action
    @with_log_admin        
    async def cmd_payment(self, update: Update, context: CallbackContext) -> None:
        """Receive and process payments

        Args:
            update (Update): _description_
            context (CallbackContext): _description_
        """
        
        try:            
            user_language = update.effective_user.language_code
            
            chat_id = update.effective_message.chat_id
            title = DEFAULT_STRIPE_TITLE
            description = DEFAULT_STRIPE_DESCRIPTION
            currency = DEFAULT_STRIPE_CURRENCY
            
            # select a payload just for you to recognize its the donation from your bot
            payload = DEFAULT_STRIPE_PAYLOAD
            
            # In order to get a provider_token see https://core.telegram.org/bots/payments#getting-a-token
            provider_token = DEFAULT_STRIPE_LIVE_TOKEN if DEFAULT_STRIPE_MODE != 'test' else DEFAULT_STRIPE_TEST_TOKEN
            start_parameter = DEFAULT_STRIPE_START_PARAMETER
            
            price = DEFAULT_STRIPE_PRICE
            
            if user_language != DEFAULT_LANGUAGE:
                title = 'Add credits to use the Bot'
                description = 'Click the "Pay" below to purchase credits:'        
                currency = 'USD'
                price = 1
            
            if context.args and len(context.args) > 0 and context.args[0].isnumeric():
                    price = int(context.args[0])
            elif context.args and len(context.args) > 0 and not context.args[0].isnumeric():
                # Handle the case when the parameter is not numeric
                # For example, you can set a default price or display an error message
                price = DEFAULT_STRIPE_PRICE
                update.effective_chat.send_message(text="Invalid price. Please provide a numeric value.")
                return
                
            # price * 100 so as to include 2 decimal points        
            price = price * 100
            
            prices: List[LabeledPrice] = [LabeledPrice('Comprar créditos para consulta', price)]

            await context.bot.send_invoice(
                chat_id=chat_id,
                title=title,
                description=description,
                payload=payload,
                provider_token=provider_token,
                start_parameter=start_parameter,
                currency=currency,
                prices=prices  # Ensure this is the only place 'prices' is mentioned
            )
        
        except Exception as e:
            # Currency_total_amount_invalid
            logging.error(str(e))
            try:
                message = f'_Sorry! The payment failed. Please try again later._'
                await context.bot.send_message(chat_id=update.effective_user.id, text=message)
                
                message = f'`{update.effective_user.id}`_: Error on payment:_{os.linesep}`{e.message.replace("_"," ")}`'
                await context.bot.send_message(chat_id=bot_user_admin, text=message)
            except Exception as ex:
                logging.error(str(ex))    
    
    @with_writing_action
    @with_log_admin
    async def cmd_show_users(self, update: Update, context: CallbackContext):
        """Show the users from the persistence file

        Args:
            update (Update): The update object
            context (CallbackContext): The callback context
        """
        
        def format_string(input_string, max_length=20):
            # Truncate the string to a maximum length of 20 characters
            truncated_string = input_string[:max_length]
            
            # Fill the string with spaces if it is less than 20 characters
            formatted_string = truncated_string.ljust(max_length)
            
            return formatted_string        
        
        def get_user_line(user):
            
            # Get the user data buffer from bot context
            last_message = context.bot_data['user_status'][user.id]['last_message_date'] if 'user_status' in context.bot_data and user.id in context.bot_data['user_status'] else (datetime.datetime.now()+ timedelta(hours=-3)).strftime('%d/%m %H:%M')      
            
            # Get the user line
            flag_admin = '👑' if user.id in self.admins_owner else ' '
            user_line = f"`{str(user.id):<11}` `{str(user.full_name)[:20]:<20}`  `{last_message}`  {format_string(user.name)}"
            user_line = f"`{str(user.full_name)[:12]:<12}` `{last_message}` {format_string(user.name,15)}"
            user_line = f"`{str(user.id)[:10]:<10}` `{last_message}` {user.name} {flag_admin}"
            
            return user_line
        
        try:
            # Get the user dictionary from the bot data
            all_users_data = context.bot_data.get('user_dict', {})
            
            # Check if there are any users in the dictionary
            if all_users_data:
                user_names = [get_user_line(user) for user in all_users_data.values()]               
                # Create a message with the user names
                message = f"_Current active bot users:_{os.linesep}" + os.linesep.join(user_names)
            else:
                message = "No users found in the persistence file."
            
            # Send the message to the user
            await update.message.reply_text(message)
            
        except Exception as e:
            logger.error(f"Error in cmd_show_users: {e}")
            await update.message.reply_text(f"Sorry, we encountered an error: {e}")    
    
    @with_writing_action
    @with_log_admin
    async def cmd_force_persistence(self, update: Update, context: CallbackContext):
        """Force the bot to save the persistence file

        Args:
            update (Update): _description_
            context (CallbackContext): _description_
        """
        
        try: 
            # Set up persistence with a custom store interval (e.g., 60 seconds)
            # persistence = PicklePersistence(filepath=self.persistence_file, update_interval=5)
            # context.application.persistence = persistence
                                    
            # context.application.persistence.store_data = True  
               
            context.bot_data['force_save'] = True
            context.application.persistence.update_bot_data(context.bot_data) if context.application.persistence else None
            await context.application.persistence.flush()
            
            # await asyncio.sleep(5)
            
            await update.message.reply_text('Persistence file has been saved.') 
            
            # # return persistence to 60 seconds interval
            # persistence = PicklePersistence(filepath='bot_data.pickle', update_interval=self.default_persistence_interval)
            # context.application.persistence = persistence           
            
        except Exception as e:
            logger.error(f"Error in cmd_force_persistence: {e}")
            await update.message.reply_text(f"Sorry, we encountered an error: {e}")
    
    @with_writing_action
    @with_log_admin
    async def cmd_show_pickle(self, update: Update, context: CallbackContext):
        """Show the bot persistence file

        Args:
            update (Update): _description_
            context (CallbackContext): _description_
        """
                        
        # Define the persistent_load function
        def persistent_load(persid):
            # Handle the persistent ID
            # For example, you can return a default value or raise an error
            if persid == "a known bot replaced by PTB's PicklePersistence":
                return persid
            # else:
            #     raise pickle.UnpicklingError(f"Unsupported persistent id: {persid}")     
                    
        try:  
            # in case the persistence file does not exist, warn the user
            if not os.path.exists(self.persistence_file):
                await update.message.reply_text(f"_Persistence file not found:_ {os.linesep}`{self.persistence_file}`")
                return
                             
            # Read the bot .pickle persistence file and show it to the user
            with open(self.persistence_file, 'rb') as file:
                unpickler = pickle.Unpickler(file)
                unpickler.persistent_load = persistent_load
                pickle_data = unpickler.load()                       
                
            # First, serialize bot data with a custom encoder because it is a telegram bot user that is not serializable
            bot_data = next(iter(pickle_data['bot_data']['user_dict'].values()))
            serialized_bot_data = json.dumps(bot_data, cls=TelegramObjectEncoder, indent=4) 
            print(f"JSON data: {serialized_bot_data}") 
                       
            # Format bot data as json snippet and show to telegram user
            formatted_json = f"```json\n{serialized_bot_data}\n```"
            print(f"JSON data: {formatted_json}")
            await update.message.reply_text(f"_Bot data:_ {os.linesep}{formatted_json}")
            
            # Now, remove the item 'bot_data" from the dictionary because it was already shown
            pickle_data.pop('bot_data')  
                      
            # Then serialize the rest of all other items of dictionary data with default encoder    
            serialized_other_data = json.dumps(pickle_data, indent=4) 
            print(f"JSON data: {serialized_other_data}") 
            
            # Then format them as json snippet and show it to the telegram user
            formatted_json = f"```json\n{serialized_other_data}\n```"
            print(f"JSON data: {formatted_json}")
            await update.message.reply_text(f"_Chat and User data:_ {os.linesep}{formatted_json}")
            
        except Exception as e:
            logger.error(f"Error in cmd_show_env: {e}")
            await update.message.reply_text(f"Sorry, we encountered an error: {e}", parse_mode=None)
    
    @with_writing_action
    @with_log_admin
    async def cmd_manage_links(self, update: Update, context: CallbackContext) :
        """Manage the useful links of the bot

        Args:
            update (Update): _description_
            context (CallbackContext): _description_
        """
        
        try:
            # command with parameters is only allowed to admin users
            if len(update.message.text.split(' ')) > 1 and update.effective_user.id in self.admins_owner:
                link = update.message.text.split(' ')[1]
                
                if link not in self.links_list:
                    self.links_list.append(link)
                    await update.message.reply_text(f"_Link added:_ {os.linesep}{link}")
                else:
                    self.links_list.remove(link)
                    await update.message.reply_text(f"_Link removed:_ {link}")
                
                #  save the new list of useful links to the .env file
                self.links_string = ','.join(self.links_list)
                dotenv.set_key(self.env_file, 'USEFUL_LINKS', ','.join(self.links_list))
            
            # convert the list of useful links to a line feeded string          
            useful_links_str = os.linesep.join(self.links_list)
            await update.message.reply_text(f"_Useful links:_ {os.linesep}{useful_links_str}")
            
        except Exception as e:
            logger.error(f"Error: {e}")
            await update.message.reply_text(f"An error occurred: {e}")
    
    @with_writing_action
    @with_log_admin
    async def cmd_manage_admin(self, update: Update, context: CallbackContext, *args, **kwargs):
        """Manage the admin users of the bot

        Args:
            update (Update): _description_
            context (CallbackContext): _description_
        """
        
        try:
            if len(update.message.text.split(' ')) > 1:
                owner_list = int(update.message.text.split(' ')[1])
                
                if owner_list not in self.admins_owner:
                    self.admins_owner.append(owner_list)
                    await self.set_admin_commands()
                    await update.message.reply_text(f"_Admin user added:_ `{owner_list}`")
                else:
                    if owner_list == self.bot_owner:
                        await update.message.reply_text(f"_Bot owner cannot be removed:_ `{owner_list}`")
                    else:
                        self.admins_owner.remove(owner_list)
                        await self.set_admin_commands()
                        await update.message.reply_text(f"_Admin user removed:_ `{owner_list}`")

                # dotenv.set_key(self.env_file, 'ADMIN_ID_LIST', self.admins_owner)
                dotenv.set_key(self.env_file, 'ADMIN_ID_LIST', ','.join(map(str, self.admins_owner)))
                                    
            else:
                await update.message.reply_text(f"_Admin users:_ `{self.admins_owner}`")                  
            
        except Exception as e:
            logger.error(f"Error: {e}")
            await update.message.reply_text(f"An error occurred: {e}")  
    
    @with_writing_action
    @with_log_admin
    async def cmd_version_handler(self, update: Update, context: CallbackContext, *args, **kwargs):
        """Show the bot version

        Args:
            update (Update): _description_
            context (CallbackContext): _description_
        """
        
        try:
            init_message = await self.get_init_message()
            await update.message.reply_text(init_message)
        except Exception as e:
            logger.error(f"Error: {e}")
        
    @with_writing_action
    @with_log_admin 
    async def set_default_language(self, update: Update, context: CallbackContext, *args, **kwargs):
        """Set the language code for the bot

        Args:
            update (Update): _description_
            context (CallbackContext): _description_
        """
        
        if len(update.message.text.split(' ')) > 1:            
            self.default_language_code = update.message.text.split(' ')[1].lower()
            
        await update.message.reply_text(f"_Default language code set to:_ `{self.default_language_code}`")

    @with_writing_action
    @with_log_admin     
    async def set_user_language(self, update: Update, context: CallbackContext, *args, **kwargs):
        """Set the language code for the user

        Args:
            update (Update): _description_
            context (CallbackContext): _description_
        """
        
        if len(update.message.text.split(' ')) > 1:            
            context.user_data['language_code'] = update.message.text.split(' ')[1].lower()
            
        await update.message.reply_text(f"_User language code set to:_ `{context.user_data.get('language_code', update.effective_user.language_code)}`")
             
    @with_writing_action
    @with_log_admin     
    async def error_handler(self, update: Update, context: CallbackContext) -> None:
        self.logger.error(context.error)
        await self.application.bot.send_message(chat_id=self.bot_owner, text=str(context.error))        

    @with_writing_action
    @with_log_admin        
    async def default_unknown_command(self, update: Update, context: CallbackContext, *args, **kwargs):
        
        self.logger.info(f"Unknown command received from {update.effective_user.name}")
        
        language_code = context.user_data.get('language_code', update.effective_user.language_code)
        reply_message = translations.get_translated_message(language_code, 'command_not_implemented', 'en', update.message.text)   
        
        await update.message.reply_text(reply_message)

    @with_writing_action
    @with_log_admin
    async def default_start_handler(self, update: Update, context: CallbackContext, *args, **kwargs):
        
        try:                
            # if the dictionary of users does not exist on bot_data, create it
            if 'user_dict' not in context.bot_data:
                context.bot_data['user_dict'] = {}
                        
            # force persistence of the bot_data dictionary
            self.application.persistence.update_bot_data(context.bot_data) if self.application.persistence else None
                      
            # set effective language code
            language_code = context.user_data['language_code'] if 'language_code' in context.user_data else update.effective_user.language_code
            
            # force persistence update of the user data
            self.application.persistence.update_user_data(update.effective_user.id, context.user_data) if self.application.persistence else None          
            
            # get user data from persistence
            user_data = await self.application.persistence.get_user_data() if self.application.persistence else None
            
            await self.set_start_message(language_code, update.effective_user.full_name, update.effective_user.id)
                
            await update.message.reply_text(self.default_start_message.format(update.effective_user.first_name))
                
        except Exception as e:
            logger.error(f"Error in default_start_handler: {e}")
            await update.message.reply_text(f"Sorry, we encountered an error: {e}")

    @with_writing_action
    @with_log_admin            
    async def default_help_handler(self, update: Update, context: CallbackContext, *args, **kwargs):        
        
        # TODO: Show embedded help html page
        # append_buttons.append([InlineKeyboardButton('📖 Docs', url="https://telegra.ph/tlgfwk_help"),]) 
        
        language_code = context.user_data.get('language_code', update.effective_user.language_code)
        self.help_text = await self.get_help_text(language_code, update.effective_user.id)
        
        self.logger.info(f"Help command received from {update.effective_user.name}")
        
        # A simple start command response
        await update.message.reply_text(self.help_text)                        

    @with_writing_action
    @with_log_admin
    async def cmd_git(self, update: Update, context: CallbackContext):
        """Update the bot's version from a git repository"""
        
        try:
            # get the branch name from the message
            # branch_name = update.message.text.split(' ')[1]
            message = f"_Updating the bot's code from the branch..._" # `{branch_name}`"
            logger.info(message)
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            
            # update the bot's code
            # command = f"git fetch origin {branch_name} && git reset --hard origin/{branch_name}"
            command = "git status"
            
            if len(update.effective_message.text.split(' ')) > 1:
                git_command = update.effective_message.text.split(' ')[1]
                logger.info(f"git command: {command}")
                command = f"git {git_command}"
            
            # execute system command and return the result
            # os.system(command=command)
            result = os.popen(command).read()
            self.logger.info(f"Result: {result}")
            
            result = f"_Result:_ `{result}`"
            
            await update.message.reply_text(result, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Error: {e}")
            await update.message.reply_text(f"An error occurred: {e}")

    @with_writing_action
    @with_log_admin
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
       
    @with_writing_action
    @with_log_admin            
    async def stop_bot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        
        await update.message.reply_text(f"*{update._bot.username} STOPPED!*", parse_mode=ParseMode.MARKDOWN)

        args = sys.argv[:]
        # args.append('stop')
        # args = ['stop']
        args.insert(0, 'stop')
        args=None
        os.chdir(os.getcwd())
        # os.execv(sys.executable, args) 
        os.abort()        
    
    # ------------------------------------------

    def run(self):
        # Run the bot using the run_polling method
        self.application.run_polling()
        
if __name__ == '__main__':
    
    # ----- How to´s -----
    
    # if first command line argument is "howto" execute the howto´s before starting the bot
    if len(sys.argv) > 1 and sys.argv[1] == 'howto':
        
        # Instantiate the bot with an optional list of useful links
        app = TlgBotFwk(links=['https://github.com/gersonfreire/telegram-bot-framework']) 
        
        # Instantiate the bot without persistence and sort commands list alphabetically
        app = TlgBotFwk(disable_persistence=True, sort_commands=True)
        
        # How to send a direct, synchronously message without start the bot
        result = app.send_message_sync(app.admins_owner[0], f"_This was sent by a direct, synchronously message without start the bot as a how-to example_")
        
        # Test global error handler
        raise Exception("A test error was intentionally raised to test the global error handler")
    
    else:    
        app = TlgBotFwk(enable_plugins=True) 
        
    # ----- Run the bot -----    
    app.run()