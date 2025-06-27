# 🤖 Echo Bot - Exemplo do New Framework

Este documento explica como executar o **Echo Bot**, um exemplo prático do Telegram Bot Framework.

## 📋 Pré-requisitos

### 1. ✅ Ambiente Virtual Ativo
```bash
cd "g:\repo\tlg\telegram-bot-framework\new_framework"
.\activate.ps1  # PowerShell
# ou
activate.bat    # Command Prompt
```

### 2. 🔑 Token do Bot Telegram
1. Acesse [@BotFather](https://t.me/BotFather) no Telegram
2. Execute `/newbot` e siga as instruções
3. Guarde o token fornecido (formato: `123456789:ABCDEFghijklmnopqrstuvwxyz`)

### 3. 🆔 Seu User ID
1. Acesse [@userinfobot](https://t.me/userinfobot) no Telegram
2. Envie qualquer mensagem para obter seu User ID

## ⚙️ Configuração

### 1. Criar arquivo `.env`
```bash
# Copie o exemplo
cp .env.example .env

# Edite com seus dados reais
notepad .env
```

### 2. Preencher variáveis obrigatórias
```bash
# Telegram Bot Configuration
BOT_TOKEN=SEU_TOKEN_AQUI
OWNER_USER_ID=SEU_USER_ID_AQUI
```

### 3. Variáveis opcionais
```bash
# Admin user IDs (comma-separated)
ADMIN_USER_IDS=123456789,987654321

# Debug mode
DEBUG=true

# Bot instance name
INSTANCE_NAME=EchoBot
```

## 🚀 Executando o Bot

### Método 1: Execução direta
```bash
python examples\echo_bot.py
```

### Método 2: Verificação prévia
```bash
# Testar configuração
python test_echo_bot.py

# Executar bot se tudo estiver OK
python examples\echo_bot.py
```

## 🎯 Funcionalidades do Echo Bot

### Comandos Disponíveis:

#### `/echo <mensagem>`
- **Descrição**: Repete a mensagem enviada
- **Exemplo**: `/echo Olá mundo!`
- **Resposta**: `🔊 Echo: Olá mundo!`

#### `/reverse <mensagem>`
- **Descrição**: Inverte a mensagem enviada
- **Exemplo**: `/reverse Hello`
- **Resposta**: `🔄 Reversed: olleH`

#### `/count <mensagem>`
- **Descrição**: Conta palavras e caracteres
- **Exemplo**: `/count Esta é uma mensagem`
- **Resposta**: 
  ```
  📊 Statistics:
  Words: 4
  Characters: 20
  ```

#### **Mensagens normais**
- **Descrição**: Eco automático de mensagens não-comando
- **Exemplo**: Enviar "Oi"
- **Resposta**: `🤖 You said: Oi`

### Comandos do Framework:

#### `/start`
- Mensagem de boas-vindas
- Informações básicas do bot

#### `/help`
- Lista todos os comandos disponíveis
- Descrições de cada comando

#### `/status` (apenas admins)
- Status do bot e sistema
- Informações de uptime

## 🔧 Resolução de Problemas

### ❌ "BOT_TOKEN environment variable is required"
- **Solução**: Configure a variável `BOT_TOKEN` no arquivo `.env`

### ❌ "OWNER_USER_ID environment variable is required"
- **Solução**: Configure a variável `OWNER_USER_ID` no arquivo `.env`

### ❌ Bot não responde no Telegram
1. Verifique se o token está correto
2. Confirme que o bot não está parado no @BotFather
3. Verifique logs para erros de rede

### ❌ "Module not found"
- **Solução**: Ative o ambiente virtual primeiro:
  ```bash
  .\activate.ps1
  ```

### ❌ Comandos de admin não funcionam
- **Solução**: Configure `ADMIN_USER_IDS` no arquivo `.env`

## 📊 Logs e Monitoramento

### Localização dos Logs
```
logs/
├── bot.log         # Log principal
├── errors.log      # Apenas erros
└── debug.log       # Logs detalhados (se DEBUG=true)
```

### Verificar Logs
```bash
# Últimas 50 linhas
Get-Content logs\bot.log -Tail 50

# Monitorar em tempo real
Get-Content logs\bot.log -Wait -Tail 10
```

## 🎉 Teste de Funcionamento

### Script Automatizado
```bash
python test_echo_bot.py
```

### Teste Manual no Telegram
1. Inicie o bot: `python examples\echo_bot.py`
2. No Telegram, procure seu bot pelo username
3. Envie `/start`
4. Teste os comandos:
   - `/echo Testando`
   - `/reverse abcdef`
   - `/count Uma frase de teste`
   - Envie uma mensagem normal

## 📁 Estrutura de Arquivos

```
new_framework/
├── .env                    # Suas configurações (não versionar!)
├── .env.example           # Exemplo de configuração
├── examples/
│   ├── echo_bot.py        # Bot principal (CORRIGIDO)
│   └── echo_bot_fixed.py  # Versão alternativa
├── test_echo_bot.py       # Script de teste
└── logs/                  # Logs gerados automaticamente
```

---

## 🎯 Resultado Esperado

Quando tudo estiver funcionando corretamente, você verá:

```
🤖 Starting Echo Bot...
✅ Bot configuration loaded!
🆔 Owner ID: 123456789
👥 Admin IDs: [123456789]
🔧 Debug mode: True
🚀 Starting bot polling...
```

E no Telegram, o bot responderá a todos os comandos e mensagens conforme descrito acima!

---
*Documentação gerada em 26/06/2025 - New Framework Echo Bot*
