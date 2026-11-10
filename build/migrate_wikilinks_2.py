#!/usr/bin/env python3
"""
migrate_wikilinks.py - High-performance CommonMark relative link converter.
Transforms Obsidian/Zettlr wikilinks directly in the source Markdown files.
Protects KaTeX blocks, code fences, inline code, and YAML frontmatter.
Part of Project Kykloi.
"""

import argparse
import os
import re
from pathlib import Path

ID_PREFIX_PATTERN = re.compile(r"^(\d{14}|\d{12}|\d{8})(?:[-_].*)?$")

WIKI_IMAGE_PATTERN = re.compile(r"!\[\[\s*([^\]\|\n]+?)(?:\|([^\]\n]+))?\s*\]\]")
WIKI_LINK_PATTERN = re.compile(r"\[\[\s*([^\]\|\n]+?)(?:\|([^\]\n]+))?\s*\]\]")

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


def build_inventory(src_root: Path) -> dict[str, Path]:
    """Indexes content directory by relative path, stem, filename, and Zettelkasten ID."""
    inventory: dict[str, Path] = {}
    for p in src_root.rglob("*"):
        if p.is_file() and not p.name.startswith("."):
            rel = p.relative_to(src_root)
            posix_rel = rel.as_posix()

            inventory[posix_rel] = rel
            inventory[p.name] = rel
            if p.suffix.lower() == ".md":
                inventory[p.stem] = rel
                inventory[rel.with_suffix("").as_posix()] = rel

                m = ID_PREFIX_PATTERN.match(p.stem)
                if m:
                    inventory[m.group(1)] = rel

    return inventory


def calculate_relative_url(source_rel: Path, target_rel: Path) -> str:
    source_dir = source_rel.parent
    rel_path = os.path.relpath(target_rel, start=source_dir)
    return Path(rel_path).as_posix()


def convert_file_content(
    doc_rel: Path,
    content: str,
    inventory: dict[str, Path],
) -> tuple[str, int]:
    replacements = 0

    def replace_image(match: re.Match) -> str:
        nonlocal replacements
        raw_target = match.group(1).strip()
        alt_text = match.group(2).strip() if match.group(2) else ""

        target_file = inventory.get(raw_target) or inventory.get(Path(raw_target).name)
        if target_file:
            rel_link = calculate_relative_url(doc_rel, target_file)
            replacements += 1
            return f"![{alt_text or target_file.name}]({rel_link})"
        return match.group(0)

    def replace_link(match: re.Match) -> str:
        nonlocal replacements
        raw_target = match.group(1).strip()
        label = match.group(2).strip() if match.group(2) else ""

        anchor = ""
        target_name = raw_target
        if "#" in raw_target:
            target_name, anchor = raw_target.split("#", 1)
            anchor = "#" + anchor.strip()

        target_file = inventory.get(target_name) or inventory.get(
            Path(target_name).name
        )
        if target_file:
            rel_link = calculate_relative_url(doc_rel, target_file)
            display = (
                label
                if label
                else target_file.stem.replace("-", " ").replace("_", " ").title()
            )
            replacements += 1
            return f"[{display}]({rel_link}{anchor})"

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
    """
    Scans Markdown documents in src_root and rewrites wikilinks in-place.
    Uses an ultra-fast byte probe b'[[' before parsing to preserve build performance.
    """
    if not src_root.exists():
        return 0, 0

    md_candidates: list[Path] = []
    for p in src_root.rglob("*.md"):
        if p.name.startswith("."):
            continue
        try:
            # Ultra-fast probe to bypass clean files completely
            with open(p, "rb") as f:
                if b"[[" in f.read():
                    md_candidates.append(p)
        except OSError:
            continue

    if not md_candidates:
        return 0, 0

    # Build inventory lazily only if candidates exist
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
                print(f"[Migrate] Rewrote {count} wikilink(s) in {doc_rel}")

    return files_modified, links_converted


def main():
    parser = argparse.ArgumentParser(
        description="Migrate Obsidian/Zettlr wikilinks to deterministic standard Markdown links."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Display changes without writing to disk.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print each converted link.",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    src_root = project_root / "content"

    modified, converted = run_migration_pipeline(
        src_root=src_root, dry_run=args.dry_run, verbose=args.verbose
    )

    action = "Identified" if args.dry_run else "Converted"
    print(
        f"Wikilink Migration: {action} {converted} link(s) across {modified} file(s)."
    )


if __name__ == "__main__":
    main()
