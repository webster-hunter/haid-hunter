import json
import uuid
import mimetypes
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

from backend.config import ALLOWED_EXTENSIONS

DEFAULT_TAGS = ["resume", "cover-letter", "cv"]


class MetadataService:
    def __init__(self, docs_dir: Path):
        self.docs_dir = docs_dir
        self.meta_path = docs_dir / ".metadata.json"
        self._lock = Lock()
        self._ensure_metadata()

    def _ensure_metadata(self):
        if not self.meta_path.exists():
            self._write({"files": {}, "tags": list(DEFAULT_TAGS)})

    def read(self) -> dict:
        with self._lock:
            return json.loads(self.meta_path.read_text())

    def _write(self, data: dict):
        self.meta_path.write_text(json.dumps(data, indent=2))

    def save(self, data: dict):
        with self._lock:
            self._write(data)

    def _check_path(self, file_path: Path) -> Path:
        """Verify resolved path stays within docs_dir."""
        if not file_path.resolve().is_relative_to(self.docs_dir.resolve()):
            raise ValueError("Invalid file path")
        return file_path

    def add_file(self, original_name: str, file_bytes: bytes, tags: list[str] | None = None) -> dict:
        file_id = uuid.uuid4().hex[:8]
        safe_name = Path(original_name).name
        stored_name = f"{file_id}_{safe_name}"
        file_path = self._check_path(self.docs_dir / stored_name)
        file_path.write_bytes(file_bytes)

        mime_type, _ = mimetypes.guess_type(safe_name)

        entry = {
            "original_name": safe_name,
            "stored_name": stored_name,
            "display_name": safe_name,
            "tags": tags or [],
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
            "size_bytes": len(file_bytes),
            "mime_type": mime_type or "application/octet-stream",
        }

        with self._lock:
            data = json.loads(self.meta_path.read_text())
            data["files"][file_id] = entry
            self._write(data)

        return {"id": file_id, **entry}

    def update_file(self, file_id: str, display_name: str | None = None, tags: list[str] | None = None) -> dict:
        with self._lock:
            data = json.loads(self.meta_path.read_text())
            if file_id not in data["files"]:
                raise KeyError(f"File {file_id} not found")
            if display_name is not None:
                data["files"][file_id]["display_name"] = display_name
            if tags is not None:
                data["files"][file_id]["tags"] = tags
            self._write(data)
            return data["files"][file_id]

    def delete_file(self, file_id: str):
        with self._lock:
            data = json.loads(self.meta_path.read_text())
            if file_id not in data["files"]:
                raise KeyError(f"File {file_id} not found")
            stored_name = data["files"][file_id]["stored_name"]
            file_path = self._check_path(self.docs_dir / stored_name)
            if file_path.exists():
                file_path.unlink()
            del data["files"][file_id]
            self._write(data)

    def get_file(self, file_id: str) -> dict:
        data = self.read()
        if file_id not in data["files"]:
            raise KeyError(f"File {file_id} not found")
        return data["files"][file_id]

    def sync(self) -> dict:
        with self._lock:
            data = json.loads(self.meta_path.read_text())
            on_disk = set()
            added = []
            removed = []

            for f in self.docs_dir.iterdir():
                if f.name.startswith(".") or f.is_dir():
                    continue
                ext = f.suffix.lower()
                if ext not in ALLOWED_EXTENSIONS:
                    continue
                on_disk.add(f.name)

                # Check if this file is already tracked
                found = False
                for fid, meta in data["files"].items():
                    if meta["stored_name"] == f.name:
                        found = True
                        break
                if not found:
                    # Try to extract ID from filename — only treat as tracked format
                    # if the prefix is exactly 8 lowercase hex characters.
                    parts = f.name.split("_", 1)
                    if (
                        len(parts) == 2
                        and len(parts[0]) == 8
                        and all(c in "0123456789abcdef" for c in parts[0])
                    ):
                        file_id = parts[0]
                        original = parts[1]
                    else:
                        file_id = uuid.uuid4().hex[:8]
                        original = f.name

                    mime_type, _ = mimetypes.guess_type(f.name)
                    data["files"][file_id] = {
                        "original_name": original,
                        "stored_name": f.name,
                        "display_name": original,
                        "tags": [],
                        "uploaded_at": datetime.now(timezone.utc).isoformat(),
                        "size_bytes": f.stat().st_size,
                        "mime_type": mime_type or "application/octet-stream",
                    }
                    added.append(file_id)

            # Remove entries for files no longer on disk
            to_remove = []
            for fid, meta in data["files"].items():
                if meta["stored_name"] not in on_disk:
                    to_remove.append(fid)
            for fid in to_remove:
                del data["files"][fid]
                removed.append(fid)

            self._write(data)
            return {"added": added, "removed": removed}

    def add_tag(self, tag: str):
        with self._lock:
            data = json.loads(self.meta_path.read_text())
            if tag not in data["tags"]:
                data["tags"].append(tag)
                self._write(data)

    def delete_tag(self, tag: str):
        with self._lock:
            data = json.loads(self.meta_path.read_text())
            if tag in data["tags"]:
                data["tags"].remove(tag)
            for fid in data["files"]:
                if tag in data["files"][fid]["tags"]:
                    data["files"][fid]["tags"].remove(tag)
            self._write(data)

    def get_tags(self) -> list[str]:
        return self.read()["tags"]
