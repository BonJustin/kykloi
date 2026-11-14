#!/usr/bin/env python3
"""
assemble_code_to_md.py - Simplified Codebase Context Aggregator.

Recursively generates an ASCII tree of the project and bundles the contents
of files specified in an inclusion whitelist into a single markdown file.
"""

import re
from pathlib import Path

# ===========================================================================
# CONFIGURATION
# ===========================================================================

ROOT_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = ROOT_DIR / "codebase_bundle.md"

# Folders to display in the tree without traversing or bundling their contents
EXCLUDED_DIRS = {
    ".git",
    ".github",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "dist",
    "katex",
    "fonts",
}

# Whitelist of files to bundle (match by filename or relative POSIX path)
INCLUDED_FILES = {
    "pyproject.toml",
    "README.md",
    "admin.html",
    "app.css",
    "app.js",
    "style.css",
    "decrypt.js",
    "pico_search.js",
    "search_worker.js",
    "index.html",
    "md_to_static_html.html",
    "build_site.py",
    "pandoc_md_to_static_html.yaml",
    "translate_links.lua",
    "launch.py",
    "serve.py",
}

# Optional overrides for markdown syntax highlighting; unlisted extensions
# default to the extension name itself (e.g., .css -> css, .html -> html)
LANG_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".sh": "bash",
    ".yml": "yaml",
}


# ===========================================================================
# TRAVERSAL & BUNDLE GENERATION
# ===========================================================================


def get_safe_fence(content: str) -> str:
    """Returns a markdown code fence backtick string long enough not to collide."""
    ticks = re.findall(r"`+", content)
    max_ticks = max((len(t) for t in ticks), default=0)
    return "`" * max(3, max_ticks + 1)


def traverse(directory: Path, prefix: str = "") -> tuple[list[str], list[Path]]:
    """Recursively constructs tree lines and collects whitelisted files in one pass."""
    tree_lines: list[str] = []
    bundle_files: list[Path] = []

    try:
        entries = sorted(
            directory.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower())
        )
    except PermissionError:
        return tree_lines, bundle_files

    # Ignore system metadata and the generated bundle itself
    entries = [
        e for e in entries if e.name not in {OUTPUT_FILE.name, ".DS_Store", "Thumbs.db"}
    ]

    total = len(entries)
    for idx, entry in enumerate(entries):
        is_last = idx == total - 1
        connector = "└── " if is_last else "├── "
        child_prefix = prefix + ("    " if is_last else "│   ")
        rel_path = entry.relative_to(ROOT_DIR).as_posix()

        if entry.is_dir():
            if entry.name in EXCLUDED_DIRS or rel_path in EXCLUDED_DIRS:
                tree_lines.append(
                    f"{prefix}{connector}{entry.name}/ (contents excluded)"
                )
            else:
                tree_lines.append(f"{prefix}{connector}{entry.name}/")
                sub_lines, sub_files = traverse(entry, child_prefix)
                tree_lines.extend(sub_lines)
                bundle_files.extend(sub_files)
        else:
            tree_lines.append(f"{prefix}{connector}{entry.name}")
            if entry.name in INCLUDED_FILES or rel_path in INCLUDED_FILES:
                bundle_files.append(entry)

    return tree_lines, bundle_files


def assemble_bundle() -> None:
    """Traverses the project and writes the directory tree and file bundle."""
    tree_lines, bundle_files = traverse(ROOT_DIR)

    output = [
        "# Project Directory Tree",
        "",
        "```text",
        f"{ROOT_DIR.name}/",
        *tree_lines,
        "```",
        "",
        "# Source Files",
        "",
    ]

    for file_path in bundle_files:
        rel_path = file_path.relative_to(ROOT_DIR).as_posix()
        try:
            content = file_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue

        fence = get_safe_fence(content)
        lang = LANG_MAP.get(
            file_path.suffix.lower(), file_path.suffix.lstrip(".").lower()
        )

        output.append(f"## {rel_path}\n")
        output.append(f"{fence}{lang}")
        output.append(content.rstrip())
        output.append(fence)
        output.append("")

    OUTPUT_FILE.write_text("\n".join(output), encoding="utf-8")
    print(f"Bundle successfully created at: {OUTPUT_FILE}")
    print(f"Total source files included: {len(bundle_files)}")


if __name__ == "__main__":
    assemble_bundle()
