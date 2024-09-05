#!/usr/bin/env python
# -*- coding: utf-8 -*-

version = '0.2.5 Save admin list to .env'

# ------------------------------------------

from __init__ import *

import translations.translations as translations

class TlgBotFwk(Application):
    
    # ------------- util functions ------------------
    
    async def get_init_message(self): 
        try:
            post_init_message = f"""@{self.bot_name} *Started!*
_Version:_   `{version}`
_Host:_     `{hostname}`
_CWD:_ `{os.getcwd()}`
_Path:_
`{main_script_path}`"""    
            logger.info(f"{post_init_message}")  
            
            return post_init_message

        except Exception as e:
            logger.error(f"Error in get_init_message: {e}")
            return f'Sorry, we encountered an error: {e}'
    
    async def set_start_message(self, language_code:str, full_name:str, user_id:int): #, update, context):
        try:
            # language_code = context.user_data.get('language_code', update.effective_user.language_code)                           
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
            self.show_config_message = f"""*Bot Configuration Settings*{os.linesep}
_Bot Name:_ `{self.bot_name}`
_Bot Owner:_ `{self.bot_owner}`
_Bot Admins:_ `{self.admin_id_list if self.admin_id_list else ''}`
_Default Language Code:_ `{self.default_language_code}`
_Decrypted Token:_ `{self.token}`"""
# _Encrypted Token:_ `{self.encrypted_token}`
# _Encrypted Bot Owner:_ `{self.encrypted_bot_owner}`

            await update.message.reply_text(self.show_config_message, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Error in cmd_show_config: {e}")
            await update.message.reply_text(f"Sorry, we encountered an error: {e}")
    
    # Function to add or update a setting in the .env file
    def add_or_update_env_setting(self, key, value):
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
    
    async def get_help_text(self, language_code = None, current_user_id = None, *args, **kwargs):
        """Generates a help text from bot commands already set and the command handlers

        Args:
            language_code (_type_, optional): _description_. Defaults to None.
            current_user_id (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        
        try: 
            # clear admin commands           
            await self.application.bot.set_my_commands([], scope={'type': 'chat', 'chat_id': self.bot_owner})            
            await self.set_admin_commands()
                
            # get all commands from bot commands menu scope=BotCommandScopeDefault()
            self.common_users_commands = await self.application.bot.get_my_commands()
            self.all_commands = await self.application.bot.get_my_commands(scope={'type': 'chat', 'chat_id': self.bot_owner})
            self.admin_commands = tuple()
            
            language_code = self.default_language_code if not language_code else language_code
            
            self.help_text = translations.get_translated_message(language_code, 'help_message', self.default_language_code, self.application.bot.name)            
            
            for command in self.common_users_commands:
                self.help_text += f"/{command.command} - {command.description}{os.linesep}"
                
            # get a dictionary of command handlers
            command_dict = self.get_command_handlers()
            
            # convert the commands dictionary into help text and update command menu
            for command_name, command_data in command_dict.items():
                try:
                    if command_name not in [bot_command.command for bot_command in self.common_users_commands]:
                        if command_data['is_admin']:
                            if current_user_id and (command_data['user_allowed'] == current_user_id): # self.bot_owner:
                                self.help_text += f"/{command_name} - {command_data['command_description']}{os.linesep}"
                                
                                # add command got from command handler to telegram menu commands only to specific admin user
                                admin_commands_list = list(self.admin_commands)
                                admin_commands_list.append(BotCommand(command_name, command_data['command_description']))
                                self.admin_commands = tuple(admin_commands_list)
                                
                        else:
                            command_description = command_data['command_description']
                            self.help_text += f"/{command_name} - {command_description}{os.linesep}" 
                            
                            # Add command got from command handler to telegram menu commands
                            users_commands_list = list(self.common_users_commands)
                            users_commands_list.append(BotCommand(command_name, command_description))
                            self.common_users_commands = tuple(users_commands_list)
                        
                        self.all_commands = tuple(list(self.common_users_commands) + list(self.admin_commands)) 

                except Exception as e:
                    logger.error(f"Error adding command to menu: {e}")
                    continue
                
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
            loop = asyncio.get_event_loop()                
            self.bot_info = loop.run_until_complete(bot.get_me())
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

            current_commands = await application.bot.get_my_commands(scope=BotCommandScopeAllPrivateChats())
            logger.info(f"Get Current commands: {current_commands}")    
            current_commands = await application.bot.get_my_commands(scope=BotCommandScopeDefault())
            logger.info(f"Get Current commands: {current_commands}") 
            
            # for all admin users set the scope of the commands to chat_id
            await self.send_admins_message(message=post_init_message)
            
        except Exception as e:
            logger.error(f"Error: {e}")

    async def post_stop(self, application: Application) -> None:
        
        try:
            stop_message = f"_STOPPING_ @{self.bot_name} {os.linesep}`{hostname}`{os.linesep}`{__file__}` {bot_version}..."
            logger.info(stop_message)
                     
            await self.send_admins_message(message=stop_message)
            
        except Exception as e:
            logger.error(f"Error: {e}")
                
        sys.exit(0)

    # ---------------- Bot constructor and initializers -------    
    
    def __init__(self, 
        token: str = None,
        validate_token = True,
        quit_if_error = True,
        env_file: str = '.env', 
        bot_owner: str = None, 
        bot_defaults_build = None, 
        disable_default_handlers = False,
        default_language_code = None,
        decrypt_key = None,
        disable_encryption = True,
        admin_id_list: list[int] = None):
        
        try: 
            self.env_file = env_file 
            self.logger = logger 
            self.token = token if token else ''
            self.bot_owner = bot_owner if bot_owner else ''
            self.admin_id_list = admin_id_list if admin_id_list else []

            # Create an empty .env file at run time if it does not exist
            if not os.path.exists(self.env_file):
                open(self.env_file, 'w').close() 
                # and add en empty line with token and bot owner
                dotenv.set_key(self.env_file, 'DEFAULT_BOT_TOKEN',self.token)
                # dotenv.set_key(self.env_file, 'DEFAULT_BOT_OWNER',self.bot_owner)            
            
            dotenv.load_dotenv(self.env_file)
            self.token = os.environ.get('DEFAULT_BOT_TOKEN', None) if not self.token else self.token
            self.bot_owner = int(os.environ.get('DEFAULT_BOT_OWNER', 999999)) if not self.bot_owner else self.bot_owner 
            
            # Set attribute of main class with a concatenated list of bot owner and admin users
            self.admins_owner = [self.bot_owner] + self.admin_id_list                      
            
            if validate_token:            
                self.validate_token(self.token, quit_if_error)  
            
            if not disable_encryption:
                # If there is a crypto key, decrypt the token and the bot_owner got from the .env file
                self.check_encrypt(token, bot_owner, decrypt_key)
            else:
                self.token = os.environ.get('DEFAULT_BOT_TOKEN', None) if not self.token else self.token
                self.bot_owner = int(os.environ.get('DEFAULT_BOT_OWNER', None)) if not self.bot_owner else int(self.bot_owner)
            
            bot_defaults_build = bot_defaults_build if bot_defaults_build else Defaults(parse_mode=ParseMode.MARKDOWN)          
            
            self.default_language_code = os.environ.get('DEFAULT_LANGUAGE_CODE', 'en-US') if not default_language_code else default_language_code
            
            self.disable_default_handlers = os.environ.get('DISABLE_DEFAULT_HANDLERS', False) if not disable_default_handlers else disable_default_handlers
            
            self.bot_defaults_build = bot_defaults_build
            
            # Create an Application instance using the builder pattern            
            self.application = Application.builder().defaults(bot_defaults_build).token(self.token).post_init(self.post_init).post_stop(self.post_stop).build() 
            
            # save botname to .env file
            dotenv.set_key(self.env_file, 'BOT_NAME', self.bot_info.username)                       
            
            self.initialize_handlers()
            
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
            
            self.application.add_handler(MessageHandler(filters.COMMAND, self.default_unknown_command))
            
        except Exception as e:
            logger.error(f"Error initializing handlers: {e}")
            return f'Sorry, we have a problem initializing handlers: {e}'
      
    # -------- Default command handlers -------- 
    
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
                    # await update.message.reply_text(f"_Admin user already exists:_ `{owner_list}`")
                    
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
            
            await self.set_start_message(update.effective_user.language_code, update.effective_user.full_name, update.effective_user.id)
                
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

    # https://github.com/python-telegram-bot/python-telegram-bot/issues/3718
    # https://github.com/python-telegram-bot/python-telegram-bot/wiki/Code-snippets#simple-way-of-restarting-the-bot
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
    
    app = TlgBotFwk()    
    app.run()