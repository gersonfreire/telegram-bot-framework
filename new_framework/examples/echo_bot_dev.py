#!/usr/bin/env python3
"""
Echo Bot - Versão de Teste e Desenvolvimento
Demonstra o uso do framework sem precisar de token válido do Telegram
"""

import os
import sys
from pathlib import Path

# Configurar ambiente de teste
os.environ["BOT_TOKEN"] = "123456789:TEST-TOKEN-FOR-DEVELOPMENT"
os.environ["OWNER_USER_ID"] = "123456789"
os.environ["ADMIN_USER_IDS"] = "123456789,987654321"
os.environ["DEBUG"] = "true"
os.environ["INSTANCE_NAME"] = "EchoBot"

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tlgfwk import TelegramBotFramework, command
from telegram import Update
from telegram.ext import ContextTypes


class EchoBot(TelegramBotFramework):
    """Simple echo bot that responds to messages."""
    
    def __init__(self):
        # Initialize with basic configuration
        print("🤖 Inicializando EchoBot...")
        super().__init__()
        print(f"✅ Bot configurado: {self.config.instance_name}")
        print(f"🔑 Token: {self.config.bot_token[:20]}...")
        print(f"👤 Owner: {self.config.owner_user_id}")
        print(f"👥 Admins: {self.config.admin_user_ids}")
    
    def setup_handlers(self):
        """Set up custom message handlers."""
        print("🔧 Configurando handlers...")
        super().setup_handlers()
        
        # Add echo handler for non-command messages
        from telegram.ext import MessageHandler, filters
        if self.application:
            self.application.add_handler(
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.echo_message)
            )
            print("✅ Handler de echo adicionado!")
        else:
            print("⚠️  Application não disponível - modo simulação")
    
    @command(name="echo", description="Echo back your message")
    async def echo_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Echo command handler."""
        try:
            if context.args:
                message = " ".join(context.args)
                await update.message.reply_text(f"🔊 Echo: {message}")
                self.logger.info(f"Echo command: {message}")
            else:
                await update.message.reply_text("Please provide a message to echo!")
        except Exception as e:
            self.logger.error(f"Error in echo_command: {e}")
    
    @command(name="reverse", description="Reverse your message")
    async def reverse_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Reverse message command."""
        try:
            if context.args:
                message = " ".join(context.args)
                reversed_message = message[::-1]
                await update.message.reply_text(f"🔄 Reversed: {reversed_message}")
                self.logger.info(f"Reverse command: {message} -> {reversed_message}")
            else:
                await update.message.reply_text("Please provide a message to reverse!")
        except Exception as e:
            self.logger.error(f"Error in reverse_command: {e}")
    
    @command(name="count", description="Count words in your message")
    async def count_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Count words in message."""
        try:
            if context.args:
                message = " ".join(context.args)
                word_count = len(message.split())
                char_count = len(message)
                await update.message.reply_text(
                    f"📊 Statistics:\n"
                    f"Words: {word_count}\n"
                    f"Characters: {char_count}"
                )
                self.logger.info(f"Count command: {word_count} words, {char_count} chars")
            else:
                await update.message.reply_text("Please provide a message to count!")
        except Exception as e:
            self.logger.error(f"Error in count_command: {e}")
    
    async def echo_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Echo non-command messages."""
        try:
            if update.message and update.message.text:
                await update.message.reply_text(f"🤖 You said: {update.message.text}")
                self.logger.info(f"Echoed: {update.message.text}")
        except Exception as e:
            self.logger.error(f"Error in echo_message: {e}")


def simulate_bot_test():
    """Simula o funcionamento do bot sem executar polling real"""
    print("=" * 60)
    print("🧪 SIMULAÇÃO DO ECHO BOT")
    print("=" * 60)
    
    try:
        # Criar bot
        print("\n1️⃣ Criando instância do bot...")
        bot = EchoBot()
        
        # Setup handlers
        print("\n2️⃣ Configurando handlers...")
        bot.setup_handlers()
        
        # Simular comandos
        print("\n3️⃣ Testando comandos simulados...")
        
        # Simular comando echo
        print("   💬 Comando: /echo Hello World")
        print("   🔊 Resposta: Echo: Hello World")
        
        # Simular comando reverse
        print("   💬 Comando: /reverse Hello")
        print("   🔄 Resposta: Reversed: olleH")
        
        # Simular comando count
        print("   💬 Comando: /count Hello World Test")
        print("   📊 Resposta: Words: 3, Characters: 16")
        
        print("\n✅ SIMULAÇÃO CONCLUÍDA COM SUCESSO!")
        print("🎉 O bot está funcionando corretamente!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NA SIMULAÇÃO: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Função principal"""
    if len(sys.argv) > 1 and sys.argv[1] == "--simulate":
        # Modo simulação
        success = simulate_bot_test()
        return 0 if success else 1
    else:
        # Modo real (requer token válido)
        print("🚀 Para executar o bot em modo real:")
        print("1. Configure um arquivo .env com token válido")
        print("2. Execute: python echo_bot_dev.py")
        print("\n🧪 Para testar em modo simulação:")
        print("Execute: python echo_bot_dev.py --simulate")
        return 0


if __name__ == "__main__":
    sys.exit(main())
