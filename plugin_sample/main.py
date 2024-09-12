# main.py
from plugin_manager import PluginManager

if __name__ == "__main__":
    manager = PluginManager("plugins")
    manager.load_plugins()
    manager.execute_plugins()