@command(name="scheduler_config", description="Configurações do scheduler")
@admin_required_simple
async def scheduler_config_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostrar configurações do scheduler."""
    config_msg = (
        f"⚙️ <b>Configurações do Scheduler</b>\n\n"
        f"🤖 <b>Nome da Instância:</b> {self.config.instance_name}\n"
        f"�� <b>Debug Mode:</b> {'✅' if self.config.debug else '❌'}\n"
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
