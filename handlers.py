from telegram.ext import Application, CommandHandler, Defaults
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CallbackContext

# from util_decorators import *

# @with_writing_action
# @with_log_admin
async def external_start(update: Update, context: CallbackContext): # , self:None, *args, **kwargs):
        
    # A simple start command response
    await update.message.reply_text('Hello! Welcome to My Telegram Bot.')