from keyring import get_password, set_password
from os import urandom
from base64 import urlsafe_b64encode
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet

SERVICE_NAME = "PyEducate"
KEY_NAME = ""

def _derive_key(password: str, salt: bytes) -> bytes:
    # Derive a Fernet key from a password and salt.
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,          # 32-byte key
        salt=salt,
        iterations=600_000, # adjust for desired security/performance
    )
    return urlsafe_b64encode(kdf.derive(password.encode()))

def encrypt_with_password(data: str, password: str) -> bytes:
    # Encrypt data using only a password. Returns salt+ciphertext.
    salt = urandom(16)        # random salt per file
    key = _derive_key(password, salt)
    f = Fernet(key)
    token = f.encrypt(data.encode())
    return salt + token          # prepend salt for transport/storage

def decrypt_with_password(encrypted: bytes, password: str) -> str:
    # Decrypt data using only the password.
    salt, token = encrypted[:16], encrypted[16:]  # extract salt
    key = _derive_key(password, salt)
    f = Fernet(key)
    plaintext = f.decrypt(token)
    return plaintext.decode()


def _write_key() -> bytes:
    key = Fernet.generate_key()
    set_password(SERVICE_NAME, KEY_NAME, key.decode())
    return key


def load_or_create_key():
    key_str = get_password(SERVICE_NAME, KEY_NAME)
    if key_str is None:
        return _write_key()
    return key_str.encode()


def encrypt_file(message) -> bytes:
    key = load_or_create_key()
    f = Fernet(key)
    if isinstance(message, bytes):
        return f.encrypt(message)
    else:
        return f.encrypt(message.encode("utf-8"))


def decrypt_file(encrypted_bytes) -> str:
    key = load_or_create_key()
    f = Fernet(key)
    return f.decrypt(encrypted_bytes).decode("utf-8")
