#!/usr/bin/env python3
"""
Script de teste manual para o Telegram Bot Framework
Executa testes básicos das principais funcionalidades
"""

import sys
import os
import traceback
from datetime import datetime

# Adicionar src ao path
sys.path.insert(0, 'src')

def test_logger():
    """Testa o sistema de logging"""
    try:
        from tlgfwk.utils.logger import Logger
        
        print("📝 Testando Logger...")
        logger = Logger("test_framework")
        logger.info("Teste de log de informação")
        logger.warning("Teste de log de aviso")
        logger.error("Teste de log de erro")
        print("✅ Logger funcionando corretamente!")
        return True
    except Exception as e:
        print(f"❌ Erro no Logger: {e}")
        traceback.print_exc()
        return False

def test_crypto():
    """Testa o sistema de criptografia"""
    try:
        from tlgfwk.utils.crypto import CryptoManager
        
        print("🔐 Testando CryptoManager...")
        crypto = CryptoManager()
        
        # Teste de geração de chave
        key = crypto.generate_key()
        print(f"Chave gerada: {len(key)} bytes")
        
        # Teste de criptografia/descriptografia
        test_data = "Dados de teste para criptografia! 🚀"
        encrypted = crypto.encrypt(test_data, key)
        decrypted = crypto.decrypt(encrypted, key)
        
        if decrypted == test_data:
            print("✅ CryptoManager funcionando corretamente!")
            print(f"Dados originais: {test_data}")
            print(f"Dados descriptografados: {decrypted}")
            return True
        else:
            print("❌ Erro na descriptografia - dados não coincidem")
            return False
            
    except Exception as e:
        print(f"❌ Erro no CryptoManager: {e}")
        traceback.print_exc()
        return False

def test_framework_core():
    """Testa o núcleo do framework"""
    try:
        from tlgfwk.core import TelegramBotFramework
        
        print("🤖 Testando Framework Core...")
        
        # Teste básico de inicialização (sem token real)
        framework = TelegramBotFramework(
            token="dummy_token_for_testing",
            test_mode=True
        )
        
        print("✅ Framework Core inicializado corretamente!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no Framework Core: {e}")
        traceback.print_exc()
        return False

def test_imports():
    """Testa importações básicas do framework"""
    try:
        print("📦 Testando importações...")
        
        import tlgfwk
        print(f"Framework versão: {tlgfwk.__version__}")
        
        from tlgfwk import core, utils
        print("✅ Importações básicas funcionando!")
        return True
        
    except Exception as e:
        print(f"❌ Erro nas importações: {e}")
        traceback.print_exc()
        return False

def main():
    """Executa todos os testes"""
    print("=" * 60)
    print("🧪 TESTE MANUAL DO TELEGRAM BOT FRAMEWORK")
    print("=" * 60)
    print(f"Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Importações", test_imports),
        ("Logger", test_logger),
        ("CryptoManager", test_crypto),
        ("Framework Core", test_framework_core),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'-' * 40}")
        result = test_func()
        results.append((test_name, result))
        print()
    
    # Relatório final
    print("=" * 60)
    print("📊 RELATÓRIO DE TESTES")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\n📈 Resumo: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! Framework funcionando corretamente.")
        return 0
    else:
        print("⚠️  Alguns testes falharam. Verifique os erros acima.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
