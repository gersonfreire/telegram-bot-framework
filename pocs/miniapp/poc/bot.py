import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
BOT_TOKEN = os.getenv("DEFAULT_BOT_TOKEN")

# get web app url from environment variable
WEB_APP_URL = os.getenv("WEB_APP_URL") # .replace("http://", "https://")

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define the /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Welcome! Use /app to open the web app.')

# Define the /app command handler
async def app(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        keyboard = [
            [InlineKeyboardButton("Open Web App", url=WEB_APP_URL)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('Click the button below to open the web app:', reply_markup=reply_markup)
    except Exception as e:
        # "Inline keyboard button url 'http://localhost:5000' is invalid: wrong http url"
        logger.error(f"Error in /app command: {e}")
        await update.message.reply_text('An error occurred while processing your request.')

# Define the data handler
async def handle_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = update.message.text
    await update.message.reply_text(f'You entered: {data}')

def main() -> None:
    # Create the Application and pass it your bot's token.
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("app", app))
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_data))
    application.add_handler(handler=MessageHandler(filters.TEXT, callback=handle_data))

    # Run the bot
    application.run_polling()

if __name__ == '__main__':
    main()