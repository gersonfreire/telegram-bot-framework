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

### 2. Demo Bot (`demo_bot.py`)
A comprehensive demonstration bot showcasing all framework features:
- Complete command system
- Permission management (admin/owner)
- User management
- Plugin system
- Cryptography utilities
- Statistics and monitoring
- Configuration management

**Features:**
- `/demo` - Interactive demonstration menu
- `/welcome` - Personalized welcome message
- `/info` - Detailed bot information
- `/admin_test` - Admin permission test
- `/owner_test` - Owner permission test
- `/user_info` - User information
- `/add_admin` - Add admin users (owner only)
- `/crypto_demo` - Cryptography demonstration
- `/demo_stats` - Demo statistics
- `/demo_config` - Demo configuration
- `/broadcast_demo` - Broadcast demonstration
- `/test_error` - Error handling test
- `/plugindemo` - Plugin demonstration
- `/plugininfo` - Plugin information
- `/botrestart` - Restart bot (owner only)
- `/botstop` - Stop bot (owner only)

### 3. Scheduler Bot (`scheduler_bot.py`)
A bot demonstrating the job scheduling system:
- One-time job scheduling
- Recurring job scheduling
- Job management and monitoring
- Statistics and reporting

**Features:**
- `/schedule` - Interactive scheduling menu
- `/schedule_once` - Schedule one-time job
- `/schedule_recurring` - Schedule recurring job
- `/list_jobs` - List all jobs (admin)
- `/cancel_job` - Cancel specific job
- `/cancel_all` - Cancel user's jobs
- `/scheduler_stats` - Scheduler statistics
- `/scheduler_config` - Scheduler configuration

### 4. Advanced Bot (`advanced_bot.py`)
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
   cp env.example .env
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

   # Comprehensive demo bot
   python demo_bot.py

   # Scheduler bot
   python scheduler_bot.py

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
- `INSTANCE_NAME`: Bot instance name
- `AUTO_LOAD_PLUGINS`: Auto-load plugins (true/false)
- `ENABLE_PERSISTENCE`: Enable data persistence (true/false)
- `STRIPE_SECRET_KEY`: Stripe API key for payments
- `PAYPAL_CLIENT_ID`: PayPal client ID
- `PAYPAL_CLIENT_SECRET`: PayPal client secret
- `DATABASE_URL`: Database URL for persistent storage
- `ENCRYPTION_KEY`: Key for encrypting sensitive data

## Framework Commands

All bots include these built-in framework commands:

### Basic Commands
- `/start` - Start the bot
- `/help` - Show help
- `/status` - Show bot status

### Admin Commands (Admin users)
- `/config` - Show configuration
- `/stats` - Show statistics
- `/users` - List users

### Owner Commands (Owner only)
- `/restart` - Restart the bot
- `/shutdown` - Shutdown the bot
- `/botrestart` - Restart the bot (alternative)
- `/botstop` - Stop the bot

### Plugin Commands
- `/plugindemo` - Plugin demonstration
- `/plugininfo` - Plugin information

## Features Demonstrated

### Basic Features (Echo Bot)
- Framework initialization
- Command registration with decorators
- Message handling
- Basic user interaction

### Complete Features (Demo Bot)
- Full command system with permissions
- Interactive menus with inline keyboards
- User management and statistics
- Plugin system integration
- Cryptography and security
- Error handling and logging
- Bot control commands

### Scheduling Features (Scheduler Bot)
- One-time and recurring job scheduling
- Job management and monitoring
- User-specific job control
- Statistics and reporting
- Automatic cleanup

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

2. **Use the Demo Bot as Reference**
   - Copy `demo_bot.py` for a complete example
   - All examples use the `.env` file from the examples directory

3. **Add Advanced Features**
   - Use the Advanced Bot as reference
   - Add plugins, scheduling, or payments as required

4. **Custom Plugin Development**
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

5. **Configuration file not found**
   - Copy `env.example` to `.env` in the examples directory
   - Configure your bot token and user ID

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
