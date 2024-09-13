# main.py
import os
from plugin_manager import PluginManager

if __name__ == "__main__":
    # get current script folder
    script_dir = os.path.dirname(os.path.realpath(__file__))    
    # Concatenate current script folder with plugins folder
    plugins_dir = os.path.join(script_dir, "plugins")
    
    # Create PluginManager object
    manager = PluginManager(plugins_dir)
    manager.load_plugins()
    manager.execute_plugins()