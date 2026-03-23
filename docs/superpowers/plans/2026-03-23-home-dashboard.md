# Home Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Home Dashboard page that shows an at-a-glance overview of the user's job-search state: profile summary, document/application stats, referral contacts, and a daily task checklist.

**Architecture:** A single `GET /api/dashboard` endpoint aggregates data from the profile JSON, document metadata, applications DB, and a new tasks table. The React frontend renders this data in a viewport-contained layout with scrollable cards. Two new DB tables (`tasks`, `settings`) support the to-do system and configurable daily target.

**Tech Stack:** FastAPI (Python), SQLite, React 19, TypeScript, Vitest, `@testing-library/react`

---

## File Structure

### Backend (new files)

| File | Responsibility |
|------|----------------|
| `backend/routers/dashboard.py` | `GET /api/dashboard` — aggregates profile, documents, applications, tasks |
| `backend/routers/tasks.py` | CRUD endpoints for user-defined tasks (`GET/POST/PATCH/DELETE /api/tasks`) |
| `backend/routers/settings.py` | `GET/PUT /api/settings/{key}` — key-value settings store |
| `backend/tests/test_tasks_api.py` | Tests for tasks CRUD and due-date logic |
| `backend/tests/test_settings_api.py` | Tests for settings CRUD |
| `backend/tests/test_dashboard_api.py` | Tests for the aggregation endpoint |

### Backend (modified files)

| File | Change |
|------|--------|
| `backend/services/database.py` | Add `tasks` and `settings` table DDL + seed data to `SCHEMA` |
| `backend/main.py` | Register `dashboard_router`, `tasks_router`, `settings_router` |

### Frontend (new files)

| File | Responsibility |
|------|----------------|
| `src/components/home/Dashboard.tsx` | Page component — fetches `/api/dashboard`, renders layout |
| `src/components/home/ProfileBanner.tsx` | Profile summary card |
| `src/components/home/StatCard.tsx` | Reusable stat card with pill badge breakdowns |
| `src/components/home/DailyTasks.tsx` | Task checklist with built-in goals + user tasks |
| `src/components/home/ReferralPopover.tsx` | Popover listing referral contacts |
| `src/components/home/PlaceholderCard.tsx` | Phase II "Coming Soon" placeholder |
| `src/__tests__/home/Dashboard.test.tsx` | Tests for Dashboard page |
| `src/__tests__/home/StatCard.test.tsx` | Tests for StatCard component |
| `src/__tests__/home/DailyTasks.test.tsx` | Tests for DailyTasks component |
| `src/__tests__/home/ProfileBanner.test.tsx` | Tests for ProfileBanner component |

### Frontend (modified files)

| File | Change |
|------|--------|
| `src/App.tsx` | Add `/home` route, change default redirect to `/home` |
| `src/components/shared/NavBar.tsx` | Add "Home" NavLink as first item |
| `src/index.css` | Add dashboard layout styles |

---

## Task 1: Database Schema — Add `tasks` and `settings` Tables

**Files:**
- Modify: `backend/services/database.py`
- Test: `backend/tests/test_database.py`

- [ ] **Step 1: Write the failing test**

In `backend/tests/test_database.py`, add tests that verify the new tables exist after `init_db`:

```python
def test_tasks_table_exists(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    conn = get_connection(db_path)
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'").fetchall()
    conn.close()
    assert len(rows) == 1


def test_settings_table_exists(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    conn = get_connection(db_path)
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='settings'").fetchall()
    conn.close()
    assert len(rows) == 1


def test_default_daily_target_seeded(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    conn = get_connection(db_path)
    row = conn.execute("SELECT value FROM settings WHERE key = 'daily_application_target'").fetchone()
    conn.close()
    assert row is not None
    assert row["value"] == "5"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && .venv/Scripts/python -m pytest tests/test_database.py -v`
Expected: FAIL — tables do not exist yet

- [ ] **Step 3: Add tables to SCHEMA in database.py**

Append to the `SCHEMA` string in `backend/services/database.py`:

```sql
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    recurrence TEXT,
    interval_days INTEGER,
    completed_at DATETIME,
    created_at DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

INSERT OR IGNORE INTO settings (key, value) VALUES ('daily_application_target', '5');
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && .venv/Scripts/python -m pytest tests/test_database.py -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add backend/services/database.py backend/tests/test_database.py
git commit -m "feat: add tasks and settings tables to database schema"
```

---

## Task 2: Settings API — `GET/PUT /api/settings/{key}`

**Files:**
- Create: `backend/routers/settings.py`
- Create: `backend/tests/test_settings_api.py`
- Modify: `backend/main.py`

- [ ] **Step 1: Write the failing tests**

Create `backend/tests/test_settings_api.py`:

```python
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.database import init_db
import backend.routers.settings as settings_mod


def setup_test_env(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    settings_mod._db_path = db_path


def test_get_seeded_setting(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.get("/api/settings/daily_application_target")
    assert response.status_code == 200
    assert response.json() == {"key": "daily_application_target", "value": "5"}


def test_get_missing_setting_returns_404(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.get("/api/settings/nonexistent")
    assert response.status_code == 404


def test_put_setting_creates_new(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.put("/api/settings/theme", json={"value": "dark"})
    assert response.status_code == 200
    get_resp = client.get("/api/settings/theme")
    assert get_resp.json()["value"] == "dark"


def test_put_setting_updates_existing(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    client.put("/api/settings/daily_application_target", json={"value": "10"})
    response = client.get("/api/settings/daily_application_target")
    assert response.json()["value"] == "10"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && .venv/Scripts/python -m pytest tests/test_settings_api.py -v`
Expected: FAIL — module/routes don't exist

- [ ] **Step 3: Implement the settings router**

Create `backend/routers/settings.py`:

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.config import DATABASE_PATH
from backend.services.database import get_connection
from pathlib import Path

router = APIRouter(prefix="/api/settings", tags=["settings"])

_db_path: Path | None = None


def get_db():
    global _db_path
    path = _db_path or DATABASE_PATH
    return get_connection(path)


class PutSettingRequest(BaseModel):
    value: str


@router.get("/{key}")
async def get_setting(key: str):
    conn = get_db()
    row = conn.execute("SELECT key, value FROM settings WHERE key = ?", (key,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Setting not found")
    return dict(row)


@router.put("/{key}")
async def put_setting(key: str, body: PutSettingRequest):
    conn = get_db()
    conn.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = ?",
        (key, body.value, body.value),
    )
    conn.commit()
    row = conn.execute("SELECT key, value FROM settings WHERE key = ?", (key,)).fetchone()
    conn.close()
    return dict(row)
```

- [ ] **Step 4: Register router in main.py**

In `backend/main.py`, add:

```python
from backend.routers.settings import router as settings_router
```

And add `app.include_router(settings_router)` after the existing router registrations.

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd backend && .venv/Scripts/python -m pytest tests/test_settings_api.py -v`
Expected: ALL PASS

- [ ] **Step 6: Commit**

```bash
git add backend/routers/settings.py backend/tests/test_settings_api.py backend/main.py
git commit -m "feat: add settings API (GET/PUT /api/settings/{key})"
```

---

## Task 3: Tasks API — CRUD for User-Defined Tasks

**Files:**
- Create: `backend/routers/tasks.py`
- Create: `backend/tests/test_tasks_api.py`
- Modify: `backend/main.py`

- [ ] **Step 1: Write the failing tests**

Create `backend/tests/test_tasks_api.py`:

```python
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.database import init_db, get_connection
import backend.routers.tasks as tasks_mod


def setup_test_env(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    tasks_mod._db_path = db_path
    return db_path


def test_list_tasks_empty(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.get("/api/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_create_task_one_time(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.post("/api/tasks", json={"title": "Tailor resume"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Tailor resume"
    assert data["recurrence"] is None
    assert data["interval_days"] is None
    assert data["id"] is not None


def test_create_task_daily(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.post("/api/tasks", json={"title": "Check email", "recurrence": "daily"})
    data = response.json()
    assert data["recurrence"] == "daily"
    assert data["interval_days"] == 1


def test_create_task_weekly(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.post("/api/tasks", json={"title": "Review connections", "recurrence": "weekly"})
    data = response.json()
    assert data["recurrence"] == "weekly"
    assert data["interval_days"] == 7


def test_create_task_custom(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.post("/api/tasks", json={"title": "Network", "recurrence": "custom", "interval_days": 3})
    data = response.json()
    assert data["recurrence"] == "custom"
    assert data["interval_days"] == 3


def test_patch_task_complete(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    create = client.post("/api/tasks", json={"title": "Do thing"})
    task_id = create.json()["id"]
    response = client.patch(f"/api/tasks/{task_id}", json={"completed": True})
    assert response.status_code == 200
    assert response.json()["completed_at"] is not None


def test_patch_task_uncomplete(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    create = client.post("/api/tasks", json={"title": "Do thing"})
    task_id = create.json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"completed": True})
    response = client.patch(f"/api/tasks/{task_id}", json={"completed": False})
    assert response.json()["completed_at"] is None


def test_patch_task_title(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    create = client.post("/api/tasks", json={"title": "Old title"})
    task_id = create.json()["id"]
    response = client.patch(f"/api/tasks/{task_id}", json={"title": "New title"})
    assert response.json()["title"] == "New title"


def test_delete_task(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    create = client.post("/api/tasks", json={"title": "Temp"})
    task_id = create.json()["id"]
    response = client.delete(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    listing = client.get("/api/tasks")
    assert len(listing.json()) == 0


def test_delete_nonexistent_task_returns_404(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.delete("/api/tasks/999")
    assert response.status_code == 404
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && .venv/Scripts/python -m pytest tests/test_tasks_api.py -v`
Expected: FAIL — module doesn't exist

- [ ] **Step 3: Implement the tasks router**

Create `backend/routers/tasks.py`:

```python
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

    # Note: To convert a recurring task to one-time, send recurrence as empty string "".
    # Pydantic cannot distinguish None (not sent) from null (explicit null) without sentinel values.


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
    cursor = conn.execute(
        "INSERT INTO tasks (title, recurrence, interval_days, created_at) VALUES (?, ?, ?, ?)",
        (body.title, body.recurrence, interval, now),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (cursor.lastrowid,)).fetchone()
    conn.close()
    return dict(row)


@router.patch("/{task_id}")
async def patch_task(task_id: int, body: PatchTaskRequest):
    conn = get_db()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")

    updates = []
    params = []
    if body.title is not None:
        updates.append("title = ?")
        params.append(body.title)
    if body.recurrence is not None:
        # Empty string means "clear recurrence" (convert to one-time)
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
    conn.close()
    return dict(row)


@router.delete("/{task_id}")
async def delete_task(task_id: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted"}
```

- [ ] **Step 4: Register router in main.py**

In `backend/main.py`, add:

```python
from backend.routers.tasks import router as tasks_router
```

And add `app.include_router(tasks_router)` after the existing router registrations.

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd backend && .venv/Scripts/python -m pytest tests/test_tasks_api.py -v`
Expected: ALL PASS

- [ ] **Step 6: Commit**

```bash
git add backend/routers/tasks.py backend/tests/test_tasks_api.py backend/main.py
git commit -m "feat: add tasks API (CRUD for user-defined tasks)"
```

---

## Task 4: Dashboard API — `GET /api/dashboard`

**Files:**
- Create: `backend/routers/dashboard.py`
- Create: `backend/tests/test_dashboard_api.py`
- Modify: `backend/main.py`

- [ ] **Step 1: Write the failing tests**

Create `backend/tests/test_dashboard_api.py`:

```python
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.database import init_db, get_connection
from backend.services.encryption import EncryptionService
from backend.services.metadata import MetadataService
from backend.services.profile import ProfileService
import backend.config as config
import backend.routers.dashboard as dashboard_mod
import backend.routers.tasks as tasks_mod
import backend.routers.settings as settings_mod
import backend.routers.applications as apps_mod
from cryptography.fernet import Fernet
from pathlib import Path
import json


def setup_test_env(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    key = Fernet.generate_key().decode()
    config.ENCRYPTION_KEY = key

    docs_dir = tmp_path / "documents"
    docs_dir.mkdir(exist_ok=True)

    profile_path = docs_dir / ".profile.json"
    profile_path.write_text(json.dumps({
        "summary": "Test engineer with 5 years experience",
        "skills": ["Python", "React", "TypeScript", "Go", "Rust"],
        "experience": [
            {"company": "Acme", "role": "Senior Dev", "start_date": "2021", "end_date": None},
            {"company": "OldCo", "role": "Junior Dev", "start_date": "2018", "end_date": "2021"},
        ],
        "education": [],
        "certifications": [],
        "objectives": "",
    }))

    meta_service = MetadataService(docs_dir)
    meta_data = meta_service.read()
    meta_data["files"] = {
        "abc1": {"original_name": "resume1.pdf", "tags": ["resume"]},
        "abc2": {"original_name": "resume2.pdf", "tags": ["resume"]},
        "abc3": {"original_name": "cover.pdf", "tags": ["cover-letter"]},
    }
    meta_service.save(meta_data)

    dashboard_mod._db_path = db_path
    dashboard_mod._profile_service = ProfileService(profile_path)
    dashboard_mod._metadata_service = meta_service
    tasks_mod._db_path = db_path
    settings_mod._db_path = db_path
    apps_mod._db_path = db_path
    apps_mod._encryption = EncryptionService(key)
    apps_mod._metadata_service = meta_service

    return db_path


def test_dashboard_returns_profile(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    profile = response.json()["profile"]
    assert "Test engineer" in profile["summary"]
    assert profile["skills"] == ["Python", "React", "TypeScript", "Go", "Rust"]
    assert "Senior Dev at Acme" in profile["current_role"]


def test_dashboard_returns_document_counts(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.get("/api/dashboard")
    docs = response.json()["documents"]
    assert docs["total"] == 3
    assert docs["by_tag"]["resume"] == 2
    assert docs["by_tag"]["cover-letter"] == 1


def test_dashboard_returns_application_stats(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    client.post("/api/applications", json={"company": "A", "position": "E", "status": "applied"})
    client.post("/api/applications", json={"company": "B", "position": "E", "status": "bookmarked"})
    client.post("/api/applications", json={"company": "C", "position": "E", "status": "applied",
                                            "has_referral": True, "referral_name": "Jane"})
    response = client.get("/api/dashboard")
    apps = response.json()["applications"]
    assert apps["total"] == 3
    assert apps["by_status"]["applied"] == 2
    assert apps["by_status"]["bookmarked"] == 1
    assert apps["referrals"]["total"] == 1
    assert apps["referrals"]["contacts"][0]["name"] == "Jane"
    assert apps["referrals"]["contacts"][0]["company"] == "C"


def test_dashboard_returns_tasks(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.get("/api/dashboard")
    tasks = response.json()["tasks"]
    assert tasks["daily_target"] == 5
    assert tasks["applied_today"] >= 0
    assert isinstance(tasks["statuses_current"], bool)
    assert isinstance(tasks["user_tasks"], list)


def test_dashboard_applied_today_count(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    # Create an application with status != bookmarked (created today)
    client.post("/api/applications", json={"company": "X", "position": "E", "status": "applied"})
    # Create a bookmarked one (should not count)
    client.post("/api/applications", json={"company": "Y", "position": "E", "status": "bookmarked"})
    response = client.get("/api/dashboard")
    assert response.json()["tasks"]["applied_today"] == 1


def test_dashboard_stale_status_detection(tmp_path):
    db_path = setup_test_env(tmp_path)
    client = TestClient(app)
    # Create an application and manually backdate its updated_at to 10 days ago
    client.post("/api/applications", json={"company": "Stale", "position": "E", "status": "applied"})
    conn = get_connection(db_path)
    old_date = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
    conn.execute("UPDATE applications SET updated_at = ? WHERE company = 'Stale'", (old_date,))
    conn.commit()
    conn.close()
    response = client.get("/api/dashboard")
    tasks = response.json()["tasks"]
    assert tasks["statuses_current"] is False
    assert tasks["stale_count"] == 1


def test_dashboard_task_due_logic(tmp_path):
    db_path = setup_test_env(tmp_path)
    client = TestClient(app)
    # One-time task, never completed => due
    client.post("/api/tasks", json={"title": "One-time"})
    # Daily task, completed today => not due
    create = client.post("/api/tasks", json={"title": "Daily", "recurrence": "daily"})
    task_id = create.json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"completed": True})

    response = client.get("/api/dashboard")
    user_tasks = response.json()["tasks"]["user_tasks"]
    one_time = next(t for t in user_tasks if t["title"] == "One-time")
    daily = next(t for t in user_tasks if t["title"] == "Daily")
    assert one_time["is_due"] is True
    assert one_time["completed_today"] is False
    assert daily["is_due"] is False
    assert daily["completed_today"] is True


def test_dashboard_empty_profile(tmp_path):
    db_path = setup_test_env(tmp_path)
    # Overwrite profile with empty state
    client = TestClient(app)
    dashboard_mod._profile_service.put({
        "summary": "", "skills": [], "experience": [], "education": [], "certifications": [], "objectives": ""
    })
    response = client.get("/api/dashboard")
    profile = response.json()["profile"]
    assert profile["summary"] == ""
    assert profile["skills"] == []
    assert profile["current_role"] is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && .venv/Scripts/python -m pytest tests/test_dashboard_api.py -v`
Expected: FAIL — module doesn't exist

- [ ] **Step 3: Implement the dashboard router**

Create `backend/routers/dashboard.py`:

```python
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
    # Daily target from settings
    setting = conn.execute(
        "SELECT value FROM settings WHERE key = 'daily_application_target'"
    ).fetchone()
    daily_target = int(setting["value"]) if setting else 5

    # Applied today: non-bookmarked applications created today
    today = date.today().isoformat()
    applied_today = conn.execute(
        "SELECT COUNT(*) as cnt FROM applications WHERE status != 'bookmarked' AND date(created_at) = ?",
        (today,),
    ).fetchone()["cnt"]

    # Stale statuses: applied/in_progress with updated_at > 7 days ago
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    stale_count = conn.execute(
        "SELECT COUNT(*) as cnt FROM applications WHERE status IN ('applied', 'in_progress') AND updated_at < ?",
        (cutoff,),
    ).fetchone()["cnt"]

    # User tasks with due/completed computation
    task_rows = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC").fetchall()
    user_tasks = []
    for t in task_rows:
        completed_at = t["completed_at"]
        completed_today = False
        is_due = True

        if completed_at:
            completed_date = completed_at[:10]  # ISO date prefix
            completed_today = completed_date == today
            if t["recurrence"] is None:
                # One-time task: done permanently
                is_due = False
            else:
                # Recurring: due if completed_at + interval_days <= today
                interval = t["interval_days"] or 1
                completed_dt = datetime.fromisoformat(completed_at)
                next_due = completed_dt + timedelta(days=interval)
                is_due = next_due.date() <= date.today()
        # else: never completed => is_due stays True

        user_tasks.append({
            "id": t["id"],
            "title": t["title"],
            "recurrence": t["recurrence"],
            "interval_days": t["interval_days"],
            "is_due": is_due,
            "completed_today": completed_today,
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
```

- [ ] **Step 4: Register router in main.py**

In `backend/main.py`, add:

```python
from backend.routers.dashboard import router as dashboard_router
```

And add `app.include_router(dashboard_router)` after the existing router registrations.

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd backend && .venv/Scripts/python -m pytest tests/test_dashboard_api.py -v`
Expected: ALL PASS

- [ ] **Step 6: Run all backend tests**

Run: `cd backend && .venv/Scripts/python -m pytest tests/ -v`
Expected: ALL PASS — no regressions

- [ ] **Step 7: Commit**

```bash
git add backend/routers/dashboard.py backend/tests/test_dashboard_api.py backend/main.py
git commit -m "feat: add dashboard aggregation endpoint (GET /api/dashboard)"
```

---

## Task 5: Frontend — Routing and NavBar Updates

**Files:**
- Modify: `src/App.tsx`
- Modify: `src/components/shared/NavBar.tsx`
- Modify: `src/__tests__/App.test.tsx`

- [ ] **Step 1: Update the existing test file with new assertions**

In `src/__tests__/App.test.tsx`, add a `fetch` stub (the Dashboard component will fetch on mount), preserve existing tests, and add a test for the new Home nav link:

```typescript
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import App from '../App'

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({
      profile: { summary: '', skills: [], current_role: null },
      documents: { total: 0, by_tag: {} },
      applications: { total: 0, by_status: {}, referrals: { total: 0, contacts: [] } },
      tasks: { daily_target: 5, applied_today: 0, statuses_current: true, stale_count: 0, user_tasks: [] },
    }),
  }))
})

describe('App routing', () => {
  it('renders navigation bar', () => {
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    )
    expect(screen.getByRole('navigation')).toBeInTheDocument()
  })

  it('has links to all sections', () => {
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    )
    expect(screen.getByRole('link', { name: /home/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /documents/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /profile/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /applications/i })).toBeInTheDocument()
  })
})
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `npx vitest run src/__tests__/App.test.tsx`
Expected: FAIL — no "Home" link exists yet

- [ ] **Step 3: Create a minimal Dashboard placeholder**

Create `src/components/home/Dashboard.tsx`:

```typescript
export default function Dashboard() {
  return <div data-testid="dashboard">Dashboard</div>
}
```

- [ ] **Step 4: Update App.tsx**

```typescript
import { lazy, Suspense } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { NavBar } from './components/shared/NavBar'

const Dashboard = lazy(() => import('./components/home/Dashboard'))
const DocumentManager = lazy(() => import('./components/documents/DocumentManager'))
const ProfileView = lazy(() => import('./components/profile/ProfileView'))
const ApplicationManager = lazy(() => import('./components/applications/ApplicationManager'))

function App() {
  return (
    <div className="app">
      <NavBar />
      <main className="main-content">
        <Suspense fallback={<div className="loading">Loading...</div>}>
          <Routes>
            <Route path="/" element={<Navigate to="/home" replace />} />
            <Route path="/home" element={<Dashboard />} />
            <Route path="/documents" element={<DocumentManager />} />
            <Route path="/profile" element={<ProfileView />} />
            <Route path="/applications" element={<ApplicationManager />} />
          </Routes>
        </Suspense>
      </main>
    </div>
  )
}

export default App
```

- [ ] **Step 5: Update NavBar.tsx**

Add a Home link as the first nav item in `src/components/shared/NavBar.tsx`:

```typescript
import { NavLink } from 'react-router-dom'

export function NavBar() {
  return (
    <nav className="navbar">
      <div className="navbar-brand">hAId-hunter</div>
      <div className="navbar-links">
        <NavLink to="/home" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
          Home
        </NavLink>
        <NavLink to="/documents" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
          Documents
        </NavLink>
        <NavLink to="/profile" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
          Profile
        </NavLink>
        <NavLink to="/applications" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
          Applications
        </NavLink>
      </div>
    </nav>
  )
}
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `npx vitest run src/__tests__/App.test.tsx`
Expected: ALL PASS

- [ ] **Step 7: Commit**

```bash
git add src/App.tsx src/components/shared/NavBar.tsx src/components/home/Dashboard.tsx src/__tests__/App.test.tsx
git commit -m "feat: add /home route and Home nav link"
```

---

## Task 6: Frontend — StatCard Component

**Files:**
- Create: `src/components/home/StatCard.tsx`
- Create: `src/__tests__/home/StatCard.test.tsx`

- [ ] **Step 1: Write the failing tests**

Create `src/__tests__/home/StatCard.test.tsx`:

```typescript
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { StatCard } from '../../components/home/StatCard'

describe('StatCard', () => {
  it('renders the title and total', () => {
    render(<StatCard title="Documents" total={12} subtitle="total documents" breakdowns={[]} />)
    expect(screen.getByText('Documents')).toBeInTheDocument()
    expect(screen.getByText('12')).toBeInTheDocument()
    expect(screen.getByText('total documents')).toBeInTheDocument()
  })

  it('renders pill badges for breakdowns', () => {
    render(
      <StatCard
        title="Documents"
        total={12}
        subtitle="total documents"
        breakdowns={[
          { label: 'resume', count: 5 },
          { label: 'cover-letter', count: 4 },
        ]}
      />
    )
    expect(screen.getByText('resume 5')).toBeInTheDocument()
    expect(screen.getByText('cover-letter 4')).toBeInTheDocument()
  })

  it('renders zero state when total is 0', () => {
    render(<StatCard title="Documents" total={0} subtitle="total documents" breakdowns={[]} />)
    expect(screen.getByText('0')).toBeInTheDocument()
    expect(screen.getByText('No documents yet')).toBeInTheDocument()
  })

  it('renders action slot when provided', () => {
    render(
      <StatCard
        title="Referrals"
        total={3}
        subtitle="total referrals"
        breakdowns={[]}
        action={<button>View all</button>}
      />
    )
    expect(screen.getByText('View all')).toBeInTheDocument()
  })
})
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `npx vitest run src/__tests__/home/StatCard.test.tsx`
Expected: FAIL — module doesn't exist

- [ ] **Step 3: Implement StatCard**

Create `src/components/home/StatCard.tsx`:

```typescript
import { ReactNode } from 'react'

interface Breakdown {
  label: string
  count: number
  color?: string
}

interface StatCardProps {
  title: string
  total: number
  subtitle: string
  breakdowns: Breakdown[]
  action?: ReactNode
  emptyMessage?: string
}

export function StatCard({ title, total, subtitle, breakdowns, action, emptyMessage }: StatCardProps) {
  return (
    <div className="dashboard-card stat-card">
      <div className="stat-card-header">{title}</div>
      <div className="stat-card-total">{total}</div>
      <div className="stat-card-subtitle">{subtitle}</div>
      {total === 0 && (
        <div className="stat-card-empty">{emptyMessage || `No ${title.toLowerCase()} yet`}</div>
      )}
      {breakdowns.length > 0 && (
        <div className="stat-card-breakdowns">
          {breakdowns.map((b) => (
            <span
              key={b.label}
              className="stat-pill"
              style={b.color ? { '--pill-color': b.color } as React.CSSProperties : undefined}
            >
              {b.label} {b.count}
            </span>
          ))}
        </div>
      )}
      {action && <div className="stat-card-action">{action}</div>}
    </div>
  )
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `npx vitest run src/__tests__/home/StatCard.test.tsx`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add src/components/home/StatCard.tsx src/__tests__/home/StatCard.test.tsx
git commit -m "feat: add StatCard component with pill badge breakdowns"
```

---

## Task 7: Frontend — ProfileBanner Component

**Files:**
- Create: `src/components/home/ProfileBanner.tsx`
- Create: `src/__tests__/home/ProfileBanner.test.tsx`

- [ ] **Step 1: Write the failing tests**

Create `src/__tests__/home/ProfileBanner.test.tsx`:

```typescript
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import { ProfileBanner } from '../../components/home/ProfileBanner'

describe('ProfileBanner', () => {
  it('renders summary and current role', () => {
    render(
      <MemoryRouter>
        <ProfileBanner
          summary="Full-stack engineer with 8 years experience"
          skills={['TypeScript', 'React', 'Python', 'Go', 'Rust']}
          currentRole="Senior Dev at Acme (2021 - Present)"
        />
      </MemoryRouter>
    )
    expect(screen.getByText(/Full-stack engineer/)).toBeInTheDocument()
    expect(screen.getByText(/Senior Dev at Acme/)).toBeInTheDocument()
  })

  it('shows first 3 skills plus overflow count', () => {
    render(
      <MemoryRouter>
        <ProfileBanner
          summary="Engineer"
          skills={['TypeScript', 'React', 'Python', 'Go', 'Rust']}
          currentRole={null}
        />
      </MemoryRouter>
    )
    expect(screen.getByText('TypeScript')).toBeInTheDocument()
    expect(screen.getByText('React')).toBeInTheDocument()
    expect(screen.getByText('Python')).toBeInTheDocument()
    expect(screen.getByText('+2 more')).toBeInTheDocument()
    expect(screen.queryByText('Go')).not.toBeInTheDocument()
  })

  it('shows empty state when no summary', () => {
    render(
      <MemoryRouter>
        <ProfileBanner summary="" skills={[]} currentRole={null} />
      </MemoryRouter>
    )
    expect(screen.getByText(/Set up your profile/)).toBeInTheDocument()
  })
})
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `npx vitest run src/__tests__/home/ProfileBanner.test.tsx`
Expected: FAIL — module doesn't exist

- [ ] **Step 3: Implement ProfileBanner**

Create `src/components/home/ProfileBanner.tsx`:

```typescript
import { Link } from 'react-router-dom'

interface ProfileBannerProps {
  summary: string
  skills: string[]
  currentRole: string | null
}

const MAX_VISIBLE_SKILLS = 3

export function ProfileBanner({ summary, skills, currentRole }: ProfileBannerProps) {
  const isEmpty = !summary && skills.length === 0

  if (isEmpty) {
    return (
      <div className="dashboard-card profile-banner">
        <div className="card-header">Profile</div>
        <div className="profile-banner-empty">
          <Link to="/profile">Set up your profile</Link> to see a summary here
        </div>
      </div>
    )
  }

  const visibleSkills = skills.slice(0, MAX_VISIBLE_SKILLS)
  const overflow = skills.length - MAX_VISIBLE_SKILLS

  return (
    <div className="dashboard-card profile-banner">
      <div className="card-header">Profile</div>
      <div className="profile-banner-summary">{summary}</div>
      {visibleSkills.length > 0 && (
        <div className="profile-banner-skills">
          {visibleSkills.map((s) => (
            <span key={s} className="skill-pill">{s}</span>
          ))}
          {overflow > 0 && <span className="skill-pill">+{overflow} more</span>}
        </div>
      )}
      {currentRole && <div className="profile-banner-role">{currentRole}</div>}
    </div>
  )
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `npx vitest run src/__tests__/home/ProfileBanner.test.tsx`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add src/components/home/ProfileBanner.tsx src/__tests__/home/ProfileBanner.test.tsx
git commit -m "feat: add ProfileBanner component"
```

---

## Task 8: Frontend — DailyTasks Component

**Files:**
- Create: `src/components/home/DailyTasks.tsx`
- Create: `src/__tests__/home/DailyTasks.test.tsx`

- [ ] **Step 1: Write the failing tests**

Create `src/__tests__/home/DailyTasks.test.tsx`:

```typescript
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { DailyTasks } from '../../components/home/DailyTasks'

const baseProps = {
  dailyTarget: 5,
  appliedToday: 2,
  statusesCurrent: true,
  staleCount: 0,
  userTasks: [],
  onToggleTask: vi.fn(),
  onAddTask: vi.fn(),
}

describe('DailyTasks', () => {
  it('renders built-in apply goal with progress', () => {
    render(<DailyTasks {...baseProps} />)
    expect(screen.getByText('Apply for positions')).toBeInTheDocument()
    expect(screen.getByText('2 of 5 today')).toBeInTheDocument()
  })

  it('shows done pill when apply target met', () => {
    render(<DailyTasks {...baseProps} appliedToday={5} />)
    expect(screen.getByText('done')).toBeInTheDocument()
  })

  it('renders status update goal as current', () => {
    render(<DailyTasks {...baseProps} />)
    expect(screen.getByText('Update application statuses')).toBeInTheDocument()
    expect(screen.getByText('All statuses current')).toBeInTheDocument()
  })

  it('renders stale status count', () => {
    render(<DailyTasks {...baseProps} statusesCurrent={false} staleCount={3} />)
    expect(screen.getByText('3 need update')).toBeInTheDocument()
  })

  it('renders user tasks', () => {
    render(
      <DailyTasks
        {...baseProps}
        userTasks={[
          { id: 1, title: 'Review LinkedIn', recurrence: 'custom', interval_days: 3, is_due: true, completed_today: false },
          { id: 2, title: 'Tailor resume', recurrence: null, interval_days: null, is_due: true, completed_today: false },
        ]}
      />
    )
    expect(screen.getByText('Review LinkedIn')).toBeInTheDocument()
    expect(screen.getByText('Tailor resume')).toBeInTheDocument()
  })

  it('calls onToggleTask when checkbox clicked', () => {
    const onToggle = vi.fn()
    render(
      <DailyTasks
        {...baseProps}
        onToggleTask={onToggle}
        userTasks={[
          { id: 1, title: 'Test task', recurrence: null, interval_days: null, is_due: true, completed_today: false },
        ]}
      />
    )
    fireEvent.click(screen.getByTestId('task-checkbox-1'))
    expect(onToggle).toHaveBeenCalledWith(1, true)
  })

  it('shows empty message with no user tasks', () => {
    render(<DailyTasks {...baseProps} />)
    expect(screen.getByText('No custom tasks yet.')).toBeInTheDocument()
  })
})
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `npx vitest run src/__tests__/home/DailyTasks.test.tsx`
Expected: FAIL — module doesn't exist

- [ ] **Step 3: Implement DailyTasks**

Create `src/components/home/DailyTasks.tsx`:

```typescript
interface UserTask {
  id: number
  title: string
  recurrence: string | null
  interval_days: number | null
  is_due: boolean
  completed_today: boolean
}

interface DailyTasksProps {
  dailyTarget: number
  appliedToday: number
  statusesCurrent: boolean
  staleCount: number
  userTasks: UserTask[]
  onToggleTask: (id: number, completed: boolean) => void
  onAddTask: () => void
}

function getApplyStatus(applied: number, target: number) {
  if (applied >= target) return 'done'
  if (applied > 0) return 'in progress'
  return 'pending'
}

function getStatusPillClass(status: string) {
  switch (status) {
    case 'done': return 'task-pill task-pill-done'
    case 'in progress': return 'task-pill task-pill-progress'
    default: return 'task-pill task-pill-muted'
  }
}

function recurrenceLabel(task: UserTask) {
  if (!task.recurrence) return 'One-time'
  if (task.recurrence === 'daily') return 'Daily'
  if (task.recurrence === 'weekly') return 'Weekly'
  return `Every ${task.interval_days} days`
}

export function DailyTasks({
  dailyTarget,
  appliedToday,
  statusesCurrent,
  staleCount,
  userTasks,
  onToggleTask,
  onAddTask,
}: DailyTasksProps) {
  const applyStatus = getApplyStatus(appliedToday, dailyTarget)

  return (
    <div className="dashboard-card daily-tasks">
      <div className="daily-tasks-header">
        <div className="card-header">Daily Tasks</div>
        <button className="daily-tasks-add" onClick={onAddTask}>+ Add Task</button>
      </div>

      <div className="daily-tasks-list">
        {/* Built-in: Apply for positions */}
        <div className={`task-row ${applyStatus === 'done' ? 'task-completed' : ''}`}>
          <div className={`task-checkbox ${applyStatus === 'done' ? 'task-checkbox-done' : ''}`}>
            {applyStatus === 'done' && '✓'}
          </div>
          <div className="task-content">
            <div className="task-title">Apply for positions</div>
            <div className="task-subtitle">{appliedToday} of {dailyTarget} today</div>
          </div>
          <span className={getStatusPillClass(applyStatus)}>{applyStatus}</span>
        </div>

        {/* Built-in: Update statuses */}
        <div className={`task-row ${statusesCurrent ? 'task-completed' : ''}`}>
          <div className={`task-checkbox ${statusesCurrent ? 'task-checkbox-done' : ''}`}>
            {statusesCurrent && '✓'}
          </div>
          <div className="task-content">
            <div className="task-title">Update application statuses</div>
            <div className="task-subtitle">
              {statusesCurrent ? 'All statuses current' : `${staleCount} need update`}
            </div>
          </div>
          <span className={statusesCurrent ? 'task-pill task-pill-done' : 'task-pill task-pill-progress'}>
            {statusesCurrent ? 'done' : 'in progress'}
          </span>
        </div>

        {/* User tasks */}
        {userTasks.map((task) => (
          <div key={task.id} className={`task-row ${task.completed_today ? 'task-completed' : ''}`}>
            <div
              data-testid={`task-checkbox-${task.id}`}
              className={`task-checkbox ${task.completed_today ? 'task-checkbox-done' : ''}`}
              onClick={() => onToggleTask(task.id, !task.completed_today)}
            >
              {task.completed_today && '✓'}
            </div>
            <div className="task-content">
              <div className="task-title">{task.title}</div>
              <div className="task-subtitle">{recurrenceLabel(task)}</div>
            </div>
            <span className={task.completed_today ? 'task-pill task-pill-done' : `task-pill task-pill-muted`}>
              {task.completed_today ? 'done' : (task.recurrence ? 'recurring' : 'one-time')}
            </span>
          </div>
        ))}

        {userTasks.length === 0 && (
          <div className="daily-tasks-empty">No custom tasks yet.</div>
        )}
      </div>
    </div>
  )
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `npx vitest run src/__tests__/home/DailyTasks.test.tsx`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add src/components/home/DailyTasks.tsx src/__tests__/home/DailyTasks.test.tsx
git commit -m "feat: add DailyTasks component with built-in goals and user tasks"
```

---

## Task 9: Frontend — ReferralPopover and PlaceholderCard Components

**Files:**
- Create: `src/components/home/ReferralPopover.tsx`
- Create: `src/components/home/PlaceholderCard.tsx`
- Create: `src/__tests__/home/ReferralPopover.test.tsx`

- [ ] **Step 1: Write the failing tests for ReferralPopover**

Create `src/__tests__/home/ReferralPopover.test.tsx`:

```typescript
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { ReferralPopover } from '../../components/home/ReferralPopover'

const contacts = [
  { name: 'Jane', company: 'Google', application_id: 1 },
  { name: 'Bob', company: 'Meta', application_id: 2 },
]

describe('ReferralPopover', () => {
  it('renders trigger button', () => {
    render(<ReferralPopover contacts={contacts} />)
    expect(screen.getByText('View all referrals →')).toBeInTheDocument()
  })

  it('shows popover with contacts on click', () => {
    render(<ReferralPopover contacts={contacts} />)
    fireEvent.click(screen.getByText('View all referrals →'))
    expect(screen.getByTestId('referral-popover')).toBeInTheDocument()
    expect(screen.getByText('Jane')).toBeInTheDocument()
    expect(screen.getByText('Google')).toBeInTheDocument()
    expect(screen.getByText('Bob')).toBeInTheDocument()
  })

  it('hides popover on second click', () => {
    render(<ReferralPopover contacts={contacts} />)
    const trigger = screen.getByText('View all referrals →')
    fireEvent.click(trigger)
    expect(screen.getByTestId('referral-popover')).toBeInTheDocument()
    fireEvent.click(trigger)
    expect(screen.queryByTestId('referral-popover')).not.toBeInTheDocument()
  })
})
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `npx vitest run src/__tests__/home/ReferralPopover.test.tsx`
Expected: FAIL — module doesn't exist

- [ ] **Step 3: Create ReferralPopover**

Create `src/components/home/ReferralPopover.tsx`:

```typescript
import { useState, useRef, useEffect } from 'react'

interface ReferralContact {
  name: string
  company: string
  application_id: number
}

interface ReferralPopoverProps {
  contacts: ReferralContact[]
}

export function ReferralPopover({ contacts }: ReferralPopoverProps) {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    if (open) document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [open])

  return (
    <div className="referral-popover-container" ref={ref}>
      <button className="referral-popover-trigger" onClick={() => setOpen(!open)}>
        View all referrals →
      </button>
      {open && (
        <div className="referral-popover" data-testid="referral-popover">
          {contacts.map((c) => (
            <div key={c.application_id} className="referral-popover-item">
              <span className="referral-name">{c.name}</span>
              <span className="referral-company">{c.company}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 4: Create PlaceholderCard**

Create `src/components/home/PlaceholderCard.tsx`:

```typescript
export function PlaceholderCard() {
  return (
    <div className="dashboard-card placeholder-card">
      <div className="card-header">Phase II</div>
      <div className="placeholder-title">Next Steps</div>
      <div className="placeholder-subtitle">Claude-driven suggestions</div>
    </div>
  )
}
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `npx vitest run src/__tests__/home/ReferralPopover.test.tsx`
Expected: ALL PASS

- [ ] **Step 6: Commit**

```bash
git add src/components/home/ReferralPopover.tsx src/components/home/PlaceholderCard.tsx src/__tests__/home/ReferralPopover.test.tsx
git commit -m "feat: add ReferralPopover and PlaceholderCard components"
```

---

## Task 10: Frontend — Dashboard Page Component (Integration)

**Files:**
- Modify: `src/components/home/Dashboard.tsx`
- Create: `src/__tests__/home/Dashboard.test.tsx`

- [ ] **Step 1: Write the failing tests**

Create `src/__tests__/home/Dashboard.test.tsx`:

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import Dashboard from '../../components/home/Dashboard'

const mockDashboardData = {
  profile: {
    summary: 'Full-stack engineer with 8 years experience',
    skills: ['TypeScript', 'React', 'Python', 'Go'],
    current_role: 'Senior Dev at Acme (2021 - Present)',
  },
  documents: {
    total: 12,
    by_tag: { resume: 5, 'cover-letter': 4, cv: 3 },
  },
  applications: {
    total: 23,
    by_status: { bookmarked: 8, applied: 5, in_progress: 6, offer: 2, closed: 2 },
    referrals: {
      total: 2,
      contacts: [
        { name: 'Jane', company: 'Google', application_id: 1 },
        { name: 'Bob', company: 'Meta', application_id: 2 },
      ],
    },
  },
  tasks: {
    daily_target: 5,
    applied_today: 2,
    statuses_current: true,
    stale_count: 0,
    user_tasks: [
      { id: 1, title: 'Review LinkedIn', recurrence: 'custom', interval_days: 3, is_due: true, completed_today: false },
    ],
  },
}

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
    ok: true,
    json: async () => mockDashboardData,
  }))
})

describe('Dashboard', () => {
  it('renders profile banner after loading', async () => {
    render(<MemoryRouter><Dashboard /></MemoryRouter>)
    expect(await screen.findByText(/Full-stack engineer/)).toBeInTheDocument()
  })

  it('renders document stat card', async () => {
    render(<MemoryRouter><Dashboard /></MemoryRouter>)
    expect(await screen.findByText('Documents')).toBeInTheDocument()
    expect(screen.getByText('12')).toBeInTheDocument()
  })

  it('renders application stat card', async () => {
    render(<MemoryRouter><Dashboard /></MemoryRouter>)
    expect(await screen.findByText('Applications')).toBeInTheDocument()
    expect(screen.getByText('23')).toBeInTheDocument()
  })

  it('renders referrals card with popover trigger', async () => {
    render(<MemoryRouter><Dashboard /></MemoryRouter>)
    expect(await screen.findByText('Referrals')).toBeInTheDocument()
    expect(screen.getByText('View all referrals →')).toBeInTheDocument()
  })

  it('opens referral popover on click', async () => {
    render(<MemoryRouter><Dashboard /></MemoryRouter>)
    const trigger = await screen.findByText('View all referrals →')
    fireEvent.click(trigger)
    expect(screen.getByTestId('referral-popover')).toBeInTheDocument()
    expect(screen.getByText('Jane')).toBeInTheDocument()
  })

  it('renders daily tasks section', async () => {
    render(<MemoryRouter><Dashboard /></MemoryRouter>)
    expect(await screen.findByText('Daily Tasks')).toBeInTheDocument()
    expect(screen.getByText('Apply for positions')).toBeInTheDocument()
    expect(screen.getByText('Review LinkedIn')).toBeInTheDocument()
  })

  it('renders phase II placeholder', async () => {
    render(<MemoryRouter><Dashboard /></MemoryRouter>)
    expect(await screen.findByText('Phase II')).toBeInTheDocument()
    expect(screen.getByText('Next Steps')).toBeInTheDocument()
  })

  it('shows error state on fetch failure', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false }))
    render(<MemoryRouter><Dashboard /></MemoryRouter>)
    expect(await screen.findByText(/failed to load/i)).toBeInTheDocument()
    expect(screen.getByText('Retry')).toBeInTheDocument()
  })
})
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `npx vitest run src/__tests__/home/Dashboard.test.tsx`
Expected: FAIL — Dashboard is a placeholder

- [ ] **Step 3: Implement Dashboard.tsx**

Replace `src/components/home/Dashboard.tsx` with the full implementation:

```typescript
import { useState, useEffect, useCallback } from 'react'
import { ProfileBanner } from './ProfileBanner'
import { StatCard } from './StatCard'
import { DailyTasks } from './DailyTasks'
import { ReferralPopover } from './ReferralPopover'
import { PlaceholderCard } from './PlaceholderCard'

const STATUS_COLORS: Record<string, string> = {
  bookmarked: 'var(--color-muted)',
  applied: 'var(--color-secondary)',
  in_progress: 'var(--color-accent)',
  offer: 'var(--color-success)',
  closed: 'var(--color-error)',
}

interface DashboardData {
  profile: { summary: string; skills: string[]; current_role: string | null }
  documents: { total: number; by_tag: Record<string, number> }
  applications: {
    total: number
    by_status: Record<string, number>
    referrals: { total: number; contacts: Array<{ name: string; company: string; application_id: number }> }
  }
  tasks: {
    daily_target: number
    applied_today: number
    statuses_current: boolean
    stale_count: number
    user_tasks: Array<{
      id: number; title: string; recurrence: string | null;
      interval_days: number | null; is_due: boolean; completed_today: boolean
    }>
  }
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [error, setError] = useState(false)

  const fetchDashboard = useCallback(async () => {
    setError(false)
    try {
      const res = await fetch('/api/dashboard')
      if (!res.ok) throw new Error('fetch failed')
      setData(await res.json())
    } catch {
      setError(true)
    }
  }, [])

  useEffect(() => { fetchDashboard() }, [fetchDashboard])

  const handleToggleTask = async (id: number, completed: boolean) => {
    await fetch(`/api/tasks/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ completed }),
    })
    fetchDashboard()
  }

  const handleAddTask = () => {
    // Out of scope for this plan. The add-task modal/form will be implemented
    // as a follow-up after the dashboard is functional. The backend CRUD is ready.
  }

  if (error) {
    return (
      <div className="dashboard" data-testid="dashboard">
        <div className="dashboard-error">
          <p>Failed to load dashboard data.</p>
          <button className="btn btn-primary" onClick={fetchDashboard}>Retry</button>
        </div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="dashboard" data-testid="dashboard">
        <div className="loading">Loading...</div>
      </div>
    )
  }

  const docBreakdowns = Object.entries(data.documents.by_tag).map(([label, count]) => ({ label, count }))
  const appBreakdowns = Object.entries(data.applications.by_status).map(([label, count]) => ({
    label,
    count,
    color: STATUS_COLORS[label],
  }))

  return (
    <div className="dashboard" data-testid="dashboard">
      <ProfileBanner
        summary={data.profile.summary}
        skills={data.profile.skills}
        currentRole={data.profile.current_role}
      />

      <div className="dashboard-stats-row">
        <StatCard title="Documents" total={data.documents.total} subtitle="total documents" breakdowns={docBreakdowns} />
        <StatCard title="Applications" total={data.applications.total} subtitle="total applications" breakdowns={appBreakdowns} />
        <StatCard
          title="Referrals"
          total={data.applications.referrals.total}
          subtitle="total referrals"
          breakdowns={[]}
          action={
            data.applications.referrals.contacts.length > 0
              ? <ReferralPopover contacts={data.applications.referrals.contacts} />
              : undefined
          }
        />
      </div>

      <div className="dashboard-bottom-row">
        <DailyTasks
          dailyTarget={data.tasks.daily_target}
          appliedToday={data.tasks.applied_today}
          statusesCurrent={data.tasks.statuses_current}
          staleCount={data.tasks.stale_count}
          userTasks={data.tasks.user_tasks}
          onToggleTask={handleToggleTask}
          onAddTask={handleAddTask}
        />
        <PlaceholderCard />
      </div>
    </div>
  )
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `npx vitest run src/__tests__/home/Dashboard.test.tsx`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add src/components/home/Dashboard.tsx src/__tests__/home/Dashboard.test.tsx
git commit -m "feat: implement Dashboard page with data fetching and all subcomponents"
```

---

## Task 11: CSS — Dashboard Layout Styles

**Files:**
- Modify: `src/index.css`

- [ ] **Step 1: Add dashboard styles to index.css**

Append the following to `src/index.css`:

```css
/* ── Dashboard ─────────────────────────────────────────── */
.dashboard {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
  padding: var(--space-lg);
  overflow: hidden;
}

.dashboard-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--color-muted);
  gap: var(--space-md);
}

.dashboard-stats-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: var(--space-md);
}

.dashboard-bottom-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-md);
  flex: 1;
  min-height: 0;
}

/* ── Dashboard Card (shared) ───────────────────────────── */
.dashboard-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-md);
  overflow-y: auto;
  min-height: 0;
}

.card-header {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-muted);
  margin-bottom: var(--space-sm);
}

/* ── Profile Banner ────────────────────────────────────── */
.profile-banner { overflow: hidden; }
.profile-banner-summary { font-size: 16px; font-weight: 600; margin-bottom: var(--space-xs); }
.profile-banner-skills { display: flex; gap: 6px; flex-wrap: wrap; margin-top: var(--space-sm); }
.profile-banner-role { font-size: 13px; color: var(--color-muted); margin-top: var(--space-sm); }
.profile-banner-empty { font-size: 14px; color: var(--color-muted); }
.profile-banner-empty a { color: var(--color-primary); text-decoration: underline; }

.skill-pill {
  background: rgba(123, 147, 212, 0.15);
  color: var(--color-secondary);
  padding: 3px 10px;
  border-radius: var(--radius-full);
  font-size: 12px;
}

/* ── Stat Card (extends .dashboard-card) ───────────────── */
.stat-card-header { font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: var(--color-muted); margin-bottom: var(--space-sm); }
.stat-card-total { font-size: 28px; font-weight: 700; color: var(--color-text); }
.stat-card-subtitle { font-size: 12px; color: var(--color-muted); margin-top: var(--space-xs); }
.stat-card-empty { font-size: 12px; color: var(--color-muted); margin-top: var(--space-sm); }
.stat-card-breakdowns { margin-top: var(--space-sm); display: flex; gap: 6px; flex-wrap: wrap; }
.stat-card-action { margin-top: var(--space-sm); }

.stat-pill {
  background: rgba(123, 147, 212, 0.15);
  color: var(--pill-color, var(--color-secondary));
  padding: 3px 10px;
  border-radius: var(--radius-full);
  font-size: 11px;
}

/* ── Daily Tasks ───────────────────────────────────────── */
.daily-tasks { display: flex; flex-direction: column; }
.daily-tasks-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-md); }
.daily-tasks-add { font-size: 12px; color: var(--color-primary); cursor: pointer; background: none; border: none; }
.daily-tasks-list { display: flex; flex-direction: column; gap: 10px; overflow-y: auto; flex: 1; min-height: 0; }
.daily-tasks-empty { font-size: 13px; color: var(--color-muted); padding: var(--space-sm) 0; }

.task-row {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: 10px 14px;
  background: var(--color-elevated);
  border-radius: var(--radius-md);
}
.task-completed .task-content { opacity: 0.6; text-decoration: line-through; }
.task-checkbox {
  width: 18px; height: 18px;
  border: 2px solid var(--color-border);
  border-radius: var(--radius-sm);
  flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; font-size: 12px;
}
.task-checkbox-done {
  border-color: var(--color-success);
  background: rgba(16, 185, 129, 0.15);
  color: var(--color-success);
}
.task-content { flex: 1; }
.task-title { font-size: 14px; }
.task-subtitle { font-size: 12px; color: var(--color-muted); }

.task-pill { font-size: 12px; padding: 2px 8px; border-radius: var(--radius-full); }
.task-pill-done { background: rgba(16, 185, 129, 0.15); color: var(--color-success); }
.task-pill-progress { background: rgba(245, 158, 11, 0.15); color: var(--color-accent); }
.task-pill-muted { background: rgba(107, 127, 163, 0.15); color: var(--color-muted); }

/* ── Referral Popover ──────────────────────────────────── */
.referral-popover-container { position: relative; }
.referral-popover-trigger {
  font-size: 12px; color: var(--color-primary);
  cursor: pointer; text-decoration: underline;
  background: none; border: none;
}
.referral-popover {
  position: absolute; bottom: 100%; left: 0;
  background: var(--color-elevated); border: 1px solid var(--color-border);
  border-radius: var(--radius-md); padding: var(--space-sm);
  min-width: 200px; z-index: 10;
  box-shadow: var(--shadow-md);
}
.referral-popover-item {
  display: flex; justify-content: space-between;
  font-size: 12px; padding: var(--space-xs) 0;
}
.referral-popover-item + .referral-popover-item { border-top: 1px solid rgba(46, 63, 92, 0.4); }
.referral-name { color: var(--color-text); }
.referral-company { color: var(--color-muted); }

/* ── Placeholder Card ──────────────────────────────────── */
.placeholder-card {
  border-style: dashed;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  text-align: center;
}
.placeholder-title { font-size: 14px; color: var(--color-muted); }
.placeholder-subtitle { font-size: 12px; color: var(--color-primary); margin-top: var(--space-xs); }
```

- [ ] **Step 2: Run all frontend tests**

Run: `npx vitest run`
Expected: ALL PASS — no regressions

- [ ] **Step 3: Commit**

```bash
git add src/index.css
git commit -m "feat: add dashboard layout and component styles"
```

---

## Task 12: Run All Tests and Final Verification

- [ ] **Step 1: Run all backend tests**

Run: `cd backend && .venv/Scripts/python -m pytest tests/ -v`
Expected: ALL PASS

- [ ] **Step 2: Run all frontend tests**

Run: `npx vitest run`
Expected: ALL PASS

- [ ] **Step 3: Start the dev server and visually verify**

Run: `npm run dev` (in one terminal) and `cd backend && python -m uvicorn backend.main:app --reload` (in another)

Navigate to `http://localhost:5173` — should redirect to `/home` and show the dashboard.

Verify:
- Profile banner shows (or empty state if no profile)
- Three stat cards render with correct pill badges
- Referral popover opens on click
- Daily Tasks section shows built-in goals and any user tasks
- Phase II placeholder is visible
- No page-level scrolling — individual cards scroll when content overflows
- NavBar has "Home" as first link and it's active

- [ ] **Step 4: Commit any fixes if needed**

```bash
git add -A
git commit -m "fix: address any issues found during visual verification"
```
