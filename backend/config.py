import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).parent.parent
DOCUMENTS_DIR = PROJECT_ROOT / "documents"
DATA_DIR = PROJECT_ROOT / "data"
PROFILE_PATH = DOCUMENTS_DIR / ".profile.json"
METADATA_PATH = DOCUMENTS_DIR / ".metadata.json"
DATABASE_PATH = DATA_DIR / "applications.db"

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "text/markdown",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/csv",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
}

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".xlsx", ".csv", ".pptx"}

MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50 MB

ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


def get_api_key() -> str | None:
    """Hybrid lookup: check DB (encrypted) first, fall back to .env."""
    try:
        from backend.services.database import get_connection
        from backend.services.encryption import EncryptionService
        conn = get_connection()
        row = conn.execute("SELECT value FROM settings WHERE key = ?", ("anthropic_api_key",)).fetchone()
        conn.close()
        if row:
            enc = EncryptionService()
            decrypted = enc.decrypt(row["value"])
            if decrypted:
                return decrypted
    except Exception:
        pass
    return ANTHROPIC_API_KEY
