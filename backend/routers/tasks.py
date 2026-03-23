from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.config import DATABASE_PATH
from backend.services.database import get_connection
from pathlib import Path

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

_db_path: Path | None = None

RECURRENCE_INTERVALS = {"daily": 1, "weekly": 7}


def get_db():
    global _db_path
    path = _db_path or DATABASE_PATH
    return get_connection(path)


class CreateTaskRequest(BaseModel):
    title: str
    recurrence: str | None = None
    interval_days: int | None = None


class PatchTaskRequest(BaseModel):
    title: str | None = None
    recurrence: str | None = None
    interval_days: int | None = None
    completed: bool | None = None


@router.get("")
async def list_tasks():
    conn = get_db()
    rows = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.post("")
async def create_task(body: CreateTaskRequest):
    now = datetime.now(timezone.utc).isoformat()
    interval = body.interval_days
    if body.recurrence in RECURRENCE_INTERVALS:
        interval = RECURRENCE_INTERVALS[body.recurrence]
    conn = get_db()
    try:
        cursor = conn.execute(
            "INSERT INTO tasks (title, recurrence, interval_days, created_at) VALUES (?, ?, ?, ?)",
            (body.title, body.recurrence, interval, now),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return dict(row)
    finally:
        conn.close()


@router.patch("/{task_id}")
async def patch_task(task_id: int, body: PatchTaskRequest):
    conn = get_db()
    try:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Task not found")

        updates = []
        params = []
        if body.title is not None:
            updates.append("title = ?")
            params.append(body.title)
        if body.recurrence is not None:
            rec = body.recurrence if body.recurrence else None
            updates.append("recurrence = ?")
            params.append(rec)
            interval = body.interval_days
            if rec and rec in RECURRENCE_INTERVALS:
                interval = RECURRENCE_INTERVALS[rec]
            elif not rec:
                interval = None
            updates.append("interval_days = ?")
            params.append(interval)
        elif body.interval_days is not None:
            updates.append("interval_days = ?")
            params.append(body.interval_days)
        if body.completed is True:
            updates.append("completed_at = ?")
            params.append(datetime.now(timezone.utc).isoformat())
        elif body.completed is False:
            updates.append("completed_at = ?")
            params.append(None)

        if updates:
            params.append(task_id)
            conn.execute(f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?", params)
            conn.commit()

        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return dict(row)
    finally:
        conn.close()


@router.delete("/{task_id}")
async def delete_task(task_id: int):
    conn = get_db()
    try:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Task not found")
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        return {"status": "deleted"}
    finally:
        conn.close()
