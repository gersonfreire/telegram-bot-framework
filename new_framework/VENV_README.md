# Ambiente Virtual - New Framework

Este diretório contém um ambiente virtual Python isolado para o projeto `new_framework`.

## Estrutura

```
new_framework/
├── .venv/                 # Ambiente virtual Python
├── activate.bat          # Script de ativação (Command Prompt)
├── activate.ps1          # Script de ativação (PowerShell)
├── requirements.txt      # Dependências do projeto
└── ...                   # Outros arquivos do projeto
```

## Como usar

### Método 1: Scripts de ativação (Recomendado)

**PowerShell:**
```powershell
.\activate.ps1
```

**Command Prompt:**
```cmd
activate.bat
```

### Método 2: Ativação manual

**PowerShell:**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Command Prompt:**
```cmd
.venv\Scripts\activate.bat
```

## Dependências instaladas

O ambiente virtual inclui as seguintes dependências principais:

- `python-telegram-bot>=21.0` - SDK para Telegram Bot API
- `python-dotenv>=1.0.0` - Carregamento de variáveis de ambiente
- `cryptography>=41.0.0` - Funcionalidades criptográficas
- `APScheduler>=3.10.0` - Agendamento de tarefas
- `requests>=2.31.0` - Cliente HTTP
- `aiofiles>=23.0.0` - Operações de arquivo assíncronas
- `sqlalchemy>=2.0.0` - ORM para banco de dados
- `alembic>=1.12.0` - Migrações de banco de dados
- `psutil>=5.9.0` - Informações do sistema

## Comandos úteis

### Instalar nova dependência
```bash
pip install nome-do-pacote
```

### Atualizar requirements.txt
```bash
pip freeze > requirements.txt
```

### Desativar ambiente virtual
```bash
deactivate
```

### Reinstalar dependências
```bash
pip install -r requirements.txt
```

## Verificação

Para verificar se o ambiente virtual está ativo:

```python
import sys
print("Virtual env ativo:", hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))
print("Python executable:", sys.executable)
```

## Notas importantes

- O ambiente virtual está configurado em `.venv/` e está incluído no `.gitignore`
- Sempre ative o ambiente virtual antes de trabalhar no projeto
- Para projetos em produção, considere usar `pipenv` ou `poetry` para gerenciamento mais avançado
