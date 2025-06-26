# Telegram Bot Framework

A comprehensive Python framework for building Telegram bots with built-in user management, payment processing, and persistent storage.

## Features

- User Management
  - User registration and tracking
  - Admin user support
  - User permissions

- Payment System
  - Balance management
  - Transaction tracking
  - Payment processing

- Settings Management
  - Global and per-user settings
  - Persistent storage
  - Default settings support

- Plugin System
  - Easy extension through plugins
  - Hot-loading of plugins
  - Automatic command registration

- Built-in Commands
  - Administrative commands
  - User utility commands
  - Customizable command registry

- Persistence
  - SQLite-based storage
  - Automatic state recovery
  - Transaction history

## Quick Start

1. Clone the repository
2. Copy `.env.example` to `.env` and fill in your bot token and admin IDs
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the bot:
   ```bash
   python src/main.py
   ```

## Creating Your Own Bot

```python
from framework.base import TelegramBotFramework

# Create your bot instance
bot = TelegramBotFramework(
    token="your_bot_token",
    admin_ids=[123456789],  # List of admin user IDs
    plugins_dir="path/to/plugins"  # Optional plugins directory
)

# Start the bot
bot.run()
```

## Creating Plugins

Create a new plugin by inheriting from `PluginBase`:

```python
from framework.plugins import PluginBase
from framework.commands import Command

class MyPlugin(PluginBase):
    @property
    def name(self) -> str:
        return "my_plugin"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def initialize(self, framework):
        self.framework = framework
    
    async def my_command(self, update, context):
        await update.message.reply_text("Hello from my plugin!")
    
    def get_commands(self) -> list[Command]:
        return [
            Command(
                name="my_command",
                handler=self.my_command,
                description="My custom command",
                admin_only=False
            )
        ]
```

Save your plugin in the plugins directory, and it will be automatically loaded when the bot starts.

## Configuration

The framework uses environment variables for configuration:

- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
- `ADMIN_IDS`: Comma-separated list of admin user IDs

## License

MIT License