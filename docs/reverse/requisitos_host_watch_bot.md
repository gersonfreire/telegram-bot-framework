# Documento de Requisitos - Bot HostWatchBot

## 1. Visão Geral

### 1.1 Propósito
O **HostWatchBot** é um bot Telegram desenvolvido para monitoramento de hosts e serviços de rede. Ele permite aos usuários monitorar a disponibilidade de servidores, verificar portas TCP, executar comandos remotos via SSH e gerenciar credenciais de acesso.

### 1.2 Versão Atual
- **Versão**: 0.6.2 Failure History
- **Framework Base**: TlgBotFwk (Telegram Bot Framework)
- **Linguagem**: Python 3.x

### 1.3 Arquitetura
O bot é construído sobre o framework `TlgBotFwk` que fornece funcionalidades base como:
- Persistência de dados
- Sistema de comandos
- Gerenciamento de usuários
- Sistema de agendamento de tarefas
- Tratamento de erros

## 2. Requisitos Funcionais

### 2.1 Monitoramento de Hosts

#### RF001 - Adicionar Host para Monitoramento
- **Comando**: `/pingadd <ip_address> <interval_in_seconds> [port]`
- **Descrição**: Adiciona um novo host à lista de monitoramento
- **Parâmetros**:
  - `ip_address`: Endereço IP ou nome do host
  - `interval_in_seconds`: Intervalo de verificação em segundos (120-2400)
  - `port`: Porta TCP para verificação (opcional, padrão: 80)
- **Comportamento**:
  - Cria um job agendado para verificação periódica
  - Armazena configurações na persistência
  - Permite apenas um job por host por usuário

#### RF002 - Remover Host do Monitoramento
- **Comando**: `/pingdelete <ip_address>`
- **Descrição**: Remove um host da lista de monitoramento
- **Parâmetros**:
  - `ip_address`: Endereço IP ou nome do host
- **Comportamento**:
  - Remove o job agendado
  - Limpa dados da persistência

#### RF003 - Listar Hosts Monitorados
- **Comando**: `/pinglist [all]`
- **Descrição**: Lista todos os hosts monitorados
- **Parâmetros**:
  - `all`: Lista hosts de todos os usuários (apenas admin)
- **Comportamento**:
  - Mostra status de ping, porta, intervalo, próximo check
  - Formatação em tabela com markdown
  - Links clicáveis para os hosts
  - Limite de 50 hosts por listagem

#### RF004 - Alterar Intervalo de Monitoramento
- **Comando**: `/pinginterval <host_name> <new_interval_in_seconds>`
- **Descrição**: Altera o intervalo de verificação de um host
- **Parâmetros**:
  - `host_name`: Nome ou IP do host
  - `new_interval_in_seconds`: Novo intervalo em segundos
- **Comportamento**:
  - Remove job existente
  - Cria novo job com intervalo atualizado
  - Atualiza persistência

#### RF005 - Alterar Porta de Verificação
- **Comando**: `/changepingport <host_name_or_ip> <new_port_number>`
- **Descrição**: Altera a porta TCP verificada pelo monitoramento
- **Parâmetros**:
  - `host_name_or_ip`: Nome ou IP do host
  - `new_port_number`: Nova porta TCP
- **Comportamento**:
  - Atualiza configuração na persistência
  - Aplica na próxima verificação

### 2.2 Verificação Manual

#### RF006 - Ping Manual de Host
- **Comando**: `/pinghost <host_name>`
- **Descrição**: Executa verificação manual de um host
- **Parâmetros**:
  - `host_name`: Nome ou IP do host
- **Comportamento**:
  - Executa ping ICMP
  - Retorna status up/down

#### RF007 - Verificação de Porta TCP
- **Comando**: `/pinghostport <host_name_or_ip> <port_number>`
- **Descrição**: Verifica se uma porta TCP está aberta
- **Parâmetros**:
  - `host_name_or_ip`: Nome ou IP do host
  - `port_number`: Número da porta TCP
- **Comportamento**:
  - Tenta conexão TCP na porta especificada
  - Timeout de 1 segundo
  - Retorna status aberta/fechada

### 2.3 Gerenciamento de Credenciais

#### RF008 - Armazenar Credenciais SSH
- **Comando**: `/storecredentials <host_name_or_ip> <username> <password> [port=22]`
- **Descrição**: Armazena credenciais SSH para um host
- **Parâmetros**:
  - `host_name_or_ip`: Nome ou IP do host
  - `username`: Nome de usuário SSH
  - `password`: Senha SSH
  - `port`: Porta SSH (opcional, padrão: 22)
- **Comportamento**:
  - Armazena credenciais criptografadas na persistência
  - Associa credenciais ao host monitorado

#### RF009 - Consultar Credenciais Armazenadas
- **Comando**: `/storecredentials <host_name>`
- **Descrição**: Exibe credenciais armazenadas para um host
- **Parâmetros**:
  - `host_name`: Nome ou IP do host
- **Comportamento**:
  - Mostra username, password e porta armazenados
  - Apenas para hosts monitorados

### 2.4 Execução de Comandos

#### RF010 - Executar Comando Local
- **Comando**: `/exec <command>`
- **Descrição**: Executa comando no sistema operacional local
- **Parâmetros**:
  - `command`: Comando a ser executado
- **Restrições**: Apenas usuários admin
- **Comportamento**:
  - Executa comando via subprocess
  - Retorna stdout/stderr
  - Escape de caracteres markdown

#### RF011 - Executar Comando SSH
- **Comando**: `/ssh <host_name_or_ip> <command>`
- **Descrição**: Executa comando via SSH em host remoto
- **Parâmetros**:
  - `host_name_or_ip`: Nome ou IP do host
  - `command`: Comando SSH a ser executado
- **Restrições**: Apenas usuários admin
- **Comportamento**:
  - Usa credenciais armazenadas
  - Conecta via SSH
  - Executa comando remoto
  - Retorna resultado

### 2.5 Relatórios e Logs

#### RF012 - Listar Falhas
- **Comando**: `/listfailures`
- **Descrição**: Lista hosts e suas últimas falhas
- **Comportamento**:
  - Mostra data/hora da última falha por host
  - Formatação em tabela
  - "No failures" para hosts sem falhas

#### RF013 - Controle de Log de Monitoramento
- **Comando**: `/pinglog`
- **Descrição**: Ativa/desativa logs detalhados de monitoramento
- **Comportamento**:
  - Toggle do flag show_success
  - Controla mensagens de debug durante ping
  - Persiste configuração por usuário

### 2.6 Monitoramento Automático

#### RF014 - Job de Monitoramento
- **Descrição**: Execução automática de verificações
- **Comportamento**:
  - Executa ping ICMP do host
  - Verifica porta TCP configurada
  - Atualiza status na persistência
  - Registra data/hora de falhas
  - Envia notificação em caso de falha
  - Suporte a logs detalhados

#### RF015 - Restauração de Jobs
- **Descrição**: Restaura jobs ao inicializar bot
- **Comportamento**:
  - Carrega configurações da persistência
  - Recria jobs agendados
  - Notifica admin sobre restauração
  - Trata erros de restauração

## 3. Requisitos Não Funcionais

### 3.1 Performance
- **RNF001**: Timeout de 1 segundo para verificações de porta
- **RNF002**: Limite de 50 hosts por listagem
- **RNF003**: Intervalo mínimo de 120 segundos entre verificações
- **RNF004**: Intervalo máximo de 2400 segundos entre verificações

### 3.2 Segurança
- **RNF005**: Comandos de execução restritos a admins
- **RNF006**: Credenciais armazenadas com criptografia
- **RNF007**: Isolamento de dados por usuário
- **RNF008**: Validação de parâmetros de entrada

### 3.3 Confiabilidade
- **RNF009**: Persistência automática de dados
- **RNF010**: Tratamento de erros em todas as operações
- **RNF011**: Logs detalhados para debugging
- **RNF012**: Restauração automática de jobs

### 3.4 Usabilidade
- **RNF013**: Mensagens formatadas em markdown
- **RNF014**: Links clicáveis para hosts
- **RNF015**: Tabelas organizadas para listagens
- **RNF016**: Escape automático de caracteres especiais

### 3.5 Compatibilidade
- **RNF017**: Suporte a Windows e Linux
- **RNF018**: Compatibilidade com Python 3.x
- **RNF019**: Framework Telegram Bot API

## 4. Estrutura de Dados

### 4.1 Persistência de Usuário
```python
user_data = {
    user_id: {
        "ping_<host>": {
            "interval": int,
            "ip_address": str,
            "job_owner": int,
            "last_status": bool,
            "http_status": bool,
            "https_status": bool,
            "http_ping_time": str,
            "port": int,
            "last_fail_date": str,
            "username": str,  # SSH
            "password": str,  # SSH
            "connection_port": int  # SSH
        },
        "show_success": bool
    }
}
```

### 4.2 Job Queue
```python
jobs = {
    user_id: {
        "ping_<host>": JobObject
    }
}
```

## 5. Dependências

### 5.1 Bibliotecas Principais
- `python-telegram-bot`: Framework Telegram
- `paramiko`: Cliente SSH
- `httpx`: Cliente HTTP assíncrono
- `python-dotenv`: Gerenciamento de variáveis de ambiente

### 5.2 Módulos Internos
- `tlgfwk`: Framework base do bot
- `util.util_watch`: Utilitários de monitoramento
- `translations`: Sistema de traduções

## 6. Comandos Disponíveis

### 6.1 Comandos de Usuário
- `/pingadd` - Adicionar host
- `/pingdelete` - Remover host
- `/pinglist` - Listar hosts
- `/pinglog` - Controle de logs
- `/pinghost` - Ping manual
- `/pinginterval` - Alterar intervalo
- `/pinghostport` - Verificar porta
- `/changepingport` - Alterar porta
- `/storecredentials` - Gerenciar credenciais
- `/listfailures` - Listar falhas

### 6.2 Comandos de Admin
- `/exec` - Executar comando local
- `/ssh` - Executar comando SSH

### 6.3 Comandos Herdados do Framework
- `/start` - Iniciar bot
- `/help` - Ajuda
- `/version` - Versão
- `/showusers` - Listar usuários
- `/showbalance` - Mostrar saldo
- `/showconfig` - Mostrar configuração

## 7. Fluxos Principais

### 7.1 Adição de Host
1. Usuário executa `/pingadd`
2. Validação de parâmetros
3. Verificação de duplicação
4. Criação do job agendado
5. Armazenamento na persistência
6. Confirmação ao usuário

### 7.2 Monitoramento Automático
1. Job agendado executa
2. Execução de ping ICMP
3. Verificação de porta TCP
4. Atualização de status
5. Notificação em caso de falha
6. Persistência de dados

### 7.3 Execução SSH
1. Usuário executa `/ssh`
2. Validação de credenciais
3. Conexão SSH
4. Execução do comando
5. Retorno do resultado
6. Fechamento da conexão

## 8. Tratamento de Erros

### 8.1 Tipos de Erro
- Host não encontrado
- Credenciais inválidas
- Timeout de conexão
- Porta fechada
- Comando inválido
- Erro de persistência

### 8.2 Estratégias
- Try-catch em todas as operações
- Logs detalhados de erro
- Mensagens amigáveis ao usuário
- Rollback de operações quando possível
- Notificação de erros críticos ao admin

## 9. Configurações

### 9.1 Arquivo de Ambiente (.env)
- Token do bot Telegram
- ID do proprietário do bot
- Configurações de persistência
- Configurações de logging

### 9.2 Configurações Padrão
- Intervalo mínimo: 120 segundos
- Intervalo máximo: 2400 segundos
- Porta padrão: 80
- Porta SSH padrão: 22
- Timeout de porta: 1 segundo

## 10. Roadmap

### 10.1 Implementado (v0.6.2)
- Monitoramento básico de hosts
- Verificação de portas TCP
- Execução de comandos SSH
- Sistema de credenciais
- Relatórios de falhas
- Controle de logs

### 10.2 Planejado
- Paginação nas listagens
- Monitoramento HTTP/HTTPS
- Notificações personalizadas
- Dashboard web
- Integração com sistemas de monitoramento
- Backup automático de configurações 