#!/usr/bin/env python3
"""
migrate_wikilinks.py - High-Performance CommonMark Link Normalizer.
Converts Obsidian, Zettlr, Logseq, and Foam wikilinks into standards-compliant CommonMark.
Handles spaces, anchors, block IDs, frontmatter IDs, and Zettelkasten timestamp prefixes.
Strips non-standard image dimension specifiers (|300, |300x200) to maintain archival purity.
Protects KaTeX blocks, code fences, inline code, and YAML frontmatter.
Filters all editor caches, workspaces, OS trash, and swap files.
Part of Project Kykloi.
"""

import argparse
import os
import re
import urllib.parse
from pathlib import Path

# Matches standard Zettelkasten timestamp formats (8 to 14 digits)
ID_PREFIX_PATTERN = re.compile(r"^(\d{14}|\d{12}|\d{8})(?:[-_\s].*)?$")

# Matches Zettlr frontmatter ID: "id: 20240101120000" or "id: '20240101120000'"
FRONTMATTER_ID_PATTERN = re.compile(r"^id:\s*['\"]?(\d{8,14})['\"]?", re.MULTILINE)

# Match ![[target#anchor|alt_or_dimensions]] or ![[target]]
WIKI_IMAGE_PATTERN = re.compile(r"!\[\[\s*([^\]\|\n]+?)(?:\|([^\]\n]*))?\s*\]\]")

# Match [[target#anchor|label]] or [[target]]
WIKI_LINK_PATTERN = re.compile(r"\[\[\s*([^\]\|\n]+?)(?:\|([^\]\n]*))?\s*\]\]")

# Matches virtual resizing dimensions like "300" or "300x200"
DIMENSION_PATTERN = re.compile(r"^\d+(?:x\d+)?$")

# Carve out protected syntactic blocks from Markdown content
PROTECTED_ZONES_PATTERN = re.compile(
    r"("
    r"^---[\s\S]*?^---|"  # YAML Frontmatter
    r"```[\s\S]*?```|"  # Fenced code blocks (backticks)
    r"~~~[\s\S]*?~~~|"  # Fenced code blocks (tildes)
    r"\$\$(?:\\.|[^\\])*?\$\$|"  # Display math $$ ... $$
    r"\\\[[\s\S]*?\\\]|"  # Display math \[ ... \]
    r"`[^`\n]+`|"  # Inline code
    r"\$(?:\\.|[^\$\\\n])+\$|"  # Inline math $ ... $
    r"\\\([\s\S]*?\\\)"  # Inline math \( ... \)
    r")",
    re.MULTILINE,
)

# Disallowed directory names (exact match, case-insensitive)
JUNK_DIRS = {
    ".obsidian",
    ".trash",
    ".zettlr",
    ".logseq",
    "logseq",
    ".git",
    ".vscode",
    ".idea",
    ".foam",
    ".dendron",
    ".sync",
    "node_modules",
}

# Disallowed filenames (exact match, case-insensitive)
JUNK_EXACT_FILES = {
    ".ds_store",
    "thumbs.db",
    "desktop.ini",
    "ehthumbs.db",
    ".gitignore",
    ".gitattributes",
    ".ztr-directory",
}


def is_junk_path(path: Path) -> bool:
    """
    Determines if a given path is an OS artifact, editor workspace file,
    VCS metadata, lock/swap file, or deleted note in .trash/.
    """
    for part in path.parts[:-1]:
        part_lower = part.lower()
        if part_lower in JUNK_DIRS or part.startswith("."):
            return True

    name = path.name
    name_lower = name.lower()

    if name_lower in JUNK_EXACT_FILES:
        return True

    if name.startswith(".") or name.startswith("._"):
        return True

    if (
        name.endswith("~")
        or name.endswith(".swp")
        or name.endswith(".swo")
        or name.startswith("~$")
        or (name.startswith(".#") and name.endswith("#"))
    ):
        return True

    return False


def extract_frontmatter_id(path: Path) -> str | None:
    """Fast probe to extract Zettlr/Obsidian ID from YAML header."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            chunk = f.read(1024)
        if chunk.startswith("---"):
            end_idx = chunk.find("---", 3)
            if end_idx != -1:
                header = chunk[3:end_idx]
                match = FRONTMATTER_ID_PATTERN.search(header)
                if match:
                    return match.group(1)
    except OSError:
        pass
    return None


def build_inventory(src_root: Path) -> dict[str, Path]:
    """
    Constructs an exhaustive dictionary of target lookups from clean files:
    - Relative POSIX path without extension: 'folder/Note'
    - Exact filename: 'Note.md', 'Image.png'
    - File stem (case-sensitive and lowercase): 'Note'
    - Zettelkasten ID (from filename prefix or frontmatter)
    """
    inventory: dict[str, Path] = {}

    for p in src_root.rglob("*"):
        if not p.is_file() or is_junk_path(p):
            continue

        rel = p.relative_to(src_root)
        posix_rel = rel.as_posix()
        name = p.name
        stem = p.stem

        inventory[posix_rel] = rel
        inventory[name] = rel
        inventory[stem] = rel
        inventory[stem.lower()] = rel

        if p.suffix.lower() == ".md":
            no_ext_rel = rel.with_suffix("").as_posix()
            inventory[no_ext_rel] = rel
            inventory[no_ext_rel.lower()] = rel

            m = ID_PREFIX_PATTERN.match(stem)
            if m:
                inventory[m.group(1)] = rel

            f_id = extract_frontmatter_id(p)
            if f_id:
                inventory[f_id] = rel

    return inventory


def format_commonmark_url(source_rel: Path, target_rel: Path, anchor: str = "") -> str:
    """
    Computes a relative path from source to target, percent-encoding spaces
    and illegal characters while preserving valid path separators and anchor hashes.
    """
    source_dir = source_rel.parent
    rel_path_str = os.path.relpath(target_rel, start=source_dir)
    posix_path = Path(rel_path_str).as_posix()

    encoded_path = urllib.parse.quote(posix_path, safe="/#%")

    if anchor:
        clean_anchor = anchor.strip()
        if not clean_anchor.startswith("#"):
            clean_anchor = "#" + clean_anchor
        encoded_anchor = urllib.parse.quote(clean_anchor, safe="#-_")
        return f"{encoded_path}{encoded_anchor}"

    return encoded_path


def resolve_target(
    raw_target: str, inventory: dict[str, Path]
) -> tuple[Path | None, str]:
    """
    Resolves targets containing anchors, paths, or ZK IDs against clean inventory.
    """
    target = raw_target.strip()
    anchor = ""

    if "#" in target:
        target, anchor = target.split("#", 1)
        target = target.strip()
        anchor = "#" + anchor.strip()

    if not target:
        return None, anchor

    if target in inventory:
        return inventory[target], anchor

    target_lower = target.lower()
    if target_lower in inventory:
        return inventory[target_lower], anchor

    base_name = Path(target).name
    if base_name in inventory:
        return inventory[base_name], anchor

    base_lower = base_name.lower()
    if base_lower in inventory:
        return inventory[base_lower], anchor

    zk_match = ID_PREFIX_PATTERN.match(base_name)
    if zk_match:
        zk_id = zk_match.group(1)
        if zk_id in inventory:
            return inventory[zk_id], anchor

    return None, anchor


def clean_image_alt_text(meta_text: str) -> str:
    """
    Strips non-standard virtual dimension suffixes (|300, |300x200, ,300)
    to preserve pure CommonMark syntax without non-standard attribute extensions.
    """
    meta = meta_text.strip()
    if not meta:
        return ""

    if DIMENSION_PATTERN.match(meta):
        return ""

    for separator in (",", "|"):
        if separator in meta:
            parts = meta.rsplit(separator, 1)
            tail = parts[1].strip()
            if DIMENSION_PATTERN.match(tail):
                return parts[0].strip()

    return meta


def convert_file_content(
    doc_rel: Path,
    content: str,
    inventory: dict[str, Path],
) -> tuple[str, int]:
    replacements = 0

    def replace_image(match: re.Match) -> str:
        nonlocal replacements
        raw_target = match.group(1).strip()
        meta_param = match.group(2).strip() if match.group(2) else ""

        target_file, _ = resolve_target(raw_target, inventory)
        if target_file:
            encoded_url = format_commonmark_url(doc_rel, target_file)
            replacements += 1

            alt_text = clean_image_alt_text(meta_param)
            display = alt_text or target_file.name

            return f"![{display}]({encoded_url})"

        return match.group(0)

    def replace_link(match: re.Match) -> str:
        nonlocal replacements
        raw_target = match.group(1).strip()
        explicit_label = match.group(2).strip() if match.group(2) else ""

        target_file, anchor = resolve_target(raw_target, inventory)

        if target_file:
            encoded_url = format_commonmark_url(doc_rel, target_file, anchor)
            replacements += 1

            if explicit_label:
                display = explicit_label
            else:
                display = target_file.stem.replace("-", " ").replace("_", " ").title()
                if anchor and not target_file.name:
                    display = anchor.lstrip("#")

            return f"[{display}]({encoded_url})"

        if not target_file and anchor:
            replacements += 1
            display = explicit_label or anchor.lstrip("#")
            clean_anchor = urllib.parse.quote(anchor, safe="#-_")
            return f"[{display}]({clean_anchor})"

        return match.group(0)

    tokens = PROTECTED_ZONES_PATTERN.split(content)
    output_segments: list[str] = []

    for idx, segment in enumerate(tokens):
        if idx % 2 == 1:
            output_segments.append(segment)
        else:
            subbed = WIKI_IMAGE_PATTERN.sub(replace_image, segment)
            subbed = WIKI_LINK_PATTERN.sub(replace_link, subbed)
            output_segments.append(subbed)

    return "".join(output_segments), replacements


def run_migration_pipeline(
    src_root: Path, dry_run: bool = False, verbose: bool = False
) -> tuple[int, int]:
    if not src_root.exists():
        return 0, 0

    md_candidates: list[Path] = []
    for p in src_root.rglob("*.md"):
        if is_junk_path(p):
            continue
        try:
            with open(p, "rb") as f:
                if b"[[" in f.read():
                    md_candidates.append(p)
        except OSError:
            continue

    if not md_candidates:
        return 0, 0

    inventory = build_inventory(src_root)
    files_modified = 0
    links_converted = 0

    for md in md_candidates:
        try:
            with open(md, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError:
            continue

        doc_rel = md.relative_to(src_root)
        new_content, count = convert_file_content(doc_rel, content, inventory)

        if count > 0:
            files_modified += 1
            links_converted += count
            if not dry_run:
                with open(md, "w", encoding="utf-8") as f:
                    f.write(new_content)
            if verbose:
                print(f"[Migrate] Converted {count} link(s) in {doc_rel}")

    return files_modified, links_converted


def main():
    parser = argparse.ArgumentParser(
        description="Migrate Obsidian/Zettlr wikilinks to standard CommonMark relative links."
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview migrations without disk writes."
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Print granular file conversions."
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    src_root = project_root / "content"

    modified, count = run_migration_pipeline(
        src_root=src_root, dry_run=args.dry_run, verbose=args.verbose
    )
    action = "Identified" if args.dry_run else "Converted"
    print(f"Wikilink Migration: {action} {count} link(s) across {modified} file(s).")


if __name__ == "__main__":
    main()
