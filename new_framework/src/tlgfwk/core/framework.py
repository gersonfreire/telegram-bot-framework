"""
Classe principal do framework Telegram Bot.

Esta é a classe central que implementa toda a funcionalidade do framework,
incluindo gerenciamento de usuários, comandos, plugins e persistência.
"""

import asyncio
import sys
import traceback
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime

from telegram import Update, BotCommand
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters, CallbackQueryHandler
)
from telegram.constants import ParseMode

from .config import Config
from .decorators import get_command_registry, command, admin_required_simple, owner_required, typing_indicator
from .user_manager import UserManager
from .plugin_manager import PluginManager
from .persistence_manager import PersistenceManager
from ..utils.logger import setup_logging, get_logger, LoggerMixin


class TelegramBotFramework(LoggerMixin):
    """
    Classe principal do framework para bots Telegram.

    Fornece funcionalidades integradas como:
    - Gerenciamento de usuários e administradores
    - Sistema de comandos com decoradores
    - Sistema de plugins extensível
    - Persistência de dados
    - Notificações administrativas
    - Sistema de configuração seguro
    """

    def __init__(
        self,
        config_file: Optional[str] = None,
        plugins_dir: Optional[str] = None,
        custom_config: Optional[Dict[str, Any]] = None
    ):
        """
        Inicializa o framework.

        Args:
            config_file: Caminho para arquivo de configuração (.env)
            plugins_dir: Diretório dos plugins
            custom_config: Configurações customizadas
        """
        # Carregar configuração
        if custom_config:
            self.config = custom_config if isinstance(custom_config, Config) else Config(**custom_config)
        elif config_file:
            self.config = Config.from_env(config_file)
        else:
            self.config = Config()

        # Atualizar plugins_dir se fornecido
        if plugins_dir:
            self.config.data['plugins_dir'] = plugins_dir

        # Configurar logging
        self.setup_logging()

        # Inicializar componentes básicos
        from telegram.ext import Application
        if hasattr(Application, 'builder'):
            app_builder = Application.builder()
            app_builder.token(self.config.bot_token)
            self.application = app_builder.build()
        else:
            self.application = None

        # Inicializar gerenciadores
        from .scheduler import JobScheduler
        self.user_manager = UserManager(self.config)
        self.plugin_manager = PluginManager(
            bot_instance=self,
            plugin_dir=self.config.plugins_dir
        )
        self.persistence_manager = None
        self.scheduler = JobScheduler(self)

        # Estado interno
        self._running = False
        self._startup_time = None
        self._command_stats = {}

        self.log_info(f"Framework inicializado: {self.config.instance_name}")

    def setup_logging(self):
        """Configura sistema de logging."""
        log_config = {
            "level": "DEBUG" if self.config.debug else "INFO",
            "console_enabled": True,
            "file_enabled": True,
            "file_path": "logs/bot.log",
            "telegram_enabled": self.config.log_chat_id is not None,
            "telegram_chat_id": self.config.log_chat_id,
        }

        setup_logging(log_config, self)

    async def initialize(self):
        """Inicializa todos os componentes do framework."""
        self.log_info("Inicializando componentes do framework...")

        # Criar aplicação Telegram
        app_builder = Application.builder()
        app_builder.token(self.config.bot_token)

        # Configurações de rede
        if not self.config.reuse_connections:
            app_builder.connection_pool_size(1)
        else:
            app_builder.connection_pool_size(self.config.connection_pool_size)

        # Configurar persistência
        if self.config.persistence_backend != "none":
            self.persistence_manager = PersistenceManager(self.config)
            persistence = await self.persistence_manager.get_persistence()
            if persistence:
                app_builder.persistence(persistence)

        self.application = app_builder.build()

        # Inicializar gerenciadores
        self.user_manager = UserManager(self.config, self.persistence_manager)

        if self.config.plugins_dir:
            self.plugin_manager = PluginManager(
                bot_instance=self,
                plugin_dir=self.config.plugins_dir
            )

        # Registrar handlers padrão
        self.register_default_handlers()

        # Carregar plugins
        if self.plugin_manager and self.config.auto_load_plugins:
            await self.plugin_manager.load_all_plugins()

            # REGISTRAR comandos dos plugins após a aplicação estar pronta
            for plugin_name, plugin_info in self.plugin_manager.plugins.items():
                # plugin_info pode ser PluginInfo ou string
                instance = getattr(plugin_info, 'instance', None)
                if instance and hasattr(instance, 'get_commands'):
                    commands = instance.get_commands()
                    if commands:
                        for command in commands:
                            command_name = command.get('name')
                            # Sempre pega o handler da instância já inicializada
                            handler = getattr(instance, f"{command_name}_command", None)
                            if command_name and handler:
                                self.add_command_handler(command_name, handler)

        # Registrar comandos do menu
        await self.setup_bot_commands()

        self.log_info("Framework inicializado com sucesso")

    def register_default_handlers(self):
        """Registra handlers padrão do framework."""
        # Comandos básicos
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self._handle_status))

        # Comandos administrativos
        self.application.add_handler(CommandHandler("config", self.config_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(CommandHandler("users", self.users_command))
        self.application.add_handler(CommandHandler("restart", self.restart_command))
        self.application.add_handler(CommandHandler("shutdown", self.shutdown_command))

        # Comandos de plugins
        if self.plugin_manager:
            # Registrar comandos de plugins apenas se os métodos existirem
            if hasattr(self, 'plugins_command'):
                self.application.add_handler(CommandHandler("plugins", self.plugins_command))
            if hasattr(self, 'plugin_command'):
                self.application.add_handler(CommandHandler("plugin", self.plugin_command))

        # Registrar comandos do registry
        self.register_decorated_commands()

        # Handler para mensagens não-comando
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )

        # Handler de erros
        self.application.add_error_handler(self.error_handler)

    def register_decorated_commands(self):
        """Registra comandos que foram decorados com @command."""
        registry = get_command_registry()

        for command_name, command_info in registry.get_all_commands().items():
            handler = command_info["handler"]

            # Criar wrapper para métodos de instância
            if hasattr(handler, '__self__'):
                # Já é um método bound
                wrapped_handler = handler
            else:
                # Criar wrapper para métodos não-bound
                def create_wrapper(method):
                    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
                        return await method(self, update, context)
                    return wrapper

                wrapped_handler = create_wrapper(handler)

            # Registrar handler
            self.application.add_handler(
                CommandHandler(command_name, wrapped_handler)
            )

            # Registrar aliases
            for alias in command_info.get("aliases", []):
                self.application.add_handler(
                    CommandHandler(alias, wrapped_handler)
                )

    async def setup_bot_commands(self):
        """Configura comandos do menu do bot."""
        try:
            commands = []
            registry = get_command_registry()

            # Comandos padrão
            commands.extend([
                BotCommand("start", "Iniciar o bot"),
                BotCommand("help", "Mostrar ajuda"),
                BotCommand("status", "Status do sistema"),
            ])

            # Comandos do registry (não-admin)
            for cmd_name, cmd_info in registry.get_all_commands().items():
                if not cmd_info["admin_only"] and not cmd_info["hidden"]:
                    commands.append(
                        BotCommand(cmd_name, cmd_info["description"] or "Comando personalizado")
                    )

            # Definir comandos
            await self.application.bot.set_my_commands(commands)
            self.log_info(f"Configurados {len(commands)} comandos no menu")
        except Exception as e:
            self.log_warning(f"Não foi possível configurar comandos do bot: {e}")
            self.log_info("Bot continuará funcionando sem comandos no menu")

    # Comandos padrão

    @command(name="start", description="Iniciar o bot")
    @typing_indicator
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando de início."""
        user = update.effective_user

        # Registrar usuário
        if self.user_manager:
            await self.user_manager.register_user(
                user_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name
            )

        welcome_text = f"""
🤖 **{self.config.instance_name}**

Olá, {user.first_name}! Bem-vindo ao bot.

Use /help para ver os comandos disponíveis.

ℹ️ Bot iniciado em: {self._startup_time.strftime('%d/%m/%Y %H:%M:%S') if self._startup_time else 'N/A'}
        """

        await update.message.reply_text(
            welcome_text,
            parse_mode=ParseMode.MARKDOWN
        )

        # Notificar admins sobre novo usuário
        if user.id not in self.config.admin_user_ids:
            await self.send_admin_message(
                f"👤 Novo usuário: {user.full_name} (ID: {user.id})"
            )

    @command(name="help", description="Mostrar ajuda")
    @typing_indicator
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando de ajuda."""
        user_id = update.effective_user.id
        is_admin = user_id in self.config.admin_user_ids
        is_owner = user_id == self.config.owner_user_id

        help_text = f"🤖 <b>{self.config.instance_name} - Ajuda</b>\n\n"

        # Comandos básicos
        help_text += "<b>Comandos Básicos:</b>\n"
        help_text += "/start - Iniciar o bot\n"
        help_text += "/help - Mostrar esta ajuda\n"
        help_text += "/status - Mostrar status do bot\n\n"

        # Comandos do registry
        registry = get_command_registry()
        user_commands = []
        admin_commands = []

        for cmd_name, cmd_info in registry.get_all_commands().items():
            if cmd_info["hidden"]:
                continue
            cmd_line = f"/{cmd_name}"
            if cmd_info["description"]:
                cmd_line += f" - {cmd_info['description']}"
            if cmd_info["admin_only"]:
                admin_commands.append(cmd_line)
            else:
                user_commands.append(cmd_line)

        if user_commands:
            help_text += "<b>Comandos Disponíveis:</b>\n"
            help_text += "\n".join(sorted(user_commands)) + "\n\n"

        if is_admin and admin_commands:
            help_text += "<b>Comandos Administrativos:</b>\n"
            help_text += "\n".join(sorted(admin_commands)) + "\n\n"

        await update.message.reply_text(help_text, parse_mode='HTML')

    @command(name="config", description="Mostrar configuração", admin_only=True)
    @admin_required_simple
    @typing_indicator
    async def config_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mostra configuração atual."""
        config_dict = self.config.to_dict()

        config_text = "🔧 **Configuração Atual:**\n\n"

        for key, value in config_dict.items():
            config_text += f"**{key}:** `{value}`\n"

        await update.message.reply_text(
            config_text,
            parse_mode=ParseMode.MARKDOWN
        )

    @command(name="stats", description="Estatísticas do bot", admin_only=True)
    @admin_required_simple
    @typing_indicator
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mostra estatísticas do bot."""
        stats_text = "📊 **Estatísticas do Bot:**\n\n"

        # Tempo de execução
        if self._startup_time:
            uptime = datetime.now() - self._startup_time
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            stats_text += f"⏱️ **Tempo Online:** {days}d {hours}h {minutes}m\n"

        # Usuários
        if self.user_manager:
            user_count = await self.user_manager.get_user_count()
            stats_text += f"👥 **Usuários:** {user_count}\n"

        # Comandos executados
        total_commands = sum(self._command_stats.values())
        stats_text += f"🔧 **Comandos Executados:** {total_commands}\n"

        # Top comandos
        if self._command_stats:
            top_commands = sorted(
                self._command_stats.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]

            stats_text += "\n**Top Comandos:**\n"
            for cmd, count in top_commands:
                stats_text += f"/{cmd}: {count}\n"

        # Plugins
        if self.plugin_manager:
            loaded_plugins = len(self.plugin_manager.loaded_plugins)
            available_plugins = len(self.plugin_manager.available_plugins)
            stats_text += f"\n🔌 **Plugins:** {loaded_plugins}/{available_plugins}\n"

        await update.message.reply_text(
            stats_text,
            parse_mode=ParseMode.MARKDOWN
        )

    @command(name="users", description="Listar usuários", admin_only=True)
    @admin_required_simple
    @typing_indicator
    async def users_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lista usuários registrados."""
        if not self.user_manager:
            await update.message.reply_text("❌ Gerenciador de usuários não disponível")
            return

        users = await self.user_manager.get_all_users()

        if not users:
            await update.message.reply_text("📭 Nenhum usuário registrado")
            return

        users_text = f"👥 **Usuários Registrados ({len(users)}):**\n\n"

        for user in users[:20]:  # Limitar a 20 usuários
            status = "👑" if user['id'] == self.config.owner_user_id else (
                "⭐" if user['id'] in self.config.admin_user_ids else "👤"
            )

            users_text += f"{status} **{user['first_name']}** "
            if user.get('last_name'):
                users_text += f"{user['last_name']} "
            if user.get('username'):
                users_text += f"(@{user['username']}) "
            users_text += f"- ID: `{user['id']}`\n"

        if len(users) > 20:
            users_text += f"\n... e mais {len(users) - 20} usuários"

        await update.message.reply_text(
            users_text,
            parse_mode=ParseMode.MARKDOWN
        )

    @command(name="restart", description="Reiniciar o bot", admin_only=True)
    @owner_required
    @typing_indicator
    async def restart_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Reinicia o bot."""
        await update.message.reply_text("🔄 Reiniciando o bot...")

        # Salvar estado se necessário
        if self.persistence_manager:
            await self.persistence_manager.flush()

        # Notificar admins
        await self.send_admin_message("🔄 Bot sendo reiniciado...")

        # Reiniciar aplicação
        await self.application.stop()
        await self.initialize()
        await self.application.start()

    @command(name="shutdown", description="Desligar o bot", admin_only=True)
    @owner_required
    @typing_indicator
    async def shutdown_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Desliga o bot."""
        await update.message.reply_text("🛑 Desligando o bot...")

        # Salvar estado se necessário
        if self.persistence_manager:
            await self.persistence_manager.flush()

        # Parar o bot
        await self.stop()

        await update.message.reply_text("✅ Bot desligado com sucesso!")

    @command(name="plugindemo", description="Demonstra funcionalidades do plugin")
    @typing_indicator
    async def plugin_demo_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Demonstra funcionalidades do plugin."""
        user = update.effective_user
        message = (
            f"🎯 <b>Demo Plugin Funcionalidades</b>\n\n"
            f"👤 <b>Usuário:</b> {user.first_name}\n"
            f"🆔 <b>ID:</b> {user.id}\n"
            f"📅 <b>Data:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"
            f"✨ Este plugin demonstra:\n"
            f"• Sistema de plugins\n"
            f"• Comandos customizados\n"
            f"• Integração com framework\n"
            f"• Notificações administrativas"
        )
        await update.message.reply_text(message, parse_mode='HTML')

    @command(name="plugininfo", description="Mostra informações do plugin")
    @typing_indicator
    async def plugin_info_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mostra informações do plugin."""
        info = (
            f"📋 <b>Informações do Plugin</b>\n\n"
            f"📦 <b>Nome:</b> DemoPlugin\n"
            f"🔢 <b>Versão:</b> 1.0.0\n"
            f"📝 <b>Descrição:</b> Plugin de demonstração com funcionalidades avançadas\n"
            f"👨‍💻 <b>Autor:</b> Framework Demo\n"
            f"🔄 <b>Status:</b> ✅ Ativo\n"
            f"🎯 <b>Comandos:</b> 2"
        )
        await update.message.reply_text(info, parse_mode='HTML')

    @command(name="botrestart", description="Reiniciar o bot", admin_only=True)
    @owner_required
    @typing_indicator
    async def bot_restart_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Reinicia o bot."""
        user = update.effective_user

        await update.message.reply_text(
            f"🔄 <b>Reiniciando o bot...</b>\n\n"
            f"👤 <b>Solicitado por:</b> {user.first_name}\n"
            f"🆔 <b>ID:</b> {user.id}\n"
            f"⏰ <b>Horário:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            parse_mode='HTML'
        )

        # Salvar estado se necessário
        if self.persistence_manager:
            await self.persistence_manager.flush()

        # Notificar admins sobre reinicialização
        await self.send_admin_message(
            f"🔄 <b>Bot sendo reiniciado</b>\n"
            f"👤 Por: {user.first_name} (ID: {user.id})\n"
            f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            parse_mode='HTML'
        )

        # Parar o bot (será reiniciado pelo sistema externo)
        await self.stop()

        await update.message.reply_text(
            "✅ <b>Bot reiniciado com sucesso!</b>\n\n"
            "🔄 O bot foi parado e será reiniciado automaticamente pelo sistema.",
            parse_mode='HTML'
        )

    @command(name="botstop", description="Parar o bot", admin_only=True)
    @owner_required
    @typing_indicator
    async def bot_stop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Para o bot."""
        user = update.effective_user

        await update.message.reply_text(
            f"🛑 <b>Parando o bot...</b>\n\n"
            f"👤 <b>Solicitado por:</b> {user.first_name}\n"
            f"🆔 <b>ID:</b> {user.id}\n"
            f"⏰ <b>Horário:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            parse_mode='HTML'
        )

        # Salvar estado se necessário
        if self.persistence_manager:
            await self.persistence_manager.flush()

        # Notificar admins sobre parada
        await self.send_admin_message(
            f"🛑 <b>Bot sendo parado</b>\n"
            f"👤 Por: {user.first_name} (ID: {user.id})\n"
            f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            parse_mode='HTML'
        )

        # Parar o bot
        await self.stop()

        await update.message.reply_text(
            "✅ <b>Bot parado com sucesso!</b>\n\n"
            "🛑 O bot foi desligado e não responderá mais a comandos.",
            parse_mode='HTML'
        )

    @command(name="gitpull", description="Atualizar o código fonte do bot via git pull", admin_only=True)
    @owner_required
    @typing_indicator
    async def gitpull_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Executa 'git pull' no diretório do projeto e retorna o resultado."""
        import subprocess
        from pathlib import Path
        try:
            repo_dir = Path(__file__).parent.parent.parent.resolve()
            result = subprocess.run(["git", "pull"], cwd=repo_dir, capture_output=True, text=True, timeout=30)
            output = result.stdout.strip() or result.stderr.strip() or "(sem saída)"
            if result.returncode == 0:
                msg = f"✅ <b>git pull executado com sucesso!</b>\n<pre>{output}</pre>"
            else:
                msg = f"❌ <b>Erro ao executar git pull:</b>\n<pre>{output}</pre>"
        except Exception as e:
            msg = f"❌ <b>Exceção ao executar git pull:</b>\n<pre>{e}</pre>"
        await update.message.reply_text(msg, parse_mode='HTML')

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para mensagens que não são comandos."""
        # Registrar usuário se necessário
        if self.user_manager:
            user = update.effective_user
            await self.user_manager.register_user(
                user_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name
            )

        # Aqui pode ser implementada lógica adicional para mensagens
        pass

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para erros."""
        error = context.error

        # Log do erro
        self.log_error(f"Erro durante update: {error}", exc_info=error)

        # Preparar informações do erro
        error_text = f"🚨 **Erro no Bot**\n\n"
        error_text += f"**Tipo:** {type(error).__name__}\n"
        error_text += f"**Mensagem:** {str(error)}\n"

        if update:
            error_text += f"**Update ID:** {update.update_id}\n"
            if update.effective_user:
                error_text += f"**Usuário:** {update.effective_user.full_name} (ID: {update.effective_user.id})\n"
            if update.effective_chat:
                error_text += f"**Chat:** {update.effective_chat.id}\n"

        # Enviar traceback para chat específico ou admins
        traceback_text = "```python\n" + "".join(traceback.format_exception(
            type(error), error, error.__traceback__
        )) + "\n```"

        chat_id = self.config.traceback_chat_id or self.config.log_chat_id
        if chat_id:
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=error_text + "\n" + traceback_text,
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                self.log_error(f"Erro ao enviar traceback: {e}")

        # Responder ao usuário se possível
        if update and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "❌ Ocorreu um erro ao processar sua solicitação. "
                    "O administrador foi notificado."
                )
            except Exception:
                pass

    # Métodos utilitários

    async def send_admin_message(self, text: str, **kwargs):
        """Envia mensagem para todos os administradores."""
        for admin_id in self.config.admin_user_ids:
            try:
                await self.application.bot.send_message(
                    chat_id=admin_id,
                    text=text,
                    parse_mode=ParseMode.MARKDOWN,
                    **kwargs
                )
            except Exception as e:
                self.log_warning(f"Erro ao enviar mensagem para admin {admin_id}: {e}")

    async def broadcast_message(self, text: str, **kwargs):
        """Envia mensagem para todos os usuários registrados."""
        if not self.user_manager:
            self.log_warning("User manager não disponível para broadcast")
            return

        users = await self.user_manager.get_all_users()
        success_count = 0

        for user in users:
            try:
                await self.application.bot.send_message(
                    chat_id=user['id'],
                    text=text,
                    **kwargs
                )
                success_count += 1
            except Exception as e:
                self.log_warning(f"Erro ao enviar broadcast para {user['id']}: {e}")

        self.log_info(f"Broadcast enviado para {success_count}/{len(users)} usuários")
        return success_count

    def run(self):
        """Executa o bot."""
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Ambiente interativo: rode como task
                loop.create_task(self._run_async())
            else:
                loop.run_until_complete(self._run_async())
        except KeyboardInterrupt:
            self.log_info("Bot interrompido pelo usuário")
        except RuntimeError:
            import asyncio
            asyncio.run(self._run_async())
        except Exception as e:
            self.log_error(f"Erro fatal ao executar bot: {e}", exc_info=e)
            sys.exit(1)

    async def _run_async(self):
        """Execução assíncrona do bot."""
        await self.initialize()

        self._startup_time = datetime.now()
        self._running = True

        # Iniciar o scheduler para executar jobs agendados
        if self.scheduler:
            self.scheduler.start()
            self.log_info("Scheduler iniciado - jobs agendados serão executados")

        # Notificar admins sobre inicialização
        await self.send_admin_message(
            f"🚀 **{self.config.instance_name}** iniciado!\n"
            f"⏰ Horário: {self._startup_time.strftime('%d/%m/%Y %H:%M:%S')}\n"
            f"🤖 Framework v1.0.0"
        )

        # Inicializar aplicação Telegram
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )

        # Manter o bot rodando
        try:
            while self._running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            self._running = False
        finally:
            # Parar o scheduler antes de finalizar
            if self.scheduler:
                self.scheduler.stop()
                self.log_info("Scheduler parado")

            await self.application.stop()
            await self.application.shutdown()

        self.log_info("Bot finalizado")

    async def stop(self):
        """Para o bot."""
        self._running = False

        # Finalizar componentes
        if self.plugin_manager:
            await self.plugin_manager.unload_all_plugins()

        if self.persistence_manager:
            await self.persistence_manager.flush()

        if self.application:
            await self.application.stop()

        self.log_info("Bot finalizado")

    @command(name="plugins", description="Listar plugins carregados", admin_only=True)
    @admin_required_simple
    @typing_indicator
    async def plugins_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lista plugins carregados."""
        if not self.plugin_manager:
            await update.message.reply_text("❌ Sistema de plugins não disponível")
            return

        plugins = self.plugin_manager.plugins
        if not plugins:
            await update.message.reply_text("📭 Nenhum plugin carregado")
            return

        plugins_text = f"🔌 **Plugins Carregados ({len(plugins)}):**\n\n"

        for plugin_name, plugin_info in plugins.items():
            if isinstance(plugin_info, str):
                # Fallback para string
                status = "✅"
                name = plugin_info
                version = "?"
                description = "Plugin carregado"
                author = "Desconhecido"
            else:
                status = "✅" if getattr(plugin_info, 'enabled', True) else "❌"
                name = getattr(plugin_info, 'name', plugin_name)
                version = getattr(plugin_info, 'version', "?")
                description = getattr(plugin_info, 'description', "Plugin carregado")
                author = getattr(plugin_info, 'author', "Desconhecido")
            plugins_text += f"{status} **{name}** v{version}\n"
            plugins_text += f"📝 {description}\n"
            plugins_text += f"👨‍💻 {author}\n\n"

        await update.message.reply_text(
            plugins_text,
            parse_mode=ParseMode.HTML
        )

    @command(name="plugin", description="Gerenciar plugin específico", admin_only=True)
    @admin_required_simple
    @typing_indicator
    async def plugin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gerencia plugin específico."""
        if not self.plugin_manager:
            await update.message.reply_text("❌ Sistema de plugins não disponível")
            return

        if not context.args:
            await update.message.reply_text(
                "📋 **Uso:** /plugin <ação> <nome>\n\n"
                "**Ações disponíveis:**\n"
                "• `info <nome>` - Informações do plugin\n"
                "• `enable <nome>` - Ativar plugin\n"
                "• `disable <nome>` - Desativar plugin\n"
                "• `reload <nome>` - Recarregar plugin\n"
                "• `list` - Listar todos os plugins"
            )
            return

        action = context.args[0].lower()

        if action == "list":
            plugins = self.plugin_manager.plugins
            if not plugins:
                await update.message.reply_text("📭 Nenhum plugin carregado")
                return

            plugins_text = f"🔌 **Plugins ({len(plugins)}):**\n\n"
            for plugin in plugins:
                status = "✅" if plugin.enabled else "❌"
                plugins_text += f"{status} **{plugin.name}** - {plugin.description}\n"

            await update.message.reply_text(
                plugins_text,
                parse_mode=ParseMode.MARKDOWN
            )
            return

        if len(context.args) < 2:
            await update.message.reply_text("❌ Nome do plugin é obrigatório")
            return

        plugin_name = context.args[1]
        plugin = self.plugin_manager.get_plugin(plugin_name)

        if not plugin:
            await update.message.reply_text(f"❌ Plugin '{plugin_name}' não encontrado")
            return

        if action == "info":
            info_text = f"📋 **Informações do Plugin**\n\n"
            info_text += f"**Nome:** {plugin.name}\n"
            info_text += f"**Versão:** {plugin.version}\n"
            info_text += f"**Descrição:** {plugin.description}\n"
            info_text += f"**Autor:** {plugin.author}\n"
            info_text += f"**Status:** {'✅ Ativo' if plugin.enabled else '❌ Inativo'}\n"
            info_text += f"**Comandos:** {len(plugin.get_commands())}"

            await update.message.reply_text(
                info_text,
                parse_mode=ParseMode.MARKDOWN
            )

        elif action == "enable":
            if plugin.enabled:
                await update.message.reply_text(f"ℹ️ Plugin '{plugin_name}' já está ativo")
            else:
                result = await self.plugin_manager.enable_plugin(plugin_name)
                if result:
                    await update.message.reply_text(f"✅ Plugin '{plugin_name}' ativado")
                else:
                    await update.message.reply_text(f"❌ Erro ao ativar plugin '{plugin_name}'")

        elif action == "disable":
            if not plugin.enabled:
                await update.message.reply_text(f"ℹ️ Plugin '{plugin_name}' já está inativo")
            else:
                result = await self.plugin_manager.disable_plugin(plugin_name)
                if result:
                    await update.message.reply_text(f"✅ Plugin '{plugin_name}' desativado")
                else:
                    await update.message.reply_text(f"❌ Erro ao desativar plugin '{plugin_name}'")

        elif action == "reload":
            result = await self.plugin_manager.reload_plugin(plugin_name)
            if result:
                await update.message.reply_text(f"🔄 Plugin '{plugin_name}' recarregado")
            else:
                await update.message.reply_text(f"❌ Erro ao recarregar plugin '{plugin_name}'")

        else:
            await update.message.reply_text(
                f"❌ Ação '{action}' não reconhecida\n"
                f"Use /plugin para ver as ações disponíveis"
            )

    # Handler methods expected by tests
    async def _handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        user = update.effective_user
        if user and self.user_manager:
            await self.user_manager.register_user(
                user_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name
            )

        await update.message.reply_text(
            f"Welcome to {self.config.instance_name}!\n"
            "Type /help to see available commands."
        )

    async def _handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_text = f"🤖 **{self.config.instance_name}** Help\n\n"
        help_text += "Available commands:\n"
        help_text += "• /start - Start the bot\n"
        help_text += "• /help - Show this help\n"
        help_text += "• /status - Show bot status\n"

        if self.user_manager and self.user_manager.is_admin(update.effective_user.id):
            help_text += "\n**Admin commands:**\n"
            help_text += "• /admin - Admin panel\n"
            help_text += "• /stats - Bot statistics\n"

        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

    async def _handle_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /admin command."""
        user_id = update.effective_user.id

        if not self.user_manager or not self.user_manager.is_admin(user_id):
            await update.message.reply_text(
                "❌ You are not authorized to access admin functions."
            )
            return

        admin_text = "🔧 **Admin Panel**\n\n"
        admin_text += "Available admin functions:\n"
        admin_text += "• Bot management\n"
        admin_text += "• User management\n"
        admin_text += "• System monitoring\n"

        await update.message.reply_text(admin_text, parse_mode=ParseMode.MARKDOWN)

    async def _handle_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command."""
        if self.user_manager:
            user_count = await self.user_manager.get_user_count()
        else:
            user_count = 0

        status_text = f"📊 **{self.config.instance_name} Status**\n\n"
        status_text += f"🟢 **Status:** {'Online' if self._running else 'Offline'}\n"
        status_text += f"👥 **Usuários:** {user_count}\n"

        if self._startup_time:
            uptime = datetime.now() - self._startup_time
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            status_text += f"⏱️ **Uptime:** {days}d {hours}h {minutes}m\n"

        # Informações do sistema
        if self.plugin_manager:
            loaded_plugins = len(self.plugin_manager.plugins) if hasattr(self.plugin_manager, 'plugins') else 0
            status_text += f"🔌 **Plugins:** {loaded_plugins} carregados\n"

        if self.persistence_manager:
            status_text += f"💾 **Persistência:** Ativa\n"

        status_text += f"🐛 **Debug:** {'Ativo' if self.config.debug else 'Inativo'}\n"
        status_text += f"⚡ **Async:** {'Ativo' if self.config.use_async else 'Inativo'}"

        await update.message.reply_text(status_text, parse_mode=ParseMode.MARKDOWN)

    def add_command_handler(self, command: str, handler):
        """Add a command handler."""
        self.log_info(f"Tentando registrar comando: /{command} com handler: {handler}")
        if self.application:
            try:
                self.application.add_handler(CommandHandler(command, handler))
                self.log_info(f"✅ Comando /{command} registrado com sucesso!")
            except Exception as e:
                self.log_error(f"❌ Erro ao registrar comando /{command}: {e}")
        else:
            self.log_warning(f"❌ Application não disponível para registrar comando /{command}")

    def command(self, command_name: str, **kwargs):
        """Decorator for registering commands."""
        def decorator(func):
            self.add_command_handler(command_name, func)
            return func
        return decorator

    async def shutdown(self):
        """Shutdown the framework."""
        self._running = False

        if self.application:
            await self.application.stop()
            await self.application.shutdown()

        if self.scheduler:
            await self.scheduler.shutdown()

        self.log_info("Framework shutdown complete")

    async def run_async(self):
        """Run the framework asynchronously."""
        if self.application:
            await self.application.run_polling()

        if self.scheduler:
            await self.scheduler.start()
