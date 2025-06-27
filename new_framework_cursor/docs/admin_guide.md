# Guia do Administrador

Este guia é destinado a administradores e proprietários de bots criados com o Telegram Bot Framework.

## Permissões

- **Owner:** Definido por `OWNER_USER_ID` no `.env`. Tem acesso total.
- **Admin:** Definido por `ADMIN_USER_IDS` no `.env`. Tem acesso a comandos administrativos.

## Comandos Administrativos

- `/config` — Mostra a configuração atual do bot.
- `/stats` — Mostra estatísticas de uso do bot.
- `/users` — Lista todos os usuários registrados.
- `/restart` — Reinicia o bot (apenas owner).
- `/shutdown` — Desliga o bot (apenas owner).

## Gerenciamento de Plugins

- `/plugins` — Lista todos os plugins carregados.
- `/plugin reload <nome>` — Recarrega um plugin.
- `/plugin enable <nome>` — Habilita um plugin.
- `/plugin disable <nome>` — Desabilita um plugin.
- `/plugin info <nome>` — Mostra informações detalhadas de um plugin.

## Logs e Notificações

- Logs são salvos em `logs/bot.log`.
- Notificações administrativas (ex: novo usuário, erro) são enviadas automaticamente para admins.
- Erros críticos podem ser enviados para um chat específico via `LOG_CHAT_ID` ou `TRACEBACK_CHAT_ID` no `.env`.

## Observações

- Para alterar permissões, edite o arquivo `.env` e reinicie o bot.
- Consulte a documentação de configuração para detalhes sobre variáveis de ambiente e segurança. 