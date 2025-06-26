"""
Test Cryptography Utilities

Tests for the crypto utilities module.
"""

import os
import tempfile
import json
import pytest
from unittest.mock import patch

# Add src to path for testing
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tlgfwk.utils.crypto import CryptoUtils, EnvCrypto, generate_encryption_key, create_secure_token


class TestCryptoUtils:
    """Test cases for CryptoUtils class."""
    
    def test_generate_key(self):
        """Test key generation."""
        key = CryptoUtils.generate_key()
        assert isinstance(key, bytes)
        assert len(key) == 32  # Default length
        
        # Test custom length
        key = CryptoUtils.generate_key(16)
        assert len(key) == 16
    
    def test_generate_token(self):
        """Test token generation."""
        # URL-safe token
        token = CryptoUtils.generate_token()
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Hex token
        token = CryptoUtils.generate_token(url_safe=False)
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_hash_password(self):
        """Test password hashing."""
        password = "test_password_123"
        hashed, salt = CryptoUtils.hash_password(password)
        
        assert isinstance(hashed, str)
        assert isinstance(salt, str)
        assert len(hashed) > 0
        assert len(salt) > 0
        
        # Test with custom salt
        import base64
        custom_salt = base64.b64encode(b"custom_salt_16b").decode()
        hashed2, salt2 = CryptoUtils.hash_password(password, base64.b64decode(custom_salt))
        
        assert salt2 == custom_salt
        assert hashed2 != hashed  # Different salt should produce different hash
    
    def test_verify_password(self):
        """Test password verification."""
        password = "test_password_123"
        wrong_password = "wrong_password"
        
        hashed, salt = CryptoUtils.hash_password(password)
        
        # Correct password should verify
        assert CryptoUtils.verify_password(password, hashed, salt) is True
        
        # Wrong password should not verify
        assert CryptoUtils.verify_password(wrong_password, hashed, salt) is False
        
        # Invalid hash/salt should not verify
        assert CryptoUtils.verify_password(password, "invalid_hash", salt) is False
        assert CryptoUtils.verify_password(password, hashed, "invalid_salt") is False
    
    def test_hash_string(self):
        """Test string hashing."""
        data = "test_string_to_hash"
        
        # SHA256
        hash_sha256 = CryptoUtils.hash_string(data, "sha256")
        assert isinstance(hash_sha256, str)
        assert len(hash_sha256) == 64  # SHA256 hex length
        
        # SHA512
        hash_sha512 = CryptoUtils.hash_string(data, "sha512")
        assert isinstance(hash_sha512, str)
        assert len(hash_sha512) == 128  # SHA512 hex length
        
        # MD5
        hash_md5 = CryptoUtils.hash_string(data, "md5")
        assert isinstance(hash_md5, str)
        assert len(hash_md5) == 32  # MD5 hex length
        
        # Unsupported algorithm
        with pytest.raises(ValueError, match="Unsupported hash algorithm"):
            CryptoUtils.hash_string(data, "unsupported")
    
    def test_hmac_sign_verify(self):
        """Test HMAC signing and verification."""
        data = "test_data_to_sign"
        key = "secret_key"
        
        # Sign data
        signature = CryptoUtils.hmac_sign(data, key)
        assert isinstance(signature, str)
        assert len(signature) > 0
        
        # Verify signature
        assert CryptoUtils.hmac_verify(data, key, signature) is True
        
        # Wrong data should not verify
        assert CryptoUtils.hmac_verify("wrong_data", key, signature) is False
        
        # Wrong key should not verify
        assert CryptoUtils.hmac_verify(data, "wrong_key", signature) is False
        
        # Wrong signature should not verify
        assert CryptoUtils.hmac_verify(data, key, "wrong_signature") is False
    
    def test_encrypt_decrypt_string(self):
        """Test string encryption and decryption."""
        crypto = CryptoUtils("test_master_key")
        
        plaintext = "This is a secret message"
        
        # Encrypt
        ciphertext = crypto.encrypt_string(plaintext)
        assert isinstance(ciphertext, str)
        assert ciphertext != plaintext
        
        # Decrypt
        decrypted = crypto.decrypt_string(ciphertext)
        assert decrypted == plaintext
        
        # Wrong key should fail decryption
        wrong_crypto = CryptoUtils("wrong_master_key")
        with pytest.raises(Exception):  # Should raise DecryptionError
            wrong_crypto.decrypt_string(ciphertext)
    
    def test_encrypt_decrypt_dict(self):
        """Test dictionary encryption and decryption."""
        crypto = CryptoUtils("test_master_key")
        
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "settings": {
                "theme": "dark",
                "notifications": True
            }
        }
        
        # Encrypt
        encrypted = crypto.encrypt_dict(data)
        assert isinstance(encrypted, str)
        
        # Decrypt
        decrypted = crypto.decrypt_dict(encrypted)
        assert decrypted == data
    
    def test_encrypt_decrypt_file(self):
        """Test file encryption and decryption."""
        crypto = CryptoUtils("test_master_key")
        
        # Create test file
        test_data = "This is test file content\nWith multiple lines\nAnd special chars: !@#$%"
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write(test_data)
            temp_file_path = temp_file.name
        
        try:
            # Encrypt file
            encrypted_path = crypto.encrypt_file(temp_file_path)
            assert os.path.exists(encrypted_path)
            assert encrypted_path == temp_file_path + '.enc'
            
            # Verify encrypted file is different
            with open(encrypted_path, 'rb') as f:
                encrypted_content = f.read()
            assert encrypted_content != test_data.encode()
            
            # Decrypt file
            decrypted_path = crypto.decrypt_file(encrypted_path)
            assert os.path.exists(decrypted_path)
            
            # Verify decrypted content
            with open(decrypted_path, 'r') as f:
                decrypted_content = f.read()
            assert decrypted_content == test_data
            
        finally:
            # Clean up
            for path in [temp_file_path, temp_file_path + '.enc', temp_file_path + '.enc.dec']:
                if os.path.exists(path):
                    os.unlink(path)
    
    def test_create_verify_signature(self):
        """Test signature creation and verification."""
        crypto = CryptoUtils("test_master_key")
        
        data = "important_data_to_sign"
        
        # Create signature
        signature = crypto.create_signature(data)
        assert isinstance(signature, str)
        assert len(signature) > 0
        
        # Verify signature
        assert crypto.verify_signature(data, signature) is True
        
        # Wrong data should not verify
        assert crypto.verify_signature("wrong_data", signature) is False
        
        # Wrong signature should not verify
        assert crypto.verify_signature(data, "wrong_signature") is False
    
    def test_derive_key_from_password(self):
        """Test key derivation from password."""
        crypto = CryptoUtils()
        
        password = "user_password_123"
        
        # Derive key
        key = crypto.derive_key_from_password(password)
        assert isinstance(key, bytes)
        assert len(key) == 32  # Default length
        
        # Same password should produce same key with same salt
        import os
        salt = os.urandom(16)
        key1 = crypto.derive_key_from_password(password, salt)
        key2 = crypto.derive_key_from_password(password, salt)
        assert key1 == key2
        
        # Different salt should produce different key
        salt2 = os.urandom(16)
        key3 = crypto.derive_key_from_password(password, salt2)
        assert key1 != key3
    
    def test_secure_compare(self):
        """Test secure string comparison."""
        string1 = "secret_value"
        string2 = "secret_value"
        string3 = "different_value"
        
        # Same strings should compare equal
        assert CryptoUtils.secure_compare(string1, string2) is True
        
        # Different strings should not compare equal
        assert CryptoUtils.secure_compare(string1, string3) is False


class TestEnvCrypto:
    """Test cases for EnvCrypto class."""
    
    def test_encrypt_decrypt_env_value(self):
        """Test encryption/decryption of individual env values."""
        env_crypto = EnvCrypto("test_key")
        
        value = "secret_api_key_123"
        
        # Encrypt
        encrypted = env_crypto.encrypt_env_value(value)
        assert isinstance(encrypted, str)
        assert encrypted.startswith("ENC[")
        assert encrypted.endswith("]")
        assert encrypted != value
        
        # Decrypt
        decrypted = env_crypto.decrypt_env_value(encrypted)
        assert decrypted == value
        
        # Non-encrypted value should pass through
        normal_value = "normal_value"
        assert env_crypto.decrypt_env_value(normal_value) == normal_value
    
    def test_is_encrypted_value(self):
        """Test checking if value is encrypted."""
        env_crypto = EnvCrypto("test_key")
        
        # Encrypted value
        encrypted = env_crypto.encrypt_env_value("secret")
        assert env_crypto.is_encrypted_value(encrypted) is True
        
        # Normal value
        assert env_crypto.is_encrypted_value("normal_value") is False
        assert env_crypto.is_encrypted_value("ENC[incomplete") is False
        assert env_crypto.is_encrypted_value("incomplete]") is False
    
    def test_encrypt_decrypt_env_file(self):
        """Test encryption/decryption of .env files."""
        env_crypto = EnvCrypto("test_key")
        
        # Create test .env content
        env_content = """# Test environment file
BOT_TOKEN=test_token_123
ADMIN_USER_ID=123456789
API_KEY=secret_api_key
DEBUG=true
# Comment line
EMPTY_VALUE=
"""
        
        # Create temporary .env file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as temp_file:
            temp_file.write(env_content)
            env_file_path = temp_file.name
        
        try:
            # Encrypt .env file
            encrypted_path = env_crypto.encrypt_env_file(env_file_path)
            assert os.path.exists(encrypted_path)
            assert encrypted_path == env_file_path + '.enc'
            
            # Verify encrypted file content is different
            with open(encrypted_path, 'r') as f:
                encrypted_content = f.read()
            assert encrypted_content != env_content
            
            # Decrypt .env file
            decrypted_path = env_crypto.decrypt_env_file(encrypted_path)
            assert os.path.exists(decrypted_path)
            
            # Verify decrypted content
            with open(decrypted_path, 'r') as f:
                decrypted_content = f.read()
            
            # Parse both original and decrypted content
            original_vars = {}
            decrypted_vars = {}
            
            for line in env_content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    original_vars[key.strip()] = value.strip()
            
            for line in decrypted_content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    decrypted_vars[key.strip()] = value.strip()
            
            # Compare parsed variables
            assert original_vars == decrypted_vars
            
        finally:
            # Clean up
            for path in [env_file_path, env_file_path + '.enc', env_file_path + '.enc.env']:
                if os.path.exists(path):
                    os.unlink(path)


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_generate_encryption_key(self):
        """Test encryption key generation."""
        key = generate_encryption_key()
        assert isinstance(key, str)
        assert len(key) > 0
        
        # Should be valid base64
        import base64
        decoded = base64.b64decode(key)
        assert len(decoded) == 32  # 32 bytes
    
    def test_create_secure_token(self):
        """Test secure token creation."""
        token = create_secure_token()
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Test custom length
        token = create_secure_token(16)
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Tokens should be unique
        token1 = create_secure_token()
        token2 = create_secure_token()
        assert token1 != token2
