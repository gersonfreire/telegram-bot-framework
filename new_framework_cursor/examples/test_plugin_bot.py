#!/usr/bin/env python3
"""
Teste simples para verificar se o plugin_bot.py está carregando plugins.
"""

import os
import sys

# Adicionar o caminho do src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from plugin_bot import PluginBot

def test():
    print("=== Teste do PluginBot ===")
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    bot = PluginBot(config_file=env_path)
    
    # Verificar se o plugin foi carregado
    if bot.plugin_manager:
        loaded_plugins = bot.plugin_manager.get_loaded_plugins()
        if 'HelloPlugin' in loaded_plugins:
            print("✅ Plugin HelloPlugin carregado com sucesso!")
            plugin = bot.plugin_manager.get_plugin('HelloPlugin')
            commands = plugin.get_commands()
            print(f"✅ Comandos registrados: {list(commands.keys())}")
        else:
            print("❌ Plugin HelloPlugin não foi carregado")
    else:
        print("❌ PluginManager não foi criado")
    
    print("🎉 Teste concluído!")

if __name__ == "__main__":
    test() 