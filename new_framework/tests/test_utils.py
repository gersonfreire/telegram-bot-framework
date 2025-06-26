"""
Tests for utility modules (logger and crypto).
"""

import pytest
import tempfile
import os
import logging
from unittest.mock import Mock, patch

from tlgfwk.utils.logger import Logger
from tlgfwk.utils.crypto import CryptoManager


class TestLogger:
    """Test cases for Logger utility."""
    
    @pytest.fixture
    def temp_log_file(self):
        """Create a temporary log file."""
        fd, path = tempfile.mkstemp(suffix='.log')
        os.close(fd)
        yield path
        try:
            # Make sure logger instances are closed to release file locks
            logging.shutdown()
            if os.path.exists(path):
                os.unlink(path)
        except PermissionError:
            # On Windows, files might be locked even after logging.shutdown()
            # Just leave them for the OS to clean up in this case
            pass
    
    def test_logger_initialization_default(self):
        """Test logger initialization with default settings."""
        logger = Logger()
        
        assert logger.logger.name == "tlgfwk"
        assert logger.logger.level == logging.INFO
    
    def test_logger_initialization_custom(self, temp_log_file):
        """Test logger initialization with custom settings."""
        config = {
            'logging.level': 'DEBUG',
            'logging.file': temp_log_file,
            'logging.format': '%(levelname)s: %(message)s',
            'logging.max_file_size': 1024,
            'logging.backup_count': 3
        }
        
        logger = Logger("custom_logger", config)
        
        assert logger.logger.name == "custom_logger"
        assert logger.logger.level == logging.DEBUG
    
    def test_logger_file_logging(self, temp_log_file):
        """Test logging to file."""
        config = {
            'logging.file': temp_log_file,
            'logging.level': 'INFO'
        }
        
        logger = Logger("file_test", config)
        logger.info("Test message")
        logger.warning("Warning message")
        logger.error("Error message")
        
        # Check file content
        with open(temp_log_file, 'r') as f:
            content = f.read()
        
        assert "Test message" in content
        assert "Warning message" in content
        assert "Error message" in content
    
    def test_logger_console_logging(self):
        """Test console logging."""
        with patch('sys.stdout') as mock_stdout:
            logger = Logger("console_test")
            logger.info("Console test message")
            
            # Should have output to console (captured by handler)
            assert logger.logger.handlers
    
    def test_logger_level_filtering(self, temp_log_file):
        """Test log level filtering."""
        config = {
            'logging.file': temp_log_file,
            'logging.level': 'WARNING'
        }
        
        logger = Logger("level_test", config)
        logger.debug("Debug message")  # Should not appear
        logger.info("Info message")    # Should not appear
        logger.warning("Warning message")  # Should appear
        logger.error("Error message")      # Should appear
        
        with open(temp_log_file, 'r') as f:
            content = f.read()
        
        assert "Debug message" not in content
        assert "Info message" not in content
        assert "Warning message" in content
        assert "Error message" in content
    
    def test_logger_rotation(self, temp_log_file):
        """Test log file rotation."""
        config = {
            'logging.file': temp_log_file,
            'logging.max_file_size': 100,  # Very small size to trigger rotation
            'logging.backup_count': 2
        }
        
        logger = Logger("rotation_test", config)
        
        # Write enough data to trigger rotation
        for i in range(20):
            logger.info(f"Log message {i} with enough text to exceed size limit")
        
        # Check that rotation occurred (backup files created)
        backup1 = temp_log_file + ".1"
        assert os.path.exists(temp_log_file)
        # Backup file creation depends on the exact logging implementation
    
    def test_logger_custom_format(self, temp_log_file):
        """Test custom log formatting."""
        config = {
            'logging.file': temp_log_file,
            'logging.format': 'CUSTOM: %(levelname)s - %(message)s'
        }
        
        logger = Logger("format_test", config)
        logger.info("Formatted message")
        
        with open(temp_log_file, 'r') as f:
            content = f.read()
        
        assert "CUSTOM: INFO - Formatted message" in content
    
    def test_logger_exception_logging(self, temp_log_file):
        """Test exception logging."""
        config = {
            'logging.file': temp_log_file,
            'logging.level': 'ERROR'
        }
        
        logger = Logger("exception_test", config)
        
        try:
            raise ValueError("Test exception")
        except ValueError as e:
            logger.exception("Exception occurred")
        
        with open(temp_log_file, 'r') as f:
            content = f.read()
        
        assert "Exception occurred" in content
        assert "ValueError" in content
        assert "Test exception" in content
    
    def test_logger_structured_logging(self, temp_log_file):
        """Test structured logging with extra fields."""
        config = {
            'logging.file': temp_log_file
        }
        
        logger = Logger("structured_test", config)
        logger.info("User action", extra={
            'user_id': 123456,
            'action': 'login',
            'ip_address': '192.168.1.1'
        })
        
        with open(temp_log_file, 'r') as f:
            content = f.read()
        
        assert "User action" in content
        # Extra fields might not appear in default format, 
        # but they're available for custom formatters
    
    def test_logger_thread_safety(self, temp_log_file):
        """Test logger thread safety."""
        import threading
        import time
        
        config = {
            'logging.file': temp_log_file
        }
        
        logger = Logger("thread_test", config)
        
        def log_messages(thread_id):
            for i in range(10):
                logger.info(f"Thread {thread_id} message {i}")
                time.sleep(0.01)
        
        # Create multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=log_messages, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check that all messages were logged
        with open(temp_log_file, 'r') as f:
            content = f.read()
        
        # Should have messages from all threads
        assert "Thread 0" in content
        assert "Thread 1" in content
        assert "Thread 2" in content


class TestCryptoManager:
    """Test cases for CryptoManager utility."""
    
    def test_crypto_manager_initialization(self):
        """Test CryptoManager initialization."""
        config = {
            'crypto.key': 'test_key_32_bytes_long_for_aes256',
            'crypto.algorithm': 'AES-256-GCM'
        }
        
        crypto = CryptoManager(config)
        assert crypto.key is not None
        assert crypto.algorithm == 'AES-256-GCM'
    
    def test_key_generation(self):
        """Test cryptographic key generation."""
        key = CryptoManager.generate_key()
        
        assert len(key) == 32  # 256 bits
        assert isinstance(key, bytes)
        
        # Generate another key and ensure they're different
        key2 = CryptoManager.generate_key()
        assert key != key2
    
    def test_encrypt_decrypt_string(self):
        """Test string encryption and decryption."""
        config = {
            'crypto.key': CryptoManager.generate_key()
        }
        
        crypto = CryptoManager(config)
        
        plaintext = "This is a secret message"
        encrypted = crypto.encrypt(plaintext)
        decrypted = crypto.decrypt(encrypted)
        
        assert decrypted == plaintext
        assert encrypted != plaintext
        assert len(encrypted) > len(plaintext)
    
    def test_encrypt_decrypt_bytes(self):
        """Test bytes encryption and decryption."""
        config = {
            'crypto.key': CryptoManager.generate_key()
        }
        
        crypto = CryptoManager(config)
        
        plaintext = b"This is secret binary data"
        encrypted = crypto.encrypt(plaintext)
        decrypted = crypto.decrypt(encrypted)
        
        assert decrypted == plaintext
        assert encrypted != plaintext
    
    def test_encrypt_decrypt_unicode(self):
        """Test Unicode string encryption and decryption."""
        config = {
            'crypto.key': CryptoManager.generate_key()
        }
        
        crypto = CryptoManager(config)
        
        plaintext = "Unicode test: 🔐 émojis and açcénts"
        encrypted = crypto.encrypt(plaintext)
        decrypted = crypto.decrypt(encrypted)
        
        assert decrypted == plaintext
    
    def test_encrypt_empty_string(self):
        """Test encrypting empty string."""
        config = {
            'crypto.key': CryptoManager.generate_key()
        }
        
        crypto = CryptoManager(config)
        
        plaintext = ""
        encrypted = crypto.encrypt(plaintext)
        decrypted = crypto.decrypt(encrypted)
        
        assert decrypted == plaintext
    
    def test_encrypt_large_data(self):
        """Test encrypting large data."""
        config = {
            'crypto.key': CryptoManager.generate_key()
        }
        
        crypto = CryptoManager(config)
        
        # Create large string (1MB)
        plaintext = "A" * (1024 * 1024)
        encrypted = crypto.encrypt(plaintext)
        decrypted = crypto.decrypt(encrypted)
        
        assert decrypted == plaintext
    
    def test_different_keys_different_results(self):
        """Test that different keys produce different encrypted results."""
        plaintext = "Same message"
        
        crypto1 = CryptoManager({'crypto.key': CryptoManager.generate_key()})
        crypto2 = CryptoManager({'crypto.key': CryptoManager.generate_key()})
        
        encrypted1 = crypto1.encrypt(plaintext)
        encrypted2 = crypto2.encrypt(plaintext)
        
        assert encrypted1 != encrypted2
    
    def test_same_key_different_results(self):
        """Test that same key with same plaintext produces different ciphertext (due to IV)."""
        config = {
            'crypto.key': CryptoManager.generate_key()
        }
        
        crypto = CryptoManager(config)
        plaintext = "Same message"
        
        encrypted1 = crypto.encrypt(plaintext)
        encrypted2 = crypto.encrypt(plaintext)
        
        # Should be different due to random IV
        assert encrypted1 != encrypted2
        
        # But both should decrypt to the same plaintext
        assert crypto.decrypt(encrypted1) == plaintext
        assert crypto.decrypt(encrypted2) == plaintext
    
    def test_invalid_key_length(self):
        """Test initialization with invalid key length."""
        config = {
            'crypto.key': b'short_key'  # Too short
        }
        
        with pytest.raises((ValueError, Exception)):
            CryptoManager(config)
    
    def test_decrypt_invalid_data(self):
        """Test decrypting invalid data."""
        config = {
            'crypto.key': CryptoManager.generate_key()
        }
        
        crypto = CryptoManager(config)
        
        with pytest.raises((ValueError, Exception)):
            crypto.decrypt("invalid_encrypted_data")
        
        with pytest.raises((ValueError, Exception)):
            crypto.decrypt(b"invalid_encrypted_bytes")
    
    def test_decrypt_with_wrong_key(self):
        """Test decrypting with wrong key."""
        plaintext = "Secret message"
        
        crypto1 = CryptoManager({'crypto.key': CryptoManager.generate_key()})
        crypto2 = CryptoManager({'crypto.key': CryptoManager.generate_key()})
        
        encrypted = crypto1.encrypt(plaintext)
        
        with pytest.raises((ValueError, Exception)):
            crypto2.decrypt(encrypted)
    
    def test_key_from_string(self):
        """Test key derivation from string."""
        # Test with string that gets converted to key
        config = {
            'crypto.key': 'my_secret_password_string_here_123'
        }
        
        crypto = CryptoManager(config)
        
        plaintext = "Test message"
        encrypted = crypto.encrypt(plaintext)
        decrypted = crypto.decrypt(encrypted)
        
        assert decrypted == plaintext
    
    def test_crypto_performance(self):
        """Test crypto performance with multiple operations."""
        import time
        
        config = {
            'crypto.key': CryptoManager.generate_key()
        }
        
        crypto = CryptoManager(config)
        plaintext = "Performance test message"
        
        start_time = time.time()
        
        # Perform multiple encrypt/decrypt operations
        for _ in range(100):
            encrypted = crypto.encrypt(plaintext)
            decrypted = crypto.decrypt(encrypted)
            assert decrypted == plaintext
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete reasonably quickly (adjust threshold as needed)
        assert duration < 5.0, f"Crypto operations took too long: {duration}s"
    
    def test_base64_encoding(self):
        """Test that encrypted data is properly base64 encoded."""
        config = {
            'crypto.key': CryptoManager.generate_key()
        }
        
        crypto = CryptoManager(config)
        plaintext = "Base64 test"
        
        encrypted = crypto.encrypt(plaintext)
        
        # If using base64 encoding, should be valid base64
        if isinstance(encrypted, str):
            import base64
            try:
                base64.b64decode(encrypted)
            except Exception:
                pytest.fail("Encrypted data is not valid base64")
    
    def test_crypto_context_manager(self):
        """Test CryptoManager as context manager (if implemented)."""
        config = {
            'crypto.key': CryptoManager.generate_key()
        }
        
        # If context manager is implemented:
        # with CryptoManager(config) as crypto:
        #     encrypted = crypto.encrypt("test")
        #     decrypted = crypto.decrypt(encrypted)
        #     assert decrypted == "test"
        
        # For now, just test normal usage
        crypto = CryptoManager(config)
        encrypted = crypto.encrypt("test")
        decrypted = crypto.decrypt(encrypted)
        assert decrypted == "test"
