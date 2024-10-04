import requests, os, dotenv

dotenv.load_dotenv()

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
bot_token = os.getenv('DEFAULT_BOT_TOKEN') #'YOUR_BOT_TOKEN'

# Replace 'CHAT_ID' with the chat ID you want to send the message to
admin_list = os.getenv('ADMIN_ID_LIST')
if isinstance(admin_list, str):
    admin_list = admin_list.split(',')[0]
chat_id = int(admin_list) # CHAT_ID'

# The message you want to send
message = 'Hello, this is a synchronous message!'

# Construct the URL for the sendMessage endpoint
url = f'https://api.telegram.org/bot{bot_token}/sendMessage'

# Define the payload
payload = {
    'chat_id': chat_id,
    'text': message
}

# Send the POST request
response = requests.post(url, data=payload)

# Check the response
if response.status_code == 200:
    print('Message sent successfully')
else:
    print('Failed to send message')