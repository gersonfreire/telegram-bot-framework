from src.tlgfwk.plugins.base import PluginBase
from src.tlgfwk.core.decorators import command

class HelloPlugin(PluginBase):
    name = "HelloPlugin"
    version = "1.0"
    description = "Um plugin de exemplo que responde /hello"
    author = "Exemplo"

    def __init__(self):
        super().__init__()
        self.register_command({
            "name": "hello",
            "handler": self.hello_command,
            "description": "Diz olá!"
        })

    @command(name="hello", description="Diz olá!")
    async def hello_command(self, update, context):
        await update.message.reply_text("Olá do plugin!") 