import stripe
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Set your Stripe secret key
stripe.api_key = 'your_stripe_secret_key'

# Set your Telegram bot token
telegram_bot_token = 'your_telegram_bot_token'

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Welcome to the Stripe Token Generator Bot! Use /get_token to get a new Stripe token.')

def get_token(update: Update, context: CallbackContext) -> None:
    try:
        # Create a new Stripe token
        token = stripe.Token.create(
            card={
                "number": "4242424242424242",
                "exp_month": 12,
                "exp_year": 2023,
                "cvc": "123"
            }
        )
        update.message.reply_text(f'New Stripe token: {token.id}')
    except Exception as e:
        update.message.reply_text(f'Error: {str(e)}')

def main() -> None:
    # Create the Updater and pass it your bot's token
    updater = Updater(telegram_bot_token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register the command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("get_token", get_token))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT
    updater.idle()

if __name__ == '__main__':
    main()