#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Telegram Bot util decorators

Returns:
    _type_: Handlers decorators
    
"""

# Define the decorator for all functions that require the bot to send a typing action
from functools import wraps

from telegram import InlineKeyboardButton, Update
from telegram.ext import CallbackContext

from util_config import * # logger

from util_telegram import *

def with_writing_action(handler):
    @wraps(handler)
    async def wrapper(self, update: Update, context: CallbackContext, *args, **kwargs):
        try:                
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
            return await handler(self, update, context, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error: {e}")
            return await handler(self, update, context, *args, **kwargs)
        
    return wrapper

def with_waiting_action(handler):
    @wraps(handler)
    async def wrapper(update: Update, context: CallbackContext):
        
        try:             
            wait_message = "_Executando, aguarde um momento, por favor..._"   
            # wait_message = "_Executing, pelase wait..._"   
            
            await update._bot.send_message(chat_id=update.effective_user.id, text=wait_message, parse_mode=ParseMode.MARKDOWN)
            
            return await handler(update, context)
        except Exception as e:
            logger.error(f"Error: {e}")
            return await handler(update, context)
        
    return wrapper

# Define the decorator to check if the user is already registered
def validate_user(handler):
    @wraps(handler)
    async def wrapper(update: Update, context: CallbackContext):
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
    async def wrapper(update: Update, context: CallbackContext):
        
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
                if update.effective_user.id != bot_user_admin:
                    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)      
                    await context.bot.send_message(chat_id=bot_user_admin, text=f"_{update.effective_message.text} - {update.effective_user.full_name} - from {update.effective_message.from_user.id} {update.effective_user.full_name}_", parse_mode=ParseMode.MARKDOWN)
            except Exception as e:
                logger.error(f"Error: {e}")
            return await handler(self, update, context, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error: {e}")
            return await handler(self, update, context,  *args, **kwargs)
    return wrapper

# Define the decorator to send the start menu after the command
def with_start_menu(handler):
    @wraps(handler)
    async def wrapper(update: Update, context: CallbackContext):
        try:
            await handler(update, context)
            # return await cmd_start(update, context)
        except Exception as e:
            logger.error(f"Error: {e}")
            return await handler(update, context)
    return wrapper

# Define the decorator that get user language and set the bot language
def with_set_language(handler):
    @wraps(handler)
    async def wrapper(update: Update, context: CallbackContext):
        try:
            if update.effective_user.language_code not in supported_languages:
                context.user_data['language'] = default_language
            else:
                context.user_data['language'] = update.effective_user.language_code
                
            # If not, insert the user into the database
            return await handler(update, context)
        
        except Exception as e:
            logger.error(f"Error: {e}")
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