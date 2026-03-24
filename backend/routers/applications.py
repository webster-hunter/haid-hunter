import logging
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from backend.config import DATABASE_PATH, DOCUMENTS_DIR
from backend.services.database import get_connection, init_db
from backend.services.encryption import EncryptionService
from backend.services.metadata import MetadataService
from pathlib import Path

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/applications", tags=["applications"])

_db_path: Path | None = None
_encryption: EncryptionService | None = None
_metadata_service: MetadataService | None = None


def get_db():
    global _db_path
    path = _db_path or DATABASE_PATH
    return get_connection(path)


def get_encryption() -> EncryptionService:
    global _encryption
    if _encryption is None:
        _encryption = EncryptionService()
    return _encryption


def get_metadata_service() -> MetadataService:
    global _metadata_service
    if _metadata_service is None:
        _metadata_service = MetadataService(DOCUMENTS_DIR)
    return _metadata_service


class CreateApplicationRequest(BaseModel):
    company: str
    position: str
    posting_url: str | None = None
    login_page_url: str | None = None
    login_email: str | None = None
    login_password: str | None = None
    status: str = "bookmarked"
    closed_reason: str | None = None
    has_referral: bool = False
    referral_name: str | None = None
    notes: str | None = None


class UpdateStatusRequest(BaseModel):
    status: str
    closed_reason: str | None = None


class LinkDocumentRequest(BaseModel):
    document_id: str
    role: str | None = None


def row_to_dict(row, reveal_credentials: bool = False) -> dict:
    enc = get_encryption()
    d = dict(row)
    if reveal_credentials:
        d["login_email"] = enc.decrypt(d.get("login_email"))
        d["login_password"] = enc.decrypt(d.get("login_password"))
    else:
        d["login_email"] = enc.mask(d.get("login_email"))
        d["login_password"] = enc.mask(d.get("login_password"))
    return d


@router.get("")
async def list_applications(status: str | None = None, search: str | None = None, has_referral: bool | None = None):
    conn = get_db()
    query = "SELECT * FROM applications WHERE 1=1"
    params: list = []
    if status:
        query += " AND status = ?"
        params.append(status)
    if search:
        query += " AND (company LIKE ? OR position LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    if has_referral is not None:
        query += " AND has_referral = ?"
        params.append(1 if has_referral else 0)
    query += " ORDER BY updated_at DESC"
    rows = conn.execute(query, params).fetchall()
    result = [row_to_dict(r) for r in rows]
    for item in result:
        count = conn.execute("SELECT COUNT(*) FROM application_documents WHERE application_id = ?", (item["id"],)).fetchone()[0]
        item["doc_count"] = count
    conn.close()
    return result


@router.get("/{app_id}")
async def get_application(app_id: int, reveal_credentials: bool = False):
    conn = get_db()
    row = conn.execute("SELECT * FROM applications WHERE id = ?", (app_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Application not found")
    result = row_to_dict(row, reveal_credentials)
    if reveal_credentials:
        logger.warning("Credentials revealed for application %d", app_id)
    docs = conn.execute("SELECT * FROM application_documents WHERE application_id = ?", (app_id,)).fetchall()
    conn.close()
    meta_svc = get_metadata_service()
    try:
        meta_data = meta_svc.read()
        files_meta = meta_data.get("files", {})
    except (FileNotFoundError, ValueError, KeyError) as e:
        logger.warning("Failed to read document metadata: %s", e)
        files_meta = {}
    enriched_docs = []
    for d in docs:
        doc_dict = dict(d)
        doc_id = doc_dict.get("document_id")
        if doc_id and doc_id in files_meta:
            doc_dict["original_name"] = files_meta[doc_id].get("original_name")
        else:
            doc_dict["original_name"] = None
        enriched_docs.append(doc_dict)
    result["documents"] = enriched_docs
    return result


@router.post("")
async def create_application(body: CreateApplicationRequest):
    enc = get_encryption()
    now = datetime.now(timezone.utc).isoformat()
    conn = get_db()
    cursor = conn.execute("""
        INSERT INTO applications (company, position, posting_url, login_page_url, login_email, login_password,
                                  status, closed_reason, has_referral, referral_name, notes, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (body.company, body.position, body.posting_url, body.login_page_url,
          enc.encrypt(body.login_email), enc.encrypt(body.login_password),
          body.status, body.closed_reason, body.has_referral, body.referral_name, body.notes, now, now))
    conn.commit()
    app_id = cursor.lastrowid
    row = conn.execute("SELECT * FROM applications WHERE id = ?", (app_id,)).fetchone()
    conn.close()
    logger.info("Application created: %d (%s at %s)", app_id, body.position, body.company)
    return row_to_dict(row)


@router.put("/{app_id}")
async def update_application(app_id: int, body: CreateApplicationRequest):
    enc = get_encryption()
    now = datetime.now(timezone.utc).isoformat()
    conn = get_db()
    conn.execute("""
        UPDATE applications SET company=?, position=?, posting_url=?, login_page_url=?,
        login_email=?, login_password=?, status=?, closed_reason=?, has_referral=?,
        referral_name=?, notes=?, updated_at=? WHERE id=?
    """, (body.company, body.position, body.posting_url, body.login_page_url,
          enc.encrypt(body.login_email), enc.encrypt(body.login_password),
          body.status, body.closed_reason, body.has_referral, body.referral_name, body.notes, now, app_id))
    conn.commit()
    row = conn.execute("SELECT * FROM applications WHERE id = ?", (app_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Application not found")
    return row_to_dict(row)


@router.delete("/{app_id}")
async def delete_application(app_id: int):
    conn = get_db()
    conn.execute("DELETE FROM applications WHERE id = ?", (app_id,))
    conn.commit()
    conn.close()
    logger.info("Application deleted: %d", app_id)
    return {"status": "deleted"}


@router.patch("/{app_id}/status")
async def update_status(app_id: int, body: UpdateStatusRequest):
    now = datetime.now(timezone.utc).isoformat()
    conn = get_db()
    conn.execute("UPDATE applications SET status=?, closed_reason=?, updated_at=? WHERE id=?",
                 (body.status, body.closed_reason, now, app_id))
    conn.commit()
    logger.info("Application %d status changed to '%s'", app_id, body.status)
    row = conn.execute("SELECT * FROM applications WHERE id = ?", (app_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Application not found")
    return row_to_dict(row)


@router.get("/{app_id}/documents")
async def list_linked_documents(app_id: int):
    conn = get_db()
    rows = conn.execute("SELECT * FROM application_documents WHERE application_id = ?", (app_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.post("/{app_id}/documents")
async def link_document(app_id: int, body: LinkDocumentRequest):
    conn = get_db()
    cursor = conn.execute("INSERT INTO application_documents (application_id, document_id, role) VALUES (?, ?, ?)",
                          (app_id, body.document_id, body.role))
    conn.commit()
    link_id = cursor.lastrowid
    conn.close()
    return {"id": link_id, "application_id": app_id, "document_id": body.document_id, "role": body.role}


@router.delete("/{app_id}/documents/{link_id}")
async def unlink_document(app_id: int, link_id: int):
    conn = get_db()
    conn.execute("DELETE FROM application_documents WHERE id = ? AND application_id = ?", (link_id, app_id))
    conn.commit()
    conn.close()
    return {"status": "unlinked"}
