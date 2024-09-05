import sys, os, logging
import base64

from telegram import Bot
import dotenv
import translations.translations as translations

from handlers import *
import translations as translations

from cryptography.fernet import Fernet

# ------------------------------------------
script_path = os.path.dirname(os.path.realpath(__file__))
parent_folder = os.path.dirname(script_path)
common_module_path = rf"{parent_folder}{os.sep}"
sys.path.append(common_module_path)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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

from util_decorators import *
# from util_config import * # logger
from util_telegram import *
from util_console import *

# from telegram.ext import filters
from handlers import *