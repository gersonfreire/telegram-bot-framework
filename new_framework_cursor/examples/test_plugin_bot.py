#!/usr/bin/env python3
"""
Teste simples para verificar se o plugin_bot.py está carregando plugins.
"""

import asyncio
import os
import sys

# Adicionar o caminho do src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from plugin_bot import setup_bot

async def test():
    print("=== Teste do PluginBot ===")
    bot = await setup_bot()
    print("✅ Bot configurado com sucesso!")
    return bot

if __name__ == "__main__":
    bot = asyncio.run(test())
    print("�� Teste concluído!") 