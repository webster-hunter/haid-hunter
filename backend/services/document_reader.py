from pathlib import Path


def read_document_contents(docs_dir: Path, metadata: dict) -> str:
    contents = []
    for file_id, meta in metadata.get("files", {}).items():
        mime = meta.get("mime_type", "")
        if mime in ("text/plain", "text/markdown", "text/csv"):
            file_path = docs_dir / meta["stored_name"]
            if not file_path.resolve().is_relative_to(docs_dir.resolve()):
                continue
            if file_path.exists():
                text = file_path.read_text(errors="ignore")
                contents.append(f"--- {meta['original_name']} ---\n{text[:5000]}")
        elif mime == "application/pdf":
            file_path = docs_dir / meta["stored_name"]
            if not file_path.resolve().is_relative_to(docs_dir.resolve()):
                continue
            if file_path.exists():
                try:
                    import pdfplumber
                    with pdfplumber.open(file_path) as pdf:
                        pages_text = []
                        for page in pdf.pages:
                            page_text = page.extract_text()
                            if page_text:
                                pages_text.append(page_text)
                        extracted = "\n".join(pages_text)[:5000]
                    contents.append(f"--- {meta['original_name']} ---\n{extracted}")
                except ImportError:
                    contents.append(
                        f"--- {meta['original_name']} ---\n"
                        f"[PDF file - text extraction not available]"
                    )
    return "\n\n".join(contents) if contents else "No previewable documents found."
