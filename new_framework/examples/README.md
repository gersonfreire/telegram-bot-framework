# Examples

This directory contains example bots demonstrating various features of the Telegram Bot Framework.

## Available Examples

### 1. Echo Bot (`echo_bot.py`)
A simple bot that demonstrates basic framework usage:
- Basic command handling
- Message echoing
- Text manipulation commands

**Features:**
- `/echo` - Echo back your message
- `/reverse` - Reverse your message
- `/count` - Count words and characters
- Automatic echoing of non-command messages

### 2. Advanced Bot (`advanced_bot.py`)
A comprehensive bot showcasing advanced framework features:
- Plugin system usage
- Job scheduling
- Payment integration
- System monitoring
- User statistics

**Features:**
- `/status` - Get bot status information
- `/schedule` - Schedule custom jobs
- `/jobs` - List scheduled jobs
- `/payment` - Create test payments
- Automatic system monitoring
- User activity tracking
- Daily reports and health checks

## Setup Instructions

1. **Install Dependencies**
   ```bash
   cd new_framework
   pip install -e .
   ```

2. **Configure Environment**
   ```bash
   cd examples
   cp .env.example .env
   # Edit .env with your bot token and settings
   ```

3. **Get Bot Token**
   - Message @BotFather on Telegram
   - Create a new bot with `/newbot`
   - Copy the token to your `.env` file

4. **Get Your User ID**
   - Message @userinfobot on Telegram
   - Copy your user ID to the `.env` file

5. **Run Examples**
   ```bash
   # Simple echo bot
   python echo_bot.py
   
   # Advanced bot with plugins
   python advanced_bot.py
   ```

## Environment Variables

### Required
- `BOT_TOKEN`: Your Telegram bot token from @BotFather
- `OWNER_USER_ID`: Your Telegram user ID (from @userinfobot)

### Optional
- `ADMIN_USER_IDS`: Comma-separated list of admin user IDs
- `LOG_CHAT_ID`: Chat ID for log messages
- `DEBUG`: Enable debug mode (true/false)
- `DATABASE_URL`: Database URL for persistent storage
- `ENABLE_SYSTEM_MONITOR`: Enable system monitoring plugin
- `ENABLE_USER_STATS`: Enable user statistics plugin
- `USE_PERSISTENT_JOBS`: Enable persistent job storage
- `STRIPE_API_KEY`: Stripe API key for payments
- `PIX_ACCOUNT_KEY`: PIX key for Brazilian payments

## Features Demonstrated

### Basic Features (Echo Bot)
- Framework initialization
- Command registration with decorators
- Message handling
- Basic user interaction

### Advanced Features (Advanced Bot)
- Plugin system integration
- Payment processing
- Job scheduling and management
- System health monitoring
- User activity analytics
- Automatic reporting
- Error handling and logging

## Creating Your Own Bot

1. **Start with the Echo Bot**
   - Copy `echo_bot.py` as a starting point
   - Modify the commands and handlers as needed

2. **Add Advanced Features**
   - Use the Advanced Bot as reference
   - Add plugins, scheduling, or payments as required

3. **Custom Plugin Development**
   - See the plugin examples in `../src/tlgfwk/plugins/`
   - Inherit from `PluginBase` for custom functionality

## Troubleshooting

### Common Issues

1. **"Module not found" errors**
   - Make sure you installed the framework: `pip install -e .`
   - Check that you're running from the examples directory

2. **Bot not responding**
   - Verify your bot token is correct
   - Check your internet connection
   - Look for error messages in the console

3. **Permission errors**
   - Make sure your user ID is correct
   - Check that you're listed as admin/owner in the config

4. **Plugin errors**
   - Install optional dependencies: `pip install psutil apscheduler`
   - Check plugin configuration in the code

### Getting Help

- Check the main README.md for detailed documentation
- Look at the plugin source code for examples
- Check the logs for error messages
- Ensure all required environment variables are set

## Next Steps

- Explore the plugin system in `../src/tlgfwk/plugins/`
- Read the API documentation in `../docs/`
- Check out the test files in `../tests/`
- Customize the examples for your specific needs
