#!/usr/bin/env python3
"""
Teste do comando user_info
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from examples.demo_bot import DemoBot
from telegram import Update, User
from telegram.ext import ContextTypes
from unittest.mock import Mock, AsyncMock

def test_user_info_command():
    """Teste do comando user_info."""
    print("🧪 Testando comando /user_info...")

    # Criar bot de teste
    bot = DemoBot(custom_config={
        'bot_token': 'test_token',
        'owner_user_id': 123456789,
        'admin_user_ids': [123456789],
        'instance_name': 'TestBot',
        'debug': True
    })

    # Mock do user_manager para teste
    bot.user_manager = Mock()
    bot.user_manager.get_user = AsyncMock(return_value={
        'id': 987654321,
        'username': 'testuser',
        'first_name': 'Test',
        'last_name': 'User',
        'is_admin': False,
        'last_activity': '2025-06-29T18:00:00'
    })
    bot.user_manager.is_admin = Mock(return_value=False)
    bot.user_manager.is_owner = Mock(return_value=False)

    # Mock do update e context
    update = Mock(spec=Update)
    update.message = Mock()
    update.message.reply_text = AsyncMock()

    context = Mock(spec=ContextTypes.DEFAULT_TYPE)

    # Simular usuário
    update.effective_user = Mock(spec=User)
    update.effective_user.id = 987654321
    update.effective_user.first_name = 'Test'
    update.effective_user.last_name = 'User'
    update.effective_user.username = 'testuser'
    update.effective_user.language_code = 'pt'

    print("✅ Bot de teste criado")

    # Executar comando
    try:
        import asyncio
        asyncio.run(bot.user_info_command(update, context))

        print("✅ Comando executado com sucesso")

        # Verificar se reply_text foi chamado
        if update.message.reply_text.called:
            print("✅ reply_text foi chamado corretamente")
            # Verificar se a mensagem contém informações do usuário
            call_args = update.message.reply_text.call_args
            if call_args and len(call_args[0]) > 0:
                message = call_args[0][0]
                if "Test" in message and "987654321" in message:
                    print("✅ Mensagem contém informações corretas do usuário")
                else:
                    print("❌ Mensagem não contém informações corretas")
        else:
            print("❌ reply_text não foi chamado")

    except Exception as e:
        print(f"❌ Erro ao executar comando: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Iniciando teste do comando /user_info")
    print("=" * 50)

    test_user_info_command()

    print("\n" + "=" * 50)
    print("✅ Teste concluído!")
