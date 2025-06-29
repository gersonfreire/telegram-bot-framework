#!/usr/bin/env python3
"""
Teste simples para verificar o decorador typing_indicator
"""

import sys
import asyncio
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from tlgfwk import TelegramBotFramework, command, typing_indicator
from telegram import Update
from telegram.ext import ContextTypes


class TestBot(TelegramBotFramework):
    """Bot de teste para verificar o typing_indicator."""

    def __init__(self):
        super().__init__()

    @command(name="test_typing", description="Teste do indicador de digitação")
    @typing_indicator
    async def test_typing_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Teste do indicador de digitação com delay."""
        import asyncio

        # Simular processamento
        await asyncio.sleep(3)

        await update.message.reply_text(
            "✅ Teste concluído! O status de 'writing...' deve ter aparecido por 3 segundos."
        )

    @command(name="fast_test", description="Teste rápido sem delay")
    @typing_indicator
    async def fast_test_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Teste rápido do indicador de digitação."""
        await update.message.reply_text(
            "⚡ Resposta rápida! O status de 'writing...' pode ter aparecido brevemente."
        )


def main():
    """Função principal."""
    print("🧪 Testando decorador typing_indicator...")

    try:
        bot = TestBot()
        print("✅ Bot de teste criado!")
        print("🤖 Use /test_typing para testar com delay de 3 segundos")
        print("⚡ Use /fast_test para teste rápido")
        print("💡 Verifique se aparece 'writing...' no Telegram")

        bot.run()

    except KeyboardInterrupt:
        print("\n⏹️ Teste interrompido")
    except Exception as e:
        print(f"❌ Erro: {e}")


if __name__ == "__main__":
    main()
