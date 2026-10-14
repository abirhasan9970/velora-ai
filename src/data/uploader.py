"""
uploader.py
-----------
Safe file ingestion. Copies user-provided files into data/uploads/ with:
- filename sanitization (no path traversal)
- size limit checks
- MIME/extension validation
- duplicate-name handling (auto-renames)
"""
from __future__ import annotations

import hashlib
import re
import shutil
from pathlib import Path

from src.utils.config import PROJECT_ROOT, get_settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

UPLOADS_DIR = PROJECT_ROOT / "data" / "uploads"
ALLOWED_EXTENSIONS = {".csv", ".tsv", ".xlsx", ".xls"}
MAX_SIZE_BYTES_DEFAULT = 50 * 1024 * 1024  # 50 MB
_SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9._-]")


class UploadError(Exception):
    """Raised when a file cannot be uploaded."""


def _sanitize_filename(name: str) -> str:
    """Remove path components and dangerous characters."""
    name = Path(name).name  # strip any directory components
    name = _SAFE_NAME_RE.sub("_", name)
    name = name.lstrip(".") or "upload"  # never start with dot
    return name[:200]  # reasonable max length


def _unique_path(directory: Path, filename: str) -> Path:
    """If a file with that name exists, append _1, _2, ... before the extension."""
    candidate = directory / filename
    if not candidate.exists():
        return candidate

    stem = candidate.stem
    suffix = candidate.suffix
    for i in range(1, 1000):
        alt = directory / f"{stem}_{i}{suffix}"
        if not alt.exists():
            return alt
    raise UploadError(f"Too many files named like '{filename}'.")


def _file_hash(path: Path, chunk_size: int = 65536) -> str:
    """SHA-256 hash of a file (used for dedupe detection)."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def upload_file(source_path: str | Path) -> dict:
    """
    Safely copy a file into data/uploads/.

    Returns:
        {
            "ok": bool,
            "stored_path": str,   # absolute path inside uploads dir
            "filename": str,      # sanitized stored filename
            "size_bytes": int,
            "sha256": str,
            "renamed": bool,      # True if name collided and was auto-renamed
            "error": str | None
        }
    """
    try:
        src = Path(source_path).expanduser().resolve()
    except Exception as e:
        return {"ok": False, "error": f"Invalid source path: {e}",
                "stored_path": None, "filename": None, "size_bytes": 0,
                "sha256": None, "renamed": False}

    if not src.exists():
        return {"ok": False, "error": f"File not found: {src}",
                "stored_path": None, "filename": None, "size_bytes": 0,
                "sha256": None, "renamed": False}

    if not src.is_file():
        return {"ok": False, "error": f"Not a file: {src}",
                "stored_path": None, "filename": None, "size_bytes": 0,
                "sha256": None, "renamed": False}

    ext = src.suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return {"ok": False,
                "error": f"File type '{ext}' not allowed. Allowed: {sorted(ALLOWED_EXTENSIONS)}",
                "stored_path": None, "filename": None, "size_bytes": 0,
                "sha256": None, "renamed": False}

    size = src.stat().st_size
    max_bytes = get_settings().max_upload_mb * 1024 * 1024

    if size > max_bytes:
        return {"ok": False,
                "error": f"File too large ({size/1024/1024:.1f} MB > "
                         f"{get_settings().max_upload_mb} MB limit)",
                "stored_path": None, "filename": None, "size_bytes": size,
                "sha256": None, "renamed": False}

    if size == 0:
        return {"ok": False, "error": "File is empty (0 bytes).",
                "stored_path": None, "filename": None, "size_bytes": 0,
                "sha256": None, "renamed": False}

    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    safe_name = _sanitize_filename(src.name)
    dest = _unique_path(UPLOADS_DIR, safe_name)
    renamed = dest.name != safe_name

    try:
        shutil.copy2(src, dest)
    except Exception as e:
        return {"ok": False, "error": f"Copy failed: {e}",
                "stored_path": None, "filename": None, "size_bytes": size,
                "sha256": None, "renamed": False}

    digest = _file_hash(dest)
    logger.info(f"Uploaded {src.name} -> {dest.name} ({size} bytes, sha256={digest[:12]}...)")

    return {
        "ok": True,
        "stored_path": str(dest),
        "filename": dest.name,
        "size_bytes": size,
        "sha256": digest,
        "renamed": renamed,
        "error": None,
    }