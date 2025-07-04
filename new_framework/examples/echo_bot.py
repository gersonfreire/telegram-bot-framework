"""
Simple Echo Bot Example

This example demonstrates the basic usage of the Telegram Bot Framework.
The bot echoes back any message it receives and provides basic commands.
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime

# Add the src directory to the path so we can import the framework
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tlgfwk import TelegramBotFramework, command
from telegram import Update
from telegram.ext import ContextTypes


class EchoBot(TelegramBotFramework):
    """Simple echo bot that responds to messages."""

    def __init__(self, cli_args=None):
        # Verificar arquivo .env na pasta examples
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")

        # Configurar pasta de plugins para usar a pasta plugins do framework (caminho absoluto)
        plugins_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "plugins")
        plugins_dir = os.path.abspath(plugins_dir)  # Converter para caminho absoluto

        # Initialize with configuration from .env file and plugins directory, and opcionalmente cli_args
        super().__init__(config_file=env_path, plugins_dir=plugins_dir, cli_args=cli_args)

        # Garantir que o carregamento automático de plugins está habilitado
        self.config.data['auto_load_plugins'] = True

        # Initialize scheduler_stats for plugin compatibility
        self.scheduler_stats = {
            'jobs_created': 0,
            'jobs_completed': 0,
            'jobs_failed': 0,
            'start_time': datetime.now()
        }

    def setup_handlers(self):
        """Set up custom message handlers."""
        # Add echo handler for non-command messages
        from telegram.ext import MessageHandler, filters
        if self.application:
            self.application.add_handler(
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.echo_message)
            )
            print("✅ Echo handler registered!")

        # Register command handlers (decorators should handle this automatically)
        self.register_decorated_commands()
        print("✅ Command handlers registered!")

    @command(name="echo", description="Echo back your message")
    async def echo_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Echo command handler."""
        if context.args:
            message = " ".join(context.args)
            await update.message.reply_text(f"🔊 Echo: {message}")
        else:
            await update.message.reply_text("Please provide a message to echo!")

    @command(name="reverse", description="Reverse your message")
    async def reverse_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Reverse message command."""
        if context.args:
            message = " ".join(context.args)
            reversed_message = message[::-1]
            await update.message.reply_text(f"🔄 Reversed: {reversed_message}")
        else:
            await update.message.reply_text("Please provide a message to reverse!")

    @command(name="count", description="Count words in your message")
    async def count_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Count words in message."""
        if context.args:
            message = " ".join(context.args)
            word_count = len(message.split())
            char_count = len(message)
            await update.message.reply_text(
                f"📊 Statistics:\n"
                f"Words: {word_count}\n"
                f"Characters: {char_count}"
            )
        else:
            await update.message.reply_text("Please provide a message to count!")

    async def echo_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Echo non-command messages."""
        if update.message and update.message.text:
            await update.message.reply_text(f"🤖 You said: {update.message.text}")


def main():
    """Main function to run the bot."""
    print("🚀 Starting Echo Bot...")
    print("=" * 50)

    # Verificar arquivo .env na pasta examples
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.exists(env_path):
        print("⚠️  Arquivo .env não encontrado na pasta examples!")
        print("📝 Crie um arquivo .env com as seguintes variáveis:")
        print("   BOT_TOKEN=seu_token_aqui")
        print("   OWNER_USER_ID=seu_id_aqui")
        print("   ADMIN_USER_IDS=id1,id2,id3")
        print("   LOG_CHAT_ID=chat_id_para_logs")
        print("   DEBUG=true")
        print("=" * 50)
        return

    try:
        import sys
        # Create and run the bot, repassando sys.argv[1:]
        bot = EchoBot(cli_args=sys.argv[1:])

        # Setup handlers
        bot.setup_handlers()

        print("✅ Echo Bot criado com sucesso!")
        print("🎯 Funcionalidades disponíveis:")
        print("   • Echo de mensagens")
        print("   • Comandos /echo, /reverse, /count")
        print("   • Framework completo")
        print("=" * 50)
        print("🤖 Bot iniciado! Pressione Ctrl+C para parar")

        # Run the bot
        bot.run()

    except KeyboardInterrupt:
        print("\n⏹️  Bot parado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao executar o bot: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
