# Telegram Bot Framework - User Guide

This comprehensive guide will help you get started with the Telegram Bot Framework and build powerful bots quickly.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Core Concepts](#core-concepts)
4. [Configuration](#configuration)
5. [Command System](#command-system)
6. [Plugin System](#plugin-system)
7. [User Management](#user-management)
8. [Persistence](#persistence)
9. [Payment Integration](#payment-integration)
10. [Job Scheduling](#job-scheduling)
11. [Logging](#logging)
12. [Security](#security)
13. [Deployment](#deployment)
14. [Troubleshooting](#troubleshooting)

## Installation

### Requirements

- Python 3.8+ (recommended: Python 3.12+)
- python-telegram-bot v21+

### Install from Source

```bash
git clone https://github.com/your-repo/telegram-bot-framework.git
cd telegram-bot-framework/new_framework
pip install -e .
```

### Install Dependencies

```bash
# Core dependencies
pip install python-telegram-bot[all] python-dotenv cryptography

# Optional dependencies for advanced features
pip install psutil apscheduler sqlalchemy stripe
```

## Quick Start

### 1. Create Your First Bot

```python
from tlgfwk import TelegramBotFramework, command

class MyBot(TelegramBotFramework):
    def __init__(self):
        super().__init__(
            token="YOUR_BOT_TOKEN",
            admin_user_ids=[123456789],  # Your user ID
            owner_user_id=123456789
        )
    
    @command(name="hello", description="Say hello")
    async def hello_command(self, update, context):
        await update.message.reply_text("Hello! 👋")

# Run the bot
if __name__ == "__main__":
    bot = MyBot()
    bot.run()
```

### 2. Set Up Environment

Create a `.env` file:

```bash
BOT_TOKEN=your_bot_token_from_botfather
OWNER_USER_ID=your_telegram_user_id
ADMIN_USER_IDS=123456789,987654321
DEBUG=true
```

### 3. Get Your Bot Token

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow the instructions
3. Copy the token to your `.env` file

### 4. Get Your User ID

1. Message [@userinfobot](https://t.me/userinfobot) on Telegram
2. Copy your user ID to the `.env` file

## Core Concepts

### Framework Architecture

The framework is built around several core components:

- **TelegramBotFramework**: Main bot class
- **Config**: Configuration management
- **UserManager**: User registration and management
- **PersistenceManager**: Data storage abstraction
- **PluginManager**: Plugin system
- **PaymentManager**: Payment processing
- **JobScheduler**: Task scheduling

### Bot Lifecycle

1. **Initialization**: Framework loads configuration and initializes components
2. **Setup**: Handlers are registered and plugins are loaded
3. **Running**: Bot processes updates and executes commands
4. **Shutdown**: Cleanup and data persistence

## Configuration

### Environment Variables

The framework uses environment variables for configuration:

```bash
# Required
BOT_TOKEN=your_bot_token
OWNER_USER_ID=123456789

# Optional
ADMIN_USER_IDS=123456789,987654321
LOG_CHAT_ID=123456789
DEBUG=true
DATABASE_URL=sqlite:///bot_data.db
ENCRYPTION_KEY=your_32_char_encryption_key
```

### Configuration Class

```python
from tlgfwk import Config

# Load from environment
config = Config.from_env()

# Manual configuration
config = Config(
    bot_token="your_token",
    owner_user_id=123456789,
    admin_user_ids=[123456789],
    debug=True
)
```

### Advanced Configuration

```python
class MyBot(TelegramBotFramework):
    def __init__(self):
        super().__init__(
            # Basic config
            token="YOUR_TOKEN",
            owner_user_id=123456789,
            admin_user_ids=[123456789],
            
            # Advanced config
            debug=True,
            log_chat_id=123456789,
            database_url="sqlite:///mybot.db",
            max_workers=8,
            use_async=True,
            rate_limit_enabled=True,
            
            # Custom persistence
            persistence_backend="sqlite",
            persistence_config={
                "database_url": "sqlite:///mybot.db"
            }
        )
```

## Command System

### Basic Commands

```python
from tlgfwk import command

class MyBot(TelegramBotFramework):
    @command(name="start", description="Start the bot")
    async def start_command(self, update, context):
        await update.message.reply_text("Welcome! 🎉")
    
    @command(name="help", description="Show help")
    async def help_command(self, update, context):
        # Custom help implementation
        await self.send_help(update.effective_chat.id)
```

### Command with Arguments

```python
@command(name="echo", description="Echo your message")
async def echo_command(self, update, context):
    if context.args:
        message = " ".join(context.args)
        await update.message.reply_text(f"You said: {message}")
    else:
        await update.message.reply_text("Please provide a message to echo!")
```

### Permission-Protected Commands

```python
from tlgfwk import command, admin_required, owner_required

@command(name="admin", description="Admin only command")
@admin_required
async def admin_command(self, update, context):
    await update.message.reply_text("You are an admin! ⭐")

@command(name="shutdown", description="Shutdown bot")
@owner_required
async def shutdown_command(self, update, context):
    await update.message.reply_text("Shutting down...")
    self.stop()
```

### Advanced Decorators

```python
from tlgfwk import rate_limit, validate_args, typing_action, log_command

@command(name="process", description="Process data")
@rate_limit(max_calls=5, window=60)  # 5 calls per minute
@validate_args(min_args=1, max_args=3)
@typing_action  # Show typing indicator
@log_command    # Log command usage
async def process_command(self, update, context):
    # Command implementation
    pass
```

## Plugin System

### Using Built-in Plugins

```python
from tlgfwk import SystemMonitorPlugin, UserStatsPlugin

class MyBot(TelegramBotFramework):
    def setup_plugins(self):
        # Load system monitor
        system_monitor = SystemMonitorPlugin(self)
        self.plugin_manager.load_plugin_instance("system_monitor", system_monitor)
        
        # Load user statistics
        user_stats = UserStatsPlugin(self)
        self.plugin_manager.load_plugin_instance("user_stats", user_stats)
```

### Creating Custom Plugins

```python
from tlgfwk import PluginBase, command

class WeatherPlugin(PluginBase):
    def __init__(self, bot):
        super().__init__(bot)
        self.name = "Weather"
        self.version = "1.0.0"
        self.description = "Weather information plugin"
    
    def initialize(self):
        super().initialize()
        # Plugin initialization code
    
    @command(name="weather", description="Get weather info")
    async def weather_command(self, update, context):
        # Weather command implementation
        await update.message.reply_text("☀️ It's sunny!")
    
    def get_help_text(self):
        return "Weather plugin provides weather information commands."
```

### Plugin Configuration

```python
class WeatherPlugin(PluginBase):
    def initialize(self):
        super().initialize()
        
        # Plugin-specific configuration
        self.config = {
            'api_key': self.bot.config.get('WEATHER_API_KEY'),
            'default_city': 'New York',
            'units': 'metric'
        }
```

## User Management

### User Registration

Users are automatically registered when they interact with the bot:

```python
# Get user information
user = self.user_manager.get_user(user_id)
if user:
    print(f"User: {user.first_name} (@{user.username})")
    print(f"Last seen: {user.last_seen}")
    print(f"Message count: {user.message_count}")
```

### Admin Management

```python
# Check if user is admin
if self.user_manager.is_admin(user_id):
    # Admin-specific code
    pass

# Add/remove admins
self.user_manager.add_admin(user_id)
self.user_manager.remove_admin(user_id)

# List all users
all_users = self.user_manager.list_users()
admin_users = self.user_manager.list_users(admin_only=True)
```

### User Statistics

```python
# Get user stats
stats = self.user_manager.get_user_stats(user_id)
print(f"Total messages: {stats['total_messages']}")
print(f"Commands used: {stats['commands_used']}")
```

## Persistence

### Data Storage

The framework provides automatic persistence for:
- User data
- Bot configuration
- Plugin data
- Payment information
- Job schedules

### Custom Data Persistence

```python
# Save custom data
self.persistence.save_user_data(user_id, "preferences", {
    "language": "en",
    "timezone": "UTC",
    "notifications": True
})

# Load custom data
preferences = self.persistence.load_user_data(user_id, "preferences")

# Bot-level data
self.persistence.save_bot_data("statistics", {
    "total_users": 1000,
    "uptime": "30 days"
})
```

### Database Backends

```python
# SQLite (default)
persistence_config = {
    "backend": "sqlite",
    "database_url": "sqlite:///bot_data.db"
}

# PostgreSQL
persistence_config = {
    "backend": "postgresql",
    "database_url": "postgresql://user:pass@localhost/botdb"
}

# JSON files
persistence_config = {
    "backend": "json",
    "data_dir": "./bot_data"
}
```

## Payment Integration

### Setting Up Payments

```python
from tlgfwk import PaymentManager

# Configure payment providers
payment_config = {
    'providers': {
        'stripe': {
            'api_key': 'sk_test_...',
            'webhook_secret': 'whsec_...'
        },
        'pix': {
            'account_key': 'your_pix_key',
            'merchant_name': 'Your Business'
        }
    }
}

payment_manager = PaymentManager(self, payment_config)
```

### Creating Payments

```python
from tlgfwk.core.payment_manager import PaymentItem, PaymentProvider

@command(name="buy", description="Purchase a service")
async def buy_command(self, update, context):
    items = [
        PaymentItem(
            name="Premium Service",
            description="Access to premium features",
            price=9.99,
            currency="USD"
        )
    ]
    
    result = self.payment_manager.create_payment(
        user_id=update.effective_user.id,
        items=items,
        provider=PaymentProvider.STRIPE,
        description="Premium service subscription"
    )
    
    if result.success:
        payment_url = result.payment_request.payment_url
        await update.message.reply_text(f"💳 Payment link: {payment_url}")
    else:
        await update.message.reply_text("❌ Payment creation failed")
```

### Payment Webhooks

```python
# Handle payment verification
def handle_payment_webhook(self, payment_data):
    result = self.payment_manager.verify_payment(
        payment_id=payment_data['payment_id'],
        provider_data=payment_data
    )
    
    if result.success and result.payment_request.status == PaymentStatus.COMPLETED:
        # Grant access to premium features
        user_id = result.payment_request.user_id
        self.grant_premium_access(user_id)
```

## Job Scheduling

### Basic Scheduling

```python
from tlgfwk import JobScheduler
from datetime import datetime, timedelta

# Schedule a one-time job
self.scheduler.add_job(
    func=self.send_reminder,
    trigger='date',
    run_date=datetime.now() + timedelta(hours=1),
    args=[user_id, "Don't forget your task!"]
)

# Schedule a recurring job
self.scheduler.add_job(
    func=self.daily_backup,
    trigger='cron',
    hour=2,  # 2 AM daily
    minute=0
)

# Schedule with interval
self.scheduler.add_job(
    func=self.health_check,
    trigger='interval',
    minutes=30
)
```

### Decorated Jobs

```python
from tlgfwk.core.scheduler import scheduled_job

@scheduled_job('cron', hour=9, minute=0, name='daily_report')
def daily_report(self):
    # Generate and send daily report
    pass

# Register decorated jobs
self.scheduler.register_job_functions(self)
```

### Job Management

```python
# List jobs
jobs = self.scheduler.list_jobs()

# Pause/resume jobs
self.scheduler.pause_job('job_id')
self.scheduler.resume_job('job_id')

# Remove jobs
self.scheduler.remove_job('job_id')

# Run job immediately
self.scheduler.run_job_now('job_id')
```

## Logging

### Basic Logging

```python
from tlgfwk import get_logger

class MyBot(TelegramBotFramework):
    def __init__(self):
        super().__init__(...)
        self.logger = get_logger(__name__)
    
    @command(name="test", description="Test command")
    async def test_command(self, update, context):
        self.logger.info(f"Test command called by {update.effective_user.id}")
        # Command implementation
```

### Advanced Logging Configuration

```python
from tlgfwk import setup_logging

# Configure logging
setup_logging(
    level="INFO",
    log_file="bot.log",
    max_file_size=10 * 1024 * 1024,  # 10MB
    backup_count=5,
    telegram_bot=self.application.bot,
    telegram_chat_id=self.config.log_chat_id
)
```

### Performance Logging

```python
from tlgfwk.utils.logger import PerformanceLogger

perf_logger = PerformanceLogger()

@perf_logger.time_it
async def slow_operation(self):
    # Operation that you want to measure
    pass

# Manual timing
with perf_logger.timer("database_query"):
    result = await self.database.query(...)
```

## Security

### Encryption

```python
from tlgfwk.utils.crypto import CryptoUtils

# Initialize crypto utilities
crypto = CryptoUtils(master_key="your_secret_key")

# Encrypt sensitive data
encrypted = crypto.encrypt_string("sensitive_data")
decrypted = crypto.decrypt_string(encrypted)

# Hash passwords
hashed, salt = crypto.hash_password("user_password")
is_valid = crypto.verify_password("user_password", hashed, salt)
```

### Environment Security

```python
from tlgfwk.utils.crypto import EnvCrypto

# Encrypt .env file
env_crypto = EnvCrypto()
env_crypto.encrypt_env_file(".env", ".env.encrypted")

# Decrypt when needed
env_crypto.decrypt_env_file(".env.encrypted", ".env")
```

### Rate Limiting

```python
from tlgfwk import rate_limit

@command(name="api_call", description="Make API call")
@rate_limit(max_calls=10, window=60)  # 10 calls per minute
async def api_call_command(self, update, context):
    # Rate-limited command
    pass
```

## Deployment

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  bot:
    build: .
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - OWNER_USER_ID=${OWNER_USER_ID}
    volumes:
      - ./data:/app/data
    restart: unless-stopped
  
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=botdb
      - POSTGRES_USER=botuser
      - POSTGRES_PASSWORD=botpass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Production Configuration

```python
# production_config.py
import os

class ProductionBot(TelegramBotFramework):
    def __init__(self):
        super().__init__(
            token=os.getenv("BOT_TOKEN"),
            owner_user_id=int(os.getenv("OWNER_USER_ID")),
            admin_user_ids=[int(x) for x in os.getenv("ADMIN_USER_IDS", "").split(",")],
            
            # Production settings
            debug=False,
            max_workers=16,
            use_async=True,
            rate_limit_enabled=True,
            
            # Database
            database_url=os.getenv("DATABASE_URL"),
            
            # Logging
            log_level="INFO",
            log_chat_id=int(os.getenv("LOG_CHAT_ID")),
            
            # Security
            encryption_key=os.getenv("ENCRYPTION_KEY")
        )
```

### Health Checks

```python
@command(name="health", description="Health check endpoint")
async def health_command(self, update, context):
    try:
        # Check database
        self.persistence.save_bot_data("health_check", "ok")
        
        # Check external services
        # ... health check logic ...
        
        await update.message.reply_text("✅ All systems operational")
    except Exception as e:
        await update.message.reply_text(f"❌ Health check failed: {e}")
```

## Troubleshooting

### Common Issues

#### Bot Not Responding

```python
# Check bot token
try:
    bot_info = await self.application.bot.get_me()
    print(f"Bot username: {bot_info.username}")
except Exception as e:
    print(f"Invalid bot token: {e}")
```

#### Permission Errors

```python
# Verify user permissions
user_id = update.effective_user.id
is_admin = self.user_manager.is_admin(user_id)
is_owner = user_id == self.config.owner_user_id

print(f"User {user_id}: admin={is_admin}, owner={is_owner}")
```

#### Database Issues

```python
# Test database connectivity
try:
    self.persistence.save_bot_data("test", "value")
    value = self.persistence.load_bot_data("test")
    print(f"Database test: {value}")
except Exception as e:
    print(f"Database error: {e}")
```

### Debug Mode

Enable debug mode for detailed logging:

```python
# In .env file
DEBUG=true

# Or in code
bot = TelegramBotFramework(
    debug=True,
    log_level="DEBUG"
)
```

### Error Handling

```python
@command(name="risky", description="Command that might fail")
async def risky_command(self, update, context):
    try:
        # Risky operation
        result = await some_api_call()
        await update.message.reply_text(f"Result: {result}")
    except Exception as e:
        self.logger.error(f"Command failed: {e}", exc_info=True)
        await update.message.reply_text("❌ Something went wrong. Please try again later.")
```

### Performance Monitoring

```python
import time
import psutil
import os

@command(name="perf", description="Performance statistics")
@admin_required
async def perf_command(self, update, context):
    # Bot uptime
    uptime = time.time() - self.start_time
    
    # Memory usage
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    
    # System resources
    cpu_percent = psutil.cpu_percent()
    memory_percent = psutil.virtual_memory().percent
    
    stats = f"""📊 **Performance Stats**
    
**Bot Uptime:** {uptime:.0f} seconds
**Memory Usage:** {memory_mb:.1f} MB
**CPU Usage:** {cpu_percent:.1f}%
**System Memory:** {memory_percent:.1f}%
**Active Users:** {len(self.user_manager.users)}
"""
    
    await update.message.reply_text(stats, parse_mode='Markdown')
```

This user guide covers the essential aspects of using the Telegram Bot Framework. For more detailed API documentation, see the API reference in the docs folder.
