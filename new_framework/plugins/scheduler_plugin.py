"""
Scheduler Plugin - Plugin para agendamento de tarefas no Telegram Bot Framework
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
from tlgfwk import (
    command, admin_required_simple, owner_required
)
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# Plugin metadata
__plugin_name__ = "scheduler_plugin"
__description__ = "Plugin de agendamento de tarefas (únicas e periódicas) para o Telegram Bot Framework."
__version__ = "1.0.0"
__author__ = "Seu Nome"
__enabled__ = True

# O framework irá injetar bot, scheduler, user_manager, etc. no contexto do plugin

def register(bot):
    """Função obrigatória para registrar comandos e inicializar o plugin."""
    plugin = SchedulerPlugin(bot)
    plugin.register_commands()
    return plugin

class SchedulerPlugin:
    def __init__(self, bot):
        self.bot = bot
        self.scheduler = bot.scheduler
        self.user_manager = bot.user_manager
        self.persistence_manager = getattr(bot, 'persistence_manager', None)
        self.config = bot.config
        self.demo_jobs = {}
        self.scheduler_stats = {
            'jobs_created': 0,
            'jobs_completed': 0,
            'jobs_failed': 0,
            'start_time': datetime.now()
        }

    def register_commands(self):
        self.bot.add_command_handler("plugin_schedule", self.plugin_schedule_command)
        self.bot.add_command_handler("schedule_once", self.schedule_once_command)
        self.bot.add_command_handler("schedule_recurring", self.schedule_recurring_command)
        self.bot.add_command_handler("list_jobs", self.list_jobs_command)
        self.bot.add_command_handler("cancel_job", self.cancel_job_command)
        self.bot.add_command_handler("cancel_all", self.cancel_all_command)
        self.bot.add_command_handler("scheduler_stats", self.scheduler_stats_command)
        self.bot.add_command_handler("scheduler_config", self.scheduler_config_command)
        self.bot.add_command_handler("plugins", self.plugins_command)
        self.bot.add_command_handler("plugin", self.plugin_command)

    # ===================== Comandos =====================
    @command(name="plugin_schedule", description="Demo do comando de plugin de agendamento")
    async def plugin_schedule_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "🔌 <b>Plugin Schedule</b>\n\nEste é um comando de demonstração para integração de plugins com o sistema de agendamento.\n\n\u2022 Use este comando para testar a integração de plugins que registram comandos de agendamento.\n\n💡 Exemplo de uso:\n/plugin_schedule",
            parse_mode='HTML'
        )

    @command(name="schedule_once", description="Agendar tarefa única")
    async def schedule_once_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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

            # Agendar a tarefa
            self.scheduler.add_job(
                func=self._send_scheduled_message,
                trigger='date',
                run_date=run_date,
                args=[user.id, message, job_id],
                job_id=job_id,
                user_id=user.id
            )

            # Registrar estatísticas
            self.scheduler_stats['jobs_created'] += 1
            self.demo_jobs[job_id] = {
                'type': 'once',
                'user_id': user.id,
                'message': message,
                'run_date': run_date,
                'created_at': datetime.now()
            }

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

            # Agendar a tarefa periódica
            self.scheduler.add_job(
                func=self._send_recurring_message,
                trigger='interval',
                minutes=interval_minutes,
                args=[user.id, message, job_id],
                job_id=job_id,
                user_id=user.id,
                replace_existing=True
            )

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

    @command(name="plugins", description="Listar plugins carregados")
    @admin_required_simple
    async def plugins_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # ...existing code from plugins_command...
        pass

    @command(name="plugin", description="Gerenciar plugin específico")
    @admin_required_simple
    async def plugin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # ...existing code from plugin_command...
        pass

    # ===================== Métodos auxiliares =====================
    async def _send_scheduled_message(self, user_id: int, message: str, job_id: str):
        try:
            await self.bot.application.bot.send_message(
                chat_id=user_id,
                text=f"⏰ <b>Mensagem Agendada</b>\n\n{message}\n\n🕐 Enviada em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
                parse_mode='HTML'
            )
            self.scheduler_stats['jobs_completed'] += 1
            if job_id in self.demo_jobs:
                del self.demo_jobs[job_id]
        except Exception as e:
            print(f"Erro ao enviar mensagem agendada: {e}")
            self.scheduler_stats['jobs_failed'] += 1

    async def _send_recurring_message(self, user_id: int, message: str, job_id: str):
        try:
            await self.bot.application.bot.send_message(
                chat_id=user_id,
                text=f"🔄 <b>Mensagem Periódica</b>\n\n{message}\n\n🕐 Enviada em: {datetime.now().strftime('%H:%M:%S')}",
                parse_mode='HTML'
            )
            self.scheduler_stats['jobs_completed'] += 1
            if job_id in self.demo_jobs:
                interval = self.demo_jobs[job_id].get('interval_minutes', 30)
                self.demo_jobs[job_id]['next_run'] = datetime.now() + timedelta(minutes=interval)
        except Exception as e:
            print(f"Erro ao enviar mensagem periódica: {e}")
            self.scheduler_stats['jobs_failed'] += 1

# O framework deve detectar e carregar automaticamente este plugin da pasta plugins.
