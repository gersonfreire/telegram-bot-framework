import sys, os, logging, socket, pdb, json, pickle, dotenv, datetime
import base64
from datetime import timedelta

from telegram import Bot, Chat, Message, User

from handlers import *
import translations as translations
# import translations.translations as translations
from typing import List

from cryptography.fernet import Fernet

# ------------------------------------------

def telegram_object_to_dict(obj):
    if isinstance(obj, User):
        return {
            "id": obj.id,
            "is_bot": obj.is_bot,
            "first_name": obj.first_name,
            "last_name": obj.last_name,
            "username": obj.username,
            "language_code": obj.language_code,
            "can_join_groups": obj.can_join_groups,
            "can_read_all_group_messages": obj.can_read_all_group_messages,
            "supports_inline_queries": obj.supports_inline_queries
        }
    elif isinstance(obj, Message):
        return {
            "message_id": obj.message_id,
            "date": obj.date.isoformat() if obj.date else None,
            "chat": telegram_object_to_dict(obj.chat),
            "from_user": telegram_object_to_dict(obj.from_user) if obj.from_user else None,
            "text": obj.text
        }
    elif isinstance(obj, Chat):
        return {
            "id": obj.id,
            "type": obj.type,
            "title": obj.title,
            "username": obj.username,
            "first_name": obj.first_name,
            "last_name": obj.last_name
        }
    # Add more elif blocks for other telegram object types as needed
    else:
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

def handle_exception(exc_type, exc_value, exc_traceback):
    """Handle global unhandled exceptions and start the debugger.

    Args:
        exc_type (_type_): _description_
        exc_value (_type_): _description_
        exc_traceback (_type_): _description_
    """
    if issubclass(exc_type, KeyboardInterrupt):
        # Call the default excepthook for KeyboardInterrupt
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    print(f"An unhandled exception occurred: {exc_value}")
    debug_mode = input_with_timeout("Press enter to continue or 'D' + enter to launch debugger ...")
    if debug_mode.lower() == 'd':
        pdb.post_mortem(exc_traceback)

# Set the custom exception handler
sys.excepthook = handle_exception

class TelegramObjectEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return telegram_object_to_dict(obj)
        except TypeError:
            return super().default(obj)
       
# ---- Add parent folder to import path ----
script_path = os.path.dirname(os.path.realpath(__file__))
parent_folder = os.path.dirname(script_path)
common_module_path = rf"{parent_folder}{os.sep}"
sys.path.append(common_module_path)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(parent_folder)
script_name = os.path.basename(sys.argv[0]).replace('.py', '')

# ---- Logging ----------------------------
log_folder = f'{script_path}{os.sep}log'

if not os.path.exists(log_folder):
    os.makedirs(log_folder)
    
logging.basicConfig(
    format="%(asctime)s:%(levelname)s:%(message)s",
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler(f'{log_folder}{os.sep}{script_name}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# set up logging error messages to red color
logging.addLevelName(logging.ERROR, "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.ERROR))

logger = logging.getLogger(__name__)
logger.debug(f"Log folder: {log_folder}")

# ------------------------------------------

from util.util_decorators import *
from util.util_telegram import *
from util.util_console import *

from handlers import *