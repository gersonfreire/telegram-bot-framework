from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings
from botbuilder.schema import Activity, ActivityTypes
from aiohttp import web

# Create the bot adapter
settings = BotFrameworkAdapterSettings("YOUR_BOT_APP_ID", "YOUR_BOT_APP_PASSWORD")
adapter = BotFrameworkAdapter(settings)

# Define the bot logic
async def on_turn(context):
    if context.activity.type == ActivityTypes.message:
        # Echo back the user's message
        await context.send_activity(f"You said: {context.activity.text}")
    else:
        await context.send_activity(f"Sorry, I only respond to text messages.")

# Create the HTTP server
app = web.Application()
app.router.add_post("/api/messages", adapter.webhook_handler)

# Start the server
web.run_app(app, host="localhost", port=3978)