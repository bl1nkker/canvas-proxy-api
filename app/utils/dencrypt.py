from cryptography.fernet import Fernet

from app_config import get_app_config

ENCRYPTION_KEY = get_app_config().secure_key


def encrypt(text: str, key=ENCRYPTION_KEY) -> str:
    cipher = Fernet(key.encode())
    return cipher.encrypt(text.encode()).decode()


def decrypt(encrypted_text: str, key=ENCRYPTION_KEY) -> str:
    cipher = Fernet(key.encode())
    return cipher.decrypt(encrypted_text.encode()).decode()
