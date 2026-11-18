# system/normalize/scanner.py
"""
system/normalize/scanner.py - Fast-Path Traversal & Stat-Cache Aware File Scanner.
Traverses content/ and avoids redundant I/O for unchanged files.
"""

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from .db import VaultDB

JUNK_DIR_NAMES = {
    ".obsidian",
    ".trash",
    ".zettlr",
    ".logseq",
    "logseq",
    ".git",
    ".vscode",
    ".idea",
}

JUNK_FILE_EXTENSIONS = {".ztr-directory", ".ds_store", "thumbs.db", "desktop.ini"}

MARKDOWN_EXTENSIONS = {".md", ".markdown"}


def is_junk_path(path: Path, root: Path) -> bool:
    """
    Checks if a given path belongs to junk/hidden editor folders or artifact files.
    """
    try:
        rel_parts = path.relative_to(root).parts
    except ValueError:
        rel_parts = path.parts

    for part in rel_parts:
        if part.lower() in JUNK_DIR_NAMES or (part.startswith(".") and part != "."):
            return True

    name_lower = path.name.lower()
    if name_lower in JUNK_FILE_EXTENSIONS:
        return True
    if any(name_lower.endswith(ext) for ext in JUNK_FILE_EXTENSIONS):
        return True
    return False


def is_secure_rel_path(rel_posix_path: str) -> bool:
    """Returns True if the path resides inside a /secure/ subfolder."""
    parts = rel_posix_path.split("/")
    return "secure" in parts


def compute_file_sha256(file_path: Path) -> str:
    """Computes SHA-256 hash using 64 KiB buffer chunks."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


@dataclass(frozen=True)
class ScannedFile:
    abs_path: Path
    rel_path: str  # POSIX format (e.g. 'notes/math.md')
    stem: str
    ext: str
    mtime: float
    size: int
    sha256: str
    is_media: bool
    is_secure: bool
    is_cache_hit: bool


@dataclass(frozen=True)
class VaultScanResult:
    files: List[ScannedFile]
    files_by_path: Dict[str, ScannedFile]
    cache_hits: int
    cache_misses: int


def scan_vault(content_root: Path, db: Optional[VaultDB] = None) -> VaultScanResult:
    """
    Scans content_root applying junk filtering, symlink suppression, and SQLite stat-cache verification.
    If db is provided and a file matches (mtime, size), disk hash computation is bypassed.
    """
    content_root = content_root.resolve()
    scanned_files: List[ScannedFile] = []
    files_by_path: Dict[str, ScannedFile] = {}
    cache_hits = 0
    cache_misses = 0

    if not content_root.exists() or not content_root.is_dir():
        return VaultScanResult([], {}, 0, 0)

    for root, dirs, filenames in os.walk(content_root, followlinks=False):
        # Boundary guard: ignore directory symlinks and prune junk directories in-place
        dirs[:] = [
            d
            for d in dirs
            if not (Path(root) / d).is_symlink()
            and not is_junk_path(Path(root) / d, content_root)
        ]

        for filename in filenames:
            abs_path = Path(root) / filename

            # Boundary guard: never follow or catalog symlinks
            if abs_path.is_symlink():
                continue

            if is_junk_path(abs_path, content_root):
                continue

            try:
                rel_path = abs_path.relative_to(content_root).as_posix()
            except ValueError:
                # Path escapes content_root; strictly ignore
                continue

            stat = abs_path.stat()
            mtime = stat.st_mtime
            size = stat.st_size

            ext = abs_path.suffix.lower()
            is_media = ext not in MARKDOWN_EXTENSIONS
            is_secure = is_secure_rel_path(rel_path)
            stem = abs_path.stem

            sha256: Optional[str] = None
            is_cache_hit = False

            if db is not None and db.is_stat_cache_hit(rel_path, mtime, size):
                cached_rec = db.get_file_by_path(rel_path)
                if cached_rec is not None:
                    sha256 = cached_rec.sha256
                    is_cache_hit = True
                    cache_hits += 1

            if sha256 is None:
                sha256 = compute_file_sha256(abs_path)
                cache_misses += 1

            record = ScannedFile(
                abs_path=abs_path,
                rel_path=rel_path,
                stem=stem,
                ext=ext,
                mtime=mtime,
                size=size,
                sha256=sha256,
                is_media=is_media,
                is_secure=is_secure,
                is_cache_hit=is_cache_hit,
            )
            scanned_files.append(record)
            files_by_path[rel_path] = record

    return VaultScanResult(
        files=scanned_files,
        files_by_path=files_by_path,
        cache_hits=cache_hits,
        cache_misses=cache_misses,
    )
