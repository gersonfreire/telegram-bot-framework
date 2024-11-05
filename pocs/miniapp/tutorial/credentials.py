"""
Author: Calixte Mayoraz (2022)
"""
import os
if os.path.exists(".env"):
    # if we see the .env file, load it
    from dotenv import load_dotenv
    load_dotenv()

# now we have it as a handy python string!
BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_USERNAME = os.getenv('BOT_USERNAME')
WEBAPP_URL = os.getenv('WEBAPP_URL')
