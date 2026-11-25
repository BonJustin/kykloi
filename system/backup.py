#!/usr/bin/env python3
"""
system/backup.py - Archival Backup Subsystem for Project Kykloi.
Creates deterministic, hardened, and portable ZIP archives of vault content
with junk filtering and cryptographic SHA-256 sidecars using Python's native zipfile engine.
"""

from __future__ import annotations

import datetime
import hashlib
import os
import stat
import sys
import time
import zipfile
from pathlib import Path

# Set up module path resolution
SYSTEM_DIR = Path(__file__).resolve().parent
ROOT_DIR = SYSTEM_DIR.parent
CONTENT_DIR = ROOT_DIR / "content"
DEFAULT_BACKUP_DIR = ROOT_DIR / "backups"

for p in (ROOT_DIR, SYSTEM_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from logger import get_logger  # noqa: E402

try:
    from system.normalize.scanner import is_junk_path  # noqa: E402
except ImportError:
    from normalize.scanner import is_junk_path  # noqa: E402


def create_vault_backup(
    content_dir: Path,
    output_dir: Path,
    archive_name: str | None = None,
    compress_level: int = 9,
) -> tuple[Path, Path, int, int]:
    """
    Creates a deterministic, hardened ZIP archive of the specified content directory
    using Python's standard library zipfile module.
    Filters junk files using is_junk_path and generates a companion SHA-256 sidecar.

    Returns:
        (zip_file_path, sha256_file_path, archived_file_count, total_uncompressed_bytes)
    """
    logger = get_logger("backup")

    if not content_dir.is_dir():
        raise FileNotFoundError(f"Content directory does not exist: {content_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    if not archive_name:
        utc_stamp = datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y%m%dT%H%M%SZ"
        )
        archive_name = f"kykloi-backup-content-{utc_stamp}.zip"

    if not archive_name.endswith(".zip"):
        archive_name += ".zip"

    zip_path = output_dir / archive_name
    sha256_path = output_dir / f"{archive_name}.sha256"

    # 1. Collect and filter source files deterministically
    candidate_files: list[Path] = []
    output_resolved = output_dir.resolve()

    for root, dirs, files in os.walk(content_dir):
        root_path = Path(root).resolve()

        # Prune junk directories in-place during walk.
        # Boundary guard: also prune output_dir if it resides within content_dir.
        pruned_dirs: list[str] = []
        for d in dirs:
            dir_path = (root_path / d).resolve()
            if dir_path == output_resolved:
                continue
            if not is_junk_path(dir_path, content_dir):
                pruned_dirs.append(d)
        dirs[:] = pruned_dirs

        for f in files:
            file_path = root_path / f
            resolved_file = file_path.resolve()

            # Boundary guard: skip archive and sidecar if written inside content_dir
            if resolved_file in (zip_path.resolve(), sha256_path.resolve()):
                continue

            # Skip existing backup archives and digests if any reside in source tree
            if resolved_file.name.startswith("kykloi-backup-content-") and (
                resolved_file.name.endswith(".zip")
                or resolved_file.name.endswith(".sha256")
            ):
                continue

            if not is_junk_path(file_path, content_dir) and file_path.is_file():
                candidate_files.append(file_path)

    # Sort deterministically by POSIX relative path for reproducible archives
    candidate_files.sort(key=lambda p: p.relative_to(content_dir).as_posix())

    # 2. Select compression method
    try:
        import zlib  # noqa: F401

        compression = zipfile.ZIP_DEFLATED
    except ImportError:
        logger.warning(
            "zlib unavailable in Python runtime; falling back to uncompressed ZIP_STORED"
        )
        compression = zipfile.ZIP_STORED

    # 3. Stream files into the ZIP archive
    archived_count = 0
    total_uncompressed = 0

    with zipfile.ZipFile(
        zip_path,
        mode="w",
        compression=compression,
        compresslevel=compress_level if compression == zipfile.ZIP_DEFLATED else None,
        allowZip64=True,
    ) as zf:
        for file_path in candidate_files:
            rel_path = file_path.relative_to(content_dir).as_posix()
            file_stat = file_path.stat()
            file_size = file_stat.st_size
            total_uncompressed += file_size

            # Create ZipInfo with normalized attributes and UTF-8 encoding
            zinfo = zipfile.ZipInfo(filename=rel_path)
            # Normalize timestamp to UTC date tuple (YYYY, MM, DD, HH, MM, SS)
            mtime_utc = time.gmtime(file_stat.st_mtime)
            zinfo.date_time = (
                mtime_utc.tm_year,
                mtime_utc.tm_mon,
                mtime_utc.tm_mday,
                mtime_utc.tm_hour,
                mtime_utc.tm_min,
                mtime_utc.tm_sec,
            )
            zinfo.compress_type = compression

            # Standardize POSIX file permissions: 0o644 for regular files
            zinfo.external_attr = (0o644 | stat.S_IFREG) << 16

            # General Purpose Bit Flag: bit 11 enables UTF-8 filename encoding
            zinfo.flag_bits |= 0x800

            with open(file_path, "rb") as src:
                data = src.read()
                zf.writestr(zinfo, data)

            archived_count += 1

    # 4. Generate cryptographic SHA-256 integrity sidecar
    hasher = hashlib.sha256()
    with open(zip_path, "rb") as zf:
        while chunk := zf.read(65536):
            hasher.update(chunk)
    digest = hasher.hexdigest()

    with open(sha256_path, "w", encoding="utf-8") as sf:
        sf.write(f"{digest}  {archive_name}\n")

    logger.info(
        "Archived %d files into %s (Uncompressed: %s, SHA-256: %s)",
        archived_count,
        zip_path.name,
        _format_bytes(total_uncompressed),
        digest[:12],
    )

    return zip_path, sha256_path, archived_count, total_uncompressed


def find_previous_backups(
    output_dir: Path,
    exclude_paths: set[Path] | None = None,
) -> list[Path]:
    """
    Discovers previous Kykloi backup archives and hash sidecars in the destination directory,
    excluding any newly generated files.
    """
    if not output_dir.is_dir():
        return []

    exclude = {p.resolve() for p in (exclude_paths or set())}
    candidates: list[Path] = []

    for item in output_dir.iterdir():
        if not item.is_file():
            continue
        if item.resolve() in exclude:
            continue
        # Strictly match Kykloi backup archives and sidecar hashes
        name = item.name
        if name.startswith("kykloi-backup-") and (
            name.endswith(".zip") or name.endswith(".sha256")
        ):
            candidates.append(item)

    # Sort deterministically by filename
    candidates.sort(key=lambda p: p.name)
    return candidates


def prune_previous_backups(
    output_dir: Path,
    exclude_paths: set[Path] | None = None,
) -> list[Path]:
    """
    Deletes previous Kykloi backup archives and sidecar files from output_dir,
    excluding newly created paths. Returns list of deleted paths.
    """
    logger = get_logger("backup")
    targets = find_previous_backups(output_dir, exclude_paths)
    deleted: list[Path] = []

    for target in targets:
        try:
            target.unlink()
            deleted.append(target)
            logger.info("Pruned old backup artifact: %s", target.name)
        except OSError as exc:
            logger.warning(
                "Failed to delete old backup artifact %s: %s", target.name, exc
            )

    return deleted


def _format_bytes(size: int | float) -> str:
    """Formats byte counts into human-readable strings."""
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024.0 or unit == "GB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024.0
    return f"{size:.1f} TB"


def run_interactive_backup(
    content_dir: Path = CONTENT_DIR,
    default_backup_dir: Path = DEFAULT_BACKUP_DIR,
) -> bool:
    """
    Guides the user through an interactive backup workflow:
    1. Prompts for destination path with default fallback to backups/.
    2. Executes compression using Python's native zipfile engine.
    3. Generates cryptographic SHA-256 verification sidecar.
    """
    logger = get_logger("backup")

    print("\n==================== ARCHIVAL BACKUP WORKFLOW ====================")
    print("  Engine:               Python Native ZIP64 (In-Process / Zero-Dependency)")
    print(f"  Source Vault:         {content_dir}")
    print(f"  Default Destination:  {default_backup_dir}")
    print("------------------------------------------------------------------")

    try:
        user_input = input(
            f"Enter backup destination directory [Enter for '{default_backup_dir.name}/']: "
        ).strip()
    except (KeyboardInterrupt, EOFError):
        print()
        logger.warning("Backup workflow cancelled by user.")
        return False

    if not user_input:
        target_dir = default_backup_dir
    else:
        target_dir = Path(os.path.expanduser(user_input)).resolve()

    try:
        resolved_content = content_dir.resolve()
        if target_dir == resolved_content or resolved_content in target_dir.parents:
            print(
                "[!] Notice: Target destination resides within the vault content directory."
            )
            print(
                "    Archive artifacts will be automatically isolated from vault indexing."
            )
    except Exception:
        pass

    print(f"\nCompressing vault content into {target_dir}...")
    try:
        t0 = time.perf_counter()
        zip_path, sha_path, count, total_bytes = create_vault_backup(
            content_dir=content_dir,
            output_dir=target_dir,
        )
        elapsed = time.perf_counter() - t0
        compressed_size = zip_path.stat().st_size

        print("\n[+] Archival Backup Created Successfully!")
        print(f"    • Archive:       {zip_path}")
        print(
            f"    • Size:          {_format_bytes(compressed_size)} "
            f"(Original: {_format_bytes(total_bytes)}, Time: {elapsed:.2f}s)"
        )
        print(f"    • Files:         {count} items (junk & caches excluded)")
        print(f"    • Digest:        {sha_path}")

        # Display first 16 characters of digest for instant verification
        with open(sha_path, "r", encoding="utf-8") as sf:
            digest_str = sf.read().strip()
        print(f"    • SHA-256:       {digest_str.split()[0]}")
        print("==================================================================")

        # Check for previous backup archives in the destination
        previous_artifacts = find_previous_backups(
            target_dir, exclude_paths={zip_path, sha_path}
        )
        if previous_artifacts:
            old_zips = [p for p in previous_artifacts if p.name.endswith(".zip")]
            old_sha = [p for p in previous_artifacts if p.name.endswith(".sha256")]
            old_bytes = sum(p.stat().st_size for p in previous_artifacts if p.exists())

            print(
                f"\n[?] Previous backups detected in destination: "
                f"{len(old_zips)} archive(s), {len(old_sha)} checksum(s) ({_format_bytes(old_bytes)})"
            )
            for z in old_zips[-3:]:
                print(f"    - {z.name}")
            if len(old_zips) > 3:
                print(f"    ... and {len(old_zips) - 3} older archive(s)")

            try:
                ans = (
                    input("\nDelete previous backups from destination? [y/N]: ")
                    .strip()
                    .lower()
                )
            except (KeyboardInterrupt, EOFError):
                ans = "n"

            if ans in ("y", "yes"):
                deleted = prune_previous_backups(
                    target_dir, exclude_paths={zip_path, sha_path}
                )
                print(f"[✓] Deleted {len(deleted)} previous backup artifact(s).\n")
            else:
                print("[i] Previous backups retained.\n")
        else:
            print()

        return True

    except Exception as exc:
        logger.error("Backup creation failed: %s", exc)
        print(f"\n[-] Backup Failed: {exc}\n")
        return False


if __name__ == "__main__":
    run_interactive_backup()
