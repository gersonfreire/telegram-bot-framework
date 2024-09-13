# main.py
import os
from .plugin_manager import PluginManager

if __name__ == "__main__":
    
    # get current script folder
    script_dir = os.path.dirname(os.path.realpath(__file__)) 
       
    # Concatenate current script folder with plugins folder
    plugins_dir = os.path.join(script_dir, "plugins")
    
    # Create PluginManager object
    manager = PluginManager(plugins_dir)
    manager.load_plugins()
    
    # execute all plugins
    manager.execute_plugins()
    
    # execute plugin by name
    manager.execute_plugin_by_name("ExamplePlugin", "execute_message", "Hello World!")    
    
    
    