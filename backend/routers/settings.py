import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.config import DATABASE_PATH
from backend.services.database import get_connection
from pathlib import Path

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/settings", tags=["settings"])

_db_path: Path | None = None


def get_db():
    global _db_path
    path = _db_path or DATABASE_PATH
    return get_connection(path)


class PutSettingRequest(BaseModel):
    value: str


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
