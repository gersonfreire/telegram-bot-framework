# main.py
import os


try:
    from plugin_manager import PluginManager
except ImportError as e:
    print(f"Failed to import PluginManager: {str(e)}")
    from .plugin_manager import PluginManager

def main():
    try:
        
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
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    
    main()   
    
    
    