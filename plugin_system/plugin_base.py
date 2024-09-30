# plugin_base.py
class Plugin:
    def execute(self):
        raise NotImplementedError("Plugins must implement the execute method")