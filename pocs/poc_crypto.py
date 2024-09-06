from cryptography.fernet import Fernet
import base64

# Define a literal string
literal_string = "mysecretpassword1234567890123456"  # Must be 32 characters

# Ensure the literal string is exactly 32 characters
if len(literal_string) != 32:
    raise ValueError("The literal string must be exactly 32 characters long.")

# Convert the literal string to bytes
key_bytes = literal_string.encode()

# Encode the byte string in URL-safe base64 format
key = base64.urlsafe_b64encode(key_bytes)

# Encrypt a string
fernet = Fernet(key)
original_string = "Hello, World!"
encrypted_string = fernet.encrypt(original_string.encode())

print(f"Encrypted: {encrypted_string}")

# Decrypt the string
decrypted_string = fernet.decrypt(encrypted_string).decode()

print(f"Decrypted: {decrypted_string}")

# Convert key_bytes back to string (if needed)
decoded_key_string = key_bytes.decode('utf-8')

print(f"Decoded Key String: {decoded_key_string}")