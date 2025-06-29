# 🤖 Demo Bot - Framework Completo

Este é um bot de demonstração completo que implementa todas as funcionalidades disponíveis no **Telegram Bot Framework**. O bot serve como exemplo prático e guia de referência para desenvolvedores que querem entender e usar o framework.

## 📋 Índice

- [Funcionalidades Demonstradas](#funcionalidades-demonstradas)
- [Configuração Inicial](#configuração-inicial)
- [Comandos Disponíveis](#comandos-disponíveis)
- [Sistema de Permissões](#sistema-de-permissões)
- [Sistema de Plugins](#sistema-de-plugins)
- [Utilitários de Criptografia](#utilitários-de-criptografia)
- [Estrutura do Código](#estrutura-do-código)
- [Como Executar](#como-executar)
- [Troubleshooting](#troubleshooting)

## 🎯 Funcionalidades Demonstradas

### ✅ Sistema de Comandos Avançado
- Decoradores para registro automático de comandos
- Sistema de aliases e categorias
- Validação de argumentos
- Rate limiting e controle de acesso
- Logging automático de comandos

### ✅ Controle de Permissões
- Níveis de acesso: Usuário, Admin, Owner
- Decoradores para controle de permissões
- Sistema de verificação automática
- Mensagens de erro personalizadas

### ✅ Gerenciamento de Usuários
- Registro automático de usuários
- Persistência de dados
- Controle de permissões dinâmico
- Estatísticas de uso

### ✅ Sistema de Plugins
- Carregamento dinâmico de plugins
- Isolamento de código
- Comandos customizados por plugin
- Sistema de dependências

### ✅ Criptografia e Segurança
- Geração de chaves seguras
- Criptografia de dados sensíveis
- Proteção de configurações
- Tokens seguros

### ✅ Estatísticas e Monitoramento
- Coleta automática de métricas
- Relatórios em tempo real
- Monitoramento de performance
- Logs estruturados

### ✅ Configurações Flexíveis
- Carregamento de variáveis de ambiente
- Validação automática
- Configurações por linguagem
- Backup automático

## ⚙️ Configuração Inicial

### 1. Criar Arquivo de Configuração

Crie um arquivo `.env` na pasta `new_framework/examples/` com o seguinte conteúdo:

```env
# Configurações Obrigatórias
BOT_TOKEN=seu_token_do_bot_aqui
OWNER_USER_ID=seu_id_de_usuario_aqui

# Configurações Opcionais
ADMIN_USER_IDS=id1,id2,id3
LOG_CHAT_ID=chat_id_para_logs
DEBUG=true
INSTANCE_NAME=DemoBot

# Configurações Avançadas
PERSISTENCE_BACKEND=sqlite
PLUGINS_DIR=./plugins
AUTO_LOAD_PLUGINS=true
REUSE_CONNECTIONS=true
USE_ASYNC=true
MAX_WORKERS=4
```

### 2. Obter Token do Bot

1. Fale com [@BotFather](https://t.me/BotFather) no Telegram
2. Use o comando `/newbot`
3. Siga as instruções para criar seu bot
4. Copie o token fornecido para o arquivo `.env`

### 3. Obter IDs de Usuário

Para obter seu ID de usuário:
1. Fale com [@userinfobot](https://t.me/userinfobot)
2. Ele retornará seu ID
3. Use esse ID como `OWNER_USER_ID` e `ADMIN_USER_IDS`

## 📚 Comandos Disponíveis

### 🎯 Comandos Principais

| Comando | Descrição | Permissão |
|---------|-----------|-----------|
| `/start` | Iniciar o bot e mostrar boas-vindas | Todos |
| `/demo` | Menu principal de demonstração | Todos |
| `/help` | Mostrar ajuda completa | Todos |
| `/info` | Informações detalhadas do bot | Todos |
| `/welcome` | Boas-vindas personalizadas | Todos |

### 🛡️ Comandos de Permissões

| Comando | Descrição | Permissão |
|---------|-----------|-----------|
| `/admin_test` | Teste de permissões de admin | Admin |
| `/owner_test` | Teste de permissões de owner | Owner |
| `/permission_denied` | Demo de acesso negado | Admin |

### 👥 Comandos de Usuários

| Comando | Descrição | Permissão |
|---------|-----------|-----------|
| `/user_info` | Informações do usuário atual | Todos |
| `/add_admin` | Adicionar usuário como admin | Owner |
| `/users` | Listar todos os usuários | Admin |

### 🔌 Comandos de Plugins

| Comando | Descrição | Permissão |
|---------|-----------|-----------|
| `/plugin_demo` | Demonstração do plugin | Todos |
| `/plugin_info` | Informações do plugin | Todos |
| `/plugins` | Listar plugins carregados | Admin |
| `/plugin` | Gerenciar plugins | Admin |

### 🔐 Comandos de Criptografia

| Comando | Descrição | Permissão |
|---------|-----------|-----------|
| `/crypto_demo` | Demonstração de criptografia | Todos |

### 📊 Comandos de Estatísticas

| Comando | Descrição | Permissão |
|---------|-----------|-----------|
| `/demo_stats` | Estatísticas do demo bot | Todos |
| `/stats` | Estatísticas do sistema | Admin |

### ⚙️ Comandos de Configuração

| Comando | Descrição | Permissão |
|---------|-----------|-----------|
| `/demo_config` | Configurações do demo | Admin |
| `/config` | Configurações do sistema | Admin |

### 🔧 Comandos Avançados

| Comando | Descrição | Permissão |
|---------|-----------|-----------|
| `/broadcast_demo` | Demonstração de broadcast | Admin |
| `/test_error` | Teste de tratamento de erros | Todos |

## 🔐 Sistema de Permissões

O framework implementa um sistema hierárquico de permissões:

### 👤 Usuário (Nível 1)
- Acesso a comandos básicos
- Visualização de informações públicas
- Uso de funcionalidades gerais

### 🛡️ Admin (Nível 2)
- Todas as permissões de usuário
- Gerenciamento de usuários
- Configurações do sistema
- Estatísticas detalhadas
- Controle de plugins

### 👑 Owner (Nível 3)
- Todas as permissões de admin
- Reiniciar/desligar o bot
- Configurações críticas
- Gerenciamento de admins
- Acesso total ao sistema

### Como Usar Decoradores

```python
from tlgfwk import command, admin_required, owner_required

@command(name="meu_comando", description="Descrição do comando")
async def meu_comando(self, update, context):
    """Comando disponível para todos os usuários."""
    pass

@command(name="comando_admin", description="Comando administrativo")
@admin_required
async def comando_admin(self, update, context):
    """Comando disponível apenas para admins."""
    pass

@command(name="comando_owner", description="Comando do proprietário")
@owner_required
async def comando_owner(self, update, context):
    """Comando disponível apenas para o owner."""
    pass
```

## 🔌 Sistema de Plugins

O framework suporta plugins modulares que podem ser carregados dinamicamente.

### Estrutura de um Plugin

```python
from tlgfwk import PluginBase

class MeuPlugin(PluginBase):
    name = "MeuPlugin"
    version = "1.0.0"
    description = "Descrição do plugin"

    async def initialize(self, framework, config):
        """Inicializar o plugin."""
        await super().initialize(framework, config)
        # Seu código de inicialização
        return True

    async def start(self):
        """Iniciar o plugin."""
        result = await super().start()
        # Seu código de inicialização
        return result

    async def stop(self):
        """Parar o plugin."""
        result = await super().stop()
        # Seu código de limpeza
        return result
```

### Comandos de Plugin

```python
# Registrar comando do plugin
self.register_command({
    "name": "comando_plugin",
    "handler": self.meu_comando,
    "description": "Descrição do comando"
})

async def meu_comando(self, update, context):
    """Comando do plugin."""
    await update.message.reply_text("Comando do plugin!")
```

## 🔐 Utilitários de Criptografia

O framework fornece utilitários completos de criptografia:

### Geração de Chaves

```python
from tlgfwk import generate_encryption_key, create_secure_token

# Gerar chave de criptografia
key = generate_encryption_key()

# Gerar token seguro
token = create_secure_token(length=32)
```

### Criptografia de Dados

```python
from tlgfwk import CryptoUtils

# Inicializar utilitário de criptografia
crypto = CryptoUtils(key)

# Criptografar texto
encrypted = crypto.encrypt_string("Texto secreto")

# Descriptografar texto
decrypted = crypto.decrypt_string(encrypted)

# Criptografar dicionário
data = {"user": "admin", "password": "secret"}
encrypted_data = crypto.encrypt_dict(data)

# Descriptografar dicionário
decrypted_data = crypto.decrypt_dict(encrypted_data)
```

### Hash de Senhas

```python
# Hash de senha
hashed_password, salt = CryptoUtils.hash_password("minha_senha")

# Verificar senha
is_valid = CryptoUtils.verify_password("minha_senha", hashed_password, salt)
```

## 🏗️ Estrutura do Código

### Classe Principal

```python
class DemoBot(TelegramBotFramework):
    def __init__(self, config_file=None):
        super().__init__(config_file=config_file)
        # Configurações específicas do demo
        self.demo_stats = {
            'commands_executed': 0,
            'users_interacted': set(),
            'start_time': datetime.now()
        }
```

### Registro de Comandos

```python
@command(name="demo", description="Menu principal de demonstração")
async def demo_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menu principal de demonstração."""
    # Implementação do comando
    pass
```

### Handlers de Callback

```python
async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manipular callbacks dos botões inline."""
    query = update.callback_query
    await query.answer()

    if query.data == "demo_basic":
        await self._show_basic_commands(query)
    # ... outros callbacks
```

## 🚀 Como Executar

### 1. Instalar Dependências

```bash
pip install -r new_framework/requirements.txt
```

### 2. Configurar Ambiente

```bash
cd new_framework/examples
cp .env.example .env
# Editar .env com suas configurações
```

### 3. Executar o Bot

```bash
python demo_bot.py
```

### 4. Testar no Telegram

1. Procure seu bot no Telegram
2. Envie `/start` para iniciar
3. Use `/demo` para acessar o menu interativo
4. Explore todas as funcionalidades

## 🔧 Troubleshooting

### Erro: "Bot token not found"
- Verifique se o arquivo `.env` existe
- Confirme se `BOT_TOKEN` está definido corretamente
- Certifique-se de que o token é válido

### Erro: "Owner user ID not found"
- Verifique se `OWNER_USER_ID` está definido no `.env`
- Confirme se o ID é um número válido
- Use [@userinfobot](https://t.me/userinfobot) para obter seu ID

### Erro: "Module not found"
- Verifique se todas as dependências estão instaladas
- Confirme se está executando do diretório correto
- Verifique se o path do Python está configurado

### Bot não responde
- Verifique se o bot está rodando
- Confirme se o token está correto
- Verifique os logs para erros
- Certifique-se de que o bot não foi bloqueado

### Comandos não funcionam
- Verifique se você tem as permissões necessárias
- Confirme se o comando está registrado corretamente
- Verifique os logs para erros de sintaxe

## 📖 Exemplos de Uso

### Criar um Comando Simples

```python
@command(name="hello", description="Comando de saudação")
async def hello_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"Olá, {user.first_name}!")
```

### Criar um Comando com Argumentos

```python
@command(name="echo", description="Repetir mensagem")
async def echo_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Uso: /echo <mensagem>")
        return

    message = " ".join(context.args)
    await update.message.reply_text(f"Você disse: {message}")
```

### Criar um Comando com Botões

```python
@command(name="menu", description="Menu com botões")
async def menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Opção 1", callback_data="option1")],
        [InlineKeyboardButton("Opção 2", callback_data="option2")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Escolha uma opção:",
        reply_markup=reply_markup
    )
```

## 🤝 Contribuindo

Para contribuir com melhorias no bot de demonstração:

1. Fork o repositório
2. Crie uma branch para sua feature
3. Implemente suas mudanças
4. Adicione testes se necessário
5. Envie um pull request

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](../LICENSE) para detalhes.

## 🆘 Suporte

Se você encontrar problemas ou tiver dúvidas:

1. Verifique a documentação do framework
2. Consulte os exemplos existentes
3. Abra uma issue no repositório
4. Entre em contato com a comunidade

---

**🎉 Agora você está pronto para explorar todas as funcionalidades do Telegram Bot Framework!**
