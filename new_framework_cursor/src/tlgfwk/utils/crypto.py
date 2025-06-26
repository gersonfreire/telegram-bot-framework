"""
Cryptography utilities for the Telegram Bot Framework.
"""

import base64
from cryptography.fernet import Fernet
from typing import Optional


def generate_key() -> str:
    """Generate a new encryption key."""
    return Fernet.generate_key().decode()


def encrypt_data(data: str, key: str) -> str:
    """Encrypt data with key."""
    fernet = Fernet(key.encode())
    encrypted = fernet.encrypt(data.encode())
    return base64.urlsafe_b64encode(encrypted).decode()


def decrypt_data(encrypted_data: str, key: str) -> str:
    """Decrypt data with key."""
    fernet = Fernet(key.encode())
    encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
    decrypted = fernet.decrypt(encrypted_bytes)
    return decrypted.decode() 