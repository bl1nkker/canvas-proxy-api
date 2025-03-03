from cryptography.fernet import Fernet

from app_config import get_app_config

ENCRYPTION_KEY = get_app_config().encryption_key
cipher = Fernet(ENCRYPTION_KEY.encode())


def encrypt_password(text: str) -> str:
    return cipher.encrypt(text.encode()).decode()


def decrypt_password(encrypted_text: str) -> str:
    """Расшифровывает пароль перед использованием"""
    return cipher.decrypt(encrypted_text.encode()).decode()
