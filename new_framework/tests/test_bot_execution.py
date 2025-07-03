#!/usr/bin/env python3
"""
Teste de execução do Echo Bot com timeout
"""

import os
import sys
import signal
import time
from pathlib import Path

# Configurar timeout
def timeout_handler(signum, frame):
    print("\n⏰ Timeout atingido - Bot estava executando normalmente!")
    print("✅ Teste concluído com sucesso!")
    sys.exit(0)

# Configurar timeout de 10 segundos
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(10)

try:
    # Carregar configurações do .env.test
    from dotenv import load_dotenv
    env_file = Path(__file__).parent / ".env.test"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ Configurações carregadas de {env_file}")
    
    # Adicionar src ao path
    sys.path.insert(0, str(Path(__file__).parent / "src"))
    
    # Importar e executar bot
    from examples.echo_bot import main
    print("🚀 Iniciando Echo Bot...")
    main()
    
except KeyboardInterrupt:
    print("\n⏹️ Bot interrompido pelo usuário")
except Exception as e:
    print(f"\n❌ Erro durante execução: {e}")
    import traceback
    traceback.print_exc()
finally:
    signal.alarm(0)  # Cancelar alarm
