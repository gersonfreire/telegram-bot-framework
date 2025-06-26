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
from .decorators import get_command_registry, command, admin_required, owner_required
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
            self.config = Config(**custom_config)
        else:
            self.config = Config.from_env(config_file)
        
        # Configurar logging
        self.setup_logging()
        
        # Inicializar componentes
        self.user_manager: Optional[UserManager] = None
        self.plugin_manager: Optional[PluginManager] = None
        self.persistence_manager: Optional[PersistenceManager] = None
        
        # Estado interno
        self._running = False
        self._startup_time = None
        self._command_stats = {}
        
        # Construir a aplicação usando o builder pattern
        app_builder = Application.builder()
        app_builder.token(self.config.telegram_bot_token)
        
        # Configurações de rede
        if not self.config.reuse_connections:
            app_builder.connection_pool_size(1)
        else:
            app_builder.connection_pool_size(self.config.connection_pool_size)
        
        # Configurar persistência
        if self.config.persistence_backend != "none":
            self.persistence_manager = PersistenceManager(self.config)
            persistence = asyncio.run(self.persistence_manager.get_persistence())
            if persistence:
                app_builder.persistence(persistence)
        
        # Construir a aplicação
        self.application = app_builder.build()
        
        # Inicializar gerenciadores
        self.user_manager = UserManager(self.config, self.persistence_manager)
        
        if self.config.plugins_dir:
            self.plugin_manager = PluginManager(
                self.config.plugins_dir, 
                self
            )
        
        # Registrar handlers padrão
        self.register_default_handlers()
        
        # Carregar plugins
        if self.plugin_manager and self.config.auto_load_plugins:
            asyncio.run(self.plugin_manager.load_all_plugins())
        
        # Registrar comandos do menu
        asyncio.run(self.setup_bot_commands())
        
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
        
        # Notificar admins sobre inicialização
        await self.send_admin_message(
            f"Bot {self.config.instance_name} iniciado com sucesso!"
        )
        
        self.log_info("Framework inicializado com sucesso")
    
    def register_default_handlers(self):
        """Registra handlers padrão do framework."""
        # Comandos básicos
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        # Comandos administrativos
        self.application.add_handler(CommandHandler("config", self.config_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(CommandHandler("users", self.users_command))
        self.application.add_handler(CommandHandler("restart", self.restart_command))
        self.application.add_handler(CommandHandler("shutdown", self.shutdown_command))
        
        # Comandos de plugins
        if self.plugin_manager:
            self.application.add_handler(CommandHandler("plugins", self.plugins_command))
            self.application.add_handler(CommandHandler("plugin", self.plugin_command))
        
        # Handler para comandos não reconhecidos
        self.application.add_handler(
            MessageHandler(filters.COMMAND, self.unknown_command)
        )
        
        # Handler para mensagens não-comando
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )
        
        # Handler de erros
        self.application.add_error_handler(self.error_handler)
        
        # Registrar comandos do registry
        self.register_decorated_commands()
    
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
        commands = [
            BotCommand("start", "Iniciar o bot"),
            BotCommand("help", "Mostrar ajuda"),
        ]
        
        # Adicionar comandos administrativos
        if self.config.admin_user_ids:
            commands.extend([
                BotCommand("config", "Configurações (Admin)"),
                BotCommand("stats", "Estatísticas (Admin)"),
                BotCommand("users", "Usuários (Admin)"),
            ])
        
        # Adicionar comandos de plugins
        if self.plugin_manager:
            commands.append(BotCommand("plugins", "Gerenciar plugins"))
        
        try:
            await self.application.bot.set_my_commands(commands)
            self.log_info("Comandos do bot configurados")
        except Exception as e:
            self.log_error(f"Erro ao configurar comandos: {e}")
    
    @command(name="start", description="Iniciar o bot")
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start - Inicialização do bot."""
        user = update.effective_user
        
        # Registrar usuário
        if self.user_manager:
            await self.user_manager.register_user(user)
        
        welcome_text = f"""
🤖 Olá, {user.first_name}!

Bem-vindo ao {self.config.instance_name}!

Use /help para ver os comandos disponíveis.
        """.strip()
        
        await update.message.reply_text(welcome_text)
        
        # Notificar admins
        await self.send_admin_message(
            f"👤 Novo usuário: {user.first_name} (@{user.username}) - ID: {user.id}"
        )
    
    @command(name="help", description="Mostrar ajuda")
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /help - Mostra ajuda do bot."""
        user = update.effective_user
        is_admin = self.user_manager and await self.user_manager.is_admin(user.id)
        is_owner = self.user_manager and await self.user_manager.is_owner(user.id)
        
        # Obter comandos disponíveis
        registry = get_command_registry()
        all_commands = registry.get_all_commands()
        
        # Separar comandos por categoria
        user_commands = []
        admin_commands = []
        
        for cmd_name, cmd_info in all_commands.items():
            if cmd_info.get("admin_only", False):
                if is_admin:
                    admin_commands.append((cmd_name, cmd_info.get("description", "")))
            else:
                user_commands.append((cmd_name, cmd_info.get("description", "")))
        
        # Construir mensagem de ajuda
        help_text = f"📚 **Comandos disponíveis**\n\n"
        
        if user_commands:
            help_text += "**Comandos gerais:**\n"
            for cmd_name, description in sorted(user_commands):
                help_text += f"• /{cmd_name} - {description}\n"
            help_text += "\n"
        
        if admin_commands and is_admin:
            help_text += "**Comandos administrativos:**\n"
            for cmd_name, description in sorted(admin_commands):
                help_text += f"• /{cmd_name} - {description}\n"
        
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
    
    @command(name="config", description="Mostrar configuração", admin_only=True)
    @admin_required
    async def config_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /config - Mostra configuração atual."""
        config_text = f"""
⚙️ **Configuração do Bot**

**Informações básicas:**
• Nome: {self.config.instance_name}
• Debug: {'Sim' if self.config.debug else 'Não'}
• Persistência: {self.config.persistence_backend}

**Usuários:**
• Owner: {self.config.owner_user_id}
• Admins: {len(self.config.admin_user_ids)} usuários
        """.strip()
        
        await update.message.reply_text(config_text, parse_mode=ParseMode.MARKDOWN)
    
    @command(name="stats", description="Estatísticas do bot", admin_only=True)
    @admin_required
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /stats - Mostra estatísticas do bot."""
        uptime = datetime.now() - self._startup_time if self._startup_time else "N/A"
        
        stats_text = f"""
📊 **Estatísticas do Bot**

**Tempo de execução:**
• Iniciado em: {self._startup_time}
• Uptime: {uptime}

**Comandos executados:**
• Total: {sum(self._command_stats.values())}
        """.strip()
        
        await update.message.reply_text(stats_text, parse_mode=ParseMode.MARKDOWN)
    
    @command(name="users", description="Listar usuários", admin_only=True)
    @admin_required
    async def users_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /users - Lista usuários registrados."""
        if not self.user_manager:
            await update.message.reply_text("❌ Gerenciador de usuários não disponível")
            return
        
        users = await self.user_manager.get_all_users()
        
        if not users:
            await update.message.reply_text("📝 Nenhum usuário registrado")
            return
        
        users_text = f"👥 **Usuários registrados ({len(users)})**\n\n"
        
        for user in users[:20]:  # Limitar a 20 usuários
            status = "👑 Owner" if user.is_owner else "🔧 Admin" if user.is_admin else "👤 User"
            users_text += f"• {user.first_name} (@{user.username}) - {status}\n"
        
        if len(users) > 20:
            users_text += f"\n... e mais {len(users) - 20} usuários"
        
        await update.message.reply_text(users_text, parse_mode=ParseMode.MARKDOWN)
    
    @command(name="restart", description="Reiniciar o bot", admin_only=True)
    @owner_required
    async def restart_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /restart - Reinicia o bot."""
        await update.message.reply_text("🔄 Reiniciando o bot...")
        
        # Notificar todos os admins
        await self.broadcast_message("🔄 Bot será reiniciado em 3 segundos...")
        
        # Aguardar e reiniciar
        await asyncio.sleep(3)
        await self.stop()
        sys.exit(0)
    
    @command(name="shutdown", description="Desligar o bot", admin_only=True)
    @owner_required
    async def shutdown_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /shutdown - Desliga o bot."""
        await update.message.reply_text("🛑 Desligando o bot...")
        
        # Notificar todos os admins
        await self.broadcast_message("🛑 Bot será desligado em 3 segundos...")
        
        # Aguardar e desligar
        await asyncio.sleep(3)
        await self.stop()
        sys.exit(0)
    
    async def unknown_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para comandos não reconhecidos."""
        command = update.message.text.split()[0]
        await update.message.reply_text(
            f"❓ Comando '{command}' não reconhecido.\n"
            f"Use /help para ver os comandos disponíveis."
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para mensagens de texto não-comando."""
        # Por padrão, não faz nada com mensagens de texto
        # Pode ser sobrescrito por subclasses
        pass
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler de erros do framework."""
        error = context.error
        
        # Log do erro
        self.log_error(f"Erro no update {update}: {error}")
        
        # Enviar traceback para admins se configurado
        if self.config.traceback_chat_id:
            tb_text = f"❌ **Erro no bot:**\n\n```\n{traceback.format_exc()}\n```"
            try:
                await self.application.bot.send_message(
                    self.config.traceback_chat_id,
                    tb_text,
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                self.log_error(f"Erro ao enviar traceback: {e}")
        
        # Responder ao usuário
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Ocorreu um erro interno. Os administradores foram notificados."
            )
    
    async def send_admin_message(self, text: str, **kwargs):
        """Envia mensagem para todos os administradores."""
        if not self.config.admin_user_ids:
            return
        
        for admin_id in self.config.admin_user_ids:
            try:
                await self.application.bot.send_message(admin_id, text, **kwargs)
            except Exception as e:
                self.log_error(f"Erro ao enviar mensagem para admin {admin_id}: {e}")
    
    async def broadcast_message(self, text: str, **kwargs):
        """Envia mensagem para todos os usuários registrados."""
        if not self.user_manager:
            return
        
        users = await self.user_manager.get_all_users()
        
        for user in users:
            try:
                await self.application.bot.send_message(user.user_id, text, **kwargs)
            except Exception as e:
                self.log_error(f"Erro ao enviar broadcast para {user.user_id}: {e}")
    
    def run(self):
        """Executa o bot."""
        try:
            self._startup_time = datetime.now()
            self._running = True
            self.application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
        except KeyboardInterrupt:
            self.log_info("Bot interrompido pelo usuário")
        except Exception as e:
            self.log_error(f"Erro fatal: {e}")
            # Não propaga para não encerrar o processo

    async def stop(self):
        """Para o bot de forma graceful."""
        if self._running:
            self._running = False

            # Salvar dados
            if self.persistence_manager:
                await self.persistence_manager.save_all()

            # Parar aplicação
            try:
                await self.application.stop()
                await self.application.shutdown()
            except RuntimeError as e:
                if "Cannot close a running event loop" in str(e):
                    self.log_error("Tentativa de fechar um event loop já rodando ao parar o bot. Ignorando.")
                else:
                    raise

            self.log_info("Bot parado com sucesso")
    
    @property
    def bot(self):
        """Retorna a instância do bot."""
        return self.application.bot if self.application else None 