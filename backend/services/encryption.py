from cryptography.fernet import Fernet
from backend.config import ENCRYPTION_KEY
from pathlib import Path


class EncryptionService:
    def __init__(self, key: str | None = None):
        if key is None:
            key = ENCRYPTION_KEY
        if key is None:
            key = Fernet.generate_key().decode()
            env_path = Path(__file__).parent.parent.parent / ".env"
            with open(env_path, "a") as f:
                f.write(f"\nENCRYPTION_KEY={key}\n")
        self._fernet = Fernet(key.encode() if isinstance(key, str) else key)

    def encrypt(self, plaintext: str | None) -> str | None:
        if plaintext is None:
            return None
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str | None) -> str | None:
        if ciphertext is None:
            return None
        return self._fernet.decrypt(ciphertext.encode()).decode()

    @staticmethod
    def mask(value: str | None) -> str | None:
        if value is None:
            return None
        return "***"
