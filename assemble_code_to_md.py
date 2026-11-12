#!/usr/bin/env python3
"""assemble_code_to_md.py

Assembles specified codebase files into a single CommonMark-compliant Markdown file.
Prioritizes explicit paths, prunes vendor bloat from directory listings, and appends
a categorized context block with justifications for all excluded components.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

# ----------------------------------------------------------------------
# 1. TARGET FILE SPECIFICATION
# Explicit relative paths eliminate path resolution ambiguity.
# ----------------------------------------------------------------------
FILES_TO_INCLUDE = [
    # Project Configuration & Architectural Intent
    "pyproject.toml",
    "README.md",
    "run_linux_mac.sh",
    "run_windows.bat",
    # Core Pipeline & Backend
    "serve.py",
    "build/build_site.py",
    "build/pandoc_md_to_static_html.yaml",
    "build/translate_links.lua",
    # Templates & Source HTML
    "build/root/index.html",
    "build/templates/md_to_static_html.html",
    "build/templates/metadata.json",
    # Client-Side Logic & Layout
    "build/assets/css/style.css",
    "build/assets/js/decrypt.js",
    "build/assets/js/pico_search.js",
    "build/assets/js/search_worker.js",
    # Representative Input Content (Schemas, Frontmatter, Encryption targets)
    "content/pandoc_markdown.md",
    "content/secure/20261031165927-nested-directory-test.md",
    "admin/admin.html",
    "admin/app.js",
    "admin/app.css",
    "launch.py",
]

OUTPUT_FILE = "codebase_bundle.md"

# ----------------------------------------------------------------------
# 2. EXCLUSION RULES & EVALUATION CONTEXT
# ----------------------------------------------------------------------
EXCLUSIONS_WITH_RATIONALE = [
    (
        "dist/",
        "Derived Build Artifacts",
        "Contains ephemeral, auto-generated HTML, media blobs (.enc), and SQLite indices. "
        "Source files under build/ and content/ represent the ground truth.",
    ),
    (
        "build/assets/katex/ & build/assets/fonts/",
        "Third-Party Vendor Binaries/Assets",
        "Contains pre-compiled upstream KaTeX assets (WASM/JS/CSS) and TTF/WOFF2 font binaries. "
        "Excluded to conserve LLM context window tokens without loss of architectural semantic meaning.",
    ),
    (
        "build/assets/js/sqlite3*.js & sqlite3.wasm",
        "Upstream SQLite3 WASM Runtime",
        "Pre-compiled official SQLite WASM engine. The proprietary integration surface "
        "resides entirely within build/assets/js/search_worker.js.",
    ),
    (
        ".git/, .github/, .venv/, __pycache__/",
        "Version Control & Environment Metadata",
        "Platform-specific cache directories, local virtual environments, and VCS internal records.",
    ),
]

TREE_IGNORE_PATTERNS = {
    ".git",
    ".github",
    ".venv",
    "venv",
    "__pycache__",
    "dist",
    "katex",
    "fonts",
    "node_modules",
}

LANGUAGE_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".json": "json",
    ".toml": "toml",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".md": "markdown",
    ".sh": "bash",
    ".bat": "bat",
    ".html": "html",
    ".css": "css",
    ".sql": "sql",
    ".lua": "lua",
}


def get_fence(content: str) -> str:
    """Returns a backtick fence strictly longer than any internal backtick sequence."""
    matches = re.findall(r"`+", content)
    longest = max((len(m) for m in matches), default=0)
    return "`" * max(3, longest + 1)


def generate_python_tree(root_dir: Path, max_depth: int = 4) -> str:
    """Pure-Python fallback for filtered directory tree generation."""
    lines: list[str] = [root_dir.name + "/"]

    def _walk(directory: Path, prefix: str = "", depth: int = 0):
        if depth >= max_depth:
            return
        entries = sorted(
            [e for e in directory.iterdir() if e.name not in TREE_IGNORE_PATTERNS],
            key=lambda e: (e.is_file(), e.name.lower()),
        )
        count = len(entries)
        for i, entry in enumerate(entries):
            is_last = i == count - 1
            connector = "└── " if is_last else "├── "
            lines.append(
                f"{prefix}{connector}{entry.name}{'/' if entry.is_dir() else ''}"
            )
            if entry.is_dir():
                sub_prefix = prefix + ("    " if is_last else "│   ")
                _walk(entry, sub_prefix, depth + 1)

    _walk(root_dir)
    return "\n".join(lines)


def get_tree_output(root_dir: Path) -> str:
    """Runs `tree` with ignore flags, falling back to pure-Python generator if unavailable."""
    ignore_pattern = "|".join(TREE_IGNORE_PATTERNS)
    try:
        cmd = ["tree", ".", "-I", ignore_pattern, "--dirsfirst"]
        result = subprocess.run(
            cmd,
            cwd=root_dir,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return generate_python_tree(root_dir)


def assemble_markdown(
    files: list[str],
    root_dir: Path,
    output_file: str,
) -> None:
    lines: list[str] = []
    assembled_count = 0

    for file_str in files:
        file_path = (root_dir / file_str).resolve()

        if not file_path.is_file():
            print(
                f"Warning: Specified file '{file_str}' not found. Skipping.",
                file=sys.stderr,
            )
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            print(
                f"Warning: '{file_str}' is binary or unreadable. Skipping.",
                file=sys.stderr,
            )
            continue

        rel_display_path = file_path.relative_to(root_dir).as_posix()
        ext = file_path.suffix.lower()
        lang = LANGUAGE_MAP.get(ext, "")
        fence = get_fence(content)

        lines.append(f"## {rel_display_path}")
        lines.append("")
        lines.append(f"{fence}{lang}")
        lines.append(content.rstrip("\r\n"))
        lines.append(fence)
        lines.append("")
        assembled_count += 1

    # Filtered Structural Tree
    tree_text = get_tree_output(root_dir)
    tree_fence = get_fence(tree_text)

    lines.append("## Filtered Project Directory Tree")
    lines.append("")
    lines.append(f"{tree_fence}text")
    lines.append(tree_text)
    lines.append(tree_fence)
    lines.append("")

    # Explicit Context and Exclusions Block
    lines.append("## Evaluation Context & Exclusion Manifest")
    lines.append("")
    lines.append(
        "The following targets are deliberately omitted from this evaluation bundle. "
        "Reviewing models must evaluate the system according to the rationales below:"
    )
    lines.append("")

    for target, category, rationale in EXCLUSIONS_WITH_RATIONALE:
        lines.append(f"### `{target}` ({category})")
        lines.append(f"{rationale}")
        lines.append("")

    output_path = root_dir / output_file
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(
        f"Assembly complete: {assembled_count} file(s) bundled into '{output_path.relative_to(root_dir)}'."
    )


def main() -> None:
    root_dir = Path.cwd()
    assemble_markdown(FILES_TO_INCLUDE, root_dir, OUTPUT_FILE)


if __name__ == "__main__":
    main()
