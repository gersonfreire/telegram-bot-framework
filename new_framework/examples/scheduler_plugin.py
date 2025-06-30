#!/usr/bin/env python3
"""
SchedulerPlugin - Plugin de demonstração para o Scheduler Bot

Este plugin demonstra como usar o sistema de agendamentos do framework
através de plugins.
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Adicionar o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tlgfwk import PluginBase
from telegram import Update
from telegram.ext import ContextTypes


class SchedulerPlugin(PluginBase):
    """Plugin de demonstração para o Scheduler Bot."""

    name = "SchedulerPlugin"
    version = "1.0.0"
    description = "Plugin de demonstração do sistema de agendamentos"
    author = "Framework Demo"

    def __init__(self):
        super().__init__()
        # Registrar comandos do plugin
        self.register_command({
            "name": "plugin_schedule",
            "handler": self.plugin_schedule_command,
            "description": "Demonstra agendamentos do plugin"
        })

    async def initialize(self, framework, config):
        """Chamado quando o plugin é inicializado."""
        await super().initialize(framework, config)
        print(f"✅ Plugin {self.name} inicializado com sucesso!")
        return True

    async def plugin_schedule_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Demonstra agendamentos do plugin."""
        user = update.effective_user

        # Criar ID único para o job
        job_id = f"plugindemo_{user.id}_{datetime.now().timestamp()}"
        self.framework.scheduler.add_job(
            func=self._send_plugin_notification,
            trigger='date',
            run_date=datetime.now() + timedelta(seconds=30),
            args=[user.id, "Plugin Demo"],
            id=job_id
        )

        message = (
            f"🔌 <b>Plugin Scheduler Demo</b>\n\n"
            f"✅ Agendamento criado com sucesso!\n"
            f"🆔 <b>Job ID:</b> {job_id}\n"
            f"⏰ <b>Execução:</b> 30 segundos\n"
            f"📝 <b>Mensagem:</b> Plugin Demo\n\n"
            f"💡 Você receberá uma notificação em 30 segundos!"
        )
        await update.message.reply_text(message, parse_mode='HTML')

    async def _send_plugin_notification(self, user_id: int, message: str):
        """Enviar notificação agendada do plugin."""
        try:
            await self.framework.application.bot.send_message(
                chat_id=user_id,
                text=f"🔌 <b>Notificação do Plugin</b>\n\n{message}\n\n⏰ Enviada em: {datetime.now().strftime('%H:%M:%S')}",
                parse_mode='HTML'
            )
        except Exception as e:
            print(f"Erro ao enviar notificação do plugin: {e}")


# Função para criar instância do plugin (requerida pelo framework)
def create_plugin():
    """Função para criar instância do plugin."""
    return SchedulerPlugin()
