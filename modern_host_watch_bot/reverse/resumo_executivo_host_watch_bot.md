# Resumo Executivo - Documento de Requisitos HostWatchBot

## Visão Geral

O **HostWatchBot** é um bot Telegram especializado em monitoramento de infraestrutura de rede, desenvolvido para permitir que usuários monitorem a disponibilidade de servidores e serviços através de comandos simples no Telegram.

## Principais Funcionalidades

### 🎯 Monitoramento Automático
- **Ping ICMP**: Verificação de conectividade básica
- **Verificação de Portas TCP**: Monitoramento de serviços específicos
- **Agendamento Flexível**: Intervalos configuráveis entre 2-40 minutos
- **Notificações Automáticas**: Alertas em tempo real quando hosts ficam indisponíveis

### 🔧 Gerenciamento de Hosts
- **Adição/Remoção**: Controle completo da lista de hosts monitorados
- **Configuração Dinâmica**: Alteração de intervalos e portas sem reiniciar
- **Isolamento por Usuário**: Cada usuário gerencia seus próprios hosts
- **Persistência**: Configurações mantidas após reinicialização

### 🔐 Execução Remota
- **Comandos SSH**: Execução de comandos em hosts remotos
- **Gerenciamento de Credenciais**: Armazenamento seguro de credenciais SSH
- **Comandos Locais**: Execução de comandos no servidor do bot (apenas admin)
- **Controle de Acesso**: Restrições baseadas em perfil de usuário

### 📊 Relatórios e Logs
- **Status em Tempo Real**: Visualização do estado atual dos hosts
- **Histórico de Falhas**: Registro de quando hosts ficaram indisponíveis
- **Logs Detalhados**: Controle de verbosidade das mensagens
- **Formatação Rica**: Tabelas organizadas e links clicáveis

## Arquitetura Técnica

### Framework Base
- **TlgBotFwk**: Framework customizado para bots Telegram
- **Python 3.x**: Linguagem de programação
- **python-telegram-bot**: Biblioteca oficial do Telegram
- **Paramiko**: Cliente SSH para execução remota

### Componentes Principais
- **Job Queue**: Sistema de agendamento de tarefas
- **Persistence Layer**: Armazenamento persistente de configurações
- **Command Handlers**: Processamento de comandos do usuário
- **Security Layer**: Autenticação e isolamento de dados

## Requisitos Funcionais Principais

| ID | Funcionalidade | Comando | Descrição |
|----|----------------|---------|-----------|
| RF001 | Adicionar Host | `/pingadd` | Adiciona host ao monitoramento |
| RF002 | Remover Host | `/pingdelete` | Remove host do monitoramento |
| RF003 | Listar Hosts | `/pinglist` | Mostra hosts monitorados |
| RF004 | Alterar Intervalo | `/pinginterval` | Modifica frequência de verificação |
| RF005 | Verificar Porta | `/pinghostport` | Testa conectividade TCP |
| RF006 | Executar SSH | `/ssh` | Comando remoto via SSH |
| RF007 | Gerenciar Credenciais | `/storecredentials` | Armazena credenciais SSH |
| RF008 | Listar Falhas | `/listfailures` | Histórico de indisponibilidade |

## Requisitos Não Funcionais

### Performance
- ⚡ Timeout de 1 segundo para verificações de porta
- 📊 Limite de 50 hosts por listagem
- ⏱️ Intervalos entre 120-2400 segundos

### Segurança
- 🔒 Comandos de execução restritos a admins
- 🔐 Credenciais armazenadas com criptografia
- 🛡️ Isolamento de dados por usuário
- ✅ Validação rigorosa de parâmetros

### Confiabilidade
- 💾 Persistência automática de dados
- 🔄 Restauração automática de jobs
- 📝 Logs detalhados para debugging
- 🛠️ Tratamento robusto de erros

## Estrutura de Dados

### Configuração de Host
```python
{
    "interval": 300,           # Segundos entre verificações
    "ip_address": "192.168.1.1",
    "port": 80,               # Porta TCP para verificar
    "last_status": True,      # Último status conhecido
    "last_fail_date": None,   # Data da última falha
    "username": "admin",      # Credenciais SSH
    "password": "encrypted",
    "connection_port": 22     # Porta SSH
}
```

## Fluxo de Monitoramento

1. **Configuração**: Usuário adiciona host via `/pingadd`
2. **Agendamento**: Sistema cria job com intervalo especificado
3. **Execução**: Job executa ping ICMP + verificação de porta
4. **Atualização**: Status é persistido e usuário notificado
5. **Recuperação**: Em caso de falha, notificação imediata é enviada

## Benefícios

### Para Usuários
- 🚀 **Simplicidade**: Interface familiar do Telegram
- 📱 **Mobilidade**: Monitoramento de qualquer lugar
- ⚡ **Tempo Real**: Notificações instantâneas
- 🔧 **Flexibilidade**: Configuração fácil e dinâmica

### Para Administradores
- 🛡️ **Segurança**: Controle de acesso granular
- 📊 **Visibilidade**: Relatórios detalhados
- 🔄 **Automação**: Redução de trabalho manual
- 💰 **Custo**: Solução de baixo custo

## Roadmap

### Implementado (v0.6.2)
- ✅ Monitoramento básico de hosts
- ✅ Verificação de portas TCP
- ✅ Execução de comandos SSH
- ✅ Sistema de credenciais
- ✅ Relatórios de falhas

### Planejado
- 📄 Paginação nas listagens
- 🌐 Monitoramento HTTP/HTTPS
- 🔔 Notificações personalizadas
- 📊 Dashboard web
- 🔗 Integração com sistemas de monitoramento

## Conclusão

O HostWatchBot representa uma solução completa e eficiente para monitoramento de infraestrutura através do Telegram, combinando simplicidade de uso com funcionalidades avançadas de monitoramento e execução remota. Sua arquitetura modular e extensível permite fácil manutenção e evolução futura.

---

**Versão do Documento**: 1.0  
**Data**: Dezembro 2024  
**Baseado em**: Engenharia Reversa do código v0.6.2 