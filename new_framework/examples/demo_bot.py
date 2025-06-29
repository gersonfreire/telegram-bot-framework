#!/usr/bin/env python3
"""
Demo Bot - Demonstração Completa do Framework Telegram Bot

Este script demonstra todas as funcionalidades disponíveis no framework:
- Comandos básicos e avançados
- Sistema de permissões (admin, owner)
- Sistema de plugins
- Gerenciamento de usuários
- Persistência de dados
- Logging e notificações
- Configurações avançadas
- Utilitários de criptografia
- Sistema de agendamento (placeholder)
- Sistema de pagamentos (placeholder)
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
    TelegramBotFramework, command, admin_required_simple, owner_required,
    PluginBase, CryptoUtils, generate_encryption_key, create_secure_token, typing_indicator
)
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


class DemoPlugin(PluginBase):
    """Plugin de demonstração para o Demo Bot."""

    name = "DemoPlugin"
    version = "1.0.0"
    description = "Plugin de demonstração com funcionalidades avançadas"
    author = "Framework Demo"

    def __init__(self):
        super().__init__()
        # Registrar comandos do plugin
        self.register_command({
            "name": "plugin_demo",
            "handler": self.plugin_demo_command,
            "description": "Demonstra funcionalidades do plugin"
        })

        self.register_command({
            "name": "plugin_info",
            "handler": self.plugin_info_command,
            "description": "Mostra informações do plugin"
        })

    async def initialize(self, framework, config):
        """Chamado quando o plugin é inicializado."""
        await super().initialize(framework, config)
        print(f"✅ Plugin {self.name} inicializado com sucesso!")
        if self.framework:
            self.framework.send_admin_message(f"🔌 Plugin {self.name} foi carregado!")
        return True

    async def start(self):
        """Chamado quando o plugin é iniciado."""
        result = await super().start()
        print(f"✅ Plugin {self.name} iniciado!")
        return result

    async def stop(self):
        """Chamado quando o plugin é parado."""
        result = await super().stop()
        print(f"❌ Plugin {self.name} parado!")
        return result

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

    async def plugin_info_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mostra informações do plugin."""
        info = (
            f"📋 <b>Informações do Plugin</b>\n\n"
            f"📦 <b>Nome:</b> {self.name}\n"
            f"🔢 <b>Versão:</b> {self.version}\n"
            f"📝 <b>Descrição:</b> {self.description}\n"
            f"👨‍💻 <b>Autor:</b> {self.author}\n"
            f"🔄 <b>Status:</b> {'✅ Ativo' if self.enabled else '❌ Inativo'}\n"
            f"🎯 <b>Comandos:</b> {len(self.get_commands())}"
        )
        await update.message.reply_text(info, parse_mode='HTML')


class DemoBot(TelegramBotFramework):
    """
    Bot de demonstração completo do framework.

    Demonstra todas as funcionalidades disponíveis:
    - Comandos básicos e avançados
    - Sistema de permissões
    - Gerenciamento de usuários
    - Plugins
    - Utilitários
    - Configurações
    """

    def __init__(self, config_file=None, custom_config=None):
        # Configurar diretório de plugins
        plugins_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "./")
        super().__init__(config_file=config_file, plugins_dir=plugins_dir, custom_config=custom_config)

        # Configurações específicas do demo
        self.config.data['auto_load_plugins'] = True
        self.config.data['debug'] = True

        # Estatísticas do demo
        self.demo_stats = {
            'commands_executed': 0,
            'users_interacted': set(),
            'start_time': datetime.now()
        }

        # Carregar o DemoPlugin manualmente
        self.demo_plugin = DemoPlugin()
        if self.plugin_manager:
            self.plugin_manager.load_plugin_instance(self.demo_plugin)

    # ============================================================================
    # COMANDOS BÁSICOS DE DEMONSTRAÇÃO
    # ============================================================================

    @command(name="demo", description="Menu principal de demonstração")
    @typing_indicator
    async def demo_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Menu principal de demonstração."""
        keyboard = [
            [InlineKeyboardButton("🔧 Comandos Básicos", callback_data="demo_basic")],
            [InlineKeyboardButton("🛡️ Sistema de Permissões", callback_data="demo_permissions")],
            [InlineKeyboardButton("👥 Gerenciamento de Usuários", callback_data="demo_users")],
            [InlineKeyboardButton("🔌 Sistema de Plugins", callback_data="demo_plugins")],
            [InlineKeyboardButton("🔐 Utilitários de Criptografia", callback_data="demo_crypto")],
            [InlineKeyboardButton("📊 Estatísticas", callback_data="demo_stats")],
            [InlineKeyboardButton("⚙️ Configurações", callback_data="demo_config")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        message = (
            "🎯 <b>Demo Bot - Framework Completo</b>\n\n"
            "Bem-vindo ao bot de demonstração do framework!\n"
            "Escolha uma categoria para explorar as funcionalidades:"
        )

        await update.message.reply_text(message, parse_mode='HTML', reply_markup=reply_markup)

    @command(name="welcome", description="Mensagem de boas-vindas personalizada")
    @typing_indicator
    async def welcome_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mensagem de boas-vindas personalizada."""
        user = update.effective_user
        chat = update.effective_chat

        # Verificar se é admin
        is_admin = self.user_manager.is_admin(user.id) if self.user_manager else False
        is_owner = self.user_manager.is_owner(user.id) if self.user_manager else False

        welcome_msg = (
            f"🎉 <b>Bem-vindo ao Demo Bot!</b>\n\n"
            f"👤 <b>Usuário:</b> {user.first_name}\n"
            f"🆔 <b>ID:</b> {user.id}\n"
            f"💬 <b>Chat:</b> {chat.type}\n"
            f"📅 <b>Data:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"
            f"🔐 <b>Permissões:</b>\n"
            f"• Admin: {'✅' if is_admin else '❌'}\n"
            f"• Owner: {'✅' if is_owner else '❌'}\n\n"
            f"💡 Use /demo para explorar todas as funcionalidades!"
        )

        await update.message.reply_text(welcome_msg, parse_mode='HTML')

        # Atualizar estatísticas
        self.demo_stats['commands_executed'] += 1
        self.demo_stats['users_interacted'].add(user.id)

    @command(name="info", description="Informações detalhadas do bot")
    @typing_indicator
    async def info_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Informações detalhadas do bot."""
        uptime = datetime.now() - self.demo_stats['start_time']
        uptime_str = str(uptime).split('.')[0]  # Remover microssegundos

        info_msg = (
            f"🤖 <b>Informações do Demo Bot</b>\n\n"
            f"📦 <b>Framework:</b> Telegram Bot Framework\n"
            f"🔢 <b>Versão:</b> 2.0.0\n"
            f"📅 <b>Iniciado em:</b> {self.demo_stats['start_time'].strftime('%d/%m/%Y %H:%M:%S')}\n"
            f"⏱️ <b>Uptime:</b> {uptime_str}\n"
            f"🎯 <b>Comandos executados:</b> {self.demo_stats['commands_executed']}\n"
            f"👥 <b>Usuários únicos:</b> {len(self.demo_stats['users_interacted'])}\n"
            f"🔌 <b>Plugins carregados:</b> {len(self.plugin_manager.plugins) if self.plugin_manager else 0}\n"
            f"💾 <b>Persistência:</b> {'✅' if self.persistence_manager else '❌'}\n"
            f"🐛 <b>Debug mode:</b> {'✅' if self.config.debug else '❌'}"
        )

        await update.message.reply_text(info_msg, parse_mode='HTML')

    # ============================================================================
    # COMANDOS DE PERMISSÕES
    # ============================================================================

    @command(name="admin_test", description="Teste de permissões de admin")
    @admin_required_simple
    @typing_indicator
    async def admin_test_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Teste de permissões de admin."""
        user = update.effective_user
        message = (
            f"🛡️ <b>Teste de Permissões - Admin</b>\n\n"
            f"✅ <b>Status:</b> Acesso permitido\n"
            f"👤 <b>Usuário:</b> {user.first_name}\n"
            f"🆔 <b>ID:</b> {user.id}\n"
            f"🔐 <b>Nível:</b> Administrador\n\n"
            f"🎯 <b>Funcionalidades disponíveis:</b>\n"
            f"• Gerenciamento de usuários\n"
            f"• Configurações do bot\n"
            f"• Estatísticas detalhadas\n"
            f"• Controle de plugins"
        )
        await update.message.reply_text(message, parse_mode='HTML')

    @command(name="owner_test", description="Teste de permissões de owner")
    @owner_required
    @typing_indicator
    async def owner_test_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Teste de permissões de owner."""
        user = update.effective_user
        message = (
            f"👑 <b>Teste de Permissões - Owner</b>\n\n"
            f"✅ <b>Status:</b> Acesso permitido\n"
            f"👤 <b>Usuário:</b> {user.first_name}\n"
            f"🆔 <b>ID:</b> {user.id}\n"
            f"🔐 <b>Nível:</b> Proprietário\n\n"
            f"🎯 <b>Funcionalidades exclusivas:</b>\n"
            f"• Reiniciar/desligar bot\n"
            f"• Configurações críticas\n"
            f"• Acesso total ao sistema\n"
            f"• Gerenciamento de admins"
        )
        await update.message.reply_text(message, parse_mode='HTML')

    @command(name="permission_denied", description="Demonstra mensagem de permissão negada")
    @admin_required_simple
    @typing_indicator
    async def permission_denied_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Este comando sempre requer admin, demonstrando controle de acesso."""
        await update.message.reply_text("✅ Se você vê esta mensagem, você tem permissões de admin!")

    # ============================================================================
    # COMANDOS DE GERENCIAMENTO DE USUÁRIOS
    # ============================================================================

    @command(name="user_info", description="Informações do usuário atual")
    @typing_indicator
    async def user_info_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Informações detalhadas do usuário atual."""
        user = update.effective_user

        if not self.user_manager:
            await update.message.reply_text("❌ User Manager não disponível")
            return

        # Verificar permissões
        is_admin = self.user_manager.is_admin(user.id)
        is_owner = self.user_manager.is_owner(user.id)

        # Obter dados do usuário
        user_data = await self.user_manager.get_user(user.id)

        info_msg = (
            f"👤 <b>Informações do Usuário</b>\n\n"
            f"📝 <b>Nome:</b> {user.first_name}\n"
            f"🆔 <b>ID:</b> {user.id}\n"
            f"🔗 <b>Username:</b> @{user.username if user.username else 'N/A'}\n"
            f"🌐 <b>Idioma:</b> {user.language_code if user.language_code else 'N/A'}\n\n"
            f"🔐 <b>Permissões:</b>\n"
            f"• Admin: {'✅' if is_admin else '❌'}\n"
            f"• Owner: {'✅' if is_owner else '❌'}\n\n"
            f"📊 <b>Dados do Sistema:</b>\n"
            f"• Registrado: {'✅' if user_data else '❌'}\n"
            f"• Última atividade: {user_data.get('last_activity', 'N/A') if user_data else 'N/A'}"
        )

        await update.message.reply_text(info_msg, parse_mode='HTML')

    @command(name="add_admin", description="Adicionar usuário como admin (apenas owner)")
    @owner_required
    @typing_indicator
    async def add_admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Adicionar usuário como admin."""
        if not context.args:
            await update.message.reply_text("❌ Uso: /add_admin <user_id>")
            return

        try:
            user_id = int(context.args[0])
            if not self.user_manager:
                await update.message.reply_text("❌ User Manager não disponível")
                return

            # Adicionar à lista de admins na config
            if user_id not in self.config.admin_user_ids:
                self.config.admin_user_ids.append(user_id)
                # Atualizar status do usuário na persistência
                user_data = await self.user_manager.get_user(user_id)
                if user_data:
                    user_data["is_admin"] = True
                    await self.user_manager.save_user(user_id, user_data)
                await update.message.reply_text(f"✅ Usuário {user_id} adicionado como admin!")
            else:
                await update.message.reply_text(f"ℹ️ Usuário {user_id} já é admin.")
        except ValueError:
            await update.message.reply_text("❌ ID de usuário inválido")

    # ============================================================================
    # COMANDOS DE CRIPTOGRAFIA
    # ============================================================================

    @command(name="crypto_demo", description="Demonstração de criptografia")
    @typing_indicator
    async def crypto_demo_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Demonstração de funcionalidades de criptografia."""
        try:
            # Gerar chave
            key = generate_encryption_key()

            # Texto para criptografar
            original_text = "Mensagem secreta do Demo Bot! 🔐"

            # Criptografar
            crypto = CryptoUtils(key)
            encrypted = crypto.encrypt_string(original_text)

            # Descriptografar
            decrypted = crypto.decrypt_string(encrypted)

            demo_msg = (
                f"🔐 <b>Demonstração de Criptografia</b>\n\n"
                f"📝 <b>Texto Original:</b>\n<code>{original_text}</code>\n\n"
                f"🔑 <b>Chave Gerada:</b>\n<code>{key}</code>\n\n"
                f"🔒 <b>Texto Criptografado:</b>\n<code>{encrypted}</code>\n\n"
                f"🔓 <b>Texto Descriptografado:</b>\n<code>{decrypted}</code>\n\n"
                f"✅ <b>Status:</b> Criptografia/Descriptografia bem-sucedida!"
            )

            await update.message.reply_text(demo_msg, parse_mode='HTML')

        except Exception as e:
            await update.message.reply_text(f"❌ Erro na demonstração de criptografia: {e}")

    # ============================================================================
    # COMANDOS DE ESTATÍSTICAS
    # ============================================================================

    @command(name="demo_stats", description="Estatísticas do demo bot")
    @typing_indicator
    async def demo_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Estatísticas detalhadas do demo bot."""
        uptime = datetime.now() - self.demo_stats['start_time']
        uptime_str = str(uptime).split('.')[0]

        # Calcular estatísticas
        total_users = len(self.demo_stats['users_interacted'])
        commands_per_user = self.demo_stats['commands_executed'] / max(total_users, 1)

        stats_msg = (
            f"📊 <b>Estatísticas do Demo Bot</b>\n\n"
            f"⏱️ <b>Tempo de Execução:</b> {uptime_str}\n"
            f"🎯 <b>Comandos Executados:</b> {self.demo_stats['commands_executed']}\n"
            f"👥 <b>Usuários Únicos:</b> {total_users}\n"
            f"📈 <b>Média de Comandos/Usuário:</b> {commands_per_user:.2f}\n\n"
            f"🔌 <b>Plugins:</b>\n"
            f"• Carregados: {len(self.plugin_manager.plugins) if self.plugin_manager else 0}\n"
            f"• Ativos: {len([p for p in self.plugin_manager.plugins.values() if p.get('enabled', False)]) if self.plugin_manager else 0}\n\n"
            f"💾 <b>Sistema:</b>\n"
            f"• Persistência: {'✅' if self.persistence_manager else '❌'}\n"
            f"• Debug Mode: {'✅' if self.config.debug else '❌'}\n"
            f"• User Manager: {'✅' if self.user_manager else '❌'}"
        )

        await update.message.reply_text(stats_msg, parse_mode='HTML')

    # ============================================================================
    # COMANDOS DE CONFIGURAÇÃO
    # ============================================================================

    @command(name="demo_config", description="Mostrar configurações do demo")
    @admin_required_simple
    @typing_indicator
    async def demo_config_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mostrar configurações do demo bot."""
        config_msg = (
            f"⚙️ <b>Configurações do Demo Bot</b>\n\n"
            f"🤖 <b>Nome da Instância:</b> {self.config.instance_name}\n"
            f"🐛 <b>Debug Mode:</b> {'✅' if self.config.debug else '❌'}\n"
            f"🔄 <b>Reuse Connections:</b> {'✅' if self.config.reuse_connections else '❌'}\n"
            f"⚡ <b>Async Mode:</b> {'✅' if self.config.use_async else '❌'}\n"
            f"👥 <b>Max Workers:</b> {self.config.max_workers}\n"
            f"🔌 <b>Auto Load Plugins:</b> {'✅' if self.config.auto_load_plugins else '❌'}\n"
            f"💾 <b>Persistence Backend:</b> {self.config.persistence_backend}\n"
            f"📝 <b>Log Chat ID:</b> {self.config.log_chat_id or 'N/A'}\n"
            f"👑 <b>Owner ID:</b> {self.config.owner_user_id}\n"
            f"🛡️ <b>Admin IDs:</b> {', '.join(map(str, self.config.admin_user_ids))}"
        )

        await update.message.reply_text(config_msg, parse_mode='HTML')

    # ============================================================================
    # COMANDOS AVANÇADOS
    # ============================================================================

    @command(name="broadcast_demo", description="Demonstração de broadcast (apenas admin)")
    @admin_required_simple
    @typing_indicator
    async def broadcast_demo_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Demonstração de broadcast para todos os usuários."""
        if not context.args:
            await update.message.reply_text("❌ Uso: /broadcast_demo <mensagem>")
            return

        message = " ".join(context.args)
        broadcast_msg = f"📢 <b>Broadcast Demo:</b>\n\n{message}"

        try:
            self.broadcast_message(broadcast_msg, parse_mode='HTML')
            await update.message.reply_text("✅ Broadcast enviado com sucesso!")
        except Exception as e:
            await update.message.reply_text(f"❌ Erro no broadcast: {e}")

    @command(name="test_error", description="Teste de tratamento de erros")
    @typing_indicator
    async def test_error_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Teste de tratamento de erros do framework."""
        try:
            # Simular um erro
            raise ValueError("Este é um erro de teste para demonstrar o tratamento de erros!")
        except Exception as e:
            await update.message.reply_text(
                f"🐛 <b>Erro Simulado Capturado:</b>\n\n"
                f"❌ <b>Tipo:</b> {type(e).__name__}\n"
                f"📝 <b>Mensagem:</b> {str(e)}\n\n"
                f"✅ O framework tratou o erro corretamente!",
                parse_mode='HTML'
            )

    # ============================================================================
    # COMANDOS DE PLUGINS
    # ============================================================================

    @command(name="plugins", description="Listar plugins carregados")
    @admin_required_simple
    @typing_indicator
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
    @typing_indicator
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
    # HANDLERS DE CALLBACK
    # ============================================================================

    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manipular callbacks dos botões inline."""
        query = update.callback_query
        await query.answer()

        if query.data == "demo_basic":
            await self._show_basic_commands(query)
        elif query.data == "demo_permissions":
            await self._show_permissions_demo(query)
        elif query.data == "demo_users":
            await self._show_users_demo(query)
        elif query.data == "demo_plugins":
            await self._show_plugins_demo(query)
        elif query.data == "demo_crypto":
            await self._show_crypto_demo(query)
        elif query.data == "demo_stats":
            await self._show_stats_demo(query)
        elif query.data == "demo_config":
            await self._show_config_demo(query)

    async def _show_basic_commands(self, query):
        """Mostrar comandos básicos."""
        message = (
            "🔧 <b>Comandos Básicos</b>\n\n"
            "📋 <b>Comandos Disponíveis:</b>\n"
            "• /start - Iniciar o bot\n"
            "• /help - Mostrar ajuda\n"
            "• /demo - Menu principal\n"
            "• /welcome - Boas-vindas\n"
            "• /info - Informações do bot\n"
            "• /status - Status do sistema\n\n"
            "💡 <b>Funcionalidades:</b>\n"
            "• Sistema de comandos com decoradores\n"
            "• Tratamento automático de erros\n"
            "• Logging integrado\n"
            "• Notificações administrativas"
        )
        await query.edit_message_text(message, parse_mode='HTML')

    async def _show_permissions_demo(self, query):
        """Mostrar demonstração de permissões."""
        message = (
            "🛡️ <b>Sistema de Permissões</b>\n\n"
            "🔐 <b>Níveis de Acesso:</b>\n"
            "• 👤 <b>Usuário:</b> Comandos básicos\n"
            "• 🛡️ <b>Admin:</b> Gerenciamento e configurações\n"
            "• 👑 <b>Owner:</b> Controle total\n\n"
            "📋 <b>Comandos de Teste:</b>\n"
            "• /admin_test - Teste de admin\n"
            "• /owner_test - Teste de owner\n"
            "• /permission_denied - Demo de acesso negado\n\n"
            "💡 <b>Decoradores:</b>\n"
            "@admin_required - Apenas admins\n"
            "@owner_required - Apenas owner"
        )
        await query.edit_message_text(message, parse_mode='HTML')

    async def _show_users_demo(self, query):
        """Mostrar demonstração de usuários."""
        message = (
            "👥 <b>Gerenciamento de Usuários</b>\n\n"
            "📊 <b>Funcionalidades:</b>\n"
            "• Registro automático de usuários\n"
            "• Controle de permissões\n"
            "• Persistência de dados\n"
            "• Estatísticas de uso\n\n"
            "📋 <b>Comandos:</b>\n"
            "• /user_info - Informações do usuário\n"
            "• /add_admin - Adicionar admin (owner)\n"
            "• /users - Listar usuários (admin)\n\n"
            "💾 <b>Persistência:</b>\n"
            "• Dados salvos automaticamente\n"
            "• Recuperação após reinicialização\n"
            "• Backup de configurações"
        )
        await query.edit_message_text(message, parse_mode='HTML')

    async def _show_plugins_demo(self, query):
        """Mostrar demonstração de plugins."""
        plugin_count = len(self.plugin_manager.plugins) if self.plugin_manager else 0
        active_plugins = len([p for p in self.plugin_manager.plugins.values() if p.get('enabled', False)]) if self.plugin_manager else 0

        message = (
            f"🔌 <b>Sistema de Plugins</b>\n\n"
            f"📦 <b>Status:</b>\n"
            f"• Plugins carregados: {plugin_count}\n"
            f"• Plugins ativos: {active_plugins}\n"
            f"• Auto-carregamento: {'✅' if self.config.auto_load_plugins else '❌'}\n\n"
            f"📋 <b>Comandos de Plugins:</b>\n"
            "• /plugins - Listar plugins\n"
            "• /plugin - Gerenciar plugin\n"
            "• /plugin_demo - Demo do plugin\n"
            "• /plugin_info - Info do plugin\n\n"
            "💡 <b>Funcionalidades:</b>\n"
            "• Carregamento dinâmico\n"
            "• Comandos customizados\n"
            "• Isolamento de código\n"
            "• Hot-reload (futuro)"
        )
        await query.edit_message_text(message, parse_mode='HTML')

    async def _show_crypto_demo(self, query):
        """Mostrar demonstração de criptografia."""
        message = (
            "🔐 <b>Utilitários de Criptografia</b>\n\n"
            "🔑 <b>Funcionalidades:</b>\n"
            "• Geração de chaves seguras\n"
            "• Criptografia de dados\n"
            "• Descriptografia segura\n"
            "• Proteção de configurações\n\n"
            "📋 <b>Comandos:</b>\n"
            "• /crypto_demo - Demonstração completa\n\n"
            "💡 <b>Casos de Uso:</b>\n"
            "• Tokens de API\n"
            "• Senhas de banco\n"
            "• Dados sensíveis\n"
            "• Configurações críticas"
        )
        await query.edit_message_text(message, parse_mode='HTML')

    async def _show_stats_demo(self, query):
        """Mostrar demonstração de estatísticas."""
        uptime = datetime.now() - self.demo_stats['start_time']
        uptime_str = str(uptime).split('.')[0]

        message = (
            f"📊 <b>Sistema de Estatísticas</b>\n\n"
            f"⏱️ <b>Métricas Atuais:</b>\n"
            f"• Uptime: {uptime_str}\n"
            f"• Comandos: {self.demo_stats['commands_executed']}\n"
            f"• Usuários únicos: {len(self.demo_stats['users_interacted'])}\n\n"
            f"📋 <b>Comandos:</b>\n"
            "• /demo_stats - Estatísticas detalhadas\n"
            "• /stats - Estatísticas do sistema\n\n"
            "💡 <b>Funcionalidades:</b>\n"
            "• Coleta automática\n"
            "• Métricas em tempo real\n"
            "• Relatórios detalhados\n"
            "• Monitoramento de performance"
        )
        await query.edit_message_text(message, parse_mode='HTML')

    async def _show_config_demo(self, query):
        """Mostrar demonstração de configuração."""
        message = (
            "⚙️ <b>Sistema de Configuração</b>\n\n"
            "🔧 <b>Funcionalidades:</b>\n"
            "• Carregamento de .env\n"
            "• Validação automática\n"
            "• Criptografia de dados sensíveis\n"
            "• Configurações dinâmicas\n\n"
            "📋 <b>Comandos:</b>\n"
            "• /config - Mostrar configuração\n"
            "• /demo_config - Config do demo\n\n"
            "💡 <b>Recursos:</b>\n"
            "• Variáveis de ambiente\n"
            "• Configurações padrão\n"
            "• Validação de tipos\n"
            "• Backup automático"
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
        """Override do comando start para incluir demo."""
        user = update.effective_user

        welcome_msg = (
            f"🎉 <b>Bem-vindo ao Demo Bot!</b>\n\n"
            f"👤 Olá, {user.first_name}!\n\n"
            f"🤖 Este é um bot de demonstração completo do <b>Telegram Bot Framework</b>.\n\n"
            f"🎯 <b>Funcionalidades Demonstradas:</b>\n"
            f"• ✅ Sistema de comandos avançado\n"
            f"• ✅ Controle de permissões\n"
            f"• ✅ Gerenciamento de usuários\n"
            f"• ✅ Sistema de plugins\n"
            f"• ✅ Criptografia e segurança\n"
            f"• ✅ Estatísticas e monitoramento\n"
            f"• ✅ Configurações flexíveis\n\n"
            f"💡 Use /demo para explorar todas as funcionalidades!\n"
            f"📚 Use /help para ver todos os comandos disponíveis."
        )

        await update.message.reply_text(welcome_msg, parse_mode='HTML')

        # Atualizar estatísticas
        self.demo_stats['commands_executed'] += 1
        self.demo_stats['users_interacted'].add(user.id)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Override do comando help para incluir comandos do demo."""
        help_msg = (
            "📚 <b>Comandos do Demo Bot</b>\n\n"
            "🎯 <b>Comandos Principais:</b>\n"
            "• /start - Iniciar o bot\n"
            "• /demo - Menu de demonstração\n"
            "• /help - Esta ajuda\n"
            "• /info - Informações do bot\n"
            "• /welcome - Boas-vindas personalizadas\n\n"
            "🛡️ <b>Comandos de Permissões:</b>\n"
            "• /admin_test - Teste de admin\n"
            "• /owner_test - Teste de owner\n"
            "• /permission_denied - Demo de acesso negado\n\n"
            "👥 <b>Comandos de Usuários:</b>\n"
            "• /user_info - Informações do usuário\n"
            "• /add_admin - Adicionar admin (owner)\n\n"
            "🔌 <b>Comandos de Plugins:</b>\n"
            "• /plugin_demo - Demo do plugin\n"
            "• /plugin_info - Info do plugin\n\n"
            "🔐 <b>Comandos de Criptografia:</b>\n"
            "• /crypto_demo - Demonstração de criptografia\n\n"
            "📊 <b>Comandos de Estatísticas:</b>\n"
            "• /demo_stats - Estatísticas do demo\n\n"
            "⚙️ <b>Comandos de Configuração:</b>\n"
            "• /demo_config - Configurações do demo\n\n"
            "🔧 <b>Comandos Avançados:</b>\n"
            "• /broadcast_demo - Demo de broadcast\n"
            "• /test_error - Teste de tratamento de erros\n\n"
            "💡 Use /demo para um menu interativo!"
        )

        await update.message.reply_text(help_msg, parse_mode='HTML')

        # Atualizar estatísticas
        self.demo_stats['commands_executed'] += 1


def main():
    """Função principal para executar o Demo Bot."""
    print("🚀 Iniciando Demo Bot - Framework Completo...")
    print("=" * 50)

    # Verificar arquivo .env na pasta examples
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.exists(env_path):
        print("⚠️  Arquivo .env não encontrado na pasta examples!")
        print("📝 Crie um arquivo .env com as seguintes variáveis:")
        print("   BOT_TOKEN=seu_token_aqui")
        print("   OWNER_USER_ID=seu_id_aqui")
        print("   ADMIN_USER_IDS=id1,id2,id3")
        print("   LOG_CHAT_ID=chat_id_para_logs")
        print("   DEBUG=true")
        print("=" * 50)

    try:
        # Criar e executar o bot
        bot = DemoBot(config_file=env_path)
        print("✅ Demo Bot criado com sucesso!")
        print("🎯 Funcionalidades disponíveis:")
        print("   • Sistema de comandos avançado")
        print("   • Controle de permissões (admin/owner)")
        print("   • Gerenciamento de usuários")
        print("   • Sistema de plugins")
        print("   • Criptografia e segurança")
        print("   • Estatísticas e monitoramento")
        print("   • Configurações flexíveis")
        print("   • Tratamento de erros")
        print("   • Logging integrado")
        print("=" * 50)
        print("🤖 Bot iniciado! Pressione Ctrl+C para parar")
        print("💡 Use /demo no Telegram para explorar as funcionalidades!")

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
