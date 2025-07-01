"""
Scheduler Plugin - Plugin para agendamento de tarefas no Telegram Bot Framework
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
from tlgfwk import (
    command, admin_required_simple, owner_required
)
from tlgfwk.plugins.base import PluginBase
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import asyncio
import functools


class SchedulerPlugin(PluginBase):
    name = "scheduler_plugin"
    version = "1.0.0"
    description = "Plugin de agendamento de tarefas (únicas e periódicas) para o Telegram Bot Framework."
    author = "Framework Demo"
    dependencies = []

    def __init__(self):
        super().__init__()
        self.bot = None
        self.scheduler = None
        self.user_manager = None
        self.persistence_manager = None
        self.config = None
        self.demo_jobs = {}
        self.scheduler_stats = {
            'jobs_created': 0,
            'jobs_completed': 0,
            'jobs_failed': 0,
            'start_time': datetime.now()
        }

    async def initialize(self, bot_instance, config=None):
        """Inicializar o plugin com a instância do bot."""
        self.bot = bot_instance
        self.scheduler = getattr(bot_instance, 'scheduler', None)
        self.user_manager = getattr(bot_instance, 'user_manager', None)
        self.persistence_manager = getattr(bot_instance, 'persistence_manager', None)
        self.config = getattr(bot_instance, 'config', None)

        print(f"✅ Plugin {self.name} inicializado com sucesso!")
        return True

    def get_commands(self) -> List[Dict[str, Any]]:
        """Retorna a lista de comandos do plugin para registro automático."""
        return [
            {
                "name": "plugin_schedule",
                "handler": self.plugin_schedule_command,
                "description": "Demo do comando de plugin de agendamento"
            },
            {
                "name": "schedule_once",
                "handler": self.schedule_once_command,
                "description": "Agendar tarefa única"
            },
            {
                "name": "schedule_recurring",
                "handler": self.schedule_recurring_command,
                "description": "Agendar tarefa periódica"
            },
            {
                "name": "list_jobs",
                "handler": self.list_jobs_command,
                "description": "Listar jobs agendados"
            },
            {
                "name": "cancel_job",
                "handler": self.cancel_job_command,
                "description": "Cancelar job específico"
            },
            {
                "name": "cancel_all",
                "handler": self.cancel_all_command,
                "description": "Cancelar todos os jobs do usuário"
            },
            {
                "name": "scheduler_stats",
                "handler": self.scheduler_stats_command,
                "description": "Estatísticas do scheduler"
            },
            {
                "name": "scheduler_config",
                "handler": self.scheduler_config_command,
                "description": "Configurações do scheduler"
            }
        ]

    # ===================== Comandos =====================
    @command(name="plugin_schedule", description="Demo do comando de plugin de agendamento")
    async def plugin_schedule_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        print(f"🔌 DEBUG: plugin_schedule_command chamado por {update.effective_user.first_name}")
        await update.message.reply_text(
            "🔌 <b>Plugin Schedule</b>\n\nEste é um comando de demonstração para integração de plugins com o sistema de agendamento.\n\n\u2022 Use este comando para testar a integração de plugins que registram comandos de agendamento.\n\n💡 Exemplo de uso:\n/plugin_schedule",
            parse_mode='HTML'
        )

    @command(name="schedule_once", description="Agendar tarefa única")
    async def schedule_once_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        print(f"⏰ DEBUG: schedule_once_command chamado por {update.effective_user.first_name}")
        if not context.args:
            await update.message.reply_text(
                "❌ Uso: /schedule_once [minutos] [mensagem]\n"
                "Exemplo: /schedule_once 5 Lembrete importante!"
            )
            return

        try:
            minutes = int(context.args[0])
            message = " ".join(context.args[1:]) if len(context.args) > 1 else "Lembrete agendado!"

            if minutes < 1 or minutes > 1440:  # Máximo 24 horas
                await update.message.reply_text("❌ Minutos devem estar entre 1 e 1440 (24 horas)")
                return

            user = update.effective_user
            job_id = f"once_{user.id}_{datetime.now().timestamp()}"
            run_date = datetime.now() + timedelta(minutes=minutes)

            # Agendar a tarefa usando método de instância diretamente
            print(f"⏰ DEBUG: Criando job no scheduler - job_id: {job_id}, run_date: {run_date}")
            self.scheduler.add_job(
                func=self._send_scheduled_message,
                trigger='date',
                run_date=run_date,
                args=[user.id, message, job_id],
                job_id=job_id,
                user_id=user.id
            )
            print(f"✅ DEBUG: Job criado com sucesso no scheduler - job_id: {job_id}")

            # Registrar estatísticas
            self.scheduler_stats['jobs_created'] += 1
            self.demo_jobs[job_id] = {
                'type': 'once',
                'user_id': user.id,
                'message': message,
                'run_date': run_date,
                'created_at': datetime.now()
            }
            print(f"📊 DEBUG: Job registrado em demo_jobs - job_id: {job_id}")

            response = (
                f"✅ <b>Agendamento Criado!</b>\n\n"
                f"🆔 <b>Job ID:</b> {job_id}\n"
                f"⏰ <b>Execução:</b> {run_date.strftime('%d/%m/%Y %H:%M:%S')}\n"
                f"📝 <b>Mensagem:</b> {message}\n"
                f"👤 <b>Usuário:</b> {user.first_name}\n\n"
                f"💡 Você receberá a mensagem em {minutes} minuto(s)!"
            )

            await update.message.reply_text(response, parse_mode='HTML')

        except ValueError:
            await update.message.reply_text("❌ Minutos deve ser um número válido")

    @command(name="schedule_recurring", description="Agendar tarefa periódica")
    async def schedule_recurring_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args or len(context.args) < 2:
            await update.message.reply_text(
                "❌ Uso: /schedule_recurring [intervalo_minutos] [mensagem]\n"
                "Exemplo: /schedule_recurring 30 Verificação periódica"
            )
            return

        try:
            interval_minutes = int(context.args[0])
            message = " ".join(context.args[1:])

            if interval_minutes < 1 or interval_minutes > 1440:
                await update.message.reply_text("❌ Intervalo deve estar entre 1 e 1440 minutos")
                return

            user = update.effective_user
            job_id = f"recurring_{user.id}_{datetime.now().timestamp()}"

            # Agendar a tarefa periódica usando método de instância diretamente
            print(f"🔄 DEBUG: Criando job periódico no scheduler - job_id: {job_id}, interval: {interval_minutes}")
            self.scheduler.add_job(
                func=self._send_recurring_message,
                trigger='interval',
                minutes=interval_minutes,
                args=[user.id, message, job_id],
                job_id=job_id,
                user_id=user.id,
                replace_existing=True
            )
            print(f"✅ DEBUG: Job periódico criado com sucesso no scheduler - job_id: {job_id}")

            # Registrar estatísticas
            self.scheduler_stats['jobs_created'] += 1
            self.demo_jobs[job_id] = {
                'type': 'recurring',
                'user_id': user.id,
                'message': message,
                'interval_minutes': interval_minutes,
                'created_at': datetime.now(),
                'next_run': datetime.now() + timedelta(minutes=interval_minutes)
            }

            response = (
                f"🔄 <b>Agendamento Periódico Criado!</b>\n\n"
                f"🆔 <b>Job ID:</b> {job_id}\n"
                f"⏰ <b>Intervalo:</b> {interval_minutes} minuto(s)\n"
                f"📝 <b>Mensagem:</b> {message}\n"
                f"👤 <b>Usuário:</b> {user.first_name}\n"
                f"🔄 <b>Próxima execução:</b> {self.demo_jobs[job_id]['next_run'].strftime('%H:%M:%S')}\n\n"
                f"💡 Você receberá a mensagem a cada {interval_minutes} minuto(s)!"
            )

            await update.message.reply_text(response, parse_mode='HTML')

        except ValueError:
            await update.message.reply_text("❌ Intervalo deve ser um número válido")

    @command(name="list_jobs", description="Listar jobs agendados")
    @admin_required_simple
    async def list_jobs_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        jobs = self.scheduler.get_all_jobs()

        if not jobs:
            await update.message.reply_text("📭 Nenhum job agendado")
            return

        jobs_text = f"📋 <b>Jobs Agendados ({len(jobs)}):</b>\n\n"

        for i, job in enumerate(jobs[:10], 1):  # Limitar a 10 jobs
            job_info = self.demo_jobs.get(job['id'], {})
            job_type = job_info.get('type', 'unknown')

            if job_type == 'once':
                run_time = job_info.get('run_date', 'N/A')
                if isinstance(run_time, datetime):
                    run_time = run_time.strftime('%d/%m %H:%M')
                jobs_text += f"{i}. ⏰ <b>{job['id']}</b> (Único)\n"
                jobs_text += f"   📅 {run_time}\n"
            elif job_type == 'recurring':
                interval = job_info.get('interval_minutes', 'N/A')
                next_run = job_info.get('next_run', 'N/A')
                if isinstance(next_run, datetime):
                    next_run = next_run.strftime('%H:%M')
                jobs_text += f"{i}. 🔄 <b>{job['id']}</b> (Periódico)\n"
                jobs_text += f"   ⏱️ {interval}min | Próximo: {next_run}\n"
            else:
                jobs_text += f"{i}. ❓ <b>{job['id']}</b> (Desconhecido)\n"

            jobs_text += "\n"

        if len(jobs) > 10:
            jobs_text += f"... e mais {len(jobs) - 10} jobs"

        await update.message.reply_text(jobs_text, parse_mode='HTML')

    @command(name="cancel_job", description="Cancelar job específico")
    async def cancel_job_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("❌ Uso: /cancel_job <job_id>")
            return

        job_id = context.args[0]
        user = update.effective_user

        # Verificar se o job existe e pertence ao usuário
        job_info = self.demo_jobs.get(job_id)
        if not job_info:
            await update.message.reply_text("❌ Job não encontrado")
            return

        if job_info['user_id'] != user.id and not self.user_manager.is_admin(user.id):
            await update.message.reply_text("❌ Você só pode cancelar seus próprios jobs")
            return

        try:
            # Remover o job
            self.scheduler.remove_job(job_id)
            del self.demo_jobs[job_id]

            await update.message.reply_text(f"✅ Job {job_id} cancelado com sucesso!")
        except Exception as e:
            await update.message.reply_text(f"❌ Erro ao cancelar job: {e}")

    @command(name="cancel_all", description="Cancelar todos os jobs do usuário")
    async def cancel_all_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        # Buscar todos os jobs do usuário diretamente do scheduler
        user_jobs = self.scheduler.list_jobs(user_id=user.id)

        # Fallback: se não encontrar jobs pelo user_id, tente pelo demo_jobs (para jobs antigos)
        if not user_jobs:
            # Busca todos os jobs do demo_jobs que pertencem ao usuário
            user_job_ids = [job_id for job_id, info in self.demo_jobs.items() if info.get('user_id') == user.id]
            if not user_job_ids:
                await update.message.reply_text("📭 Você não tem jobs agendados")
                return
            cancelled_count = 0
            for job_id in user_job_ids:
                try:
                    self.scheduler.remove_job(job_id)
                    self.demo_jobs.pop(job_id, None)
                    cancelled_count += 1
                except Exception as e:
                    print(f"Erro ao cancelar job {job_id}: {e}")
            await update.message.reply_text(f"✅ {cancelled_count} job(s) cancelado(s) com sucesso!")
            return

        cancelled_count = 0
        for job in user_jobs:
            job_id = job.id
            try:
                self.scheduler.remove_job(job_id)
                self.demo_jobs.pop(job_id, None)
                cancelled_count += 1
            except Exception as e:
                print(f"Erro ao cancelar job {job_id}: {e}")

        await update.message.reply_text(f"✅ {cancelled_count} job(s) cancelado(s) com sucesso!")

    @command(name="scheduler_stats", description="Estatísticas do scheduler")
    async def scheduler_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        uptime = datetime.now() - self.scheduler_stats['start_time']
        uptime_str = str(uptime).split('.')[0]

        total_jobs = len(self.scheduler.get_all_jobs())
        user_jobs = len([j for j in self.demo_jobs.values() if j['user_id'] == update.effective_user.id])

        stats_msg = (
            f"📊 <b>Estatísticas do Scheduler</b>\n\n"
            f"⏱️ <b>Uptime:</b> {uptime_str}\n"
            f"📈 <b>Jobs Criados:</b> {self.scheduler_stats['jobs_created']}\n"
            f"✅ <b>Jobs Concluídos:</b> {self.scheduler_stats['jobs_completed']}\n"
            f"❌ <b>Jobs Falharam:</b> {self.scheduler_stats['jobs_failed']}\n\n"
            f"🔄 <b>Jobs Ativos:</b>\n"
            f"• Total: {total_jobs}\n"
            f"• Seus: {user_jobs}\n\n"
            f"💡 <b>Tipos de Jobs:</b>\n"
            f"• Únicos: {len([j for j in self.demo_jobs.values() if j['type'] == 'once'])}\n"
            f"• Periódicos: {len([j for j in self.demo_jobs.values() if j['type'] == 'recurring'])}"
        )

        await update.message.reply_text(stats_msg, parse_mode='HTML')

    @command(name="scheduler_config", description="Configurações do scheduler")
    @admin_required_simple
    async def scheduler_config_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        config_msg = (
            f"⚙️ <b>Configurações do Scheduler</b>\n\n"
            f"🤖 <b>Nome da Instância:</b> {self.config.instance_name}\n"
            f"🐛 <b>Debug Mode:</b> {'✅' if self.config.debug else '❌'}\n"
            f"⏰ <b>Scheduler Ativo:</b> {'✅' if self.scheduler else '❌'}\n"
            f"🔄 <b>Auto Start:</b> {'✅' if hasattr(self.scheduler, 'running') and self.scheduler.running else '❌'}\n"
            f"📝 <b>Log Level:</b> {getattr(self.config, 'log_level', 'INFO')}\n"
            f"💾 <b>Persistência:</b> {'✅' if self.persistence_manager else '❌'}\n"
            f"👥 <b>User Manager:</b> {'✅' if self.user_manager else '❌'}"
        )

        await update.message.reply_text(config_msg, parse_mode='HTML')

    # ===================== Métodos auxiliares =====================
    def _send_scheduled_message(self, user_id: int, message: str, job_id: str):
        # Wrapper síncrono para rodar o método assíncrono no event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.run_coroutine_threadsafe(self._send_scheduled_message_async(user_id, message, job_id), loop)
        else:
            loop.run_until_complete(self._send_scheduled_message_async(user_id, message, job_id))

    async def _send_scheduled_message_async(self, user_id: int, message: str, job_id: str):
        print(f"🔔 DEBUG: _send_scheduled_message_async chamado - user_id: {user_id}, message: {message}, job_id: {job_id}")
        try:
            print(f"🔔 DEBUG: Tentando enviar mensagem para user_id: {user_id}")
            await self.bot.application.bot.send_message(
                chat_id=user_id,
                text=f"⏰ <b>Mensagem Agendada</b>\n\n{message}\n\n🕐 Enviada em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
                parse_mode='HTML'
            )
            print(f"✅ DEBUG: Mensagem agendada enviada com sucesso para user_id: {user_id}")
            self.scheduler_stats['jobs_completed'] += 1
            if job_id in self.demo_jobs:
                del self.demo_jobs[job_id]
        except Exception as e:
            print(f"❌ DEBUG: Erro ao enviar mensagem agendada: {e}")
            print(f"❌ DEBUG: Tipo de erro: {type(e)}")
            import traceback
            print(f"❌ DEBUG: Traceback: {traceback.format_exc()}")
            self.scheduler_stats['jobs_failed'] += 1

    def _send_recurring_message(self, user_id: int, message: str, job_id: str):
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.run_coroutine_threadsafe(self._send_recurring_message_async(user_id, message, job_id), loop)
        else:
            loop.run_until_complete(self._send_recurring_message_async(user_id, message, job_id))

    async def _send_recurring_message_async(self, user_id: int, message: str, job_id: str):
        print(f"🔄 DEBUG: _send_recurring_message_async chamado - user_id: {user_id}, message: {message}, job_id: {job_id}")
        try:
            print(f"🔄 DEBUG: Tentando enviar mensagem periódica para user_id: {user_id}")
            await self.bot.application.bot.send_message(
                chat_id=user_id,
                text=f"🔄 <b>Mensagem Periódica</b>\n\n{message}\n\n🕐 Enviada em: {datetime.now().strftime('%H:%M:%S')}",
                parse_mode='HTML'
            )
            print(f"✅ DEBUG: Mensagem periódica enviada com sucesso para user_id: {user_id}")
            self.scheduler_stats['jobs_completed'] += 1
            if job_id in self.demo_jobs:
                interval = self.demo_jobs[job_id].get('interval_minutes', 30)
                self.demo_jobs[job_id]['next_run'] = datetime.now() + timedelta(minutes=interval)
        except Exception as e:
            print(f"❌ DEBUG: Erro ao enviar mensagem periódica: {e}")
            print(f"❌ DEBUG: Tipo de erro: {type(e)}")
            import traceback
            print(f"❌ DEBUG: Traceback: {traceback.format_exc()}")
            self.scheduler_stats['jobs_failed'] += 1

# O framework deve detectar e carregar automaticamente este plugin da pasta plugins.
