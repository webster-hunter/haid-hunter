from pathlib import Path


def _pdf_to_text(file_path: Path) -> str:
    """
    Extract text from a PDF with layout-aware word ordering.

    pdfplumber's default extract_text() merges columns line-by-line across
    the full page width, which interleaves multi-column resume layouts and
    can split or join terms incorrectly.  Instead we collect individual word
    objects (which carry x/y coordinates), sort them top-to-bottom then
    left-to-right, group words that share the same vertical position into
    lines, and rejoin them.  This preserves skills lists in the left column
    and experience bullets in the right column as separate, intact phrases.
    """
    import pdfplumber

    pages: list[str] = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            words = page.extract_words(x_tolerance=3, y_tolerance=3)
            if not words:
                continue

            # Group words into lines: words within 3 pts vertically share a line.
            lines: list[list[str]] = []
            current_line: list[str] = []
            prev_top: float | None = None

            for word in sorted(words, key=lambda w: (w["top"], w["x0"])):
                if prev_top is None or abs(word["top"] - prev_top) <= 3:
                    current_line.append(word["text"])
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = [word["text"]]
                prev_top = word["top"]

            if current_line:
                lines.append(current_line)

            pages.append("\n".join(" ".join(line) for line in lines))

    return "\n\n".join(pages)


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
                contents.append(f"--- {meta['original_name']} ---\n{text}")
        elif mime == "application/pdf":
            file_path = docs_dir / meta["stored_name"]
            if not file_path.resolve().is_relative_to(docs_dir.resolve()):
                continue
            if file_path.exists():
                try:
                    extracted = _pdf_to_text(file_path)
                    contents.append(f"--- {meta['original_name']} ---\n{extracted}")
                except ImportError:
                    contents.append(
                        f"--- {meta['original_name']} ---\n"
                        f"[PDF file - text extraction not available]"
                    )
    return "\n\n".join(contents) if contents else "No previewable documents found."
