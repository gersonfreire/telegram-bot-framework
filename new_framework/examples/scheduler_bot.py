#!/usr/bin/env python3
"""
Scheduler Bot - Demonstração do Sistema de Agendamentos

Este bot demonstra como usar o sistema de agendamentos do framework:
- Agendamento de tarefas periódicas
- Agendamento de tarefas únicas
- Agendamento com diferentes intervalos
- Gerenciamento de jobs
- Notificações agendadas
- Limpeza automática
"""

import os
import sys
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Adicionar o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tlgfwk import (
    TelegramBotFramework, command, admin_required_simple, owner_required
)
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes



class SchedulerBot(TelegramBotFramework):
    @command(name="plugin_schedule", description="Demo do comando de plugin de agendamento")
    async def plugin_schedule_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Demonstração do comando /plugin_schedule."""
        await update.message.reply_text(
            "🔌 <b>Plugin Schedule</b>\n\nEste é um comando de demonstração para integração de plugins com o sistema de agendamento.\n\n\u2022 Use este comando para testar a integração de plugins que registram comandos de agendamento.\n\n💡 Exemplo de uso:\n/plugin_schedule",
            parse_mode='HTML'
        )
    """
    Bot de demonstração do sistema de agendamentos.

    Demonstra todas as funcionalidades de agendamento:
    - Agendamento de tarefas periódicas
    - Agendamento de tarefas únicas
    - Gerenciamento de jobs
    - Notificações agendadas
    - Limpeza automática
    """

    def __init__(self, config_file=None, custom_config=None):
        # Configurar diretório de plugins
        plugins_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "./")
        super().__init__(config_file=config_file, plugins_dir=plugins_dir, custom_config=custom_config)

        # Configurações específicas do scheduler
        self.config.data['auto_load_plugins'] = True
        self.config.data['debug'] = True

        # Estatísticas do scheduler
        self.scheduler_stats = {
            'jobs_created': 0,
            'jobs_completed': 0,
            'jobs_failed': 0,
            'start_time': datetime.now()
        }

        # Jobs de demonstração
        self.demo_jobs = {}

    # ============================================================================
    # COMANDOS BÁSICOS DE AGENDAMENTO
    # ============================================================================

    @command(name="schedule", description="Menu principal de agendamentos")
    async def schedule_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Menu principal de agendamentos."""
        keyboard = [
            [InlineKeyboardButton("⏰ Agendamento Único", callback_data="schedule_once")],
            [InlineKeyboardButton("🔄 Agendamento Periódico", callback_data="schedule_recurring")],
            [InlineKeyboardButton("📊 Gerenciar Jobs", callback_data="manage_jobs")],
            [InlineKeyboardButton("🧹 Limpeza Automática", callback_data="auto_cleanup")],
            [InlineKeyboardButton("📈 Estatísticas", callback_data="scheduler_stats")],
            [InlineKeyboardButton("⚙️ Configurações", callback_data="scheduler_config")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        message = (
            "⏰ <b>Scheduler Bot - Sistema de Agendamentos</b>\n\n"
            "Bem-vindo ao bot de demonstração do sistema de agendamentos!\n"
            "Escolha uma categoria para explorar as funcionalidades:"
        )

        await update.message.reply_text(message, parse_mode='HTML', reply_markup=reply_markup)

    @command(name="schedule_once", description="Agendar tarefa única")
    async def schedule_once_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Agendar uma tarefa única."""
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
                id=job_id
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
        """Agendar uma tarefa periódica."""
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
                id=job_id,
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
        """Listar todos os jobs agendados."""
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
        """Cancelar um job específico."""
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
        """Cancelar todos os jobs do usuário atual."""
        user = update.effective_user
        # Buscar todos os jobs do usuário diretamente do scheduler
        user_jobs = self.scheduler.list_jobs(user_id=user.id)

        if not user_jobs:
            await update.message.reply_text("📭 Você não tem jobs agendados")
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

    # ============================================================================
    # COMANDOS DE ESTATÍSTICAS E CONFIGURAÇÃO
    # ============================================================================

    @command(name="scheduler_stats", description="Estatísticas do scheduler")
    async def scheduler_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mostrar estatísticas do scheduler."""
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
        """Mostrar configurações do scheduler."""
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

    # ============================================================================
    # COMANDOS DE PLUGINS (REQUERIDOS PELO FRAMEWORK)
    # ============================================================================

    @command(name="plugins", description="Listar plugins carregados")
    @admin_required_simple
    async def plugins_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Listar todos os plugins carregados."""
        if not self.plugin_manager:
            await update.message.reply_text("❌ Plugin Manager não disponível")
            return

        plugins = self.plugin_manager.plugins
        if not plugins:
            await update.message.reply_text("📦 Nenhum plugin carregado")
            return

        plugins_msg = "🔌 <b>Plugins Carregados:</b>\n\n"

        for name, plugin_info in plugins.items():
            status = "✅ Ativo" if plugin_info.get('enabled', False) else "❌ Inativo"
            version = plugin_info.get('version', 'N/A')
            description = plugin_info.get('description', 'Sem descrição')

            plugins_msg += (
                f"📦 <b>{name}</b> v{version}\n"
                f"📝 {description}\n"
                f"🔄 {status}\n\n"
            )

        await update.message.reply_text(plugins_msg, parse_mode='HTML')

    @command(name="plugin", description="Gerenciar plugin específico")
    @admin_required_simple
    async def plugin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gerenciar plugin específico."""
        if not context.args:
            await update.message.reply_text(
                "❌ Uso: /plugin <nome> <ação>\n"
                "Ações: start, stop, reload, info"
            )
            return

        if len(context.args) < 2:
            await update.message.reply_text("❌ Uso: /plugin <nome> <ação>")
            return

        plugin_name = context.args[0]
        action = context.args[1].lower()

        if not self.plugin_manager:
            await update.message.reply_text("❌ Plugin Manager não disponível")
            return

        if plugin_name not in self.plugin_manager.plugins:
            await update.message.reply_text(f"❌ Plugin '{plugin_name}' não encontrado")
            return

        try:
            if action == "start":
                success = self.plugin_manager.start_plugin(plugin_name)
                if success:
                    await update.message.reply_text(f"✅ Plugin '{plugin_name}' iniciado!")
                else:
                    await update.message.reply_text(f"❌ Erro ao iniciar plugin '{plugin_name}'")

            elif action == "stop":
                success = self.plugin_manager.stop_plugin(plugin_name)
                if success:
                    await update.message.reply_text(f"✅ Plugin '{plugin_name}' parado!")
                else:
                    await update.message.reply_text(f"❌ Erro ao parar plugin '{plugin_name}'")

            elif action == "reload":
                success = self.plugin_manager.reload_plugin(plugin_name)
                if success:
                    await update.message.reply_text(f"✅ Plugin '{plugin_name}' recarregado!")
                else:
                    await update.message.reply_text(f"❌ Erro ao recarregar plugin '{plugin_name}'")

            elif action == "info":
                plugin_info = self.plugin_manager.plugins[plugin_name]
                info_msg = (
                    f"📋 <b>Informações do Plugin: {plugin_name}</b>\n\n"
                    f"🔢 <b>Versão:</b> {plugin_info.get('version', 'N/A')}\n"
                    f"📝 <b>Descrição:</b> {plugin_info.get('description', 'N/A')}\n"
                    f"🔄 <b>Status:</b> {'✅ Ativo' if plugin_info.get('enabled', False) else '❌ Inativo'}\n"
                    f"🎯 <b>Comandos:</b> {len(plugin_info.get('commands', []))}\n"
                    f"🔧 <b>Handlers:</b> {len(plugin_info.get('handlers', []))}"
                )
                await update.message.reply_text(info_msg, parse_mode='HTML')

            else:
                await update.message.reply_text(
                    "❌ Ação inválida. Use: start, stop, reload, info"
                )

        except Exception as e:
            await update.message.reply_text(f"❌ Erro ao gerenciar plugin: {e}")

    # ============================================================================
    # MÉTODOS DE CALLBACK PARA TAREFAS AGENDADAS
    # ============================================================================

    async def _send_scheduled_message(self, user_id: int, message: str, job_id: str):
        """Enviar mensagem agendada única."""
        try:
            await self.application.bot.send_message(
                chat_id=user_id,
                text=f"⏰ <b>Mensagem Agendada</b>\n\n{message}\n\n🕐 Enviada em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
                parse_mode='HTML'
            )

            # Atualizar estatísticas
            self.scheduler_stats['jobs_completed'] += 1

            # Remover job da lista de demo
            if job_id in self.demo_jobs:
                del self.demo_jobs[job_id]

        except Exception as e:
            print(f"Erro ao enviar mensagem agendada: {e}")
            self.scheduler_stats['jobs_failed'] += 1

    async def _send_recurring_message(self, user_id: int, message: str, job_id: str):
        """Enviar mensagem agendada periódica."""
        try:
            await self.application.bot.send_message(
                chat_id=user_id,
                text=f"🔄 <b>Mensagem Periódica</b>\n\n{message}\n\n🕐 Enviada em: {datetime.now().strftime('%H:%M:%S')}",
                parse_mode='HTML'
            )

            # Atualizar estatísticas
            self.scheduler_stats['jobs_completed'] += 1

            # Atualizar próxima execução
            if job_id in self.demo_jobs:
                interval = self.demo_jobs[job_id].get('interval_minutes', 30)
                self.demo_jobs[job_id]['next_run'] = datetime.now() + timedelta(minutes=interval)

        except Exception as e:
            print(f"Erro ao enviar mensagem periódica: {e}")
            self.scheduler_stats['jobs_failed'] += 1

    # ============================================================================
    # HANDLERS DE CALLBACK
    # ============================================================================

    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manipular callbacks dos botões inline."""
        query = update.callback_query
        await query.answer()

        if query.data == "schedule_once":
            await self._show_once_scheduling(query)
        elif query.data == "schedule_recurring":
            await self._show_recurring_scheduling(query)
        elif query.data == "manage_jobs":
            await self._show_job_management(query)
        elif query.data == "auto_cleanup":
            await self._show_auto_cleanup(query)
        elif query.data == "scheduler_stats":
            await self._show_scheduler_stats(query)
        elif query.data == "scheduler_config":
            await self._show_scheduler_config(query)

    async def _show_once_scheduling(self, query):
        """Mostrar informações sobre agendamento único."""
        message = (
            "⏰ <b>Agendamento Único</b>\n\n"
            "📋 <b>Comando:</b> /schedule_once [minutos] [mensagem]\n\n"
            "💡 <b>Exemplos:</b>\n"
            "• /schedule_once 5 Lembrete importante!\n"
            "• /schedule_once 30 Reunião em 30 minutos\n"
            "• /schedule_once 60 Verificar emails\n\n"
            "⚙️ <b>Limites:</b>\n"
            "• Mínimo: 1 minuto\n"
            "• Máximo: 1440 minutos (24 horas)\n\n"
            "✅ <b>Funcionalidades:</b>\n"
            "• Agendamento preciso\n"
            "• Mensagens personalizadas\n"
            "• Cancelamento individual"
        )
        await query.edit_message_text(message, parse_mode='HTML')

    async def _show_recurring_scheduling(self, query):
        """Mostrar informações sobre agendamento periódico."""
        message = (
            "🔄 <b>Agendamento Periódico</b>\n\n"
            "📋 <b>Comando:</b> /schedule_recurring [intervalo] [mensagem]\n\n"
            "💡 <b>Exemplos:</b>\n"
            "• /schedule_recurring 30 Verificação periódica\n"
            "• /schedule_recurring 60 Backup automático\n"
            "• /schedule_recurring 120 Relatório de status\n\n"
            "⚙️ <b>Limites:</b>\n"
            "• Mínimo: 1 minuto\n"
            "• Máximo: 1440 minutos (24 horas)\n\n"
            "✅ <b>Funcionalidades:</b>\n"
            "• Execução automática\n"
            "• Intervalos personalizados\n"
            "• Cancelamento em lote"
        )
        await query.edit_message_text(message, parse_mode='HTML')

    async def _show_job_management(self, query):
        """Mostrar informações sobre gerenciamento de jobs."""
        message = (
            "📊 <b>Gerenciamento de Jobs</b>\n\n"
            "📋 <b>Comandos Disponíveis:</b>\n"
            "• /list_jobs - Listar todos os jobs\n"
            "• /cancel_job <id> - Cancelar job específico\n"
            "• /cancel_all - Cancelar seus jobs\n\n"
            "💡 <b>Funcionalidades:</b>\n"
            "• Visualização de jobs ativos\n"
            "• Cancelamento individual\n"
            "• Cancelamento em lote\n"
            "• Controle de permissões\n\n"
            "🔐 <b>Permissões:</b>\n"
            "• Usuários: Cancelam apenas seus jobs\n"
            "• Admins: Podem listar todos os jobs"
        )
        await query.edit_message_text(message, parse_mode='HTML')

    async def _show_auto_cleanup(self, query):
        """Mostrar informações sobre limpeza automática."""
        message = (
            "🧹 <b>Limpeza Automática</b>\n\n"
            "✅ <b>Funcionalidades Automáticas:</b>\n"
            "• Jobs únicos são removidos após execução\n"
            "• Jobs falhados são registrados\n"
            "• Estatísticas são atualizadas\n"
            "• Cache é limpo automaticamente\n\n"
            "📊 <b>Monitoramento:</b>\n"
            "• Contagem de jobs criados\n"
            "• Contagem de jobs concluídos\n"
            "• Contagem de jobs falhados\n"
            "• Tempo de execução\n\n"
            "💡 <b>Benefícios:</b>\n"
            "• Sistema sempre limpo\n"
            "• Performance otimizada\n"
            "• Relatórios precisos"
        )
        await query.edit_message_text(message, parse_mode='HTML')

    async def _show_scheduler_stats(self, query):
        """Mostrar estatísticas do scheduler."""
        uptime = datetime.now() - self.scheduler_stats['start_time']
        uptime_str = str(uptime).split('.')[0]
        total_jobs = len(self.scheduler.get_all_jobs())

        message = (
            f"📈 <b>Estatísticas do Scheduler</b>\n\n"
            f"⏱️ <b>Uptime:</b> {uptime_str}\n"
            f"📊 <b>Jobs Criados:</b> {self.scheduler_stats['jobs_created']}\n"
            f"✅ <b>Jobs Concluídos:</b> {self.scheduler_stats['jobs_completed']}\n"
            f"❌ <b>Jobs Falharam:</b> {self.scheduler_stats['jobs_failed']}\n"
            f"🔄 <b>Jobs Ativos:</b> {total_jobs}\n\n"
            f"💡 <b>Taxa de Sucesso:</b>\n"
            f"• {self.scheduler_stats['jobs_completed'] / max(self.scheduler_stats['jobs_created'], 1) * 100:.1f}%"
        )
        await query.edit_message_text(message, parse_mode='HTML')

    async def _show_scheduler_config(self, query):
        """Mostrar configurações do scheduler."""
        message = (
            f"⚙️ <b>Configurações do Scheduler</b>\n\n"
            f"🤖 <b>Instância:</b> {self.config.instance_name}\n"
            f"🐛 <b>Debug:</b> {'✅' if self.config.debug else '❌'}\n"
            f"⏰ <b>Scheduler:</b> {'✅' if self.scheduler else '❌'}\n"
            f"🔄 <b>Executando:</b> {'✅' if hasattr(self.scheduler, 'running') and self.scheduler.running else '❌'}\n"
            f"💾 <b>Persistência:</b> {'✅' if self.persistence_manager else '❌'}\n"
            f"👥 <b>User Manager:</b> {'✅' if self.user_manager else '❌'}\n\n"
            f"💡 <b>Recursos:</b>\n"
            f"• Agendamento único e periódico\n"
            f"• Gerenciamento de jobs\n"
            f"• Estatísticas detalhadas\n"
            f"• Limpeza automática"
        )
        await query.edit_message_text(message, parse_mode='HTML')

    # ============================================================================
    # OVERRIDE DE MÉTODOS DO FRAMEWORK
    # ============================================================================

    def register_default_handlers(self):
        """Registra handlers padrão incluindo callbacks."""
        super().register_default_handlers()

        # Adicionar handler para callbacks
        from telegram.ext import CallbackQueryHandler
        self.application.add_handler(CallbackQueryHandler(self.handle_callback_query))

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Override do comando start para incluir scheduler."""
        user = update.effective_user

        welcome_msg = (
            f"⏰ <b>Bem-vindo ao Scheduler Bot!</b>\n\n"
            f"👤 Olá, {user.first_name}!\n\n"
            f"🤖 Este é um bot de demonstração do <b>Sistema de Agendamentos</b> do framework.\n\n"
            f"🎯 <b>Funcionalidades Demonstradas:</b>\n"
            f"• ✅ Agendamento de tarefas únicas\n"
            f"• ✅ Agendamento de tarefas periódicas\n"
            f"• ✅ Gerenciamento de jobs\n"
            f"• ✅ Estatísticas detalhadas\n"
            f"• ✅ Limpeza automática\n"
            f"• ✅ Controle de permissões\n\n"
            f"💡 Use /schedule para explorar todas as funcionalidades!\n"
            f"📚 Use /help para ver todos os comandos disponíveis."
        )

        await update.message.reply_text(welcome_msg, parse_mode='HTML')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Override do comando help para incluir comandos do scheduler."""
        help_msg = (
            "⏰ <b>Comandos do Scheduler Bot</b>\n\n"
            "🎯 <b>Comandos Principais:</b>\n"
            "• /start - Iniciar o bot\n"
            "• /schedule - Menu de agendamentos\n"
            "• /help - Esta ajuda\n"
            "• /status - Status do sistema\n\n"
            "⏰ <b>Comandos de Agendamento:</b>\n"
            "• /schedule_once - Agendar tarefa única\n"
            "• /schedule_recurring - Agendar tarefa periódica\n"
            "• /list_jobs - Listar jobs (admin)\n"
            "• /cancel_job - Cancelar job específico\n"
            "• /cancel_all - Cancelar seus jobs\n\n"
            "📊 <b>Comandos de Estatísticas:</b>\n"
            "• /scheduler_stats - Estatísticas do scheduler\n"
            "• /scheduler_config - Configurações (admin)\n\n"
            "🔌 <b>Comandos de Plugins:</b>\n"
            "• /plugin_schedule - Demo do plugin\n\n"
            "💡 Use /schedule para um menu interativo!"
        )

        await update.message.reply_text(help_msg, parse_mode='HTML')

    def add_command_handler(self, command_name, handler):
        """Permite que plugins registrem comandos dinamicamente."""
        from telegram.ext import CommandHandler
        self.application.add_handler(CommandHandler(command_name, handler))


def main():
    """Função principal para executar o Scheduler Bot."""
    print("⏰ Iniciando Scheduler Bot - Sistema de Agendamentos...")
    print("=" * 60)

    # Verificar arquivo .env
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.exists(env_path):
        print("⚠️  Arquivo .env não encontrado!")
        print("📝 Crie um arquivo .env com as seguintes variáveis:")
        print("   BOT_TOKEN=seu_token_aqui")
        print("   OWNER_USER_ID=seu_id_aqui")
        print("   ADMIN_USER_IDS=id1,id2,id3")
        print("   LOG_CHAT_ID=chat_id_para_logs")
        print("   DEBUG=true")
        print("=" * 60)

    try:
        bot = SchedulerBot(config_file=env_path)
        print("✅ Scheduler Bot criado com sucesso!")
        print("🎯 Funcionalidades disponíveis:")
        print("   • Agendamento de tarefas únicas")
        print("   • Agendamento de tarefas periódicas")
        print("   • Gerenciamento de jobs")
        print("   • Estatísticas detalhadas")
        print("   • Limpeza automática")
        print("   • Controle de permissões")
        print("   • Sistema de plugins")
        print("   • Logging integrado")
        print("=" * 60)
        print("🤖 Bot iniciado! Pressione Ctrl+C para parar")
        print("💡 Use /schedule no Telegram para explorar as funcionalidades!")

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
