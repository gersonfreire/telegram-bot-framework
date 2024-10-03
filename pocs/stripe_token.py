import os
import dotenv
import stripe
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

dotenv.load_dotenv()

# Set your Stripe secret key
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')  # 'your_stripe_secret_key'

# Set your Telegram bot token
telegram_bot_token = os.getenv('DEFAULT_BOT_TOKEN')  # 'your_telegram_bot_token'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Welcome to the Stripe Token Generator Bot! Use /get_token to get a new Stripe token.')

async def get_token(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        # Create a new Stripe token
        token = stripe.Token.create(
            card={
                # "number": "4242424242424242",
                "number": "4242",
                "exp_month": 12,
                "exp_year": 2023,
                # "cvc": "123"
            }
        )
        await update.message.reply_text(f'New Stripe token: {token.id}')
    except Exception as e:
        await update.message.reply_text(f'Error: {str(e)}')

"""
Error: Request req_F7AAWbxdEgwdJC: Sending credit card numbers directly to the Stripe API is generally unsafe. To continue processing use Stripe.js, the Stripe mobile bindings, or Stripe Elements. For more information, see https://dashboard.stripe.com/account/integration/settings. If you are qualified to handle card data directly, see https://support.stripe.com/questions/enabling-access-to-raw-card-data-apis.

Stripe (https://dashboard.stripe.com/account/integration/settings)
Stripe Login | Sign in to the Stripe Dashboard
Sign in to the Stripe Dashboard to manage business payments and operations in your account. Manage payments and refunds, respond to disputes and more.
"""        

def main() -> None:
    # Create the Application and pass it your bot's token
    application = Application.builder().token(telegram_bot_token).build()

    # Register the command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("get_token", get_token))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()
