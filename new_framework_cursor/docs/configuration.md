# Guia de Configuração

O framework utiliza um arquivo `.env` para configuração segura.

## Variáveis Principais

- `BOT_TOKEN` — Token do bot Telegram (obrigatório)
- `OWNER_USER_ID` — ID do proprietário do bot (obrigatório)
- `ADMIN_USER_IDS` — IDs dos administradores, separados por vírgula
- `LOG_CHAT_ID` — Chat ID para logs administrativos (opcional)
- `DEBUG` — Ativa modo debug (`true` ou `false`)
- `PERSISTENCE_BACKEND` — Backend de persistência (atualmente não implementado)
- `PLUGINS_DIR` — Diretório dos plugins
- `AUTO_LOAD_PLUGINS` — Carregar plugins automaticamente (`true` ou `false`)

## Exemplo de .env

```
BOT_TOKEN=123456:ABC-DEF...
OWNER_USER_ID=123456789
ADMIN_USER_IDS=987654321,1122334455
LOG_CHAT_ID=-1001234567890
DEBUG=true
PERSISTENCE_BACKEND=sqlite
PLUGINS_DIR=plugins
AUTO_LOAD_PLUGINS=true
```

## Criptografia de Valores Sensíveis

- O framework suporta criptografia de valores usando Fernet.
- Use utilitários em `tlgfwk.utils.crypto` para gerar chaves e criptografar valores.
- Para usar valores criptografados, configure a chave de criptografia no código.

## Observações

- Sempre proteja seu arquivo `.env` e nunca compartilhe seu token do bot.
- Consulte o código-fonte para detalhes sobre métodos de criptografia. 