# Modern Host Watch Bot 🤖

A modern, well-architected Telegram bot for monitoring hosts and services with clean code and best practices.

## 🚀 Features

### 🎯 Host Monitoring
- **Ping Monitoring**: ICMP ping checks for host availability
- **Port Monitoring**: TCP port connectivity verification
- **Flexible Scheduling**: Configurable intervals (2-40 minutes)
- **Real-time Notifications**: Instant alerts when hosts go down

### 🔧 Management
- **Easy Setup**: Simple commands to add/remove hosts
- **Dynamic Configuration**: Change intervals and ports without restart
- **User Isolation**: Each user manages their own hosts
- **Persistent Storage**: Configurations survive bot restarts

### 🔐 Remote Access
- **SSH Commands**: Execute commands on remote hosts
- **Secure Credentials**: Encrypted storage of SSH credentials
- **Local Commands**: Execute commands on bot server (admin only)
- **Access Control**: Role-based permissions

### 📊 Reporting
- **Status Overview**: Real-time host status display
- **Failure History**: Track when hosts went down
- **Detailed Logs**: Configurable logging levels
- **Rich Formatting**: Markdown tables and clickable links

## 🏗️ Architecture

The bot is built with modern Python practices:

- **Clean Architecture**: Separation of concerns with clear layers
- **Type Hints**: Full type annotations for better code quality
- **Async/Await**: Non-blocking operations throughout
- **Pydantic Models**: Data validation and serialization
- **SQLite Database**: Lightweight, persistent storage
- **Modular Design**: Easy to extend and maintain

## 📦 Installation

### Prerequisites
- Python 3.8+
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd modern_host_watch_bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the bot**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Generate encryption key**
   ```python
   from cryptography.fernet import Fernet
   print(Fernet.generate_key().decode())
   ```

5. **Run the bot**
   ```bash
   python main.py
   ```

## ⚙️ Configuration

Create a `.env` file with the following variables:

```env
# Required
BOT_TOKEN=your_telegram_bot_token_here
BOT_OWNER_ID=123456789
ENCRYPTION_KEY=your_32_character_encryption_key_here

# Optional
ADMIN_USER_IDS=123456789,987654321
DATABASE_URL=sqlite:///./bot_data.db
LOG_LEVEL=INFO
```

## 📋 Commands

### Basic Commands
- `/start` - Initialize the bot
- `/help` - Show help and available commands

### Host Management
- `/pingadd <host> <interval>` - Add host to monitoring
- `/pingdelete <host>` - Remove host from monitoring
- `/pinglist` - List your monitored hosts
- `/pinglist all` - List all hosts (admin only)

### Manual Checks
- `/pinghost <host>` - Manual ping check
- `/pinghostport <host> <port>` - Check specific port

### Configuration
- `/pinginterval <host> <seconds>` - Change check interval
- `/changepingport <host> <port>` - Change monitored port
- `/storecredentials <host> <user> <pass> [port]` - Store SSH credentials
- `/pinglog` - Toggle success notifications

### Reports
- `/listfailures` - Show recent failures

### Admin Commands
- `/exec <command>` - Execute local command (admin only)
- `/ssh <host> <command>` - Execute SSH command (admin only)

## 🔧 Usage Examples

### Monitor a Web Server
```bash
/pingadd example.com 300 80
```
Monitors example.com every 5 minutes, checking port 80.

### Monitor HTTPS Service
```bash
/pingadd api.example.com 600 443
```
Monitors API server every 10 minutes, checking HTTPS port.

### Store SSH Credentials
```bash
/storecredentials myserver admin mypassword 22
```
Stores SSH credentials for remote command execution.

### Execute Remote Command
```bash
/ssh myserver uptime
```
Runs `uptime` command on the remote server.

## 🏛️ Project Structure

```
modern_host_watch_bot/
├── src/
│   ├── config/          # Configuration management
│   ├── core/            # Main bot application
│   ├── handlers/        # Command handlers
│   ├── models/          # Data models
│   ├── services/        # Business logic services
│   └── utils/           # Utility functions
├── tests/               # Test files
├── docs/                # Documentation
├── main.py              # Entry point
├── requirements.txt     # Dependencies
└── README.md           # This file
```

## 🔒 Security Features

- **Encrypted Credentials**: SSH passwords are encrypted using Fernet
- **Access Control**: Admin-only commands for sensitive operations
- **Input Validation**: All inputs are validated using Pydantic
- **SQL Injection Protection**: Parameterized queries
- **Error Handling**: Secure error messages without information leakage

## 🧪 Testing

Run tests with pytest:

```bash
pytest tests/
```

## 📈 Performance

- **Concurrent Checks**: Multiple hosts checked simultaneously
- **Efficient Database**: SQLite with optimized queries
- **Memory Management**: Proper cleanup of resources
- **Timeout Protection**: Prevents hanging operations

## 🔄 Monitoring Workflow

1. **Add Host**: User adds host with `/pingadd`
2. **Schedule Job**: Bot creates recurring monitoring job
3. **Execute Checks**: Bot pings host and checks port
4. **Update Status**: Results stored in database
5. **Send Notifications**: Alerts sent on failures
6. **Persist Data**: All data survives restarts

## 🛠️ Development

### Code Style
- **Black**: Code formatting
- **isort**: Import sorting
- **mypy**: Type checking

### Running in Development
```bash
# Install development dependencies
pip install -r requirements.txt

# Run with debug logging
LOG_LEVEL=DEBUG python main.py
```

## 📝 Logging

The bot provides comprehensive logging:

- **File Logging**: All logs saved to `bot.log`
- **Console Logging**: Real-time log output
- **Configurable Levels**: DEBUG, INFO, WARNING, ERROR
- **Structured Format**: Timestamp, level, module, message

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- Create an issue on GitHub
- Check the documentation in `/docs`
- Review the example configuration

## 🚀 Roadmap

- [ ] HTTP/HTTPS monitoring
- [ ] Custom notification channels
- [ ] Web dashboard
- [ ] Integration with monitoring systems
- [ ] Backup and restore functionality
- [ ] Multi-language support

---

**Modern Host Watch Bot** - Built with ❤️ and modern Python practices 