import os
import shutil
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

# Resolve Claude Code CLI path — prefer system-installed over bundled
CLAUDE_CLI_PATH = os.getenv("CLAUDE_CLI_PATH") or shutil.which("claude")
