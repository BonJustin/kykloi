"""
system/normalize/graph.py - Read-Only Link Extraction, Validation & Prescriptive Diagnostics.
Provides CommonMark link parsing, character-span extraction, and deterministic patch planning.
"""

import posixpath
import re
import urllib.parse
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

from .db import LinkRecord
from .slugify import slugify_stem

# Detect external protocols or anchor-only references
EXTERNAL_OR_ANCHOR_PATTERN = re.compile(
    r"^(?:[a-zA-Z][a-zA-Z0-9+.-]*://|//|mailto:|tel:|#)"
)

# CommonMark link pattern: matches [label](<destination with spaces>) or [label](destination)
LINK_OR_IMAGE_PATTERN = re.compile(
    r"(!?\[((?:[^\[\]]|\\.)*)\])\(\s*(?:<([^>]+)>|([^\s\)\"\']+(?:\s+[^\s\)\"\']+)*))(?:\s+([\"'])(.*?)\5)?\s*\)"
)


@dataclass(frozen=True)
class ExtractedLink:
    source_canonical: str
    target_canonical: str
    target_stem: str
    raw_target: str
    line_number: int
    is_image: bool
    label: str
    target_path: str
    suffix: str  # #fragment or ?query
    start_char: int
    end_char: int
    has_angle_brackets: bool = False


@dataclass(frozen=True)
class BrokenLinkDiagnostic:
    source_rel_path: str
    line_number: int
    raw_target: str
    suggested_fix: str | None
    reason: str
    category: str = (
        "DEAD_LINK"  # BOUNDARY_VIOLATION, CASE_6_QUARANTINE, DEAD_LINK, STEM_COLLISION
    )


@dataclass(frozen=True)
class LinkPatch:
    source_rel_path: str
    start_char: int
    end_char: int
    old_target: str
    new_target: str


@dataclass
class LinkHealingPlan:
    patches_by_file: dict[str, list[LinkPatch]] = field(default_factory=dict)

    @property
    def has_patches(self) -> bool:
        return any(bool(p) for p in self.patches_by_file.values())

    @property
    def total_patch_count(self) -> int:
        return sum(len(p) for p in self.patches_by_file.values())


def mask_inline_code_spans(text: str) -> str:
    """
    Scans a single line and replaces contents of inline code spans with whitespace.
    Strictly adheres to CommonMark delimiter matching without regex backtracking.
    """
    out = []
    i = 0
    n = len(text)
    while i < n:
        if text[i] == "`":
            start = i
            while i < n and text[i] == "`":
                i += 1
            delim_len = i - start
            delim = "`" * delim_len
            end = text.find(delim, i)
            if end != -1:
                total_len = (end + delim_len) - start
                out.append(" " * total_len)
                i = end + delim_len
            else:
                out.append(text[start:i])
                i = n
        else:
            out.append(text[i])
            i += 1
    return "".join(out)


def mask_code_and_delimiters(content: str) -> str:
    """
    Replaces contents of fenced code blocks, inline code spans, and HTML comments
    with spaces while retaining exact string character length and newline positions.
    """
    chars = list(content)

    # 1. Mask fenced code blocks (``` or ~~~)
    lines = content.splitlines(keepends=True)
    pos = 0
    in_fenced = False
    fence_char = ""
    fence_len = 0

    for line in lines:
        stripped = line.strip()
        line_len = len(line)
        if not in_fenced:
            if stripped.startswith("```") or stripped.startswith("~~~"):
                f_char = stripped[0]
                m = re.match(r"^[`~]+", stripped)
                if m and len(m.group(0)) >= 3:
                    in_fenced = True
                    fence_char = f_char
                    fence_len = len(m.group(0))
        else:
            # Mask inner lines completely except newline
            for p in range(pos, pos + line_len):
                if chars[p] not in ("\r", "\n"):
                    chars[p] = " "
            if stripped.startswith(fence_char * fence_len):
                in_fenced = False
        pos += line_len

    # 2. Mask HTML comments (<!-- ... -->)
    comment_pattern = re.compile(r"<!--[\s\S]*?-->")
    for cm in comment_pattern.finditer("".join(chars)):
        for p in range(cm.start(), cm.end()):
            if chars[p] not in ("\r", "\n"):
                chars[p] = " "

    # 3. Mask inline code spans per line
    masked_text = "".join(chars)
    final_lines = []
    for line in masked_text.splitlines(keepends=True):
        final_lines.append(mask_inline_code_spans(line))

    return "".join(final_lines)


def split_target_url(raw_target: str) -> tuple[str, str]:
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


def parse_markdown_links(content: str, source_canonical: str) -> list[ExtractedLink]:
    """
    Parses Markdown text and extracts relative links and images with exact character offsets.
    Accurately ignores links enclosed inside fenced code blocks and inline code spans.
    """
    extracted: list[ExtractedLink] = []
    masked = mask_code_and_delimiters(content)

    for match in LINK_OR_IMAGE_PATTERN.finditer(masked):
        is_image = match.group(1).startswith("!")
        label = match.group(2)

        has_angle = match.group(3) is not None
        if has_angle:
            raw_url = match.group(3).strip()
            start_char = match.start(3)
            end_char = match.end(3)
        else:
            raw_url = (match.group(4) or "").strip()
            start_char = match.start(4)
            end_char = match.end(4)

        if not raw_url or is_external_or_anchor(raw_url):
            continue

        path_part, suffix_part = split_target_url(raw_url)
        unquoted_path = urllib.parse.unquote(path_part)
        target_pure = PurePosixPath(unquoted_path)

        target_stem = slugify_stem(target_pure.stem)
        if not target_stem:
            continue

        ext = target_pure.suffix.lower()
        if not ext:
            ext = ".md"
        target_canonical = f"{target_stem}{ext}"
        line_number = content[: match.start()].count("\n") + 1

        extracted.append(
            ExtractedLink(
                source_canonical=source_canonical,
                target_canonical=target_canonical,
                target_stem=target_stem,
                raw_target=raw_url,
                line_number=line_number,
                is_image=is_image,
                label=label,
                target_path=path_part,
                suffix=suffix_part,
                start_char=start_char,
                end_char=end_char,
                has_angle_brackets=has_angle,
            )
        )

    return extracted


def to_link_records(
    extracted_links: list[ExtractedLink],
    target_rel_map: dict[str, str] | None = None,
    current_canonicals: set[str] | None = None,
) -> list[LinkRecord]:
    """Converts ExtractedLink items into SQLite LinkRecord objects."""
    records = []
    target_map = target_rel_map or {}
    canonicals = current_canonicals or set()

    for link in extracted_links:
        is_broken = link.target_canonical not in canonicals if canonicals else False
        rel_target = target_map.get(link.target_canonical, link.target_path)
        records.append(
            LinkRecord(
                source_canonical=link.source_canonical,
                target_canonical=link.target_canonical,
                raw_target=link.raw_target,
                line_number=link.line_number,
                target_rel_path=rel_target,
                start_char=link.start_char,
                end_char=link.end_char,
                is_image=link.is_image,
                is_broken=is_broken,
            )
        )
    return records


def compute_relative_link(source_rel_path: str, target_rel_path: str) -> str:
    """
    Calculates the explicit relative POSIX path from source_rel_path to target_rel_path.
    Guaranteed deterministic forward-slash output across all host operating systems.
    """
    src_parent = PurePosixPath(source_rel_path).parent
    src_dir_str = "." if str(src_parent) == "." else str(src_parent)
    return posixpath.relpath(target_rel_path, start=src_dir_str)


def plan_link_healing(
    content_root: Path,
    scanned_files: list,
    relocation_map: dict[str, str],  # old_rel/old_canonical -> final_rel
    canonical_to_final_rel: dict[str, str],
    boundary_violations: list[tuple[str, str, int, str]],
) -> tuple[LinkHealingPlan, list[BrokenLinkDiagnostic]]:
    """
    Evaluates all Markdown files and generates exact character-span patches
    for both inbound and outbound link relocations, while capturing broken diagnostics.
    """
    healing_plan = LinkHealingPlan()
    diagnostics: list[BrokenLinkDiagnostic] = []
    content_root = content_root.resolve()

    # Set of (source_rel_path, line_number) representing boundary violations to skip
    boundary_violation_keys = {(v[0], v[2]) for v in boundary_violations}

    for f in scanned_files:
        if f.is_media or f.ext not in (".md", ".markdown"):
            continue

        file_abs = content_root / f.rel_path
        if not file_abs.is_file():
            continue

        try:
            content = file_abs.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        links = parse_markdown_links(content, f.canonical_filename)
        if not links:
            continue

        file_patches: list[LinkPatch] = []
        final_source_rel: str = relocation_map.get(f.rel_path) or f.rel_path
        source_dir = PurePosixPath(f.rel_path).parent

        for link in links:
            # 1. Skip if this link is a security boundary violation
            if (f.rel_path, link.line_number) in boundary_violation_keys:
                diagnostics.append(
                    BrokenLinkDiagnostic(
                        source_rel_path=f.rel_path,
                        line_number=link.line_number,
                        raw_target=link.raw_target,
                        suggested_fix=None,
                        reason="Security boundary violation (cross-context reference)",
                        category="BOUNDARY_VIOLATION",
                    )
                )
                continue

            unquoted_path = urllib.parse.unquote(link.target_path)
            if str(source_dir) != ".":
                expected_rel = posixpath.normpath(
                    posixpath.join(str(source_dir), unquoted_path)
                )
            else:
                expected_rel = posixpath.normpath(unquoted_path)

            # Determine final target relative path
            final_target_rel = (
                relocation_map.get(expected_rel)
                or relocation_map.get(expected_rel + ".md")
                or canonical_to_final_rel.get(link.target_canonical)
                or relocation_map.get(link.target_canonical)
            )

            if not final_target_rel:
                diagnostics.append(
                    BrokenLinkDiagnostic(
                        source_rel_path=f.rel_path,
                        line_number=link.line_number,
                        raw_target=link.raw_target,
                        suggested_fix=None,
                        reason="Target document or asset does not exist in vault",
                        category="DEAD_LINK",
                    )
                )
                continue

            # Calculate deterministic relative link from final source to final target
            new_rel = compute_relative_link(final_source_rel, final_target_rel)
            new_full_target = f"{new_rel}{link.suffix}"

            # Only generate patch if the destination string actually changed
            if new_full_target != link.raw_target:
                # If target originally had angle brackets or new target has spaces, format accordingly
                formatted_target = (
                    f"<{new_full_target}>"
                    if (link.has_angle_brackets or " " in new_full_target)
                    else new_full_target
                )
                file_patches.append(
                    LinkPatch(
                        source_rel_path=f.rel_path,
                        start_char=link.start_char,
                        end_char=link.end_char,
                        old_target=link.raw_target,
                        new_target=formatted_target,
                    )
                )

        if file_patches:
            # Sort patches descending by start_char to guarantee non-conflicting slices
            sorted_patches = sorted(
                file_patches, key=lambda p: p.start_char, reverse=True
            )

            # Overlap assertion: ensure no patch spans overlap
            for i in range(len(sorted_patches) - 1):
                if sorted_patches[i + 1].end_char > sorted_patches[i].start_char:
                    raise ValueError(
                        f"Patch collision detected in {f.rel_path}: "
                        f"span [{sorted_patches[i + 1].start_char}:{sorted_patches[i + 1].end_char}] "
                        f"overlaps with [{sorted_patches[i].start_char}:{sorted_patches[i].end_char}]"
                    )

            healing_plan.patches_by_file[f.rel_path] = sorted_patches

    return healing_plan, diagnostics
