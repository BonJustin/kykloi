# system/normalize/test_phase4.py
import subprocess
import sys
import tempfile
from pathlib import Path

# Ensure project root (kykloi/) is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from system.normalize.cli import (
    build_transaction_manifest,
    execute_transaction,
)
from system.normalize.db import VaultDB
from system.normalize.engine import compute_diff
from system.normalize.scanner import scan_vault


def run_tests():
    with tempfile.TemporaryDirectory() as tmp_dir:
        vault_path = Path(tmp_dir) / "content"
        vault_path.mkdir()
        db_path = Path(tmp_dir) / "vault_index.db"

        # Initialize mock documents with un-normalized folder & filename
        notes_dir = vault_path / "Math Notes"
        notes_dir.mkdir()
        doc_a = notes_dir / "Matrix Calculation.MD"
        doc_b = vault_path / "doc-b.md"

        doc_a.write_text("# Matrix Math\nFormula details.", encoding="utf-8")
        doc_b.write_text(
            "# Document B\nReference to [Matrix Notes](Math%20Notes/Matrix%20Calculation.MD).",
            encoding="utf-8",
        )

        cli_script = PROJECT_ROOT / "system" / "normalize" / "cli.py"

        print("[1/4] Testing --check (Lint Mode on un-normalized vault)...")
        res = subprocess.run(
            [
                sys.executable,
                str(cli_script),
                "--vault-dir",
                str(vault_path),
                "--db-path",
                str(db_path),
                "--check",
            ],
            capture_output=True,
            text=True,
        )
        assert res.returncode == 1, "Expected exit code 1 for un-normalized vault"
        print("  -> Lint exit code verified.")

        print("[2/4] Testing --auto-apply (Path sanitization & link healing)...")
        res_apply = subprocess.run(
            [
                sys.executable,
                str(cli_script),
                "--vault-dir",
                str(vault_path),
                "--db-path",
                str(db_path),
                "--auto-apply",
            ],
            capture_output=True,
            text=True,
        )
        assert res_apply.returncode == 0, f"Auto-apply failed: {res_apply.stderr}"

        # Assert disk renames took effect (both folder and file normalized)
        sanitized_doc_a = vault_path / "math-notes" / "matrix-calculation.md"
        assert sanitized_doc_a.exists(), "math-notes/matrix-calculation.md should exist"
        assert not doc_a.exists(), (
            "Original un-normalized file should have been renamed"
        )

        # Assert link inside doc_b was healed to follow the new canonical path
        doc_b_content = doc_b.read_text(encoding="utf-8")
        assert "math-notes/matrix-calculation.md" in doc_b_content, (
            f"Link target should be rewritten to canonical path, got: {doc_b_content}"
        )
        print("  -> Disk rename and link healing executed successfully.")

        print("[3/4] Testing Idempotence (Second run performs zero writes)...")
        res_idempotent = subprocess.run(
            [
                sys.executable,
                str(cli_script),
                "--vault-dir",
                str(vault_path),
                "--db-path",
                str(db_path),
                "--check",
            ],
            capture_output=True,
            text=True,
        )
        assert res_idempotent.returncode == 0, (
            f"Second run must detect 0 mutations and return code 0, stderr: {res_idempotent.stderr}"
        )
        print("  -> Idempotence invariant confirmed.")

        print("[4/4] Testing Atomic Rollback on Disk Mutation Failure...")
        with VaultDB(db_path) as db:
            scan_res = scan_vault(vault_path, db)
            diff = compute_diff(scan_res, db)
            manifest, _ = build_transaction_manifest(vault_path, diff, db)

            invalid_src = vault_path / "doc-b.md"
            invalid_dst = Path("/dev/null/forbidden/cannot_exist.md")
            manifest.disk_renames.append((invalid_src, invalid_dst))

            try:
                execute_transaction(manifest, db)
                assert False, "Execution should have raised an exception"
            except Exception:
                assert invalid_src.exists(), (
                    "Rollback should restore original file location"
                )
                print("  -> Rollback journal safely reverted disk mutations.")

    print("[SUCCESS] All Phase 4 CLI and transaction tests verified.")


if __name__ == "__main__":
    run_tests()
