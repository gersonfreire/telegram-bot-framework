#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Telegram Bot util decorators

Returns:
    _type_: Handlers decorators
    
"""

# Define the decorator for all functions that require the bot to send a typing action
from datetime import timedelta
from functools import wraps

from telegram import InlineKeyboardButton, Update
from telegram.ext import CallbackContext

from .util_telegram import *

def with_writing_action(handler):
    @wraps(handler)
    async def wrapper(self, update: Update, context: CallbackContext, *args, **kwargs):
        
        try:      
                      
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
            self.logger.debug(f"Typing action sent to chat_id: {update.effective_chat.id}")            
             
            # Insert or update user on the bot_data dictionary
            context.bot_data['user_dict'] = {} if 'user_dict' not in context.bot_data else context.bot_data['user_dict']
            context.bot_data['user_dict'][update.effective_user.id] = update.effective_user 
            
            # Add to bot_data the last time the user accessed the bot
            if 'user_status' not in context.bot_data:
                context.bot_data['user_status'] = {}
            if update.effective_user.id not in context.bot_data['user_status']:
                context.bot_data['user_status'][update.effective_user.id] = {}
            
            context.bot_data['user_status'][update.effective_user.id]['last_message_date'] = (update.message.date + timedelta(hours=-3)).strftime('%d/%m %H:%M')
            
            return await handler(self, update, context, *args, **kwargs)
        
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return await handler(self, update, context, *args, **kwargs)
        
    return wrapper

def with_writing_action_sync(handler):
    @wraps(handler)
    def wrapper(self, chat_id: int, message: str):
        try:                
            self.loop.run_until_complete(self.application.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING))
            self.logger.debug(f"Typing action sent to chat_id: {chat_id}")
            
        except Exception as e:
            self.logger.error(f"Error: {e}")
        
        return handler(self, chat_id, message)
        
    return wrapper

def with_waiting_action(handler):
    @wraps(handler)
    async def wrapper(self, update: Update, context: CallbackContext):
        
        try:             
            wait_message = "_Executando, aguarde um momento, por favor..._"   
            # wait_message = "_Executing, pelase wait..._"   
            
            await update._bot.send_message(chat_id=update.effective_user.id, text=wait_message, parse_mode=ParseMode.MARKDOWN)
            
            return await handler(update, context)
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return await handler(update, context)
        
    return wrapper

# Define the decorator to check if the user is already registered
def validate_user(handler):
    @wraps(handler)
    async def wrapper(self, update: Update, context: CallbackContext):
        try:
            # Load all users data
            # all_users_data = db.load_all_users_data()
            # # Check if the user is already registered
            # if str(update.effective_user.id) in all_users_data:
            #     current_user = all_users_data[str(update.effective_user.id)]
            # else:
            #     current_user = db.new_user_data
                
            # If not, insert the user into the database
            return await handler(update, context)
        
        except Exception as e:
            logger.error(f"Error: {e}")
            return await handler(update, context)
    
    return wrapper

# Define the decorator to check if the user is already registered
def check_user_allowed(handler):
    @wraps(handler)
    async def wrapper(self, update: Update, context: CallbackContext):
        
        try:
            contabo = None
            contabo_profiles_dict = load_all_users_settings()     
            
            user_id = update.effective_user.id     

            if str(update.effective_user.id) in contabo_profiles_dict:
                contabo_profiles_dict = contabo_profiles_dict[str(update.effective_user.id)]
                
                return await handler(update, context)
        
        except Exception as e:
            logger.error(f"Error: {e}")
            return await handler(update, context)
    
    return wrapper

# Define the decorator and duplicate all non-admin messages to admin
def with_log_admin(handler):
    @wraps(handler)
    async def wrapper(self, update: Update, context: CallbackContext, *args, **kwargs):
        try:
            try:
                if update.effective_user.id not in self.admins_owner:
                    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)      
                    await context.bot.send_message(chat_id=self.admins_owner[0], text=f"_{update.effective_message.text} - {update.effective_user.full_name} - from {update.effective_message.from_user.id} {update.effective_user.full_name}_", parse_mode=ParseMode.MARKDOWN)
                    
            except Exception as e:
                self.logger.error(f"Error: {e}")
                
            return await handler(self, update, context, *args, **kwargs)
        
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return await handler(self, update, context,  *args, **kwargs)
        
    return wrapper

# Define the decorator to send the start menu after the command
def with_start_menu(handler):
    @wraps(handler)
    async def wrapper(self, update: Update, context: CallbackContext):
        try:
            await handler(update, context)
            # return await cmd_start(update, context)
            
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return await handler(update, context)
        
    return wrapper

# Define the decorator that get user language and set the bot language
def with_set_language(handler):
    @wraps(handler)
    async def wrapper(self, update: Update, context: CallbackContext):
        try:
            if update.effective_user.language_code not in self.default_language_code:
                context.user_data['language'] = self.default_language_code
            else:
                context.user_data['language'] = update.effective_user.language_code
                
            # If not, insert the user into the database
            return await handler(update, context)
        
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return await handler(update, context)
    
    return wrapper

# ------------------------------------------

# https://github.com/python-telegram-bot/python-telegram-bot/wiki/Code-snippets#post-a-text-message

def with_command_handler(command, application):
    def decorator(func):
        handler = CommandHandler(command, func)
        application.add_handler(handler)
        return func
    return decorator

LIST_OF_ADMINS = [12345678, 87654321]

def restricted(func):
    @wraps(func)
    async def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in LIST_OF_ADMINS:
            print(f"Unauthorized access denied for {user_id}.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapped

@restricted
async def my_handler(update, context):
    pass  # only accessible if `user_id` is in `LIST_OF_ADMINS`.

# ------------------------------------------