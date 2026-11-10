#!/usr/bin/env python3
"""
migrate_wikilinks.py - Permanently convert Obsidian/Zettlr wikilinks to deterministic relative CommonMark links.
Context-aware parser that protects KaTeX math ($$, $, \\[), code blocks, inline code, and YAML frontmatter.
Includes Zettlr ID prefix mapping support.
Part of Project Kykloi.
"""

import argparse
import os
import re
import sys
from pathlib import Path

ID_PREFIX_PATTERN = re.compile(r"^(\d{14}|\d{12}|\d{8})(?:[-_].*)?$")


def build_inventory(src_root: Path) -> dict[str, Path]:
    """Indexes all files in content/ by relative path, stem, filename, and Zettelkasten ID prefix."""
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
                    id_prefix = m.group(1)
                    inventory[id_prefix] = rel

    return inventory


def calculate_relative_url(source_file: Path, target_rel: Path) -> str:
    source_dir = source_file.parent
    rel_path = os.path.relpath(target_rel, start=source_dir)
    return Path(rel_path).as_posix()


# Matches ![[target|alt]] or ![[target]]
WIKI_IMAGE_PATTERN = re.compile(r"!\[\[\s*([^\]\|\n]+?)(?:\|([^\]\n]+))?\s*\]\]")

# Matches [[target|text]] or [[target]]
WIKI_LINK_PATTERN = re.compile(r"\[\[\s*([^\]\|\n]+?)(?:\|([^\]\n]+))?\s*\]\]")

# Tokenizer regex to carve out protected blocks from Markdown content
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


def convert_file_content(
    file_path: Path,
    content: str,
    inventory: dict[str, Path],
    src_root: Path,
) -> tuple[str, int]:
    doc_rel = file_path.relative_to(src_root)
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


def main():
    parser = argparse.ArgumentParser(
        description="Migrate Obsidian/Zettlr wikilinks to deterministic standard Markdown links (KaTeX/Code safe)."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Display changes without writing them to disk.",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    src_root = project_root / "content"

    if not src_root.exists():
        print(f"Error: content directory does not exist at {src_root}", file=sys.stderr)
        sys.exit(1)

    inventory = build_inventory(src_root)
    md_files = sorted(src_root.rglob("*.md"))

    total_files_modified = 0
    total_links_converted = 0

    for md in md_files:
        try:
            with open(md, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError as e:
            print(f"Skipping unreadable file {md}: {e}", file=sys.stderr)
            continue

        new_content, count = convert_file_content(md, content, inventory, src_root)

        if count > 0:
            total_files_modified += 1
            total_links_converted += count
            rel_path = md.relative_to(src_root)

            if args.dry_run:
                print(f"[DRY-RUN] {rel_path}: {count} wikilink(s) to convert.")
            else:
                with open(md, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"Converted {count} wikilink(s) in {rel_path}.")

    if args.dry_run:
        print(
            f"\nDry run complete: Found {total_links_converted} wikilink(s) across {total_files_modified} file(s)."
        )
    else:
        print(
            f"\nMigration complete: Converted {total_links_converted} wikilink(s) across {total_files_modified} file(s)."
        )


if __name__ == "__main__":
    main()
