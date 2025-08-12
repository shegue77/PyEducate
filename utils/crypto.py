import keyring
from cryptography.fernet import Fernet

SERVICE_NAME = "PyEducate Launcher"
KEY_NAME = "ConfigID"

def _write_key():
    key = Fernet.generate_key()
    keyring.set_password(SERVICE_NAME, KEY_NAME, key.decode())
    return key

def load_or_create_key():
    key_str = keyring.get_password(SERVICE_NAME, KEY_NAME)
    if key_str is None:
        return _write_key()
    return key_str.encode()


def encrypt_file(message):
    key = load_or_create_key()
    f = Fernet(key)
    if isinstance(message, bytes):
        return f.encrypt(message)
    else:
        return f.encrypt(message.encode("utf-8"))


def decrypt_file(encrypted_bytes):
    key = load_or_create_key()
    f = Fernet(key)
    return f.decrypt(encrypted_bytes).decode("utf-8")
