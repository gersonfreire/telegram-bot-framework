import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from tlgfwk.core import TelegramBotFramework

class PluginBot(TelegramBotFramework):
    def __init__(self, config_file=None):
        # Aponta plugins_dir para a pasta examples
        plugins_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "./")
        super().__init__(config_file=config_file, plugins_dir=plugins_dir)
        
        # Definir configurações de plugins
        self.config.data['auto_load_plugins'] = True

if __name__ == "__main__":
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    print("Starting PluginBot with HelloPlugin...")
    bot = PluginBot(config_file=env_path)
    bot.run() 