#!/usr/bin/env python3
"""
Teste simples para verificar se o comando /hello está funcionando.
"""

import os
import sys
import asyncio
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tlgfwk.core.framework import TelegramBotFramework

async def test_hello_command():
    """Teste do comando /hello."""
    print("=== Teste do Comando /hello ===")
    
    # Carregar configuração
    config_file = Path(__file__).parent / ".env"
    if not config_file.exists():
        print("❌ Arquivo .env não encontrado")
        return
    
    print("✅ Arquivo .env encontrado")
    
    # Criar framework
    framework = TelegramBotFramework(
        config_file=str(config_file),
        plugins_dir=str(Path(__file__).parent)
    )
    
    print("✅ Framework criado")
    
    # Verificar se o plugin foi carregado
    if framework.plugin_manager:
        await framework.plugin_manager.load_all_plugins()
        
        # Verificar se o comando hello está registrado
        hello_found = False
        for handler in framework.application.handlers[0]:
            if hasattr(handler, 'commands') and 'hello' in handler.commands:
                hello_found = True
                print(f"✅ Comando /hello encontrado no handler: {handler}")
                break
        
        if not hello_found:
            print("❌ Comando /hello NÃO encontrado")
            return
        
        print("✅ Comando /hello registrado corretamente")
        
        # Verificar se não há unknown_command interferindo
        unknown_before_hello = False
        hello_index = -1
        unknown_index = -1
        
        for i, handler in enumerate(framework.application.handlers[0]):
            if hasattr(handler, 'commands') and 'hello' in handler.commands:
                hello_index = i
            elif hasattr(handler, 'callback') and handler.callback.__name__ == 'unknown_command':
                unknown_index = i
        
        if hello_index != -1 and unknown_index != -1:
            if unknown_index < hello_index:
                print(f"⚠️  PROBLEMA: unknown_command ({unknown_index}) está ANTES de hello ({hello_index})")
                unknown_before_hello = True
            else:
                print(f"✅ OK: hello ({hello_index}) está ANTES de unknown_command ({unknown_index})")
        else:
            print(f"✅ OK: hello_index: {hello_index}, unknown_index: {unknown_index}")
        
        if not unknown_before_hello:
            print("\n🎉 SUCESSO! O comando /hello deve funcionar corretamente!")
            print("💡 Teste no Telegram enviando: /hello")
        else:
            print("\n❌ PROBLEMA: O comando /hello pode não funcionar devido à ordem dos handlers")
    
    else:
        print("❌ PluginManager não disponível")

if __name__ == "__main__":
    asyncio.run(test_hello_command()) 