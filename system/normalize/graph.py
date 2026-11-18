"""
system/normalize/graph.py - CommonMark Link Extraction, Validation & Path Healing.
Provides POSIX relative path calculation and AST-safe link rewriting.
"""

import posixpath
import re
import urllib.parse
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Dict, List, Tuple

from .db import LinkRecord
from .slugify import slugify_stem

# Detect external protocols or anchor-only references
EXTERNAL_OR_ANCHOR_PATTERN = re.compile(
    r"^(?:[a-zA-Z][a-zA-Z0-9+.-]*://|//|mailto:|tel:|#)"
)

# Inline code span regex: `code` or ``code``
INLINE_CODE_PATTERN = re.compile(r"`+[^`]+`+")

# CommonMark Link and Image Regex:
# Matches [label](url "optional title") and ![alt](url)
LINK_OR_IMAGE_PATTERN = re.compile(
    r"(!?\[((?:[^\[\]]|\\.)*)\])\(\s*([^\s\)\"\']+)(?:\s+([\"'])(.*?)\4)?\s*\)"
)


@dataclass(frozen=True)
class ExtractedLink:
    source_stem: str
    target_stem: str
    raw_target: str
    line_number: int
    is_image: bool
    label: str
    target_path: str
    suffix: str  # #fragment or ?query


def split_target_url(raw_target: str) -> Tuple[str, str]:
    """
    Splits a raw link target into (path_portion, suffix_portion).
    Example: '../notes/energy.md#first-law' -> ('../notes/energy.md', '#first-law')
    """
    match = re.search(r"[#?]", raw_target)
    if match:
        idx = match.start()
        return raw_target[:idx], raw_target[idx:]
    return raw_target, ""


def is_external_or_anchor(url: str) -> bool:
    """Checks whether the link is external or purely a local in-page anchor."""
    clean = url.strip()
    return bool(EXTERNAL_OR_ANCHOR_PATTERN.match(clean))


def extract_stem_from_path(path_str: str) -> str:
    """
    Extracts and canonicalizes the filename stem from a relative path string.
    Decodes percent-encoding (e.g. 'Math%20Notes/Matrix.md' -> 'matrix').
    """
    unquoted = urllib.parse.unquote(path_str)
    pure = PurePosixPath(unquoted)
    return slugify_stem(pure.stem)


def parse_markdown_links(content: str, source_stem: str) -> List[ExtractedLink]:
    """
    Parses Markdown text and extracts relative links and images.
    Accurately ignores links enclosed inside fenced or inline code spans.
    """
    extracted: List[ExtractedLink] = []
    lines = content.splitlines()

    in_fenced_block = False
    fenced_fence_char = ""
    fenced_fence_len = 0

    for line_idx, line in enumerate(lines, start=1):
        stripped = line.strip()

        # Fenced code block detection: ``` or ~~~
        if not in_fenced_block:
            if stripped.startswith("```") or stripped.startswith("~~~"):
                fence_char = stripped[0]
                match = re.match(r"^[`~]+", stripped)
                if match and len(match.group(0)) >= 3:
                    in_fenced_block = True
                    fenced_fence_char = fence_char
                    fenced_fence_len = len(match.group(0))
                    continue
        else:
            if stripped.startswith(fenced_fence_char * fenced_fence_len):
                in_fenced_block = False
            continue

        if in_fenced_block:
            continue

        # Mask inline code spans to prevent false link extraction
        def mask_inline_code(m):
            return " " * len(m.group(0))

        sanitized_line = INLINE_CODE_PATTERN.sub(mask_inline_code, line)

        for match in LINK_OR_IMAGE_PATTERN.finditer(sanitized_line):
            is_image = match.group(1).startswith("!")
            label = match.group(2)
            raw_url = match.group(3)

            if is_external_or_anchor(raw_url):
                continue

            path_part, suffix_part = split_target_url(raw_url)
            target_stem = extract_stem_from_path(path_part)

            if not target_stem:
                continue

            extracted.append(
                ExtractedLink(
                    source_stem=source_stem,
                    target_stem=target_stem,
                    raw_target=raw_url,
                    line_number=line_idx,
                    is_image=is_image,
                    label=label,
                    target_path=path_part,
                    suffix=suffix_part,
                )
            )

    return extracted


def to_link_records(extracted_links: List[ExtractedLink]) -> List[LinkRecord]:
    """Converts ExtractedLink items into SQLite LinkRecord objects."""
    return [
        LinkRecord(
            source_stem=link.source_stem,
            target_stem=link.target_stem,
            raw_target=link.raw_target,
            line_number=link.line_number,
        )
        for link in extracted_links
    ]


def compute_relative_link(source_rel_path: str, target_rel_path: str) -> str:
    """
    Calculates the explicit relative POSIX path from source_rel_path to target_rel_path.
    Guaranteed deterministic forward-slash output across all host operating systems.
    """
    src_parent = PurePosixPath(source_rel_path).parent
    src_dir_str = "." if str(src_parent) == "." else str(src_parent)
    return posixpath.relpath(target_rel_path, start=src_dir_str)


def heal_markdown_links(
    content: str,
    source_rel_path: str,
    stem_to_new_rel_path: Dict[str, str],
) -> Tuple[str, int]:
    """
    Rewrites relative links targeting files that have changed paths or stems.
    Preserves link labels, images, optional titles, and anchors/query strings.
    Ignores links inside fenced code blocks and inline code spans.
    """
    lines = content.splitlines(keepends=True)
    new_lines: List[str] = []
    total_rewrites = 0

    in_fenced_block = False
    fenced_fence_char = ""
    fenced_fence_len = 0

    for line in lines:
        stripped = line.strip()

        if not in_fenced_block:
            if stripped.startswith("```") or stripped.startswith("~~~"):
                fence_char = stripped[0]
                match = re.match(r"^[`~]+", stripped)
                if match and len(match.group(0)) >= 3:
                    in_fenced_block = True
                    fenced_fence_char = fence_char
                    fenced_fence_len = len(match.group(0))
                    new_lines.append(line)
                    continue
        else:
            if stripped.startswith(fenced_fence_char * fenced_fence_len):
                in_fenced_block = False
            new_lines.append(line)
            continue

        if in_fenced_block:
            new_lines.append(line)
            continue

        # Detect spans of inline code on the current line to guard against false rewrites
        inline_spans = [m.span() for m in INLINE_CODE_PATTERN.finditer(line)]
        line_rewrites = 0

        def replace_link(m: re.Match) -> str:
            nonlocal line_rewrites

            # Bypass replacement if the match begins inside an inline code span
            if any(start <= m.start() < end for start, end in inline_spans):
                return m.group(0)

            prefix = m.group(1)
            raw_url = m.group(3)
            quote_char = m.group(4) or ""
            title_text = m.group(5) or ""

            if is_external_or_anchor(raw_url):
                return m.group(0)

            path_part, suffix_part = split_target_url(raw_url)
            target_stem = extract_stem_from_path(path_part)

            if target_stem not in stem_to_new_rel_path:
                return m.group(0)

            new_target_rel_path = stem_to_new_rel_path[target_stem]
            healed_rel_path = compute_relative_link(
                source_rel_path, new_target_rel_path
            )
            new_url = f"{healed_rel_path}{suffix_part}"

            if new_url == raw_url:
                return m.group(0)

            line_rewrites += 1
            if quote_char and title_text:
                return f"{prefix}({new_url} {quote_char}{title_text}{quote_char})"
            return f"{prefix}({new_url})"

        new_line = LINK_OR_IMAGE_PATTERN.sub(replace_link, line)
        new_lines.append(new_line)
        total_rewrites += line_rewrites

    return "".join(new_lines), total_rewrites
