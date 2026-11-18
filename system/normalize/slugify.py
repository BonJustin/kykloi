"""
system/normalize/slugify.py - Deterministic Cross-Platform Slugifier & Path Sanitizer.
Strictly adheres to POSIX and Windows-safe constraints.
"""

import re
import unicodedata
from pathlib import PurePosixPath

# Matches valid stems: starts with [a-z0-9], followed by [a-z0-9], '-', or '_'
STEM_PATTERN = re.compile(r"^[a-z0-9][a-z0-9\-_]*$")

# Characters explicitly forbidden across POSIX and Windows filesystems
FORBIDDEN_CHARS_PATTERN = re.compile(r'[<>:"/\\|?*\x00-\x1f]')

# Non-alphanumeric separators (excluding hyphen and underscore)
PUNCTUATION_SEPARATOR_PATTERN = re.compile(r"[\s\.,;!#$@%^&()\[\]{}+=~`'\"]+")

# Runs of hyphens or underscores
COLLAPSE_HYPHENS = re.compile(r"-{2,}")
COLLAPSE_UNDERSCORES = re.compile(r"_{2,}")


def is_valid_stem(stem: str) -> bool:
    """
    Validates whether a filename stem meets the strict archival UID specification:
      Regex: ^[a-z0-9][a-z0-9\\-_]*$
    """
    if not stem or len(stem) > 255:
        return False
    return bool(STEM_PATTERN.match(stem))


def slugify_stem(raw_stem: str, default_fallback: str = "untitled") -> str:
    """
    Transforms an arbitrary filename stem into a canonical, normalized UID:
      1. Normalizes Unicode to NFC.
      2. Converts ASCII/Unicode characters to lowercase.
      3. Replaces spaces, dots, and common punctuation with hyphens.
      4. Strips forbidden filesystem characters.
      5. Collapses redundant consecutive hyphens/underscores.
      6. Trims leading/trailing hyphens, underscores, and dots.
      7. Ensures leading character is alphanumeric; prepends 'n-' if it starts with a hyphen/digit boundary.
    """
    if not raw_stem or not raw_stem.strip():
        return default_fallback

    # Step 1: Unicode NFC Normalization
    text = unicodedata.normalize("NFC", raw_stem.strip())

    # Step 2: Lowercase conversion
    text = text.lower()

    # Step 3: Strip absolute forbidden chars
    text = FORBIDDEN_CHARS_PATTERN.sub("", text)

    # Step 4: Convert whitespace and punctuation clusters to hyphens
    text = PUNCTUATION_SEPARATOR_PATTERN.sub("-", text)

    # Step 5: Retain only ASCII [a-z0-9], hyphens, and underscores
    # Strips non-ASCII unicode diacritics / symbols to ensure pure cross-platform portability
    text = re.sub(r"[^a-z0-9\-_]", "", text)

    # Step 6: Collapse consecutive hyphens and underscores
    text = COLLAPSE_HYPHENS.sub("-", text)
    text = COLLAPSE_UNDERSCORES.sub("_", text)

    # Step 7: Trim leading/trailing hyphens and underscores
    text = text.strip("-_")

    if not text:
        return default_fallback

    # Step 8: Ensure leading character is in [a-z0-9]
    if not text[0].isalnum():
        text = f"doc-{text.lstrip('-_')}"

    return text[:255]


def sanitize_path_segments(rel_path: str) -> str:
    """
    Sanitizes all directory segments and the filename in a relative POSIX path.
    Preserves file extension in lowercase.

    Example:
      'My Notes/2026 Math/Matrix Calculation.MD' -> 'my-notes/2026-math/matrix-calculation.md'
    """
    pure_path = PurePosixPath(rel_path)
    sanitized_parts = []

    for part in pure_path.parent.parts:
        if part in (".", ""):
            continue
        sanitized_parts.append(slugify_stem(part))

    stem = slugify_stem(pure_path.stem)
    ext = pure_path.suffix.lower()

    filename = f"{stem}{ext}"
    if sanitized_parts:
        return "/".join(sanitized_parts) + "/" + filename
    return filename
