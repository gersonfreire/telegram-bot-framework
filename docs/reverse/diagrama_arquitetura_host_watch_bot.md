# Diagrama de Arquitetura - HostWatchBot

## 1. Arquitetura Geral

```mermaid
graph TB
    subgraph "Telegram Platform"
        TG[Telegram API]
        USER[Usuário]
    end
    
    subgraph "HostWatchBot Application"
        BOT[HostWatchBot]
        FWK[TlgBotFwk Framework]
        JQ[Job Queue]
        PERS[Persistence]
    end
    
    subgraph "External Services"
        HOST1[Host 1]
        HOST2[Host 2]
        HOSTN[Host N]
        SSH[SSH Service]
    end
    
    subgraph "System Components"
        ICMP[ICMP Ping]
        TCP[TCP Port Check]
        HTTP[HTTP Client]
    end
    
    USER -->|Comandos| TG
    TG -->|Updates| BOT
    BOT --> FWK
    FWK --> JQ
    FWK --> PERS
    
    JQ -->|Scheduled Jobs| BOT
    BOT -->|Ping| ICMP
    BOT -->|Port Check| TCP
    BOT -->|HTTP Check| HTTP
    
    ICMP --> HOST1
    ICMP --> HOST2
    ICMP --> HOSTN
    
    TCP --> HOST1
    TCP --> HOST2
    TCP --> HOSTN
    
    BOT -->|SSH Commands| SSH
    SSH --> HOST1
    SSH --> HOST2
    SSH --> HOSTN
```

## 2. Fluxo de Monitoramento

```mermaid
sequenceDiagram
    participant U as Usuário
    participant B as Bot
    participant JQ as Job Queue
    participant H as Host
    participant P as Persistence
    
    U->>B: /pingadd host interval
    B->>JQ: Create scheduled job
    B->>P: Store configuration
    B->>U: Confirmation
    
    loop Every interval seconds
        JQ->>B: Execute job
        B->>H: ICMP ping
        B->>H: TCP port check
        H->>B: Response
        B->>P: Update status
        alt Host down
            B->>U: Failure notification
        end
    end
```

## 3. Estrutura de Classes

```mermaid
classDiagram
    class TlgBotFwk {
        +bot_owner: int
        +admins_owner: list
        +application: Application
        +jobs: dict
        +__init__()
        +run()
        +initialize_handlers()
    }
    
    class HostWatchBot {
        +jobs: dict
        +__init__()
        +run()
        +load_all_user_data()
        +job_event_handler()
        +ping_host()
        +http_ping()
    }
    
    class CommandHandlers {
        +ping_add()
        +ping_delete()
        +ping_list()
        +ping_host_command()
        +ping_host_port_command()
        +ping_interval()
        +change_ping_port_command()
        +store_credentials()
        +execute_command()
        +execute_ssh_command()
        +list_failures()
        +ping_log()
    }
    
    class Utils {
        +check_port()
        +escape_markdown()
    }
    
    TlgBotFwk <|-- HostWatchBot
    HostWatchBot --> CommandHandlers
    HostWatchBot --> Utils
```

## 4. Estrutura de Dados

```mermaid
erDiagram
    USER {
        int user_id PK
        string language_code
        bool show_success
    }
    
    HOST_JOB {
        string job_name PK
        int user_id FK
        string ip_address
        int interval
        int port
        bool last_status
        string last_fail_date
        string http_ping_time
        string username
        string password
        int connection_port
    }
    
    JOB_QUEUE {
        string job_name PK
        int user_id FK
        datetime next_t
        string data
    }
    
    USER ||--o{ HOST_JOB : "owns"
    USER ||--o{ JOB_QUEUE : "schedules"
    HOST_JOB ||--|| JOB_QUEUE : "references"
```

## 5. Fluxo de Comandos SSH

```mermaid
flowchart TD
    A[Usuário: /ssh host command] --> B{Admin?}
    B -->|Não| C[Erro: Acesso negado]
    B -->|Sim| D{Host monitorado?}
    D -->|Não| E[Erro: Host não encontrado]
    D -->|Sim| F{Credenciais armazenadas?}
    F -->|Não| G[Erro: Credenciais não encontradas]
    F -->|Sim| H[Conectar SSH]
    H --> I{Conectou?}
    I -->|Não| J[Erro: Falha na conexão]
    I -->|Sim| K[Executar comando]
    K --> L[Retornar resultado]
    L --> M[Fechar conexão]
```

## 6. Sistema de Persistência

```mermaid
graph LR
    subgraph "Runtime Memory"
        USER_DATA[User Data]
        JOB_DATA[Job Data]
    end
    
    subgraph "Persistence Layer"
        PICKLE[Pickle File]
        JSON[JSON Config]
    end
    
    subgraph "External Storage"
        ENV[Environment File]
    end
    
    USER_DATA -->|Auto Save| PICKLE
    JOB_DATA -->|Auto Save| PICKLE
    PICKLE -->|Load| USER_DATA
    PICKLE -->|Load| JOB_DATA
    
    ENV -->|Config| JSON
    JSON -->|Settings| USER_DATA
```

## 7. Monitoramento de Estado

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Monitoring: /pingadd
    Monitoring --> Checking: Job triggered
    Checking --> Success: Host up + Port open
    Checking --> Failure: Host down OR Port closed
    Success --> Monitoring: Wait interval
    Failure --> Monitoring: Wait interval
    Monitoring --> Idle: /pingdelete
    Failure --> [*]: Stop monitoring
    Success --> [*]: Stop monitoring
```

## 8. Componentes de Segurança

```mermaid
graph TB
    subgraph "Security Layer"
        AUTH[Authentication]
        ENCRYPT[Encryption]
        VALID[Validation]
        ISOLATE[Isolation]
    end
    
    subgraph "Commands"
        USER_CMD[User Commands]
        ADMIN_CMD[Admin Commands]
    end
    
    subgraph "Data"
        CREDS[Credentials]
        CONFIG[Configuration]
    end
    
    USER_CMD --> AUTH
    ADMIN_CMD --> AUTH
    CREDS --> ENCRYPT
    CONFIG --> ENCRYPT
    USER_CMD --> VALID
    ADMIN_CMD --> VALID
    USER_CMD --> ISOLATE
    ADMIN_CMD --> ISOLATE
```

## 9. Integração com Framework Base

```mermaid
graph TB
    subgraph "TlgBotFwk Framework"
        CORE[Core Framework]
        HANDLERS[Command Handlers]
        PERSIST[Persistence System]
        SCHED[Job Scheduler]
        LOG[Logging System]
    end
    
    subgraph "HostWatchBot Extensions"
        PING[Ping Commands]
        SSH[SSH Commands]
        MONITOR[Monitoring Jobs]
        CREDS[Credential Management]
    end
    
    CORE --> PING
    CORE --> SSH
    CORE --> MONITOR
    CORE --> CREDS
    
    HANDLERS --> PING
    HANDLERS --> SSH
    
    PERSIST --> MONITOR
    PERSIST --> CREDS
    
    SCHED --> MONITOR
    
    LOG --> PING
    LOG --> SSH
    LOG --> MONITOR
    LOG --> CREDS
```

## 10. Fluxo de Inicialização

```mermaid
flowchart TD
    A[Start Bot] --> B[Load Environment]
    B --> C[Initialize Framework]
    C --> D[Register Command Handlers]
    D --> E[Load Persistence Data]
    E --> F[Restore Jobs]
    F --> G[Start Job Queue]
    G --> H[Send Startup Message]
    H --> I[Bot Ready]
    
    F --> F1{Jobs Found?}
    F1 -->|Yes| F2[Recreate Jobs]
    F1 -->|No| F3[No Jobs to Restore]
    F2 --> G
    F3 --> G
``` 