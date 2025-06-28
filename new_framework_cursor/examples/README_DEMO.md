# Demo Bot - Demonstração Completa do Framework

## 📋 Visão Geral

O `demo_bot.py` é um script de demonstração completo que mostra todas as funcionalidades disponíveis no **Telegram Bot Framework**. Este bot serve como um exemplo prático e educativo de como utilizar o framework em um projeto real.

## 🎯 Funcionalidades Demonstradas

### 🔧 Comandos Básicos
- **Sistema de comandos com decoradores** (`@command`)
- **Tratamento automático de erros**
- **Logging integrado**
- **Notificações administrativas**

### 🛡️ Sistema de Permissões
- **Controle de acesso por níveis** (Usuário, Admin, Owner)
- **Decoradores de permissão** (`@admin_required`, `@owner_required`)
- **Testes de permissões** com feedback visual

### 👥 Gerenciamento de Usuários
- **Registro automático de usuários**
- **Controle de permissões**
- **Persistência de dados**
- **Estatísticas de uso**

### 🔌 Sistema de Plugins
- **Carregamento dinâmico de plugins**
- **Comandos customizados por plugin**
- **Isolamento de código**
- **Integração com framework**

### 🔐 Utilitários de Criptografia
- **Geração de chaves seguras**
- **Criptografia/descriptografia de dados**
- **Proteção de configurações sensíveis**

### 📊 Estatísticas e Monitoramento
- **Coleta automática de métricas**
- **Relatórios em tempo real**
- **Monitoramento de performance**

### ⚙️ Configurações Avançadas
- **Carregamento de variáveis de ambiente**
- **Validação automática**
- **Configurações dinâmicas**

## 🚀 Como Executar

### 1. Preparação do Ambiente

```bash
# Navegar para o diretório do framework
cd new_framework_cursor

# Instalar dependências (se necessário)
pip install -r requirements.txt
```

### 2. Configuração

Crie um arquivo `.env` no diretório `examples/` com as seguintes variáveis:

```env
# Token do bot (obrigatório)
BOT_TOKEN=seu_token_do_bot_aqui

# ID do proprietário (obrigatório)
OWNER_USER_ID=seu_id_de_usuario_aqui

# IDs dos administradores (opcional)
ADMIN_USER_IDS=id1,id2,id3

# Chat ID para logs (opcional)
LOG_CHAT_ID=chat_id_para_logs

# Modo debug (opcional, padrão: true)
DEBUG=true

# Nome da instância (opcional, padrão: TelegramBot)
INSTANCE_NAME=DemoBot

# Persistência (opcional, padrão: none)
PERSISTENCE_BACKEND=json

# Auto-carregamento de plugins (opcional, padrão: true)
AUTO_LOAD_PLUGINS=true
```

### 3. Execução

```bash
# Navegar para o diretório examples
cd examples

# Executar o demo bot
python demo_bot.py
```

## 📱 Comandos Disponíveis

### 🎯 Comandos Principais
- `/start` - Iniciar o bot
- `/demo` - Menu principal de demonstração (interativo)
- `/help` - Lista completa de comandos
- `/info` - Informações detalhadas do bot
- `/welcome` - Boas-vindas personalizadas

### 🛡️ Comandos de Permissões
- `/admin_test` - Teste de permissões de admin
- `/owner_test` - Teste de permissões de owner
- `/permission_denied` - Demonstração de acesso negado

### 👥 Comandos de Usuários
- `/user_info` - Informações do usuário atual
- `/add_admin` - Adicionar usuário como admin (apenas owner)

### 🔌 Comandos de Plugins
- `/plugin_demo` - Demonstração do plugin
- `/plugin_info` - Informações do plugin
- `/plugins` - Listar plugins carregados
- `/plugin` - Gerenciar plugin específico

### 🔐 Comandos de Criptografia
- `/crypto_demo` - Demonstração completa de criptografia

### 📊 Comandos de Estatísticas
- `/demo_stats` - Estatísticas detalhadas do demo
- `/stats` - Estatísticas do sistema

### ⚙️ Comandos de Configuração
- `/demo_config` - Configurações do demo bot
- `/config` - Configurações do sistema

### 🔧 Comandos Avançados
- `/broadcast_demo` - Demonstração de broadcast (apenas admin)
- `/test_error` - Teste de tratamento de erros

## 🎮 Menu Interativo

O comando `/demo` apresenta um menu interativo com botões inline que permite explorar todas as funcionalidades de forma organizada:

- 🔧 **Comandos Básicos** - Visão geral dos comandos fundamentais
- 🛡️ **Sistema de Permissões** - Explicação dos níveis de acesso
- 👥 **Gerenciamento de Usuários** - Funcionalidades de usuários
- 🔌 **Sistema de Plugins** - Informações sobre plugins
- 🔐 **Utilitários de Criptografia** - Recursos de segurança
- 📊 **Estatísticas** - Métricas e monitoramento
- ⚙️ **Configurações** - Sistema de configuração

## 🔌 Plugin de Demonstração

O demo inclui um plugin chamado `DemoPlugin` que demonstra:

- **Carregamento automático** de plugins
- **Comandos customizados** (`/plugin_demo`, `/plugin_info`)
- **Integração** com o framework
- **Notificações** administrativas

## 📊 Estatísticas Coletadas

O bot coleta automaticamente:

- **Tempo de execução** (uptime)
- **Número de comandos** executados
- **Usuários únicos** que interagiram
- **Média de comandos** por usuário
- **Status dos plugins** (carregados/ativos)
- **Estado do sistema** (persistência, debug, etc.)

## 🛠️ Estrutura do Código

### Classes Principais

1. **`DemoBot`** - Classe principal que herda de `TelegramBotFramework`
   - Demonstra todas as funcionalidades do framework
   - Implementa comandos customizados
   - Gerencia estatísticas do demo

2. **`DemoPlugin`** - Plugin de demonstração
   - Herda de `PluginBase`
   - Implementa comandos específicos do plugin
   - Demonstra integração com framework

### Organização dos Comandos

Os comandos estão organizados em seções:

```python
# ============================================================================
# COMANDOS BÁSICOS DE DEMONSTRAÇÃO
# ============================================================================

# ============================================================================
# COMANDOS DE PERMISSÕES
# ============================================================================

# ============================================================================
# COMANDOS DE GERENCIAMENTO DE USUÁRIOS
# ============================================================================

# E assim por diante...
```

## 🔧 Personalização

Para personalizar o demo bot:

1. **Adicionar novos comandos** usando o decorador `@command`
2. **Criar novos plugins** herdando de `PluginBase`
3. **Modificar estatísticas** no dicionário `demo_stats`
4. **Customizar mensagens** e formatação
5. **Adicionar novas funcionalidades** específicas

## 🐛 Tratamento de Erros

O framework inclui tratamento automático de erros:

- **Captura de exceções** em comandos
- **Logging automático** de erros
- **Notificações** para administradores
- **Comando de teste** (`/test_error`) para demonstração

## 📝 Logs e Debug

Com `DEBUG=true` no `.env`, o bot fornece:

- **Logs detalhados** no console
- **Logs em arquivo** (`logs/bot.log`)
- **Notificações** no chat de logs (se configurado)
- **Informações de debug** nos comandos

## 🚨 Troubleshooting

### Problemas Comuns

1. **Erro de importação**: Verifique se o path está correto
2. **Token inválido**: Confirme o token no `.env`
3. **Permissões negadas**: Verifique se você é admin/owner
4. **Plugin não carrega**: Verifique o diretório de plugins

### Verificações

```bash
# Verificar se o arquivo .env existe
ls -la .env

# Verificar se as dependências estão instaladas
pip list | grep telegram

# Verificar logs
tail -f logs/bot.log
```

## 📚 Próximos Passos

Após explorar o demo bot:

1. **Estude o código** para entender as implementações
2. **Modifique comandos** para suas necessidades
3. **Crie seus próprios plugins** baseados no exemplo
4. **Implemente funcionalidades** específicas do seu projeto
5. **Consulte a documentação** do framework para mais detalhes

## 🤝 Contribuição

Para contribuir com melhorias no demo bot:

1. **Fork** o repositório
2. **Crie uma branch** para sua feature
3. **Implemente** as melhorias
4. **Teste** todas as funcionalidades
5. **Submeta** um pull request

---

**🎯 Este demo bot demonstra o poder e flexibilidade do Telegram Bot Framework, fornecendo uma base sólida para desenvolvimento de bots profissionais e escaláveis.** 