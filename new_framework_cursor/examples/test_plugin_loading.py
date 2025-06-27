#!/usr/bin/env python3
"""
Script de teste para verificar se os plugins estão sendo carregados corretamente.
"""

import os
import sys
import asyncio

# Adicionar o caminho do src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tlgfwk.core import TelegramBotFramework
from tlgfwk.core.plugin_manager import PluginManager

async def test_plugin_loading():
    """Testa o carregamento de plugins."""
    print("=== Teste de Carregamento de Plugins ===")
    
    # Criar uma instância do framework com configuração mínima
    config = {
        'bot_token': 'test_token',
        'owner_user_id': 123456789,
        'debug': True
    }
    
    plugins_dir = os.path.dirname(os.path.abspath(__file__))
    
    framework = TelegramBotFramework(custom_config=config, plugins_dir=plugins_dir)
    
    # Definir configurações de plugins após a criação do framework
    framework.config.data['auto_load_plugins'] = True
    
    # Verificar se o plugin manager foi criado
    if framework.plugin_manager:
        print(f"✅ PluginManager criado com sucesso")
        print(f"📁 Diretório de plugins: {framework.plugin_manager.plugins_dir}")
        
        # Tentar carregar plugins
        print("\n🔄 Carregando plugins...")
        await framework.plugin_manager.load_all_plugins()
        
        # Verificar plugins carregados
        loaded_plugins = framework.plugin_manager.get_loaded_plugins()
        print(f"\n📦 Plugins carregados: {loaded_plugins}")
        
        if loaded_plugins:
            for plugin_name in loaded_plugins:
                plugin = framework.plugin_manager.get_plugin(plugin_name)
                print(f"  - {plugin_name}: {plugin.description}")
                commands = plugin.get_commands()
                print(f"    Comandos: {list(commands.keys())}")
        else:
            print("❌ Nenhum plugin foi carregado")
    else:
        print("❌ PluginManager não foi criado")

if __name__ == "__main__":
    asyncio.run(test_plugin_loading()) 