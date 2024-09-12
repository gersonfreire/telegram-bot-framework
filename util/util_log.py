import logging
import sys, os

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