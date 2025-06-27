import sys
sys.path.insert(0, 'src')

print("🧪 Testando Framework...")

try:
    import tlgfwk
    print(f"✅ tlgfwk versão: {tlgfwk.__version__}")
except Exception as e:
    print(f"❌ Erro ao importar tlgfwk: {e}")

try:
    from tlgfwk.utils.logger import Logger
    logger = Logger('test')
    print("✅ Logger: OK")
except Exception as e:
    print(f"❌ Logger: {e}")

try:
    from tlgfwk.utils.crypto import CryptoManager
    crypto = CryptoManager()
    print("✅ CryptoManager: OK")
except Exception as e:
    print(f"❌ CryptoManager: {e}")

try:
    from tlgfwk.core.config import Config
    config = Config()
    print("✅ Config: OK")
except Exception as e:
    print(f"❌ Config: {e}")

print("🎉 Testes concluídos!")
