"""Safe, explicit, allowlisted log discovery and token-aware parsing."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePosixPath
from typing import Any

from engineering_os.chunking import ChunkingConfig, split_text


class LogIngestionError(RuntimeError):
    """Raised when an allowlisted log violates the ingestion policy."""


@dataclass(frozen=True)
class LogIngestionConfig:
    enabled: bool = False
    allowlist: tuple[str, ...] = (
        "runtime/logs/rag/*.log",
        "runtime/logs/services/*.log",
    )
    max_file_size_mb: int = 10
    retention_days: int = 14

    @classmethod
    def from_settings(cls, settings: dict[str, Any]) -> "LogIngestionConfig":
        knowledge = settings.get("knowledge", {})
        values = knowledge.get("logs", {}) if isinstance(knowledge, dict) else {}
        if not isinstance(values, dict):
            raise LogIngestionError("knowledge.logs must be an object.")
        enabled = values.get("enabled", False)
        allowlist = values.get("allowlist", list(cls.allowlist))
        maximum = values.get("maxFileSizeMB", 10)
        retention = values.get("retentionDays", 14)
        if not isinstance(enabled, bool):
            raise LogIngestionError("knowledge.logs.enabled must be a boolean.")
        if (
            not isinstance(allowlist, list)
            or not all(isinstance(item, str) and item.strip() for item in allowlist)
        ):
            raise LogIngestionError("knowledge.logs.allowlist must contain path patterns.")
        if not isinstance(maximum, int) or isinstance(maximum, bool) or maximum < 1:
            raise LogIngestionError("knowledge.logs.maxFileSizeMB must be positive.")
        if not isinstance(retention, int) or isinstance(retention, bool) or retention < 0:
            raise LogIngestionError("knowledge.logs.retentionDays must not be negative.")
        normalized: list[str] = []
        for pattern in allowlist:
            candidate = PurePosixPath(pattern)
            if candidate.is_absolute() or ".." in candidate.parts:
                raise LogIngestionError("Log allowlist patterns must stay inside the project.")
            normalized.append(candidate.as_posix())
        return cls(enabled, tuple(normalized), maximum, retention)


@dataclass(frozen=True)
class LogChunkDraft:
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
    source_timestamp: str


_SENSITIVE_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", re.IGNORECASE),
    re.compile(r"\bauthorization\s*:\s*bearer\s+\S+", re.IGNORECASE),
    re.compile(
        r"\b(?:password|passwd|access[_-]?token|api[_-]?key|client[_-]?secret)\s*[:=]\s*\S+",
        re.IGNORECASE,
    ),
)


def discover_allowed_logs(
    project_root: Path,
    config: LogIngestionConfig,
    *,
    now: datetime | None = None,
) -> list[Path]:
    if not config.enabled:
        return []
    project_root = project_root.resolve()
    cutoff = (now or datetime.now(timezone.utc)) - timedelta(days=config.retention_days)
    discovered: set[Path] = set()
    for pattern in config.allowlist:
        for candidate in project_root.glob(pattern):
            if candidate.suffix.lower() != ".log" or not candidate.is_file():
                continue
            if candidate.is_symlink():
                raise LogIngestionError(f"Allowlisted log must not be a symlink: {candidate}")
            resolved = candidate.resolve()
            try:
                resolved.relative_to(project_root)
            except ValueError as error:
                raise LogIngestionError("Allowlisted log resolved outside the project.") from error
            stat = resolved.stat()
            if stat.st_size > config.max_file_size_mb * 1024 * 1024:
                raise LogIngestionError(f"Allowlisted log exceeds size limit: {resolved}")
            modified = datetime.fromtimestamp(stat.st_mtime, timezone.utc)
            if modified < cutoff:
                continue
            discovered.add(resolved)
    return sorted(discovered)


def read_log_chunk_drafts(
    path: Path,
    project_root: Path,
    *,
    config: ChunkingConfig | None = None,
    default_language: str | None = None,
) -> list[LogChunkDraft]:
    raw = path.read_bytes()
    if b"\x00" in raw:
        raise LogIngestionError(f"Binary log is not indexable: {path}")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise LogIngestionError(f"Log must be valid UTF-8 text: {path}") from error
    if any(pattern.search(text) for pattern in _SENSITIVE_PATTERNS):
        raise LogIngestionError(f"Sensitive material detected in allowlisted log: {path}")
    normalized = "\n".join(line.rstrip() for line in text.splitlines()).strip()
    if not normalized:
        return []
    relative_path = path.resolve().relative_to(project_root.resolve()).as_posix()
    document_id = hashlib.sha256(relative_path.encode("utf-8")).hexdigest()[:24]
    timestamp = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()
    drafts: list[LogChunkDraft] = []
    for chunk_index, piece in enumerate(split_text(normalized, config)):
        identity = "\0".join((document_id, str(chunk_index), piece))
        drafts.append(
            LogChunkDraft(
                relative_path,
                path.name,
                (path.name,),
                piece,
                "log",
                default_language,
                None,
                None,
                ("log",),
                document_id,
                hashlib.sha256(identity.encode("utf-8")).hexdigest()[:32],
                chunk_index,
                timestamp,
            )
        )
    return drafts
