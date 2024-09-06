
# pip install cryptography

from cryptography.fernet import Fernet

# Generate a key and instantiate a Fernet instance
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Encrypt data
cipher_text = cipher_suite.encrypt(b"Sensitive Information")

# Decrypt data
plain_text = cipher_suite.decrypt(cipher_text)

print(f"Encrypted: {cipher_text}")
print(f"Decrypted: {plain_text.decode()}")