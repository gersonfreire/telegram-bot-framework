#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=unused-argument

# ------------------------------------------
import os
from dotenv import * # load_dotenv

from .util_log import *


# ------------------------------------------

def load_env_settings():

  try:
    env_path = os.path.join(os.path.dirname(__file__), f'..{os.sep}.env')
    if os.path.exists(env_path):
        if load_dotenv():
            logger.info("Loaded .env file.")
        else:
            logger.error("Error: failed to load .env file.")
    else:
        logger.error(f"Error: no .env file found at {env_path}")
           
    return True
  
  except Exception as e:
    logger.error(f"An error occurred while getting the settings: {str(e)}")
    return None  

# ------------------------------------------

def main_util_env():
    
    load_env_settings()
    
    # Print only the settings from the .env file
    dotenv_settings = dotenv_values()
    for key, value in dotenv_settings.items():
        print(f"{key}: {value}")
    
    return dotenv_settings
    
if __name__ == "__main__":
    main_util_env()
    
    print("Done.")