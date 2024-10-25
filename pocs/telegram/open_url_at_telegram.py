import os
from telegram import Bot
from telegram.constants import ParseMode

# Load environment variables
from dotenv import load_dotenv
import asyncio
load_dotenv()

# Initialize the bot with your token
bot_token = os.getenv('DEFAULT_BOT_TOKEN')
bot = Bot(token=bot_token)

# Replace 'CHAT_ID' with the chat ID you want to send the message to
chat_id = int(os.getenv('ADMIN_ID_LIST').split(',')[0])

# The URL message you want to send
url_message = 'Check this link: [Open in Telegram](https://example.com)'

# Send the URL message
async def send_message():
    response = await bot.send_message(chat_id=chat_id, text=url_message, parse_mode=ParseMode.MARKDOWN)
    return response

response = asyncio.run(send_message())

# Check the response
if response.message_id:
    print('Message sent successfully')
else:
    print('Failed to send message')