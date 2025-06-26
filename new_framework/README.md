# Telegram Bot Framework

Uma framework abrangente em Python para construção de bots Telegram com gerenciamento integrado de usuários, processamento de pagamentos e armazenamento persistente.

## 🚀 Funcionalidades

- **Gerenciamento de Usuários**: Registro automático, rastreamento e sistema de permissões
- **Sistema de Comandos**: Handlers automáticos, help integrado e comandos personalizados
- **Sistema de Plugins**: Extensibilidade através de plugins com hot-loading
- **Persistência**: Armazenamento automático de estado com múltiplos backends
- **Sistema de Pagamentos**: Integração com Stripe, PayPal e outros provedores
- **Agendamento**: Tarefas agendadas com APScheduler
- **Configuração**: Gerenciamento seguro via arquivos .env com criptografia
- **Notificações**: Sistema completo de notificações administrativas
- **Logging**: Sistema avançado de logs com integração Telegram

## 📦 Instalação

```bash
pip install tlgfwk
```

### Instalação para Desenvolvimento

```bash
git clone https://github.com/gersonfreire/telegram-bot-framework.git
cd telegram-bot-framework/new_framework
pip install -e ".[dev]"
```

## 🏁 Início Rápido

### 1. Configuração Básica

Crie um arquivo `.env` no diretório do seu projeto:

```env
# Configurações obrigatórias
TELEGRAM_BOT_TOKEN=seu_token_aqui
BOT_OWNER_ID=seu_user_id_aqui
ADMIN_IDS=123456789,987654321

# Configurações opcionais
DEBUG=true
LOG_CHAT_ID=seu_chat_id_para_logs
ENCRYPTION_KEY=sua_chave_de_criptografia
```

### 2. Bot Básico

```python
from tlgfwk import TelegramBotFramework

# Criar instância do bot
bot = TelegramBotFramework()

# Executar o bot
if __name__ == "__main__":
    bot.run()
```

### 3. Bot com Comandos Personalizados

```python
from tlgfwk import TelegramBotFramework
from tlgfwk.decorators import command, admin_required
from telegram import Update
from telegram.ext import ContextTypes

class MeuBot(TelegramBotFramework):
    
    @command(name="ola", description="Comando de saudação")
    async def comando_ola(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando simples de saudação."""
        await update.message.reply_text(f"Olá, {update.effective_user.first_name}!")
    
    @command(name="admin", description="Comando administrativo")
    @admin_required
    async def comando_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando disponível apenas para administradores."""
        await update.message.reply_text("Você é um administrador!")

# Executar o bot
if __name__ == "__main__":
    bot = MeuBot()
    bot.run()
```

## 🔌 Sistema de Plugins

### Criando um Plugin

```python
from tlgfwk.plugins import PluginBase
from tlgfwk.decorators import command

class MeuPlugin(PluginBase):
    """Plugin de exemplo."""
    
    name = "meu_plugin"
    version = "1.0.0"
    description = "Plugin de exemplo"
    
    @command(name="plugin_cmd", description="Comando do plugin")
    async def comando_plugin(self, update, context):
        await update.message.reply_text("Comando do plugin executado!")
    
    def on_load(self):
        """Executado quando o plugin é carregado."""
        self.logger.info("Plugin carregado com sucesso!")
    
    def on_unload(self):
        """Executado quando o plugin é descarregado."""
        self.logger.info("Plugin descarregado!")
```

### Carregando Plugins

```python
bot = TelegramBotFramework(plugins_dir="./plugins")
bot.load_plugin("meu_plugin")
```

## 💰 Sistema de Pagamentos

```python
from tlgfwk.payments import PaymentManager

class BotComPagamentos(TelegramBotFramework):
    def __init__(self):
        super().__init__()
        self.payment_manager = PaymentManager(
            stripe_key="sk_test_...",
            paypal_client_id="...",
            paypal_client_secret="..."
        )
    
    @command(name="comprar", description="Realizar compra")
    async def comando_comprar(self, update, context):
        user_id = update.effective_user.id
        amount = 1000  # R$ 10,00 em centavos
        
        payment_url = await self.payment_manager.create_payment(
            user_id=user_id,
            amount=amount,
            description="Compra de exemplo"
        )
        
        await update.message.reply_text(
            f"Clique aqui para pagar: {payment_url}"
        )
```

## 📅 Agendamento de Tarefas

```python
from tlgfwk.scheduler import schedule_task

class BotComTarefas(TelegramBotFramework):
    
    def setup_tasks(self):
        # Tarefa que executa a cada hora
        @schedule_task(interval="1h")
        async def tarefa_horaria():
            await self.send_admin_message("Relatório horário")
        
        # Tarefa que executa diariamente às 9h
        @schedule_task(cron="0 9 * * *")
        async def tarefa_diaria():
            await self.broadcast_message("Bom dia!")
```

## 🔧 Configuração Avançada

### Múltiplos Backends de Persistência

```python
bot = TelegramBotFramework(
    persistence_backend="sqlite",  # ou "pickle", "redis"
    database_url="sqlite:///bot_data.db"
)
```

### Configurações de Rede

```python
bot = TelegramBotFramework(
    network_workers=8,
    connection_pool_size=20,
    request_timeout=30
)
```

## 📚 Documentação

- [Guia do Usuário](docs/user_guide.md)
- [Referência da API](docs/api_reference.md)
- [Desenvolvimento de Plugins](docs/plugins.md)
- [Sistema de Pagamentos](docs/payments.md)
- [Exemplos](examples/)

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Executar com cobertura
pytest --cov=tlgfwk

# Executar testes específicos
pytest tests/test_core.py
```

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor, leia o [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes.

### Configuração do Ambiente de Desenvolvimento

```bash
git clone https://github.com/gersonfreire/telegram-bot-framework.git
cd telegram-bot-framework/new_framework
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
pip install -e ".[dev]"
```

### Executando Verificações de Qualidade

```bash
# Formatação de código
black src/ tests/

# Verificação de lint
flake8 src/ tests/

# Verificação de tipos
mypy src/

# Testes
pytest
```

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👥 Autores

- **Gerson Freire** - *Desenvolvimento inicial* - [@gersonfreire](https://github.com/gersonfreire)

## 🙏 Agradecimentos

- Equipe do python-telegram-bot
- Comunidade Python
- Contribuidores do projeto

## 📞 Suporte

- [Issues no GitHub](https://github.com/gersonfreire/telegram-bot-framework/issues)
- [Grupo no Telegram](https://t.me/TlgBotFwk)
- [Documentação](https://tlgfwk.readthedocs.io)
