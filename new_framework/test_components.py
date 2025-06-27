#!/usr/bin/env python3
"""
Teste Simplificado do Framework - Execução Individual de Componentes
"""

import sys
import os

# Adicionar src ao path
sys.path.insert(0, 'src')

def test_individual_components():
    """Testa componentes individuais"""
    print("🧪 INICIANDO TESTES INDIVIDUAIS")
    print("=" * 50)
    
    # 1. Teste Logger
    try:
        print("\n1️⃣ Testando Logger...")
        from tlgfwk.utils.logger import Logger
        logger = Logger("test")
        logger.info("Teste de log")
        print("   ✅ Logger: OK")
    except Exception as e:
        print(f"   ❌ Logger: ERRO - {e}")
    
    # 2. Teste Crypto
    try:
        print("\n2️⃣ Testando CryptoManager...")
        from tlgfwk.utils.crypto import CryptoManager
        crypto = CryptoManager()
        key = crypto.generate_key()
        encrypted = crypto.encrypt("test", key)
        decrypted = crypto.decrypt(encrypted, key)
        assert decrypted == "test"
        print("   ✅ CryptoManager: OK")
    except Exception as e:
        print(f"   ❌ CryptoManager: ERRO - {e}")
    
    # 3. Teste Config
    try:
        print("\n3️⃣ Testando Config...")
        from tlgfwk.core.config import Config
        config = Config()
        print("   ✅ Config: OK")
    except Exception as e:
        print(f"   ❌ Config: ERRO - {e}")
    
    # 4. Teste UserManager
    try:
        print("\n4️⃣ Testando UserManager...")
        from tlgfwk.core.user_manager import UserManager
        user_manager = UserManager()
        print("   ✅ UserManager: OK")
    except Exception as e:
        print(f"   ❌ UserManager: ERRO - {e}")
    
    # 5. Teste Decorators
    try:
        print("\n5️⃣ Testando Decorators...")
        from tlgfwk.core.decorators import command, admin_required
        
        @command("test")
        def test_command():
            return "test"
        
        print("   ✅ Decorators: OK")
    except Exception as e:
        print(f"   ❌ Decorators: ERRO - {e}")
    
    # 6. Teste Framework Principal
    try:
        print("\n6️⃣ Testando Framework Principal...")
        from tlgfwk.core.framework import TelegramBotFramework
        
        # Teste apenas a inicialização básica
        framework = TelegramBotFramework(
            token="test_token",
            test_mode=True
        )
        print("   ✅ Framework Principal: OK")
    except Exception as e:
        print(f"   ❌ Framework Principal: ERRO - {e}")
    
    print("\n" + "=" * 50)
    print("🏁 TESTES INDIVIDUAIS CONCLUÍDOS")

if __name__ == "__main__":
    test_individual_components()
