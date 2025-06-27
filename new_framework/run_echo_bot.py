#!/usr/bin/env python3
"""
Executar Echo Bot com configurações do .env.test
"""

import os
import sys
from pathlib import Path

# Carregar variáveis do .env.test
os.environ["BOT_TOKEN"] = "1076729431:AAE95s3Q_QKkEtVxnProc5BRxdqxKo_S7v8"
os.environ["OWNER_USER_ID"] = "438429121"
os.environ["ADMIN_USER_IDS"] = "438429121"
os.environ["DEBUG"] = "true"
os.environ["INSTANCE_NAME"] = "EchoBot"

print("🤖 Configurações carregadas:")
print(f"BOT_TOKEN: {os.environ['BOT_TOKEN'][:20]}...")
print(f"OWNER_USER_ID: {os.environ['OWNER_USER_ID']}")
print(f"ADMIN_USER_IDS: {os.environ['ADMIN_USER_IDS']}")
print(f"DEBUG: {os.environ['DEBUG']}")
print(f"INSTANCE_NAME: {os.environ['INSTANCE_NAME']}")

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Importar e executar o bot
try:
    from examples.echo_bot import main
    print("\n🚀 Iniciando Echo Bot...")
    main()
except KeyboardInterrupt:
    print("\n⏹️ Bot interrompido pelo usuário")
except Exception as e:
    print(f"\n❌ Erro: {e}")
    import traceback
    traceback.print_exc()
