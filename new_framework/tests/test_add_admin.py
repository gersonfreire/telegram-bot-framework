#!/usr/bin/env python3
"""
Teste do comando add_admin sem precisar de token real
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

def test_add_admin_command():
    """Teste do comando add_admin."""
    print("🧪 Testando comando /add_admin...")

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
        'is_admin': False
    })
    bot.user_manager.save_user = AsyncMock()

    # Mock do update e context
    update = Mock(spec=Update)
    update.message = Mock()
    update.message.reply_text = AsyncMock()

    context = Mock(spec=ContextTypes.DEFAULT_TYPE)
    context.args = ['987654321']  # ID do usuário a ser adicionado como admin

    # Simular que o usuário atual é owner
    update.effective_user = Mock(spec=User)
    update.effective_user.id = 123456789  # Owner ID

    print("✅ Bot de teste criado")
    print(f"📋 Config inicial - Admin IDs: {bot.config.admin_user_ids}")

    # Executar comando
    try:
        import asyncio
        asyncio.run(bot.add_admin_command(update, context))

        print(f"✅ Comando executado com sucesso")
        print(f"📋 Config final - Admin IDs: {bot.config.admin_user_ids}")

        # Verificar se o user_id foi adicionado
        if 987654321 in bot.config.admin_user_ids:
            print("✅ Usuário 987654321 foi adicionado como admin!")
        else:
            print("❌ Usuário não foi adicionado à lista de admins")

        # Verificar se save_user foi chamado
        if bot.user_manager.save_user.called:
            print("✅ save_user foi chamado corretamente")
        else:
            print("❌ save_user não foi chamado")

    except Exception as e:
        print(f"❌ Erro ao executar comando: {e}")
        import traceback
        traceback.print_exc()

def test_add_admin_already_admin():
    """Teste do comando add_admin quando usuário já é admin."""
    print("\n🧪 Testando comando /add_admin (usuário já é admin)...")

    # Criar bot de teste
    bot = DemoBot(custom_config={
        'bot_token': 'test_token',
        'owner_user_id': 123456789,
        'admin_user_ids': [123456789],
        'instance_name': 'TestBot',
        'debug': True
    })
    bot.config.admin_user_ids.append(987654321)  # Adicionar usuário como admin

    # Mock do user_manager para teste
    bot.user_manager = Mock()
    bot.user_manager.get_user = AsyncMock(return_value={
        'id': 987654321,
        'username': 'testuser',
        'first_name': 'Test',
        'last_name': 'User',
        'is_admin': True
    })
    bot.user_manager.save_user = AsyncMock()

    # Mock do update e context
    update = Mock(spec=Update)
    update.message = Mock()
    update.message.reply_text = AsyncMock()

    context = Mock(spec=ContextTypes.DEFAULT_TYPE)
    context.args = ['987654321']  # ID do usuário que já é admin

    # Simular que o usuário atual é owner
    update.effective_user = Mock(spec=User)
    update.effective_user.id = 123456789  # Owner ID

    print(f"📋 Config inicial - Admin IDs: {bot.config.admin_user_ids}")

    # Executar comando
    try:
        import asyncio
        asyncio.run(bot.add_admin_command(update, context))

        print(f"✅ Comando executado com sucesso")
        print(f"📋 Config final - Admin IDs: {bot.config.admin_user_ids}")

        # Verificar se a mensagem correta foi enviada
        update.message.reply_text.assert_called_with("ℹ️ Usuário 987654321 já é admin.")
        print("✅ Mensagem correta foi enviada")

    except Exception as e:
        print(f"❌ Erro ao executar comando: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Iniciando testes do comando /add_admin")
    print("=" * 50)

    test_add_admin_command()
    test_add_admin_already_admin()

    print("\n" + "=" * 50)
    print("✅ Testes concluídos!")
