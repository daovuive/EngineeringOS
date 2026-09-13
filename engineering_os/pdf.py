"""Controlled local extraction and chunking for text-based PDF documents."""

from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from engineering_os.chunking import ChunkingConfig, split_text


class PDFExtractionError(RuntimeError):
    """Raised when a PDF is malformed or has no useful extractable text."""


@dataclass(frozen=True)
class PDFChunkDraft:
    path: str
    heading: str
    heading_path: tuple[str, ...]
    text: str
    document_type: str
    language: str | None
    project: str | None
    version: str | None
    tags: tuple[str, ...]
    document_id: str
    chunk_id: str
    chunk_index: int
    page_start: int
    page_end: int
    source_timestamp: str
    document_title: str | None
    document_author: str | None


def read_pdf_chunk_drafts(
    path: Path,
    root: Path,
    *,
    config: ChunkingConfig | None = None,
    default_language: str | None = None,
) -> list[PDFChunkDraft]:
    try:
        from pypdf import PdfReader
        from pypdf.errors import PdfReadError
    except ImportError as error:
        raise PDFExtractionError(
            "PDF ingestion requires the local 'pypdf' dependency."
        ) from error

    reader_logger = logging.getLogger("pypdf._reader")
    previous_disabled = reader_logger.disabled
    try:
        reader_logger.disabled = True
        reader = PdfReader(path, strict=False)
        if reader.is_encrypted:
            try:
                decrypt_result = reader.decrypt("")
            except Exception as error:
                raise PDFExtractionError(
                    "Password-protected PDFs are not supported."
                ) from error
            if not decrypt_result:
                raise PDFExtractionError(
                    "Password-protected PDFs are not supported."
                )
    except PDFExtractionError:
        raise
    except (OSError, PdfReadError, ValueError) as error:
        raise PDFExtractionError("PDF is malformed or unreadable.") from error
    finally:
        reader_logger.disabled = previous_disabled

    relative_path = path.relative_to(root).as_posix()
    document_id = hashlib.sha256(relative_path.encode("utf-8")).hexdigest()[:24]
    timestamp = datetime.fromtimestamp(
        path.stat().st_mtime, timezone.utc
    ).isoformat()
    parts = Path(relative_path).parts
    project = parts[1] if len(parts) >= 2 and parts[0] == "projects" else None
    drafts: list[PDFChunkDraft] = []
    pdf_metadata = reader.metadata
    document_title = (
        str(pdf_metadata.title).strip()
        if pdf_metadata is not None and pdf_metadata.title
        else None
    )
    document_author = (
        str(pdf_metadata.author).strip()
        if pdf_metadata is not None and pdf_metadata.author
        else None
    )
    chunk_index = 0
    for page_number, page in enumerate(reader.pages, 1):
        try:
            extracted = page.extract_text() or ""
        except Exception as error:
            raise PDFExtractionError(
                f"Could not extract text from PDF page {page_number}."
            ) from error
        normalized = _normalize_text(extracted)
        for piece in split_text(normalized, config):
            identity = "\0".join(
                (document_id, str(page_number), str(chunk_index), piece)
            )
            drafts.append(
                PDFChunkDraft(
                    relative_path,
                    f"Page {page_number}",
                    (f"Page {page_number}",),
                    piece,
                    "pdf",
                    default_language,
                    project,
                    None,
                    (),
                    document_id,
                    hashlib.sha256(identity.encode("utf-8")).hexdigest()[:32],
                    chunk_index,
                    page_number,
                    page_number,
                    timestamp,
                    document_title,
                    document_author,
                )
            )
            chunk_index += 1
    if not drafts:
        raise PDFExtractionError(
            "PDF has no meaningful extractable text; OCR is required for scanned PDFs."
        )
    return drafts


def _normalize_text(text: str) -> str:
    text = text.replace("\x00", " ").replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line).strip()
