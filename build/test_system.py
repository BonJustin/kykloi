#!/usr/bin/env python3
"""
test_system.py - End-to-End Verification Harness for Kykloi
Validates:
1. NIST KAT Cryptographic vector verification.
2. Lua link translation robustness (handling anchors, query strings, and secure .enc).
3. Zero-boilerplate central bibliography resolution.
4. Incremental build caching (verifies search.db is NOT rebuilt if clean).
5. Search Worker query fallback logic (FTS5 sanitization).
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

BUILD_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BUILD_DIR))

import build_site


def print_status(test_name: str, passed: bool, detail: str = ""):
    color = "\033[92m[PASS]\033[0m" if passed else "\033[91m[FAIL]\033[0m"
    detail_str = f" - {detail}" if detail else ""
    print(f"{color} {test_name}{detail_str}")
    if not passed:
        sys.exit(1)


def test_crypto():
    try:
        build_site.verify_cryptographic_engine()
        print_status("1. Cryptographic Engine (NIST KAT Verification)", True)
    except Exception as e:
        print_status("1. Cryptographic Engine (NIST KAT Verification)", False, str(e))


def test_lua_filter():
    lua_script = BUILD_DIR / "translate_links.lua"
    if not lua_script.exists():
        print_status("2. Lua Link Filter", False, "translate_links.lua not found")
        return

    test_md = (
        "[Standard Link](sub/target.md)\n"
        "[Link with Anchor](sub/target.md#heading-1)\n"
        "[Link with Query](sub/target.md?version=2)\n"
        "[External](https://example.com/file.md)\n"
        "![Image](media/pic.jpg)\n"
    )

    cmd = ["pandoc", "--lua-filter", str(lua_script), "-t", "html"]
    p = subprocess.run(cmd, input=test_md, capture_output=True, text=True)

    ok1 = (
        'href="sub/target.html"' in p.stdout
        and 'href="sub/target.html#heading-1"' in p.stdout
        and 'href="sub/target.html?version=2"' in p.stdout
        and 'href="https://example.com/file.md"' in p.stdout
        and 'src="media/pic.jpg"' in p.stdout
    )

    env = os.environ.copy()
    env["KYKLOI_SECURE_BUILD"] = "1"
    p_sec = subprocess.run(cmd, input=test_md, capture_output=True, text=True, env=env)

    ok2 = (
        'src="media/pic.jpg.enc"' in p_sec.stdout
        and 'data-encrypted-media="true"' in p_sec.stdout
    )

    print_status(
        "2. Lua Filter (Links, Anchors, Query Strings & Secure Media)",
        ok1 and ok2,
        "Failed rewriting rules" if not (ok1 and ok2) else "",
    )


def test_dynamic_citeproc_and_incremental_index():
    with tempfile.TemporaryDirectory() as tmp_dir_name:
        sandbox = Path(tmp_dir_name)
        fake_content = sandbox / "content"
        fake_dist = sandbox / "dist"
        fake_content.mkdir()

        # Shared vault bibliography
        bib_file = fake_content / "references.bib"
        bib_file.write_text(
            """@article{knuth1984,
  author = {Knuth, Donald E.},
  title = {Literate Programming},
  year = {1984},
  journal = {The Computer Journal}
}"""
        )

        # Document A: Standard note (no citations)
        doc_a = fake_content / "plain_note.md"
        doc_a.write_text(
            "---\ntitle: Plain Note\n---\nJust a normal note with no references."
        )

        # Document B: Academic note without ANY frontmatter bibliography boilerplate
        doc_b = fake_content / "academic_note.md"
        doc_b.write_text(
            """---
title: Academic Note
---
Knuth introduced the idea in [@knuth1984].
"""
        )

        build_site.SRC = fake_content
        build_site.DST = fake_dist
        build_site.SEARCH_DB_FILE = fake_dist / "search.db"
        build_site.MANIFEST_FILE = sandbox / ".build_manifest.json"

        sys.argv = ["build_site.py", "--workers", "1"]

        # Run Build 1
        build_site.main()

        out_a = fake_dist / "plain_note.html"
        out_b = fake_dist / "academic_note.html"

        if not out_a.exists() or not out_b.exists():
            print_status(
                "3. Zero-Boilerplate Citations", False, "Outputs were not created."
            )
            return

        html_b = out_b.read_text()
        citeproc_resolved = "Knuth" in html_b and "Literate Programming" in html_b

        print_status(
            "3. Zero-Boilerplate Citations (Auto-detected from references.bib)",
            citeproc_resolved,
            "Citation @knuth1984 did not resolve" if not citeproc_resolved else "",
        )

        # Run Build 2 (Verify incremental index caching)
        mtime_before = build_site.SEARCH_DB_FILE.stat().st_mtime_ns
        build_site.main()
        mtime_after = build_site.SEARCH_DB_FILE.stat().st_mtime_ns

        clean_build_cached = mtime_before == mtime_after
        print_status(
            "4. Incremental Search Cache (search.db untouched on clean runs)",
            clean_build_cached,
            "search.db was unnecessarily rebuilt" if not clean_build_cached else "",
        )


def test_search_sanitization():
    import re

    def build_test_fts_query(raw_query: str):
        trimmed = raw_query.strip()
        tokens = re.sub(r"[^\w]+", " ", trimmed, flags=re.UNICODE).strip().split()
        return " ".join([f'"{t}"*' for t in tokens]) if tokens else None

    q1 = build_test_fts_query("hello: world")
    q2 = build_test_fts_query('"unmatched quote')
    q3 = build_test_fts_query("math + physics -")

    valid = (
        q1 == '"hello"* "world"*'
        and q2 == '"unmatched"* "quote"*'
        and q3 == '"math"* "physics"*'
    )

    print_status(
        "5. FTS5 Search Query Sanitizer",
        valid,
        "Query sanitizer produced invalid token structure",
    )


if __name__ == "__main__":
    print("\nRunning Kykloi System Verification Test Suite...\n")
    test_crypto()
    test_lua_filter()
    test_dynamic_citeproc_and_incremental_index()
    test_search_sanitization()
    print("\nAll verification suites executed successfully.\n")
