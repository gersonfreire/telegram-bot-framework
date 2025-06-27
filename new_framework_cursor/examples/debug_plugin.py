#!/usr/bin/env python3
"""
Script de debug para verificar o carregamento do plugin.
"""

import os
import sys
import asyncio

# Adicionar o caminho do src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tlgfwk.core import TelegramBotFramework

async def debug_plugin():
    """Debug do carregamento de plugin."""
    print("=== DEBUG PLUGIN ===")
    
    # Criar configuração mínima
    config = {
        'bot_token': 'test_token',
        'owner_user_id': 123456789,
        'debug': True
    }
    
    plugins_dir = os.path.dirname(os.path.abspath(__file__))
    
    print(f"📁 Diretório de plugins: {plugins_dir}")
    
    # Criar framework
    framework = TelegramBotFramework(custom_config=config, plugins_dir=plugins_dir)
    framework.config.data['auto_load_plugins'] = True
    
    print("✅ Framework criado")
    
    if framework.plugin_manager:
        print("✅ PluginManager criado")
        print(f"📁 PluginManager plugins_dir: {framework.plugin_manager.plugins_dir}")
        
        # Carregar plugins manualmente
        print("\n🔄 Carregando plugins...")
        await framework.plugin_manager.load_all_plugins()
        
        # Verificar plugins carregados
        loaded_plugins = framework.plugin_manager.get_loaded_plugins()
        print(f"\n📦 Plugins carregados: {loaded_plugins}")
        
        if 'HelloPlugin' in loaded_plugins:
            plugin = framework.plugin_manager.get_plugin('HelloPlugin')
            print(f"✅ Plugin HelloPlugin encontrado")
            print(f"📋 Comandos do plugin: {list(plugin.get_commands().keys())}")
            
            # Verificar se o comando está registrado no framework
            handlers = framework.application.handlers.get(0, [])
            command_handlers = [h for h in handlers if hasattr(h, 'command')]
            print(f"🔧 Handlers de comando no framework: {[h.command for h in command_handlers]}")
            
            # Verificar handlers em todos os grupos
            print("=== Handlers por grupo ===")
            for group, handlers in framework.application.handlers.items():
                print(f"Grupo {group}: {[getattr(h, 'command', None) for h in handlers]}")
                for idx, h in enumerate(handlers):
                    print(f"  Handler[{idx}] type: {type(h)}")
                    print(f"    dir: {dir(h)}")
                    if hasattr(h, 'command'):
                        print(f"    command: {getattr(h, 'command', None)}")
                    if hasattr(h, 'commands'):
                        print(f"    commands: {getattr(h, 'commands', None)}")
                    if hasattr(h, 'callback'):
                        print(f"    callback: {getattr(h, 'callback', None)}")
        else:
            print("❌ Plugin HelloPlugin não encontrado")
    else:
        print("❌ PluginManager não criado")

if __name__ == "__main__":
    asyncio.run(debug_plugin()) 