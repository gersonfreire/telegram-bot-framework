try:
    from src.tlgfwk.plugins.base import PluginBase
    from src.tlgfwk.core.decorators import command
except ImportError:
    # Fallback para quando executado diretamente
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    from tlgfwk.plugins.base import PluginBase
    from tlgfwk.core.decorators import command

class HelloPlugin(PluginBase):
    name = "HelloPlugin"
    version = "1.0"
    description = "Um plugin de exemplo que responde /hello"
    author = "Exemplo"

    def __init__(self):
        super().__init__()
        print(f"[DEBUG] HelloPlugin.__init__() chamado")
        self.register_command({
            "name": "hello",
            "handler": self.hello_command,
            "description": "Diz olá!"
        })
        print(f"[DEBUG] Comando 'hello' registrado no plugin")

    async def on_load(self):
        """Chamado quando o plugin é carregado."""
        print(f"[DEBUG] HelloPlugin.on_load() chamado")
        print(f"[DEBUG] Framework disponível: {self.framework is not None}")
        if self.framework:
            print(f"[DEBUG] Application disponível: {hasattr(self.framework, 'application')}")
        print(f"Plugin {self.name} carregado com sucesso!")

    async def on_unload(self):
        """Chamado quando o plugin é descarregado."""
        print(f"Plugin {self.name} descarregado!")

    async def hello_command(self, update, context):
        """Handler para o comando /hello"""
        print(f"[DEBUG] hello_command() chamado!")
        await update.message.reply_text("Olá do plugin!") 