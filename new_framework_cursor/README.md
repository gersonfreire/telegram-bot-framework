# Telegram Bot Framework (Modern)

A modern, extensible Python framework for building Telegram bots with user management, plugins, payments, persistence, and more.

## Features  

- User registration and permissions (admin/owner)
- Command system with decorators and help
- Plugin system with hot-reload
- Persistent storage (SQLite, pickle, etc.)
- Payment integration (Stripe, PayPal)
- Job scheduling (APScheduler)
- Secure config via .env and encryption
- Admin notifications and logging
- Fully async, type-annotated, and tested

## Installation

```bash
pip install -e .
```

## Quick Start

1. Copy `.env.example` to `.env` and fill in your bot token and user IDs.
2. Run an example bot:

```bash
cd examples
python echo_bot.py
```

## Documentação

- [Guia do Usuário](docs/user_guide.md)
- [Guia do Administrador](docs/admin_guide.md)
- [Guia de Plugins](docs/plugins.md)
- [Guia de Configuração](docs/configuration.md)
- [Funcionalidades do Framework](docs/features.md)

## API Reference

- [API Reference](docs/api_reference.md)
- [Payments](docs/payments.md)
- [Examples](examples/)

## Testing

```bash
pytest --cov=src/tlgfwk
```

## License

MIT
