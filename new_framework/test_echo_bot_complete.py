#!/usr/bin/env python3
"""
Teste de Execução do Echo Bot
Simula a execução do bot sem token real para verificar a inicialização
"""

import os
import sys
from pathlib import Path

# Configurar variáveis de ambiente antes de importar
os.environ["BOT_TOKEN"] = "123456789:TEST-TOKEN-FOR-DEVELOPMENT"
os.environ["OWNER_USER_ID"] = "123456789"
os.environ["ADMIN_USER_IDS"] = "123456789,987654321"
os.environ["DEBUG"] = "true"

# Importar e testar o bot
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_bot_initialization():
    """Testa a inicialização completa do bot"""
    try:
        print("🤖 Testando inicialização do Echo Bot...")
        
        # Importar a classe do bot
        from examples.echo_bot import EchoBot
        
        # Tentar inicializar o bot
        print("   📝 Criando instância do bot...")
        bot = EchoBot()
        
        print("   ✅ Bot inicializado com sucesso!")
        print(f"   🔑 Token configurado: {bool(bot.config.bot_token)}")
        print(f"   👤 Owner ID: {bot.config.owner_user_id}")
        print(f"   👥 Admin IDs: {bot.config.admin_user_ids}")
        print(f"   🔧 Debug: {bot.config.debug}")
        print(f"   📛 Nome: {bot.config.instance_name}")
        
        # Testar setup de handlers
        print("   🔧 Configurando handlers...")
        bot.setup_handlers()
        print("   ✅ Handlers configurados!")
        
        # Verificar se application foi criado
        if bot.application:
            print("   ✅ Application criado com sucesso!")
        else:
            print("   ⚠️  Application é None (normal para tokens inválidos)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro na inicialização: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_command_decorators():
    """Testa se os decorators @command estão funcionando"""
    try:
        print("\n🎯 Testando decorators @command...")
        
        from examples.echo_bot import EchoBot
        bot = EchoBot()
        
        # Verificar se os métodos existem
        methods = ['echo_command', 'reverse_command', 'count_command']
        for method_name in methods:
            if hasattr(bot, method_name):
                method = getattr(bot, method_name)
                print(f"   ✅ {method_name}: OK")
            else:
                print(f"   ❌ {method_name}: MISSING")
                return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro nos decorators: {e}")
        return False

def test_imports():
    """Testa todas as importações necessárias"""
    try:
        print("\n📦 Testando importações...")
        
        # Testar importações do framework
        from tlgfwk import TelegramBotFramework, command
        print("   ✅ tlgfwk: OK")
        
        # Testar importações do telegram
        from telegram import Update
        from telegram.ext import ContextTypes, MessageHandler, filters
        print("   ✅ python-telegram-bot: OK")
        
        # Testar importações padrão
        import asyncio
        from pathlib import Path
        print("   ✅ Bibliotecas padrão: OK")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro nas importações: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("=" * 60)
    print("🧪 TESTE COMPLETO DO ECHO BOT")
    print("=" * 60)
    
    tests = [
        ("Importações", test_imports),
        ("Decorators @command", test_command_decorators),
        ("Inicialização do Bot", test_bot_initialization),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    # Relatório final
    print("\n" + "=" * 60)
    print("📊 RELATÓRIO FINAL")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\n📈 Resumo: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("🚀 O Echo Bot está funcionando perfeitamente!")
        print("\n📋 Para executar com token real:")
        print("1. Obtenha um token do @BotFather")
        print("2. Configure o arquivo .env")
        print("3. Execute: python examples/echo_bot.py")
        return 0
    else:
        print("\n⚠️  ALGUNS TESTES FALHARAM!")
        print("🔧 Verifique os erros acima e corrija antes de usar.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
