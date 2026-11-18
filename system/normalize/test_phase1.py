# system/normalize/test_phase1.py
import sys
from pathlib import Path

# Ensure project root (kykloi/) is on sys.path regardless of execution cwd
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from system.normalize.db import FileRecord, LinkRecord, VaultDB
from system.normalize.slugify import is_valid_stem, sanitize_path_segments, slugify_stem


def run_tests():
    print("[1/3] Testing slugify and validation...")
    test_cases = [
        ("My Note 2026!", "my-note-2026"),
        ("über_mathematics...", "ber_mathematics"),
        ("20261116170353-kykloi-introduction", "20261116170353-kykloi-introduction"),
        ("test:::invalid<chars>", "testinvalidchars"),
        ("---leading-and-trailing---", "leading-and-trailing"),
        ("__double__underscores__", "double_underscores"),
    ]
    for raw, expected in test_cases:
        slug = slugify_stem(raw)
        assert slug == expected, f"Expected '{expected}', got '{slug}' for '{raw}'"
        assert is_valid_stem(slug), f"Slug '{slug}' is not valid per UID regex"

    path_test = "Research Folder/Quantum Physics/Wave Function.MD"
    assert (
        sanitize_path_segments(path_test)
        == "research-folder/quantum-physics/wave-function.md"
    )
    print("  -> Slugify & Path tests passed.")

    print("[2/3] Testing SQLite schema initialization & FileRecord operations...")
    test_db_path = Path(__file__).resolve().parent / "test_vault_index.db"

    # Clean previous run artifacts
    for f in test_db_path.parent.glob("test_vault_index.db*"):
        try:
            f.unlink()
        except OSError:
            pass

    with VaultDB(test_db_path) as db:
        db.init_schema()
        assert db.get_meta("schema_version") == "1.0"

        rec1 = FileRecord(
            id=None,
            stem="matrix-notes",
            rel_path="math/matrix-notes.md",
            sha256="abc123hash",
            mtime=1700000000.0,
            size=1024,
            is_media=False,
            is_secure=False,
        )
        db.upsert_file(rec1)

        fetched = db.get_file_by_stem("matrix-notes")
        assert fetched is not None
        assert fetched.rel_path == "math/matrix-notes.md"
        assert fetched.size == 1024

        # Stat-cache test
        assert db.is_stat_cache_hit("math/matrix-notes.md", 1700000000.0, 1024) is True
        assert db.is_stat_cache_hit("math/matrix-notes.md", 1700000000.0, 2048) is False

        print("  -> File ledger and stat-cache tests passed.")

        print("[3/3] Testing Foreign Key cascading & link graph operations...")
        rec2 = FileRecord(
            id=None,
            stem="linear-algebra",
            rel_path="math/linear-algebra.md",
            sha256="def456hash",
            mtime=1700000001.0,
            size=2048,
            is_media=False,
            is_secure=False,
        )
        db.upsert_file(rec2)

        links = [
            LinkRecord(
                "matrix-notes", "linear-algebra", "../math/linear-algebra.md", 12
            )
        ]
        db.replace_document_links("matrix-notes", links)

        refs = db.get_referencing_links("linear-algebra")
        assert len(refs) == 1
        assert refs[0].source_stem == "matrix-notes"

        # Cascade test: Deleting source file cascades to its outgoing links
        db.delete_file_by_stem("matrix-notes")
        assert len(db.get_outgoing_links("matrix-notes")) == 0
        assert len(db.get_referencing_links("linear-algebra")) == 0

        print("  -> Link graph & cascading delete tests passed.")

    # Clean up test artifacts
    for f in test_db_path.parent.glob("test_vault_index.db*"):
        try:
            f.unlink()
        except OSError:
            pass

    print("[SUCCESS] All Phase 1 modules verified.")


if __name__ == "__main__":
    run_tests()
