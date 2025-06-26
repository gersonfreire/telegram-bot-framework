"""
Cryptography Utilities

This module provides encryption and cryptographic utilities for the Telegram Bot Framework.
Includes symmetric encryption, hashing, and secure token generation.
"""

import os
import base64
import hashlib
import hmac
import secrets
import json
from typing import Union, Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import logging

from .logger import get_logger


class CryptoError(Exception):
    """Base exception for cryptography errors."""
    pass


class EncryptionError(CryptoError):
    """Exception raised for encryption errors."""
    pass


class DecryptionError(CryptoError):
    """Exception raised for decryption errors."""
    pass


class CryptoUtils:
    """
    Cryptography utilities for secure data handling.
    
    Provides methods for encryption, decryption, hashing, and secure token generation.
    """
    
    def __init__(self, master_key: Optional[str] = None):
        """
        Initialize crypto utilities.
        
        Args:
            master_key: Master key for encryption (generated if not provided)
        """
        self.logger = get_logger(__name__)
        
        if master_key:
            self.master_key = master_key.encode()
        else:
            self.master_key = self.generate_key()
        
        # Initialize Fernet cipher
        self._fernet = self._create_fernet_cipher(self.master_key)
    
    @staticmethod
    def generate_key(length: int = 32) -> bytes:
        """
        Generate a cryptographically secure random key.
        
        Args:
            length: Key length in bytes
            
        Returns:
            Random key bytes
        """
        return secrets.token_bytes(length)
    
    @staticmethod
    def generate_token(length: int = 32, url_safe: bool = True) -> str:
        """
        Generate a cryptographically secure random token.
        
        Args:
            length: Token length in bytes
            url_safe: Whether to generate URL-safe token
            
        Returns:
            Random token string
        """
        if url_safe:
            return secrets.token_urlsafe(length)
        else:
            return secrets.token_hex(length)
    
    @staticmethod
    def hash_password(password: str, salt: Optional[bytes] = None) -> tuple[str, str]:
        """
        Hash a password using PBKDF2.
        
        Args:
            password: Password to hash
            salt: Salt bytes (generated if not provided)
            
        Returns:
            Tuple of (hashed_password, salt) as base64 strings
        """
        if salt is None:
            salt = os.urandom(32)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = kdf.derive(password.encode())
        
        return (
            base64.b64encode(key).decode(),
            base64.b64encode(salt).decode()
        )
    
    @staticmethod
    def verify_password(password: str, hashed_password: str, salt: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Password to verify
            hashed_password: Base64 encoded hash
            salt: Base64 encoded salt
            
        Returns:
            True if password matches
        """
        try:
            salt_bytes = base64.b64decode(salt.encode())
            expected_hash = base64.b64decode(hashed_password.encode())
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt_bytes,
                iterations=100000,
                backend=default_backend()
            )
            
            kdf.verify(password.encode(), expected_hash)
            return True
            
        except Exception:
            return False
    
    @staticmethod
    def hash_string(data: str, algorithm: str = 'sha256') -> str:
        """
        Hash a string using the specified algorithm.
        
        Args:
            data: String to hash
            algorithm: Hash algorithm (sha256, sha512, md5)
            
        Returns:
            Hexadecimal hash string
        """
        if algorithm == 'sha256':
            return hashlib.sha256(data.encode()).hexdigest()
        elif algorithm == 'sha512':
            return hashlib.sha512(data.encode()).hexdigest()
        elif algorithm == 'md5':
            return hashlib.md5(data.encode()).hexdigest()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    
    @staticmethod
    def hmac_sign(data: str, key: str, algorithm: str = 'sha256') -> str:
        """
        Create HMAC signature for data.
        
        Args:
            data: Data to sign
            key: Signing key
            algorithm: HMAC algorithm
            
        Returns:
            HMAC signature as hexadecimal string
        """
        if algorithm == 'sha256':
            digest = hashlib.sha256
        elif algorithm == 'sha512':
            digest = hashlib.sha512
        else:
            raise ValueError(f"Unsupported HMAC algorithm: {algorithm}")
        
        signature = hmac.new(
            key.encode(),
            data.encode(),
            digest
        ).hexdigest()
        
        return signature
    
    @staticmethod
    def hmac_verify(data: str, key: str, signature: str, algorithm: str = 'sha256') -> bool:
        """
        Verify HMAC signature.
        
        Args:
            data: Original data
            key: Signing key
            signature: HMAC signature to verify
            algorithm: HMAC algorithm
            
        Returns:
            True if signature is valid
        """
        try:
            expected_signature = CryptoUtils.hmac_sign(data, key, algorithm)
            return hmac.compare_digest(signature, expected_signature)
        except Exception:
            return False
    
    def encrypt_string(self, plaintext: str) -> str:
        """
        Encrypt a string using Fernet symmetric encryption.
        
        Args:
            plaintext: String to encrypt
            
        Returns:
            Base64 encoded encrypted string
        """
        try:
            encrypted = self._fernet.encrypt(plaintext.encode())
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            raise EncryptionError(f"Failed to encrypt string: {e}")
    
    def decrypt_string(self, ciphertext: str) -> str:
        """
        Decrypt a string using Fernet symmetric encryption.
        
        Args:
            ciphertext: Base64 encoded encrypted string
            
        Returns:
            Decrypted plaintext string
        """
        try:
            encrypted_data = base64.b64decode(ciphertext.encode())
            decrypted = self._fernet.decrypt(encrypted_data)
            return decrypted.decode()
        except Exception as e:
            raise DecryptionError(f"Failed to decrypt string: {e}")
    
    def encrypt_dict(self, data: Dict[str, Any]) -> str:
        """
        Encrypt a dictionary as JSON.
        
        Args:
            data: Dictionary to encrypt
            
        Returns:
            Base64 encoded encrypted JSON string
        """
        try:
            json_string = json.dumps(data, ensure_ascii=False)
            return self.encrypt_string(json_string)
        except Exception as e:
            raise EncryptionError(f"Failed to encrypt dictionary: {e}")
    
    def decrypt_dict(self, ciphertext: str) -> Dict[str, Any]:
        """
        Decrypt an encrypted dictionary.
        
        Args:
            ciphertext: Base64 encoded encrypted JSON string
            
        Returns:
            Decrypted dictionary
        """
        try:
            json_string = self.decrypt_string(ciphertext)
            return json.loads(json_string)
        except Exception as e:
            raise DecryptionError(f"Failed to decrypt dictionary: {e}")
    
    def encrypt_file(self, file_path: str, output_path: Optional[str] = None) -> str:
        """
        Encrypt a file.
        
        Args:
            file_path: Path to file to encrypt
            output_path: Output path (defaults to file_path + '.enc')
            
        Returns:
            Path to encrypted file
        """
        if output_path is None:
            output_path = file_path + '.enc'
        
        try:
            with open(file_path, 'rb') as infile:
                plaintext = infile.read()
            
            encrypted = self._fernet.encrypt(plaintext)
            
            with open(output_path, 'wb') as outfile:
                outfile.write(encrypted)
            
            self.logger.info(f"File encrypted: {file_path} -> {output_path}")
            return output_path
            
        except Exception as e:
            raise EncryptionError(f"Failed to encrypt file {file_path}: {e}")
    
    def decrypt_file(self, file_path: str, output_path: Optional[str] = None) -> str:
        """
        Decrypt a file.
        
        Args:
            file_path: Path to encrypted file
            output_path: Output path (defaults to file_path without '.enc')
            
        Returns:
            Path to decrypted file
        """
        if output_path is None:
            if file_path.endswith('.enc'):
                output_path = file_path[:-4]
            else:
                output_path = file_path + '.dec'
        
        try:
            with open(file_path, 'rb') as infile:
                encrypted = infile.read()
            
            plaintext = self._fernet.decrypt(encrypted)
            
            with open(output_path, 'wb') as outfile:
                outfile.write(plaintext)
            
            self.logger.info(f"File decrypted: {file_path} -> {output_path}")
            return output_path
            
        except Exception as e:
            raise DecryptionError(f"Failed to decrypt file {file_path}: {e}")
    
    def create_signature(self, data: str) -> str:
        """
        Create a signature for data using the master key.
        
        Args:
            data: Data to sign
            
        Returns:
            Base64 encoded signature
        """
        signature = hmac.new(
            self.master_key,
            data.encode(),
            hashlib.sha256
        ).digest()
        
        return base64.b64encode(signature).decode()
    
    def verify_signature(self, data: str, signature: str) -> bool:
        """
        Verify a signature for data.
        
        Args:
            data: Original data
            signature: Base64 encoded signature
            
        Returns:
            True if signature is valid
        """
        try:
            expected_signature = self.create_signature(data)
            return hmac.compare_digest(signature, expected_signature)
        except Exception:
            return False
    
    def derive_key_from_password(self, password: str, salt: Optional[bytes] = None) -> bytes:
        """
        Derive an encryption key from a password.
        
        Args:
            password: Password to derive key from
            salt: Salt bytes (generated if not provided)
            
        Returns:
            Derived key bytes
        """
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        return kdf.derive(password.encode())
    
    def _create_fernet_cipher(self, key: bytes) -> Fernet:
        """Create a Fernet cipher instance from a key."""
        # Derive Fernet key from master key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'telegram_bot_framework',  # Fixed salt for consistency
            iterations=100000,
            backend=default_backend()
        )
        
        fernet_key = base64.urlsafe_b64encode(kdf.derive(key))
        return Fernet(fernet_key)
    
    @staticmethod
    def secure_compare(a: str, b: str) -> bool:
        """
        Securely compare two strings to prevent timing attacks.
        
        Args:
            a: First string
            b: Second string
            
        Returns:
            True if strings are equal
        """
        return hmac.compare_digest(a.encode(), b.encode())


class EnvCrypto:
    """
    Utility class for encrypting/decrypting environment variables.
    
    Provides methods to secure .env files and configuration data.
    """
    
    def __init__(self, key: Optional[str] = None):
        """
        Initialize environment crypto utility.
        
        Args:
            key: Encryption key (generated if not provided)
        """
        self.crypto = CryptoUtils(key)
        self.logger = get_logger(__name__)
    
    def encrypt_env_file(self, env_path: str, output_path: Optional[str] = None) -> str:
        """
        Encrypt an .env file.
        
        Args:
            env_path: Path to .env file
            output_path: Output path (defaults to env_path + '.enc')
            
        Returns:
            Path to encrypted file
        """
        if output_path is None:
            output_path = env_path + '.enc'
        
        try:
            # Read and parse .env file
            env_data = {}
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_data[key.strip()] = value.strip()
            
            # Encrypt the data
            encrypted_data = self.crypto.encrypt_dict(env_data)
            
            # Write encrypted file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(encrypted_data)
            
            self.logger.info(f"Environment file encrypted: {env_path} -> {output_path}")
            return output_path
            
        except Exception as e:
            raise EncryptionError(f"Failed to encrypt env file {env_path}: {e}")
    
    def decrypt_env_file(self, encrypted_path: str, output_path: Optional[str] = None) -> str:
        """
        Decrypt an encrypted .env file.
        
        Args:
            encrypted_path: Path to encrypted file
            output_path: Output path (defaults to encrypted_path without '.enc')
            
        Returns:
            Path to decrypted .env file
        """
        if output_path is None:
            if encrypted_path.endswith('.enc'):
                output_path = encrypted_path[:-4]
            else:
                output_path = encrypted_path + '.env'
        
        try:
            # Read encrypted file
            with open(encrypted_path, 'r', encoding='utf-8') as f:
                encrypted_data = f.read()
            
            # Decrypt the data
            env_data = self.crypto.decrypt_dict(encrypted_data)
            
            # Write .env file
            with open(output_path, 'w', encoding='utf-8') as f:
                for key, value in env_data.items():
                    f.write(f"{key}={value}\n")
            
            self.logger.info(f"Environment file decrypted: {encrypted_path} -> {output_path}")
            return output_path
            
        except Exception as e:
            raise DecryptionError(f"Failed to decrypt env file {encrypted_path}: {e}")
    
    def encrypt_env_value(self, value: str) -> str:
        """
        Encrypt a single environment variable value.
        
        Args:
            value: Value to encrypt
            
        Returns:
            Encrypted value with prefix
        """
        encrypted = self.crypto.encrypt_string(value)
        return f"ENC[{encrypted}]"
    
    def decrypt_env_value(self, value: str) -> str:
        """
        Decrypt a single environment variable value.
        
        Args:
            value: Value to decrypt (with ENC[] prefix)
            
        Returns:
            Decrypted value
        """
        if value.startswith("ENC[") and value.endswith("]"):
            encrypted_value = value[4:-1]
            return self.crypto.decrypt_string(encrypted_value)
        else:
            # Not encrypted, return as-is
            return value
    
    def is_encrypted_value(self, value: str) -> bool:
        """
        Check if a value is encrypted.
        
        Args:
            value: Value to check
            
        Returns:
            True if value is encrypted
        """
        return value.startswith("ENC[") and value.endswith("]")


def generate_encryption_key() -> str:
    """
    Generate a new encryption key for the framework.
    
    Returns:
        Base64 encoded encryption key
    """
    key = CryptoUtils.generate_key(32)
    return base64.b64encode(key).decode()


def create_secure_token(length: int = 32) -> str:
    """
    Create a secure token for API keys, session tokens, etc.
    
    Args:
        length: Token length in bytes
        
    Returns:
        URL-safe token string
    """
    return CryptoUtils.generate_token(length, url_safe=True)
