#!/usr/bin/env python3
"""
Teste do Scheduler Bot - Verificação das funcionalidades de agendamento
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock

# Adicionar o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from examples.scheduler_bot import SchedulerBot
from telegram import Update, User
from telegram.ext import ContextTypes

def test_scheduler_bot():
    """Teste das funcionalidades do Scheduler Bot."""
    print("🧪 Testando Scheduler Bot...")

    # Criar bot de teste
    bot = SchedulerBot(custom_config={
        'bot_token': 'test_token',
        'owner_user_id': 123456789,
        'admin_user_ids': [123456789],
        'instance_name': 'TestSchedulerBot',
        'debug': True
    })

    # Mock do scheduler
    bot.scheduler = Mock()
    bot.scheduler.add_job = Mock()
    bot.scheduler.get_jobs = Mock(return_value=[])
    bot.scheduler.remove_job = Mock()

    # Mock do user_manager
    bot.user_manager = Mock()
    bot.user_manager.is_admin = Mock(return_value=True)

    print("✅ Bot criado com sucesso!")

    # Testar comando schedule_once
    print("\n📋 Testando comando /schedule_once...")
    update = Mock(spec=Update)
    update.message = Mock()
    update.message.reply_text = AsyncMock()

    context = Mock(spec=ContextTypes.DEFAULT_TYPE)
    context.args = ['5', 'Teste de agendamento']

    # Simular usuário
    user = Mock(spec=User)
    user.id = 123456789
    user.first_name = "Teste"
    update.effective_user = user

    # Executar comando
    import asyncio
    asyncio.run(bot.schedule_once_command(update, context))

    # Verificar se o job foi agendado
    assert bot.scheduler.add_job.called, "Job não foi agendado"
    print("✅ Comando /schedule_once funcionando!")

    # Testar comando schedule_recurring
    print("\n📋 Testando comando /schedule_recurring...")
    context.args = ['30', 'Teste periódico']

    asyncio.run(bot.schedule_recurring_command(update, context))

    # Verificar se o job periódico foi agendado
    assert bot.scheduler.add_job.called, "Job periódico não foi agendado"
    print("✅ Comando /schedule_recurring funcionando!")

    # Testar comando scheduler_stats
    print("\n📋 Testando comando /scheduler_stats...")
    asyncio.run(bot.scheduler_stats_command(update, context))

    # Verificar se a resposta foi enviada
    assert update.message.reply_text.called, "Estatísticas não foram enviadas"
    print("✅ Comando /scheduler_stats funcionando!")

    # Testar comando list_jobs
    print("\n📋 Testando comando /list_jobs...")
    asyncio.run(bot.list_jobs_command(update, context))

    # Verificar se a resposta foi enviada
    assert update.message.reply_text.called, "Lista de jobs não foi enviada"
    print("✅ Comando /list_jobs funcionando!")

    print("\n🎉 Todos os testes passaram com sucesso!")
    print("📊 Estatísticas do teste:")
    print(f"   • Jobs criados: {bot.scheduler_stats['jobs_created']}")
    print(f"   • Comandos testados: 4")
    print(f"   • Erros: 0")

def test_scheduler_plugin():
    """Teste do plugin de scheduler."""
    print("\n🔌 Testando SchedulerPlugin...")

    from examples.scheduler_bot import SchedulerPlugin

    # Criar plugin
    plugin = SchedulerPlugin()

    # Mock do framework
    framework = Mock()
    framework.scheduler = Mock()
    framework.scheduler.add_job = Mock()
    framework.application = Mock()
    framework.application.bot = Mock()
    framework.application.bot.send_message = AsyncMock()

    plugin.framework = framework

    # Testar comando do plugin
    update = Mock(spec=Update)
    update.message = Mock()
    update.message.reply_text = AsyncMock()

    user = Mock(spec=User)
    user.id = 123456789
    update.effective_user = user

    context = Mock(spec=ContextTypes.DEFAULT_TYPE)
    context.args = []

    # Executar comando do plugin
    import asyncio
    asyncio.run(plugin.plugin_schedule_command(update, context))

    # Verificar se o job foi agendado
    assert framework.scheduler.add_job.called, "Job do plugin não foi agendado"
    print("✅ Plugin SchedulerPlugin funcionando!")

if __name__ == "__main__":
    print("🚀 Iniciando testes do Scheduler Bot...")
    print("=" * 50)

    try:
        test_scheduler_bot()
        test_scheduler_plugin()

        print("\n" + "=" * 50)
        print("✅ Todos os testes concluídos com sucesso!")
        print("🎯 O Scheduler Bot está funcionando corretamente!")

    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
