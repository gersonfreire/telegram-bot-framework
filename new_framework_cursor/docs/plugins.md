# Guia de Plugins

O framework suporta plugins dinâmicos para estender funcionalidades do bot.

## Estrutura de Plugins

- Plugins devem herdar de `PluginBase` (`from tlgfwk.plugins import PluginBase`).
- Devem implementar os métodos `on_load` e `on_unload`.
- Devem registrar comandos via `register_command`.

## Diretório de Plugins

- Os plugins devem ser colocados no diretório configurado (ex: `plugins/`).
- O framework carrega todos os arquivos `.py` desse diretório ao iniciar.

## Comandos de Gerenciamento

- `/plugins` — Lista plugins carregados.
- `/plugin reload <nome>` — Recarrega um plugin.
- `/plugin enable <nome>` — Habilita um plugin.
- `/plugin disable <nome>` — Desabilita um plugin.
- `/plugin info <nome>` — Mostra informações detalhadas de um plugin.

## Exemplo de Plugin

```python
from tlgfwk.plugins import PluginBase

class HelloPlugin(PluginBase):
    name = "HelloPlugin"
    version = "1.0"
    description = "Exemplo de plugin."
    author = "Seu Nome"

    async def on_load(self):
        self.register_command({
            "name": "hello",
            "handler": self.hello_command,
            "description": "Diz olá!"
        })

    async def on_unload(self):
        pass

    async def hello_command(self, update, context):
        await update.message.reply_text("Olá do plugin!")
```

Coloque o arquivo no diretório de plugins e use `/plugin reload HelloPlugin` para recarregar. 