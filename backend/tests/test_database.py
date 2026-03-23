import sqlite3
from backend.services.database import init_db, get_connection


def test_init_creates_tables(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}
    assert "applications" in tables
    assert "application_documents" in tables
    conn.close()


def test_insert_and_read_application(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    conn.execute("""
        INSERT INTO applications (company, position, status, created_at, updated_at)
        VALUES (?, ?, ?, datetime('now'), datetime('now'))
    """, ("Acme", "Engineer", "bookmarked"))
    conn.commit()
    row = conn.execute("SELECT company, position, status FROM applications").fetchone()
    assert row == ("Acme", "Engineer", "bookmarked")
    conn.close()


def test_cascade_delete(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("""
        INSERT INTO applications (company, position, status, created_at, updated_at)
        VALUES (?, ?, ?, datetime('now'), datetime('now'))
    """, ("Acme", "Engineer", "applied"))
    conn.commit()
    app_id = conn.execute("SELECT id FROM applications").fetchone()[0]
    conn.execute("INSERT INTO application_documents (application_id, document_id, role) VALUES (?, ?, ?)",
                 (app_id, "doc123", "resume"))
    conn.commit()
    conn.execute("DELETE FROM applications WHERE id = ?", (app_id,))
    conn.commit()
    docs = conn.execute("SELECT * FROM application_documents WHERE application_id = ?", (app_id,)).fetchall()
    assert len(docs) == 0
    conn.close()


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
