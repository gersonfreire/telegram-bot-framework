import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from tlgfwk import TelegramBotFramework

if __name__ == "__main__":
    # Create a dummy .env file for testing
    with open('.env', 'w') as f:
        f.write("BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN\n")
        f.write("OWNER_ID=123456789\n")
        f.write("ADMIN_IDS=123456789\n")

    try:
        bot = TelegramBotFramework()
        bot.run()
    except Exception as e:
        print(f"Failed to run the bot: {e}")
    finally:
        # Clean up the dummy .env file
        if os.path.exists('.env'):
            os.remove('.env')
        if os.path.exists('secret.key'):
            os.remove('secret.key')
        if os.path.exists('data/jobs.sqlite'):
            os.remove('data/jobs.sqlite')
        if os.path.exists('data/users.pkl'):
            os.remove('data/users.pkl')
        if os.path.exists('data'):
            os.rmdir('data')