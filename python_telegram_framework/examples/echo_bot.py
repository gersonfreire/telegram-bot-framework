import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from tlgfwk import TelegramBotFramework

if __name__ == "__main__":
    # This bot requires a .env file in the same directory
    # with the following content:
    # BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
    # OWNER_ID=YOUR_TELEGRAM_USER_ID

    if not os.path.exists(os.path.join(os.path.dirname(__file__), '.env')):
        print("Error: .env file not found in the examples directory.")
        print("Please create a .env file with your BOT_TOKEN and OWNER_ID.")
        sys.exit(1)

    try:
        # When running from the 'examples' directory, the .env file is in the right place.
        bot = TelegramBotFramework(env_file=os.path.join(os.path.dirname(__file__), '.env'))
        bot.run()
    except Exception as e:
        print(f"Failed to run the bot: {e}")