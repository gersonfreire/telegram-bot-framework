#!/usr/bin/env python3
"""
Teste de inicialização do Echo Bot
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis do .env.test
env_file = Path(__file__).parent / ".env.test"
if env_file.exists():
    load_dotenv(env_file)
    print(f"✅ Configurações carregadas de {env_file}")

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    print("🤖 Importando classes...")
    from examples.echo_bot import EchoBot
    
    print("🔧 Criando instância do bot...")
    bot = EchoBot()
    
    print("⚙️ Configurando handlers...")
    bot.setup_handlers()
    
    print("✅ Bot inicializado com sucesso!")
    print(f"🔑 Token: {bot.config.bot_token[:20]}...")
    print(f"👤 Owner: {bot.config.owner_user_id}")
    print(f"👥 Admins: {bot.config.admin_user_ids}")
    print(f"🔧 Debug: {bot.config.debug}")
    
    print("\n🎉 TESTE DE INICIALIZAÇÃO PASSOU!")
    print("📱 O bot está pronto para executar com 'bot.run()'")
    
except Exception as e:
    print(f"❌ Erro durante teste: {e}")
    import traceback
    traceback.print_exc()
