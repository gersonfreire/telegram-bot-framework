

import asyncio
from functools import wraps
import random
import shutil
from telegram.ext import CallbackQueryHandler
from telegram.constants import ChatAction

from telegram import BotCommand, ForceReply, InlineKeyboardButton, InputFile, LabeledPrice, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardMarkup
from telegram.constants import ParseMode

from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.ext import PreCheckoutQueryHandler

from telegram.ext import CallbackContext

# Usa a versão python-telegram-bot==21.2 ao inves da 13.7
from telegram import BotCommand, ForceReply, InlineKeyboardButton, LabeledPrice, Update, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.ext import CallbackContext
from telegram.ext import CallbackQueryHandler
from telegram.ext import ConversationHandler

from telegram import BotCommandScopeAllPrivateChats, BotCommandScopeDefault, BotCommandScopeAllGroupChats, BotCommandScopeAllChatAdministrators, BotCommandScopeChat, BotCommandScopeChatAdministrators, BotCommandScopeChatMember, BotCommandScopeDefault, BotCommandScopeAllPrivateChats, BotCommandScopeAllGroupChats, BotCommandScopeAllChatAdministrators, BotCommandScopeChat, BotCommandScopeChatAdministrators, BotCommandScopeChatMember, BotCommandScope