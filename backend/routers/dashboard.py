from datetime import datetime, timezone, timedelta, date
from fastapi import APIRouter
from backend.config import DATABASE_PATH, DOCUMENTS_DIR, PROFILE_PATH
from backend.services.database import get_connection
from backend.services.metadata import MetadataService
from backend.services.profile import ProfileService
from pathlib import Path

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

_db_path: Path | None = None
_profile_service: ProfileService | None = None
_metadata_service: MetadataService | None = None


def get_db():
    global _db_path
    path = _db_path or DATABASE_PATH
    return get_connection(path)


def get_profile_service() -> ProfileService:
    global _profile_service
    if _profile_service is None:
        _profile_service = ProfileService(PROFILE_PATH)
    return _profile_service


def get_metadata_service() -> MetadataService:
    global _metadata_service
    if _metadata_service is None:
        _metadata_service = MetadataService(DOCUMENTS_DIR)
    return _metadata_service


def _build_profile_section() -> dict:
    profile = get_profile_service().get()
    current_role = None
    for exp in profile.get("experience", []):
        if exp.get("end_date") is None:
            current_role = f"{exp['role']} at {exp['company']} ({exp['start_date']} - Present)"
            break
    return {
        "summary": profile.get("summary", ""),
        "skills": profile.get("skills", []),
        "current_role": current_role,
    }


def _build_documents_section() -> dict:
    meta = get_metadata_service().read()
    files = meta.get("files", {})
    by_tag: dict[str, int] = {}
    for file_meta in files.values():
        for tag in file_meta.get("tags", []):
            by_tag[tag] = by_tag.get(tag, 0) + 1
    return {
        "total": len(files),
        "by_tag": by_tag,
    }


def _build_applications_section(conn) -> dict:
    rows = conn.execute("SELECT * FROM applications").fetchall()
    total = len(rows)
    by_status: dict[str, int] = {}
    referral_contacts = []
    for row in rows:
        status = row["status"]
        by_status[status] = by_status.get(status, 0) + 1
        if row["has_referral"]:
            referral_contacts.append({
                "name": row["referral_name"],
                "company": row["company"],
                "application_id": row["id"],
            })
    return {
        "total": total,
        "by_status": by_status,
        "referrals": {
            "total": len(referral_contacts),
            "contacts": referral_contacts,
        },
    }


def _build_tasks_section(conn) -> dict:
    setting = conn.execute(
        "SELECT value FROM settings WHERE key = 'daily_application_target'"
    ).fetchone()
    daily_target = int(setting["value"]) if setting else 5

    today = datetime.now(timezone.utc).date().isoformat()
    applied_today = conn.execute(
        "SELECT COUNT(*) as cnt FROM applications WHERE status != 'bookmarked' AND date(created_at) = ?",
        (today,),
    ).fetchone()["cnt"]

    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    stale_count = conn.execute(
        "SELECT COUNT(*) as cnt FROM applications WHERE status IN ('applied', 'in_progress') AND updated_at < ?",
        (cutoff,),
    ).fetchone()["cnt"]

    task_rows = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC").fetchall()
    user_tasks = []
    for t in task_rows:
        completed_at = t["completed_at"]
        completed_today = False
        is_due = True

        if completed_at:
            completed_date = completed_at[:10]
            completed_today = completed_date == today
            if t["recurrence"] is None:
                is_due = False
            else:
                interval = t["interval_days"] or 1
                completed_dt = datetime.fromisoformat(completed_at)
                next_due = completed_dt + timedelta(days=interval)
                is_due = next_due.date() <= datetime.now(timezone.utc).date()

        user_tasks.append({
            "id": t["id"],
            "title": t["title"],
            "recurrence": t["recurrence"],
            "interval_days": t["interval_days"],
            "is_due": is_due,
            "completed_today": completed_today,
            "completed_at": completed_at,
        })

    return {
        "daily_target": daily_target,
        "applied_today": applied_today,
        "statuses_current": stale_count == 0,
        "stale_count": stale_count,
        "user_tasks": user_tasks,
    }


@router.get("")
async def get_dashboard():
    conn = get_db()
    try:
        profile = _build_profile_section()
        documents = _build_documents_section()
        applications = _build_applications_section(conn)
        tasks = _build_tasks_section(conn)
    finally:
        conn.close()
    return {
        "profile": profile,
        "documents": documents,
        "applications": applications,
        "tasks": tasks,
    }
