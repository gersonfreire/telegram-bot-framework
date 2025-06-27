#!/usr/bin/env python3
"""
Debug script para verificar handlers registrados no framework.
"""

import os
import sys
import asyncio
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tlgfwk.core.framework import TelegramBotFramework
from tlgfwk.core.config import Config

async def debug_handlers():
    """Debug detalhado dos handlers registrados."""
    print("=== DEBUG HANDLERS ===")
    
    # Carregar configuração
    config_file = Path(__file__).parent / ".env"
    if not config_file.exists():
        print("❌ Arquivo .env não encontrado")
        return
    
    print("✅ Arquivo .env encontrado")
    
    # Criar framework
    framework = TelegramBotFramework(
        config_file=str(config_file),
        plugins_dir=str(Path(__file__).parent),
        custom_config={"auto_load_plugins": True}
    )
    
    print("✅ Framework criado")
    
    # Verificar handlers antes de carregar plugins
    print("\n📋 Handlers ANTES de carregar plugins:")
    for i, handler in enumerate(framework.application.handlers[0]):
        if hasattr(handler, 'commands'):
            print(f"  Handler[{i}]: {handler.commands} -> {handler.callback.__name__}")
        else:
            print(f"  Handler[{i}]: {type(handler).__name__} -> {handler.callback.__name__}")
    
    # Carregar plugins
    if framework.plugin_manager:
        await framework.plugin_manager.load_all_plugins()
        print("\n✅ Plugins carregados")
    
    # Verificar handlers depois de carregar plugins
    print("\n📋 Handlers DEPOIS de carregar plugins:")
    for i, handler in enumerate(framework.application.handlers[0]):
        if hasattr(handler, 'commands'):
            print(f"  Handler[{i}]: {handler.commands} -> {handler.callback.__name__}")
        else:
            print(f"  Handler[{i}]: {type(handler).__name__} -> {handler.callback.__name__}")
    
    # Verificar especificamente o comando hello
    print("\n🔍 Procurando por comando 'hello':")
    hello_found = False
    for i, handler in enumerate(framework.application.handlers[0]):
        if hasattr(handler, 'commands') and 'hello' in handler.commands:
            print(f"  ✅ Encontrado: Handler[{i}] -> {handler.callback}")
            hello_found = True
            break
    
    if not hello_found:
        print("  ❌ Comando 'hello' NÃO encontrado nos handlers")
    
    # Verificar se unknown_command está antes de hello
    print("\n🔍 Verificando ordem dos handlers:")
    hello_index = -1
    unknown_index = -1
    
    for i, handler in enumerate(framework.application.handlers[0]):
        if hasattr(handler, 'commands') and 'hello' in handler.commands:
            hello_index = i
        elif hasattr(handler, 'callback') and handler.callback.__name__ == 'unknown_command':
            unknown_index = i
    
    if hello_index != -1 and unknown_index != -1:
        if unknown_index < hello_index:
            print(f"  ⚠️  PROBLEMA: unknown_command ({unknown_index}) está ANTES de hello ({hello_index})")
        else:
            print(f"  ✅ OK: hello ({hello_index}) está ANTES de unknown_command ({unknown_index})")
    else:
        print(f"  ❓ hello_index: {hello_index}, unknown_index: {unknown_index}")

if __name__ == "__main__":
    asyncio.run(debug_handlers()) 