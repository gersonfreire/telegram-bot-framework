#!/usr/bin/env python3
"""
Script final para testar o bot com plugin funcionando.
"""

import os
import sys

# Adicionar o caminho do src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tlgfwk.core import TelegramBotFramework

def main():
    """Função principal para testar o bot."""
    print("=== Teste Final do Bot com Plugin ===")
    
    # Verificar se o arquivo .env existe
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.exists(env_path):
        print("❌ Arquivo .env não encontrado!")
        print("Por favor, crie um arquivo .env com:")
        print("BOT_TOKEN=seu_token_aqui")
        print("OWNER_USER_ID=seu_user_id_aqui")
        return
    
    print("✅ Arquivo .env encontrado")
    
    # Criar o bot
    plugins_dir = os.path.dirname(os.path.abspath(__file__))
    bot = TelegramBotFramework(config_file=env_path, plugins_dir=plugins_dir)
    
    # Verificar se o plugin foi carregado
    if bot.plugin_manager:
        # Carregar plugins manualmente
        import asyncio
        asyncio.run(bot.plugin_manager.load_all_plugins())
        
        loaded_plugins = bot.plugin_manager.get_loaded_plugins()
        if 'HelloPlugin' in loaded_plugins:
            print("✅ Plugin HelloPlugin carregado com sucesso!")
            print("✅ Comando /hello disponível")
            print("\n🎉 Tudo pronto! Execute o bot com:")
            print("python plugin_bot.py")
        else:
            print("❌ Plugin HelloPlugin não foi carregado")
    else:
        print("❌ PluginManager não foi criado")

if __name__ == "__main__":
    main() 