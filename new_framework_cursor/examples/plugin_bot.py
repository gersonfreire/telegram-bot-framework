import os
import sys
import asyncio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from tlgfwk.core import TelegramBotFramework

class PluginBot(TelegramBotFramework):
    def __init__(self, config_file=None):
        # Aponta plugins_dir para a pasta examples
        plugins_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "./")
        super().__init__(config_file=config_file, plugins_dir=plugins_dir)
        # O PluginManager irá carregar plugins automaticamente se auto_load_plugins=True

async def setup_bot():
    """Configura o bot e carrega os plugins."""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    print("Starting PluginBot with HelloPlugin...")
    bot = PluginBot(config_file=env_path)

    # Definir configurações de plugins após a criação do framework
    bot.config.data['auto_load_plugins'] = True
    
    # Verificar se o plugin manager foi criado
    if bot.plugin_manager:
        print(f"✅ PluginManager criado com sucesso")
        print(f"📁 Diretório de plugins: {bot.plugin_manager.plugins_dir}")
        
        # Tentar carregar plugins
        print("\n🔄 Carregando plugins...")
        await bot.plugin_manager.load_all_plugins()
        
        # Verificar plugins carregados
        loaded_plugins = bot.plugin_manager.get_loaded_plugins()
        print(f"\n📦 Plugins carregados: {loaded_plugins}")
        
        if loaded_plugins:
            for plugin_name in loaded_plugins:
                plugin = bot.plugin_manager.get_plugin(plugin_name)
                print(f"  - {plugin_name}: {plugin.description}")
                commands = plugin.get_commands()
                print(f"    Comandos: {list(commands.keys())}")
        else:
            print("❌ Nenhum plugin foi carregado")
    else:
        print("❌ PluginManager não foi criado")

    return bot

if __name__ == "__main__":
    bot = asyncio.run(setup_bot())
    bot.run() 