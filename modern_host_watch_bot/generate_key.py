#!/usr/bin/env python3
"""
Generate encryption key for Modern Host Watch Bot.
"""

from cryptography.fernet import Fernet
import base64


def generate_key():
    """Generate a new encryption key."""
    key = Fernet.generate_key()
    return key.decode()


def main():
    """Main function."""
    print("🔐 Generating encryption key for Modern Host Watch Bot...")
    print()
    
    key = generate_key()
    
    print("✅ Encryption key generated successfully!")
    print()
    print("📋 Add this key to your .env file:")
    print(f"ENCRYPTION_KEY={key}")
    print()
    print("⚠️  Important:")
    print("- Keep this key secure and private")
    print("- Don't share it or commit it to version control")
    print("- If you lose this key, you'll need to regenerate SSH credentials")
    print()
    print("🔑 Key length:", len(key), "characters")


if __name__ == "__main__":
    main() 