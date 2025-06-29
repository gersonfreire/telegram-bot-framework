# Scheduler Bot - Demonstração do Sistema de Agendamentos

## 📋 Visão Geral

O **Scheduler Bot** é um bot de demonstração completo que mostra como usar o sistema de agendamentos (scheduler) do framework. Ele demonstra todas as funcionalidades de agendamento disponíveis, incluindo tarefas únicas, periódicas, gerenciamento de jobs e estatísticas.

## 🎯 Funcionalidades Demonstradas

### ⏰ Agendamento de Tarefas
- **Tarefas Únicas**: Agendar mensagens para execução em um momento específico
- **Tarefas Periódicas**: Agendar mensagens que se repetem em intervalos regulares
- **Flexibilidade de Tempo**: Intervalos de 1 minuto a 24 horas
- **Mensagens Personalizadas**: Texto customizado para cada agendamento

### 📊 Gerenciamento de Jobs
- **Listagem de Jobs**: Visualizar todos os jobs ativos (admin)
- **Cancelamento Individual**: Cancelar jobs específicos
- **Cancelamento em Lote**: Cancelar todos os jobs do usuário
- **Controle de Permissões**: Usuários só cancelam seus próprios jobs

### 📈 Estatísticas e Monitoramento
- **Estatísticas Detalhadas**: Jobs criados, concluídos e falhados
- **Taxa de Sucesso**: Percentual de jobs executados com sucesso
- **Uptime**: Tempo de execução do scheduler
- **Métricas por Usuário**: Jobs ativos por usuário

### 🧹 Limpeza Automática
- **Remoção Automática**: Jobs únicos são removidos após execução
- **Registro de Falhas**: Jobs falhados são registrados para análise
- **Atualização de Estatísticas**: Métricas atualizadas automaticamente
- **Cache Limpo**: Sistema sempre otimizado

### 🔌 Sistema de Plugins
- **Plugin de Demonstração**: Exemplo de plugin com agendamentos
- **Integração Completa**: Plugins podem usar o scheduler do framework
- **Comandos Customizados**: Funcionalidades específicas do plugin

## 🚀 Como Executar

### 1. Configuração
Crie um arquivo `.env` na pasta `examples` com as seguintes variáveis:

```env
# Configurações do Bot Telegram
BOT_TOKEN=seu_token_aqui
OWNER_USER_ID=123456789
ADMIN_USER_IDS=123456789,987654321
LOG_CHAT_ID=123456789
TRACEBACK_CHAT_ID=123456789

# Configurações do Framework
INSTANCE_NAME=SchedulerBot
DEBUG=true
USE_ASYNC=true
REUSE_CONNECTIONS=true
MAX_WORKERS=4
AUTO_LOAD_PLUGINS=true

# Configurações de Persistência
PERSISTENCE_BACKEND=json
PERSISTENCE_FILE=scheduler_bot_data.json

# Configurações de Logging
LOG_LEVEL=INFO
LOG_FILE=scheduler_bot.log
```

### 2. Execução
```bash
cd new_framework/examples
python scheduler_bot.py
```

## 📚 Comandos Disponíveis

### 🎯 Comandos Principais
- `/start` - Iniciar o bot
- `/schedule` - Menu principal de agendamentos
- `/help` - Mostrar ajuda
- `/status` - Status do sistema

### ⏰ Comandos de Agendamento
- `/schedule_once <minutos> <mensagem>` - Agendar tarefa única
- `/schedule_recurring <intervalo> <mensagem>` - Agendar tarefa periódica
- `/list_jobs` - Listar jobs agendados (admin)
- `/cancel_job <job_id>` - Cancelar job específico
- `/cancel_all` - Cancelar seus jobs

### 📊 Comandos de Estatísticas
- `/scheduler_stats` - Estatísticas do scheduler
- `/scheduler_config` - Configurações (admin)

### 🔌 Comandos de Plugins
- `/plugin_schedule` - Demo do plugin

## 💡 Exemplos de Uso

### Agendamento Único
```
/schedule_once 30 Lembrete: Reunião em 30 minutos!
/schedule_once 60 Verificar emails
/schedule_once 120 Backup do sistema
```

### Agendamento Periódico
```
/schedule_recurring 30 Verificação de status
/schedule_recurring 60 Backup automático
/schedule_recurring 120 Relatório diário
```

### Gerenciamento
```
/list_jobs          # Listar todos os jobs (admin)
/cancel_job once_123456789_1234567890.123  # Cancelar job específico
/cancel_all         # Cancelar todos os seus jobs
```

## 🔧 Funcionalidades Técnicas

### Sistema de Agendamentos
- **APScheduler**: Motor de agendamento robusto
- **Múltiplos Triggers**: Date, interval, cron
- **Persistência**: Jobs sobrevivem a reinicializações
- **Concorrência**: Execução assíncrona de jobs

### Controle de Permissões
- **Usuários**: Podem criar e cancelar seus próprios jobs
- **Admins**: Podem listar todos os jobs e acessar configurações
- **Owner**: Controle total sobre o sistema

### Tratamento de Erros
- **Captura de Exceções**: Jobs falhados são registrados
- **Retry Logic**: Tentativas de reexecução (configurável)
- **Logging Detalhado**: Rastreamento completo de erros

### Performance
- **Limpeza Automática**: Jobs únicos removidos após execução
- **Cache Otimizado**: Sistema sempre limpo
- **Estatísticas em Tempo Real**: Métricas atualizadas

## 🎨 Interface do Usuário

### Menu Interativo
O comando `/schedule` apresenta um menu com botões inline para:
- ⏰ Agendamento Único
- 🔄 Agendamento Periódico
- 📊 Gerenciar Jobs
- 🧹 Limpeza Automática
- 📈 Estatísticas
- ⚙️ Configurações

### Mensagens Formatadas
- **HTML Markup**: Formatação rica com emojis e estrutura
- **Informações Detalhadas**: Job ID, horários, status
- **Feedback Imediato**: Confirmações e erros claros

## 🔌 Plugin de Demonstração

O `SchedulerPlugin` demonstra como plugins podem usar o scheduler:

### Funcionalidades
- **Comando Customizado**: `/plugin_schedule`
- **Agendamento de Plugin**: Jobs específicos do plugin
- **Integração**: Acesso ao scheduler do framework
- **Notificações**: Mensagens agendadas do plugin

### Implementação
```python
class SchedulerPlugin(PluginBase):
    async def plugin_schedule_command(self, update, context):
        # Agendar tarefa única para 30 segundos
        job_id = f"plugin_demo_{user.id}_{datetime.now().timestamp()}"
        self.framework.scheduler.add_job(
            self._send_plugin_notification,
            'date',
            run_date=datetime.now() + timedelta(seconds=30),
            args=[user.id, "Plugin Demo"],
            id=job_id
        )
```

## 📊 Estatísticas e Métricas

### Coleta Automática
- **Jobs Criados**: Contador de agendamentos criados
- **Jobs Concluídos**: Contador de execuções bem-sucedidas
- **Jobs Falhados**: Contador de execuções com erro
- **Uptime**: Tempo de execução do scheduler

### Relatórios
- **Taxa de Sucesso**: Percentual de jobs executados com sucesso
- **Distribuição por Tipo**: Jobs únicos vs periódicos
- **Métricas por Usuário**: Jobs ativos por usuário
- **Performance**: Tempo médio de execução

## 🔐 Segurança e Permissões

### Controle de Acesso
- **Usuários**: Apenas seus próprios jobs
- **Admins**: Visualização de todos os jobs
- **Owner**: Controle total do sistema

### Validação de Entrada
- **Limites de Tempo**: 1 minuto a 24 horas
- **Sanitização**: Validação de parâmetros
- **Prevenção de Spam**: Limites por usuário

## 🚀 Casos de Uso

### Lembretes Pessoais
- Agendar lembretes para reuniões
- Notificações de compromissos
- Lembretes de tarefas importantes

### Monitoramento de Sistemas
- Verificações periódicas de status
- Relatórios automáticos
- Backups agendados

### Notificações de Equipe
- Lembretes para equipes
- Anúncios agendados
- Relatórios periódicos

## 🔧 Configuração Avançada

### Parâmetros do Scheduler
```python
# Configurações específicas
self.config.data['auto_load_plugins'] = True
self.config.data['debug'] = True

# Estatísticas personalizadas
self.scheduler_stats = {
    'jobs_created': 0,
    'jobs_completed': 0,
    'jobs_failed': 0,
    'start_time': datetime.now()
}
```

### Customização de Jobs
```python
# Job único
self.scheduler.add_job(
    self._send_scheduled_message,
    'date',
    run_date=datetime.now() + timedelta(minutes=minutes),
    args=[user.id, message, job_id],
    id=job_id
)

# Job periódico
self.scheduler.add_job(
    self._send_recurring_message,
    'interval',
    minutes=interval_minutes,
    args=[user.id, message, job_id],
    id=job_id,
    replace_existing=True
)
```

## 📝 Logs e Debugging

### Níveis de Log
- **INFO**: Operações normais
- **DEBUG**: Informações detalhadas
- **ERROR**: Erros e falhas
- **WARNING**: Avisos importantes

### Informações Registradas
- Criação de jobs
- Execução de tarefas
- Falhas e erros
- Estatísticas de performance

## 🤝 Contribuição

Para contribuir com melhorias no Scheduler Bot:

1. **Fork** o repositório
2. **Crie** uma branch para sua feature
3. **Implemente** as melhorias
4. **Teste** todas as funcionalidades
5. **Submeta** um pull request

## 📄 Licença

Este projeto está licenciado sob a mesma licença do framework principal.

---

**Scheduler Bot** - Demonstração completa do sistema de agendamentos do Telegram Bot Framework! ⏰🤖
