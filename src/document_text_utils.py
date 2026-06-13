"""Extract plain text from uploaded CV/resume files."""

from __future__ import annotations

from io import BytesIO


SUPPORTED_CV_EXTENSIONS = {".txt", ".pdf", ".docx"}


def _decode_text_bytes(data: bytes) -> str:
    for encoding in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def _extract_pdf_text(data: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ValueError(
            "PDF support requires pypdf. Run: pip install pypdf python-docx  OR  .\\setup.ps1"
        ) from exc

    reader = PdfReader(BytesIO(data))
    parts: list[str] = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        if page_text.strip():
            parts.append(page_text.strip())
    return "\n\n".join(parts)


def _extract_docx_text(data: bytes) -> str:
    try:
        from docx import Document
    except ImportError as exc:
        raise ValueError(
            "DOCX support requires python-docx. Run: pip install pypdf python-docx  OR  .\\setup.ps1"
        ) from exc

    document = Document(BytesIO(data))
    parts = [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]
    return "\n".join(parts)


def extract_text_from_upload(data: bytes, filename: str) -> str:
    """Return plain text extracted from an uploaded CV file."""
    if not data:
        raise ValueError("Uploaded file is empty.")

    suffix = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if suffix == "txt":
        text = _decode_text_bytes(data)
    elif suffix == "pdf":
        text = _extract_pdf_text(data)
    elif suffix == "docx":
        text = _extract_docx_text(data)
    else:
        raise ValueError("Unsupported file type. Upload .txt, .pdf, or .docx.")

    cleaned = text.strip()
    if not cleaned:
        raise ValueError("No readable text found in the uploaded file.")
    return cleaned


def merge_cv_text(uploaded_text: str, pasted_text: str) -> str:
    """Prefer uploaded CV text; fall back to pasted text."""
    uploaded = uploaded_text.strip()
    pasted = pasted_text.strip()
    if uploaded:
        return uploaded
    return pasted
