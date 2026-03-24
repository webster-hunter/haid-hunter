import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.config import DATABASE_PATH, ANTHROPIC_API_KEY
from backend.services.database import get_connection
from backend.services.encryption import EncryptionService
from pathlib import Path

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/settings", tags=["settings"])

_db_path: Path | None = None


def get_db():
    global _db_path
    path = _db_path or DATABASE_PATH
    return get_connection(path)


def get_encryption() -> EncryptionService:
    return EncryptionService()


def get_env_api_key() -> str | None:
    return ANTHROPIC_API_KEY


def build_claude_client(api_key: str):
    import anthropic
    return anthropic.Anthropic(api_key=api_key)


def _mask_key(key: str) -> str:
    if len(key) <= 8:
        return "***"
    return key[:4] + "***" + key[-4:]


def _resolve_api_key() -> tuple[str | None, str | None]:
    """Return (api_key, source) checking DB first, then env."""
    conn = get_db()
    try:
        row = conn.execute("SELECT value FROM settings WHERE key = ?", ("anthropic_api_key",)).fetchone()
        if row:
            enc = get_encryption()
            try:
                decrypted = enc.decrypt(row["value"])
                if decrypted:
                    return decrypted, "database"
            except Exception:
                pass
    finally:
        conn.close()

    env_key = get_env_api_key()
    if env_key:
        return env_key, "env"

    return None, None


class PutSettingRequest(BaseModel):
    value: str


class PutApiKeyRequest(BaseModel):
    api_key: str


# ===== API Key management =====

@router.get("/api-key")
async def get_api_key_status():
    key, source = _resolve_api_key()
    if key:
        return {"configured": True, "source": source, "masked": _mask_key(key)}
    return {"configured": False, "source": None}


@router.put("/api-key")
async def set_api_key(body: PutApiKeyRequest):
    enc = get_encryption()
    encrypted = enc.encrypt(body.api_key)
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = ?",
            ("anthropic_api_key", encrypted, encrypted),
        )
        conn.commit()
    finally:
        conn.close()
    logger.info("API key updated via settings")
    return {"configured": True, "source": "database", "masked": _mask_key(body.api_key)}


@router.delete("/api-key")
async def delete_api_key():
    conn = get_db()
    try:
        conn.execute("DELETE FROM settings WHERE key = ?", ("anthropic_api_key",))
        conn.commit()
    finally:
        conn.close()
    logger.info("API key removed from database")
    return {"status": "deleted"}


@router.post("/api-key/test")
async def test_api_key():
    key, source = _resolve_api_key()
    if not key:
        return {"valid": False, "error": "No API key configured"}
    try:
        client = build_claude_client(key)
        client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=10,
            messages=[{"role": "user", "content": "Hi"}],
        )
        return {"valid": True, "source": source}
    except Exception as e:
        error_msg = str(e)
        # Distinguish auth failures from billing/other issues
        if "credit balance" in error_msg or "purchase credits" in error_msg:
            return {"valid": True, "source": source, "warning": "API key is valid but account has insufficient credits."}
        if "401" in error_msg or "authentication" in error_msg.lower() or "invalid.*key" in error_msg.lower():
            return {"valid": False, "error": "Invalid API key"}
        return {"valid": False, "error": error_msg}


# ===== Generic key-value settings =====

@router.get("/{key}")
async def get_setting(key: str):
    conn = get_db()
    try:
        row = conn.execute("SELECT key, value FROM settings WHERE key = ?", (key,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Setting not found")
        return dict(row)
    finally:
        conn.close()


@router.put("/{key}")
async def put_setting(key: str, body: PutSettingRequest):
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = ?",
            (key, body.value, body.value),
        )
        conn.commit()
        row = conn.execute("SELECT key, value FROM settings WHERE key = ?", (key,)).fetchone()
        return dict(row)
    finally:
        conn.close()
