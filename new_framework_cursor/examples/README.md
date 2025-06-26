# Examples

[...TRUNCATED: Copy the full content from new_framework/examples/README.md here for reference...]

# Exemplo de Plugin com o Framework Cursor

## Como rodar o PluginBot

1. Certifique-se de ter um arquivo `.env` com o token do bot Telegram na pasta `examples`.
2. Execute o bot de exemplo com:

```bash
python plugin_bot.py
```

## O que faz o HelloPlugin?

- O `HelloPlugin` é carregado automaticamente pelo `PluginBot`.
- Ele adiciona o comando `/hello` ao bot.
- Ao enviar `/hello` para o bot, ele responde com:

```
Olá do plugin!
``` 