import os
from cryptography.fernet import Fernet


def _get_cipher() -> Fernet:
    key = os.environ.get("ENCRYPTION_KEY")
    if not key:
        raise RuntimeError("ENCRYPTION_KEY no definida en variables de entorno")
    return Fernet(key.encode())


def encrypt(value: str) -> str:
    return _get_cipher().encrypt(value.encode()).decode()


def decrypt(value: str) -> str:
    return _get_cipher().decrypt(value.encode()).decode()
