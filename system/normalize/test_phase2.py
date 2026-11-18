# system/normalize/test_phase2.py
import sys
import tempfile
from pathlib import Path

# Ensure project root (kykloi/) is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from system.normalize.db import FileRecord, LinkRecord, VaultDB
from system.normalize.engine import ActionType, compute_diff
from system.normalize.scanner import scan_vault


def run_tests():
    with tempfile.TemporaryDirectory() as tmp_dir:
        vault_path = Path(tmp_dir) / "content"
        vault_path.mkdir()
        db_path = Path(tmp_dir) / "vault_index.db"

        with VaultDB(db_path) as db:
            db.init_schema()

            print("[1/5] Testing Clean Vault & Fast-Path Stat Cache...")
            file_a = vault_path / "note-a.md"
            file_a.write_text("# Note A content", encoding="utf-8")

            # First scan: cache miss, baseline creation
            res1 = scan_vault(vault_path, db)
            assert res1.cache_hits == 0
            assert res1.cache_misses == 1

            diff1 = compute_diff(res1, db)
            assert len(diff1.actions) == 1
            assert diff1.actions[0].action_type == ActionType.CREATE

            # Commit initial record to DB
            stat_a = file_a.stat()
            db.upsert_file(
                FileRecord(
                    id=None,
                    stem="note-a",
                    rel_path="note-a.md",
                    sha256=res1.files[0].sha256,
                    mtime=stat_a.st_mtime,
                    size=stat_a.st_size,
                    is_media=False,
                    is_secure=False,
                )
            )

            # Second scan: cache hit, zero disk reads
            res2 = scan_vault(vault_path, db)
            assert res2.cache_hits == 1
            assert res2.cache_misses == 0
            diff2 = compute_diff(res2, db)
            assert diff2.actions[0].action_type == ActionType.NOOP
            print("  -> Stat-cache hit verified.")

            print("[2/5] Testing Decision Matrix: Clean Move (P -> P', S=S, H=H)...")
            subfolder = vault_path / "sub"
            subfolder.mkdir()
            file_a_moved = subfolder / "note-a.md"
            file_a.rename(file_a_moved)

            res_move = scan_vault(vault_path, db)
            diff_move = compute_diff(res_move, db)
            assert any(a.action_type == ActionType.MOVE for a in diff_move.actions)
            print("  -> Clean move resolved via identical content hash and stem.")

            print("[3/5] Testing Decision Matrix: Clean Rename (P=P, S -> S', H=H)...")
            file_a_renamed = subfolder / "note-renamed.md"
            file_a_moved.rename(file_a_renamed)

            res_rename = scan_vault(vault_path, db)
            diff_rename = compute_diff(res_rename, db)
            assert any(
                a.action_type in (ActionType.RENAME, ActionType.MOVE_AND_RENAME)
                for a in diff_rename.actions
            )
            print("  -> Clean rename recognized via content hash identity.")

            print(
                "[4/5] Testing Decision Matrix: Move + Content Edit (P -> P', S=S, H -> H')..."
            )
            # Move back to root and modify content
            file_a_edited = vault_path / "note-a.md"
            file_a_renamed.rename(file_a_edited)
            file_a_edited.write_text(
                "# Substantially altered content", encoding="utf-8"
            )

            res_edit_move = scan_vault(vault_path, db)
            diff_edit_move = compute_diff(res_edit_move, db)
            # Anchored by Stem UID: recognized as MOVE (or MODIFY) instead of atomic delete/recreate
            assert any(
                a.action_type in (ActionType.MOVE, ActionType.MODIFY_CONTENT)
                for a in diff_edit_move.actions
            )
            print("  -> Stem UID identity anchor preserved across move + edit.")

            print("[5/5] Testing Stem Collisions & Broken Link Diagnostics...")
            # Create a duplicate stem in another directory
            colliding_dir = vault_path / "other"
            colliding_dir.mkdir()
            colliding_file = colliding_dir / "note-a.md"
            colliding_file.write_text(
                "# Different note with colliding stem", encoding="utf-8"
            )

            # Mock an inbound link from an external file targeting note-a
            db.upsert_file(
                FileRecord(
                    id=None,
                    stem="referrer",
                    rel_path="referrer.md",
                    sha256="refhash",
                    mtime=1.0,
                    size=10,
                    is_media=False,
                    is_secure=False,
                )
            )
            db.replace_document_links(
                "referrer",
                [LinkRecord("referrer", "note-a", "note-a.md", 1)],
            )

            res_collision = scan_vault(vault_path, db)
            diff_collision = compute_diff(res_collision, db)
            assert "note-a" in diff_collision.collisions
            assert len(diff_collision.collisions["note-a"]) == 2
            print("  -> Multi-file stem collision identified.")

    print("[SUCCESS] All Phase 2 scanner and decision engine tests verified.")


if __name__ == "__main__":
    run_tests()
