# Telegram Bot Framework

Um framework moderno e robusto para desenvolvimento de bots Telegram em Python, baseado na biblioteca `python-telegram-bot`.

## 🚀 Características

- **Arquitetura Modular**: Estrutura limpa e organizada com separação clara de responsabilidades
- **Sistema de Plugins**: Suporte a plugins para extensibilidade
- **Gerenciamento de Usuários**: Sistema completo de gerenciamento de usuários com persistência
- **Sistema de Pagamentos**: Integração com Stripe e PayPal
- **Agendamento de Tarefas**: Sistema de jobs agendados com APScheduler
- **Logging Avançado**: Sistema de logging estruturado e configurável
- **Internacionalização**: Suporte a múltiplos idiomas
- **Segurança**: Criptografia de dados sensíveis e controle de acesso
- **Testes**: Suporte completo a testes unitários e de integração

## 📋 Requisitos

- Python 3.8+
- python-telegram-bot 20.0+
- APScheduler 3.10+
- SQLAlchemy 2.0+
- Pydantic 2.0+

## 🛠️ Instalação

```bash
# Clone o repositório
git clone <repository-url>
cd telegram-bot-framework

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

## 🏗️ Estrutura do Projeto

```
new_framework_cursor/
├── src/
│   ├── tlgfwk/
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── framework.py
│   │   │   ├── config.py
│   │   │   ├── decorators.py
│   │   │   ├── user_manager.py
│   │   │   ├── persistence_manager.py
│   │   │   ├── payment_manager.py
│   │   │   ├── plugin_manager.py
│   │   │   └── scheduler.py
│   │   ├── plugins/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── system_monitor.py
│   │   │   └── user_stats.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── logger.py
│   │       ├── crypto.py
│   │       └── formatters.py
│   └── __init__.py
├── examples/
│   ├── __init__.py
│   ├── echo_bot.py
│   ├── advanced_bot.py
│   └── README.md
├── tests/
│   ├── __init__.py
│   ├── test_framework.py
│   ├── test_plugins.py
│   └── test_utils.py
├── docs/
│   ├── api.md
│   ├── plugins.md
│   └── deployment.md
├── requirements.txt
├── setup.py
├── .env.example
├── .gitignore
└── README.md
```

## 🚀 Uso Rápido

```python
from tlgfwk import TelegramBotFramework

class MyBot(TelegramBotFramework):
    async def start_command(self, update, context):
        await update.message.reply_text("Olá! Bem-vindo ao meu bot!")
    
    async def echo_command(self, update, context):
        text = ' '.join(context.args)
        await update.message.reply_text(f"Você disse: {text}")

if __name__ == "__main__":
    bot = MyBot()
    bot.run()
```

## 📚 Documentação

- [Guia de Início Rápido](docs/quickstart.md)
- [API Reference](docs/api.md)
- [Sistema de Plugins](docs/plugins.md)
- [Guia de Deployment](docs/deployment.md)

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

Se você encontrar algum problema ou tiver dúvidas, por favor abra uma issue no GitHub.

## 🔄 Changelog

Veja o arquivo [CHANGELOG.md](CHANGELOG.md) para informações sobre as versões. 