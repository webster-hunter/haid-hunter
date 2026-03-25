from cryptography.fernet import Fernet
import backend.config as config
from pathlib import Path


class EncryptionService:
    def __init__(self, key: str | None = None):
        if key is None:
            key = config.ENCRYPTION_KEY
        if key is None:
            key = Fernet.generate_key().decode()
            env_path = Path(__file__).parent.parent.parent / ".env"
            # Parse .env line-by-line to check if ENCRYPTION_KEY already exists
            existing_lines = []
            has_key = False
            if env_path.exists():
                existing_lines = env_path.read_text().splitlines()
                for line in existing_lines:
                    if line.strip().startswith("ENCRYPTION_KEY="):
                        has_key = True
                        break
            if not has_key:
                with open(env_path, "a") as f:
                    f.write(f"\nENCRYPTION_KEY={key}\n")
            else:
                # Use the existing key from the file instead of overwriting
                for line in existing_lines:
                    stripped = line.strip()
                    if stripped.startswith("ENCRYPTION_KEY="):
                        key = stripped.split("=", 1)[1]
                        break
            # Update the in-process config so subsequent calls use this key
            config.ENCRYPTION_KEY = key
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
