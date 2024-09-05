
import logging
import sys, os
import socket

import json


# ------------------------------------------
    
DEFAULT_CONFIG_FILE_NAME = "bot_config.json"        
DEFAULT_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "json", DEFAULT_CONFIG_FILE_NAME)    
DEFAULT_FILE_PATH_UNICODE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "json", "bot_config_unicode.json") 

# ------------------------------------------

# add python parent dir to sys.path
script_path = os.path.dirname(os.path.realpath(__file__))
parent_folder = os.path.dirname(script_path)
common_module_path = rf"{parent_folder}{os.sep}"
sys.path.append(common_module_path)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
nome_do_script = os.path.basename(sys.argv[0]).replace('.py', '')

# ------------------------------------------
# Obtem o nome do script principal que está sendo executado
main_script_path = sys.argv[0]
main_script_folder = os.path.dirname(script_path)
main_script_name = os.path.basename(script_path)

# ---- Logging ----------------------------
log_folder = f'{script_path}{os.sep}log'

if not os.path.exists(log_folder):
    os.makedirs(log_folder)
    
logging.basicConfig(
    format="%(asctime)s:%(levelname)s:%(message)s",
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler(f'{log_folder}{os.sep}{nome_do_script}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# set up logging error messages to red color
logging.addLevelName(logging.ERROR, "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.ERROR))

logger = logging.getLogger(__name__)
logger.debug(f"Log folder: {log_folder}")

# ------------------------------------------

# from util.util_console import input_with_timeout
# import util.util_open_ai as openai

# import util.util_multi_sql as db
# db.default_database_file = os.path.join(f'{os.path.dirname(__file__)}{os.sep}db', "multi.db")
# logger.info(f"default_database_file: {db.default_database_file} {sys.argv[0]}")

# import util.util_bulk_questions as bq

# ------------------------------------------

hostname = socket.getfqdn()

bot_version = "9.0.0"

environment = 'dev'

# create a dictionary to store each bot tokens
bot_tokens_dict = dict()

# save a dictionary to json file
current_dir = os.path.dirname(os.path.abspath(__file__))

bot_config_file = f'{current_dir}{os.sep}..{os.sep}json{os.sep}bot_config.json'    
all_user_data_file = f'{current_dir}{os.sep}..{os.sep}json{os.sep}user_data.json'

contabo_profiles_file_name = f'{current_dir}{os.sep}..{os.sep}json{os.sep}contabo_profiles.json'

bot_tokens_dict = dict()
user_profiles_dict = {int: dict()}

bot_name = 'ContaboToolsBot'

default_keyboard_file = ''

# ------------------------------------------

# TODO : import emoji
# CHECK_MARK_EMOJI = emoji.emojize(":check_mark_button:", language="alias")
# CROSS_MARK_EMOJI = emoji.emojize(":x:", language="alias")

help_button_unicode = "❓"
download_button_unicode = "\U0001F4E5"  # Unicode for download button
profile_button_unicode = "\U0001F464"  # Unicode for profile button
web_browser_button_unicode = "🌐"  # Unicode for web browser button  (Globe with Meridians)
android_app_button_unicode = "📱"  # Unicode for android app button  (Mobile Phone)
whatsapp_button_unicode = "\U0001F4DE"  # Unicode for green phone symbol (Telephone Receiver)
# ------------------------------------------

new_user_data = {
    "username": "",
    "password": "",
    "clientid": "",
    "apikey": "",
    "is_admin": False,
    "balance": 4
}

users_questions_totals = {    
    0: #  "user_id"
    {
        "total_questions": 0,
        "correct_answers": 0,
        "last_questions": 0,
        "last_correct_answers": 0,
    }
}


# ------------------------------------------

def get_translation(message, lang):
    # implementation of get_translation function
    pass

# ------------------------------------------

back_message = "🏠 Back to main menu"
back_message = get_translation(back_message, lang='pt')
back_message = "🏠 Voltar para o menu inicial"

help_button_caption = "Help"
help_button_caption = get_translation(help_button_caption, lang='pt')
help_button_caption = "Ajuda"

# ------------------------------------------

from dotenv import load_dotenv

def load_env_settings():

  try:
    env_path = os.path.join(os.path.dirname(__file__), self.env_file)
    if os.path.exists(env_path):
        # if we see the .env file, load it
        load_dotenv()
        default_db_connection_string = os.getenv("default_db_connection_string")
    else:
        logger.error(f"Error: no .env file found at {env_path}")
           
    return True
  
  except Exception as e:
    logger.error(f"An error occurred while getting the settings: {str(e)}")
    return None  

load_env_settings()

# ------------------------------------------

def save_bot_tokens():
    with open(bot_config_file, 'w') as fp:
        json.dump(bot_tokens_dict, fp, indent=4)

def save_json_settings(settings, settings_file=f'settings_file.json'):
    try:
        with open(settings_file, 'w', encoding='utf-8') as fp:
            json.dump(settings, fp, indent=4)
            return True
        
    except Exception as e:
        logger.error(f"Error saving settings: {e}")
        return False

def load_json_settings(settings_file=f'settings_file.json'):
    try:
        with open(settings_file, 'r', encoding='utf-8') as fp:
            settings = json.load(fp)
            return settings
        
    except Exception as e:
        logger.error(f"Error loading settings: {e}")
        return None
    
def save_user_data(all_users_data):
    with open(all_user_data_file, 'w', encoding='utf-8') as fp:
        json.dump(all_users_data, fp, indent=4)    

def load_all_users_data():
    all_users_data = dict()
    if os.path.exists(all_user_data_file):
        with open(all_user_data_file, 'r', encoding='utf-8') as fp:
            all_users_data = json.load(fp)

    return all_users_data

def load_contabo_profiles():
    
    contabo_profiles_dict = dict()
    
    try:
        if os.path.exists(contabo_profiles_file_name):
            with open(contabo_profiles_file_name, 'r', encoding='utf-8') as fp:
                contabo_profiles_dict = json.load(fp)
                
    except Exception as e:
        logger.error(f"Error loading contabo profiles: {e}")
        contabo_profiles_dict = {}

    return contabo_profiles_dict

def save_contabo_profiles(contabo_profiles_dict=user_profiles_dict, contabo_profiles_file_name=contabo_profiles_file_name):
    try:
        with open(contabo_profiles_file_name, 'w', encoding='utf-8') as fp:
            json.dump(contabo_profiles_dict, fp, indent=4)
            
    except Exception as e:
        logger.error(f"Error saving contabo profiles: {e}")

def load_bot_tokens():
    
    try:
        global bot_tokens_dict
        if os.path.exists(bot_config_file):
            with open(bot_config_file, 'r', encoding='utf-8') as fp:
                bot_tokens_dict = json.load(fp)
                
    except Exception as e:
        logger.error(f"Error loading json bot tokens: {e}")
        timeout_seconds = 5  # Set your timeout (seconds)
        input_with_timeout("Press Enter to finish: ", timeout_seconds)        
        sys.exit()
        
    return bot_tokens_dict

# ------------------------------------------

# function to convert a latin characters in json file to unicode characters
def convert_to_unicode(source_file_path, dest_file_path = None):
    
    try:      
        
        with open(source_file_path, 'r', encoding='utf-8', errors='replace') as f:
            text = f.read()
            
        if dest_file_path:
            with open(dest_file_path, 'w', encoding='utf-8') as f:
            # with open(source_file_path, 'w', encoding='utf8') as json_file:
                # f.write(text.encode('utf-8').decode('unicode-escape'))
                
                # json.dump("ברי צקלה", json_file, ensure_ascii=False)        
                json.dump(text, dest_file_path, ensure_ascii=False)
                
                # >>> json_string = json.dumps("ברי צקלה", ensure_ascii=False).encode('utf8')
                # >>> json_string
                # b'"\xd7\x91\xd7\xa8\xd7\x99 \xd7\xa6\xd7\xa7\xd7\x9c\xd7\x94"'
                # >>> print(json_string.decode())
                # "ברי צקלה"                  
        
        return text.encode('utf-8').decode('unicode-escape')
    
    except Exception as e:
        logger.error(f"Error: {e}")
        # Handle the exception here

# ------------------------------------------

try:
    all_bot_settings = load_bot_tokens()
    user_profiles_dict = load_all_users_data()
    bot_user_admin = bot_tokens_dict[bot_name]['admin']

    # If current machine is developer machine, use the development bot
    current_bot_settings = bot_tokens_dict[bot_name]
except Exception as e:
    logger.error(f"Error: {e}")

# If bot name has been provided at command line, use it as index for bot config dictionary
if len(sys.argv) > 1:
    
    bot_name = sys.argv[1]
    
    # compare the bot name with the keys in the bot_tokens_dict, if found, case insensitive, use it    
    if any(bot_name.lower() in key.lower() for key in all_bot_settings.keys()):
        # get the key that contains the bot name
        bot_name = next(key for key in all_bot_settings.keys() if bot_name.lower() in key.lower())
        current_bot_settings = all_bot_settings[bot_name]

# handle possible failure to get bot config items
TELEGRAM_BOT_TOKEN = ''
owner_phone = ''
stripe_enviroment = ''
STRIPE_PROVIDER_TOKEN = ''  
try:
    TELEGRAM_BOT_TOKEN = current_bot_settings['token']
    bot_user_admin = current_bot_settings['admin']
    bot_owner = current_bot_settings['owner']
    owner_phone = current_bot_settings['owner_phone']
    stripe_enviroment = 'live' if environment != 'prod' else 'test'
    STRIPE_PROVIDER_TOKEN = current_bot_settings['stripe_token'][stripe_enviroment]

except Exception as e:
    logger.error(f"Error: {e}")
#------------------------------------------
# Telegram Bot commands
# Telegram Bot commands
help_text = (
    f"/start - Greet the new user{os.linesep}"
    f"/help - Show this help message{os.linesep}"
    f"/pay - Pay $1 and add to user balance{os.linesep}"
)

try:
    bot_user_admin = int(os.environ.get('DEFAULT_BOT_OWNER', None))
except Exception as e:
    logger.error(f"Error: {e}")
    bot_user_admin = None

# function to return current bot version        
async def version_command2(update, context) -> None:
    try:
    #    await update.message.reply_text(f"Current version is {bot_version}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Current version is {bot_version}")
    except Exception as e:
        logger.error(f"Error: {e}")


# Main function to unit tests
def get_bot_names_main(): 
    
    # Test the function to convert latin characters to unicode
    # charmap' codec can't encode character '\x83' in position 785: character maps to <undefined>
    converted_text = convert_to_unicode(DEFAULT_FILE_PATH, f'{current_dir}{os.sep}bot_tokens_unicode.json')
    logger.debug(f"Unicode for 'help': {converted_text}")
    
    logger.debug(f"Bot name: {bot_name}")
    logger.debug(f"Bot token: {TELEGRAM_BOT_TOKEN}")
    logger.debug(f"Bot admin: {bot_user_admin}")
    logger.debug(f"Bot owner: {bot_owner}")
    logger.debug(f"Owner phone: {owner_phone}")
    logger.debug(f"Stripe token: {STRIPE_PROVIDER_TOKEN}")
    logger.debug(f"Bot version: {bot_version}")
    logger.debug(f"Environment: {environment}")
    logger.debug(f"Bot tokens: {bot_tokens_dict}")
    logger.debug(f"User data: {user_profiles_dict}")
    # logger.debug(f"User balances: {user_balances}")
        
if __name__ == "__main__":
        
    import json

    # Seu dicionário com caracteres acentuados
    weird_dict = {
        "person": "ç",
        "á": "à",
        "ç": "ã"
    }
    
    # ler arquivo json com caracteres acentuados da lingua portugesa e preserválos na leitura
    with open(DEFAULT_FILE_PATH, 'r', encoding='utf-8') as f:
        weird_dict = json.load(f)

    # Converter para JSON com caracteres especiais preservados
    json_output = json.dumps(weird_dict, indent=4, sort_keys=True, ensure_ascii=False)
    
    # salve o JSON em um arquivo
    with open('weird_dict.json', 'w') as f:
        f.write(json_output)

    print(json_output)
    
    get_bot_names_main()    
    
