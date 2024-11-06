from tlgfwk import TlgBotFwk
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

class MyBot(TlgBotFwk):
    
    async def start_command(self, update: Update, context: CallbackContext) -> None:
        """Send a welcome message when the /start command is issued."""
        await update.message.reply_text("Welcome to MyBot!")

    def run(self):
        try:
            # Add command handlers
            self.application.add_handler(CommandHandler("start", self.start_command))
            
            # Call the parent class run method to start the bot
            super().run()
            
        except Exception as e:
            logger.error(f"An error occurred while adding handlers or running the bot: {e}")
            self.send_message_by_api(self.bot_owner, f"An error occurred while adding handlers or running the bot: {e}")

def main():
    # Create an instance of the bot
    bot = MyBot(token="YOUR_BOT_TOKEN")
    
    # Start the bot's main loop
    bot.run()

if __name__ == '__main__':
    main()