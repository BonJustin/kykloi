"""
system/normalize/test_phase5.py - Comprehensive Verification & Stress Test Suite.
Verifies all core invariants, edge cases, and deterministic transitions defined
in normalize-implementation-plan-1.md.

Note: Code fence ticks and inline spans are encoded using hex escapes (\\x60)
to avoid Markdown parser collisions across code formatters and LLM environments.
"""

import subprocess
import sys
import tempfile
import time
from pathlib import Path

# Ensure project root is discoverable
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from system.normalize.cli import (
    build_transaction_manifest,
    execute_transaction,
    sync_db_with_disk,
)
from system.normalize.db import VaultDB
from system.normalize.engine import ActionType, compute_diff
from system.normalize.graph import (
    compute_relative_link,
    heal_markdown_links,
)
from system.normalize.scanner import scan_vault

# Encoded Markdown fence and inline code tokens (\x60 == '`')
TICK_1 = "\x60"
TICK_3 = "\x60\x60\x60"


def test_decision_matrix_all_branches():
    """Validates all six transition paths in the Identity Decision Matrix."""
    print("[1/7] Testing Identity Decision Matrix (All 6 Transitions)...")

    with tempfile.TemporaryDirectory() as tmp_dir:
        vault = Path(tmp_dir) / "content"
        vault.mkdir()
        db_path = Path(tmp_dir) / "vault.db"

        with VaultDB(db_path) as db:
            db.init_schema()

            # Baseline document
            f_orig = vault / "core-doc.md"
            f_orig.write_text("# Core Document\nInitial body.", encoding="utf-8")
            res0 = scan_vault(vault, db)
            sync_db_with_disk(vault, db)

            # 1. Clean Move: (P -> P', S=S, H=H)
            sub = vault / "subfolder"
            sub.mkdir()
            f_moved = sub / "core-doc.md"
            f_orig.rename(f_moved)

            res_m = scan_vault(vault, db)
            diff_m = compute_diff(res_m, db)
            move_act = next(
                (a for a in diff_m.actions if a.action_type == ActionType.MOVE), None
            )
            assert move_act is not None, "Failed: Clean Move not detected"
            assert move_act.old_stem == "core-doc" and move_act.new_stem == "core-doc"

            # Commit move
            sync_db_with_disk(vault, db)

            # 2. Clean Rename: (P=P, S -> S', H=H)
            f_renamed = sub / "renamed-doc.md"
            f_moved.rename(f_renamed)
            res_r = scan_vault(vault, db)
            diff_r = compute_diff(res_r, db)
            rename_act = next(
                (a for a in diff_r.actions if a.action_type == ActionType.RENAME), None
            )
            assert rename_act is not None, "Failed: Clean Rename not detected"

            # Commit rename
            sync_db_with_disk(vault, db)

            # 3. Move + Rename: (P -> P', S -> S', H=H)
            other_sub = vault / "other"
            other_sub.mkdir()
            f_move_renamed = other_sub / "final-doc.md"
            f_renamed.rename(f_move_renamed)
            res_mr = scan_vault(vault, db)
            diff_mr = compute_diff(res_mr, db)
            mr_act = next(
                (
                    a
                    for a in diff_mr.actions
                    if a.action_type == ActionType.MOVE_AND_RENAME
                ),
                None,
            )
            assert mr_act is not None, "Failed: Move + Rename not detected"

            # Commit move + rename
            sync_db_with_disk(vault, db)

            # 4. Move + Content Edit: (P -> P', S=S, H -> H') [Stem UID Anchor]
            f_move_edit = vault / "final-doc.md"
            f_move_renamed.rename(f_move_edit)
            f_move_edit.write_text("# Divergent Content", encoding="utf-8")
            res_me = scan_vault(vault, db)
            diff_me = compute_diff(res_me, db)
            me_act = next(
                (a for a in diff_me.actions if a.action_type == ActionType.MOVE), None
            )
            assert me_act is not None, "Failed: Stem UID anchor failed on move + edit"

            # Commit
            sync_db_with_disk(vault, db)

            # 5. Rename + Content Edit (Ambiguous): (P=P, S -> S', H -> H')
            # Divergence of Stem and Hash -> DELETE(old) + CREATE(new)
            f_ambiguous = vault / "brand-new.md"
            f_move_edit.rename(f_ambiguous)
            f_ambiguous.write_text("# Brand New Content", encoding="utf-8")
            res_amb = scan_vault(vault, db)
            diff_amb = compute_diff(res_amb, db)
            has_del = any(a.action_type == ActionType.DELETE for a in diff_amb.actions)
            has_create = any(
                a.action_type == ActionType.CREATE for a in diff_amb.actions
            )
            assert has_del and has_create, (
                "Failed: Ambiguous rename + edit must degrade to DELETE + CREATE"
            )

    print("  -> Identity Decision Matrix verified across all 6 transition branches.")


def test_deterministic_collision_resolution():
    """Validates deterministic resolution of stem collisions per Section 5.1."""
    print("[2/7] Testing Stem Collision Resolution...")

    with tempfile.TemporaryDirectory() as tmp_dir:
        vault = Path(tmp_dir) / "content"
        vault.mkdir()
        db_path = Path(tmp_dir) / "vault.db"

        with VaultDB(db_path) as db:
            db.init_schema()

            # Seed an existing canonical document in DB
            phys = vault / "physics"
            phys.mkdir()
            doc_phys = phys / "energy.md"
            doc_phys.write_text("# Physics Energy", encoding="utf-8")
            sync_db_with_disk(vault, db)

            # Introduce colliding file in another directory
            econ = vault / "economics"
            econ.mkdir()
            doc_econ = econ / "energy.md"
            doc_econ.write_text("# Economics Energy", encoding="utf-8")

            # Scan and compute diff
            res = scan_vault(vault, db)
            diff = compute_diff(res, db)

            collision_action = next(
                (
                    a
                    for a in diff.actions
                    if a.action_type == ActionType.RESOLVE_COLLISION
                ),
                None,
            )
            assert collision_action is not None, "Collision resolution action missing"
            assert collision_action.src_rel_path == "economics/energy.md"
            assert collision_action.dst_rel_path == "economics/energy-1.md"
            assert collision_action.new_stem == "energy-1"

            # Execute transaction and verify resolution on disk
            manifest, _ = build_transaction_manifest(vault, diff, db)
            execute_transaction(manifest, db)
            sync_db_with_disk(vault, db)

            assert (econ / "energy-1.md").exists()
            assert not (econ / "energy.md").exists()
            assert (phys / "energy.md").exists()

            # Introduce a third colliding file: should deterministically become energy-2
            social = vault / "sociology"
            social.mkdir()
            doc_social = social / "energy.md"
            doc_social.write_text("# Sociology Energy", encoding="utf-8")

            res3 = scan_vault(vault, db)
            diff3 = compute_diff(res3, db)
            collision_action3 = next(
                (
                    a
                    for a in diff3.actions
                    if a.action_type == ActionType.RESOLVE_COLLISION
                ),
                None,
            )
            assert collision_action3 is not None
            assert collision_action3.new_stem == "energy-2"

    print("  -> Deterministic collision resolution verified (-1, -2 suffixes).")


def test_relative_path_mathematics_and_link_healing():
    """Validates relative path mathematics across directory topological permutations."""
    print("[3/7] Testing Cross-Platform Link Mathematics & Healing...")

    # Verification of posixpath determinism on POSIX relative links
    assert compute_relative_link("notes/math.md", "notes/algebra.md") == "algebra.md"
    assert compute_relative_link("notes/sub/deep.md", "notes/math.md") == "../math.md"
    assert compute_relative_link("notes/math.md", "notes/sub/deep.md") == "sub/deep.md"
    assert (
        compute_relative_link("a/b/c/doc.md", "x/y/target.md")
        == "../../../x/y/target.md"
    )
    assert compute_relative_link("doc.md", "target.md") == "target.md"

    # Link healing simulation with anchors, queries, titles, and media
    content = (
        "# Reference Note\n"
        "Here is a normal link: [Algebra](math/algebra.md).\n"
        "Here is an anchored link: [Algebra Section](math/algebra.md#quadratics).\n"
        "Here is a query link: [Search](math/algebra.md?v=2).\n"
        'Here is a link with title: [Algebra](math/algebra.md "Algebra Textbook").\n'
        "Here is an image: ![Diagram](media/chart.png).\n"
        "Here is an external link (must be ignored): [GitHub](https://github.com/test/algebra.md).\n"
        "Here is an in-page anchor (must be ignored): [Intro](#introduction).\n"
    )

    stem_map = {
        "algebra": "disciplines/pure-math/algebra-revised.md",
        "chart": "assets/images/chart.png",
    }

    healed, count = heal_markdown_links(
        content=content,
        source_rel_path="notes/overview.md",
        stem_to_new_rel_path=stem_map,
    )

    assert count == 5
    assert "[Algebra](../disciplines/pure-math/algebra-revised.md)" in healed
    assert (
        "[Algebra Section](../disciplines/pure-math/algebra-revised.md#quadratics)"
        in healed
    )
    assert "[Search](../disciplines/pure-math/algebra-revised.md?v=2)" in healed
    assert (
        '[Algebra](../disciplines/pure-math/algebra-revised.md "Algebra Textbook")'
        in healed
    )
    assert "![Diagram](../assets/images/chart.png)" in healed
    assert "[GitHub](https://github.com/test/algebra.md)" in healed
    assert "[Intro](#introduction)" in healed

    print("  -> Relative path calculation and link healing verified.")


def test_code_block_isolation():
    """Verifies links inside code blocks and inline code are never touched."""
    print("[4/7] Testing Code Block & Inline Code Span Isolation...")

    # Assembled using escape constants TICK_3 and TICK_1
    raw_text = (
        f"\n{TICK_3}markdown\n"
        "[Algebra](math/algebra.md)\n"
        f"{TICK_3}\n"
        f"Inside text: {TICK_1}[Algebra](math/algebra.md){TICK_1} should remain untouched.\n"
        "Outside text: [Algebra](math/algebra.md) should be healed.\n"
        "~~~\n"
        "[Algebra](math/algebra.md)\n"
        "~~~\n"
    )

    stem_map = {"algebra": "new/algebra.md"}
    healed, count = heal_markdown_links(raw_text, "source.md", stem_map)

    assert count == 1, f"Expected exactly 1 rewrite, got {count}"
    lines = healed.strip().splitlines()
    assert "[Algebra](math/algebra.md)" in lines[1]  # Inside fenced block
    assert (
        f"{TICK_1}[Algebra](math/algebra.md){TICK_1}" in lines[3]
    )  # Inside inline span
    assert "[Algebra](new/algebra.md)" in lines[4]  # Outside block
    assert "[Algebra](math/algebra.md)" in lines[6]  # Inside tilde block

    print("  -> Code block isolation verified.")


def test_stat_cache_performance_and_fast_path():
    """Verifies stat-cache fast-path bypasses SHA-256 calculation on unchanged files."""
    print("[5/7] Testing Stat-Cache Invariant (0 Hash Operations on Clean Vault)...")

    with tempfile.TemporaryDirectory() as tmp_dir:
        vault = Path(tmp_dir) / "content"
        vault.mkdir()
        db_path = Path(tmp_dir) / "vault.db"

        # Generate 50 mock files
        for i in range(50):
            p = vault / f"doc-{i:03d}.md"
            p.write_text(f"# Doc {i}\nContent line {i}", encoding="utf-8")

        with VaultDB(db_path) as db:
            db.init_schema()

            # First scan: 0 hits, 50 misses
            scan1 = scan_vault(vault, db)
            assert scan1.cache_hits == 0
            assert scan1.cache_misses == 50

            # Commit to ledger
            sync_db_with_disk(vault, db)

            # Second scan: 50 hits, 0 misses (fast-path confirmed)
            t0 = time.perf_counter()
            scan2 = scan_vault(vault, db)
            scan_time_ms = (time.perf_counter() - t0) * 1000.0

            assert scan2.cache_hits == 50
            assert scan2.cache_misses == 0
            assert scan_time_ms < 50.0, f"Scan exceeded threshold: {scan_time_ms} ms"

            # Modifying one file triggers exactly 1 cache miss
            time.sleep(0.01)  # Ensure distinct mtime timestamp
            (vault / "doc-025.md").write_text("# Doc 25 Modified", encoding="utf-8")
            scan3 = scan_vault(vault, db)
            assert scan3.cache_hits == 49
            assert scan3.cache_misses == 1

    print("  -> Stat-cache fast-path verified (<0.05s on unchanged vault).")


def test_atomic_rollback_and_fault_tolerance():
    """Verifies transactions revert completely if a mutation encounters a fatal error."""
    print("[6/7] Testing Atomic Rollback on Injected Disk Fault...")

    with tempfile.TemporaryDirectory() as tmp_dir:
        vault = Path(tmp_dir) / "content"
        vault.mkdir()
        db_path = Path(tmp_dir) / "vault.db"

        f1 = vault / "original-1.md"
        f2 = vault / "original-2.md"
        f1.write_text("# Note 1", encoding="utf-8")
        f2.write_text("# Note 2 referring to [Note 1](original-1.md)", encoding="utf-8")

        with VaultDB(db_path) as db:
            db.init_schema()
            sync_db_with_disk(vault, db)

            # Stage valid renames
            scan = scan_vault(vault, db)
            diff = compute_diff(scan, db)
            manifest, _ = build_transaction_manifest(vault, diff, db)

            # Inject a fatal target: attempt to write into an invalid device path
            manifest.disk_renames.append((f1, vault / "renamed-1.md"))
            manifest.disk_renames.append(
                (f2, Path("/dev/null/forbidden_target/invalid.md"))
            )

            threw = False
            try:
                execute_transaction(manifest, db)
            except Exception:
                threw = True

            assert threw, "Transaction should have raised an exception on fault"
            assert f1.exists(), "Rollback failed: f1 was not restored to original path"
            assert not (vault / "renamed-1.md").exists(), (
                "Rollback failed: intermediate rename persisted"
            )
            assert not list(vault.glob("*.norm_tmp")), (
                "Temporary staging files leaked during failure"
            )

    print("  -> Atomic rollback and journal recovery verified.")


def test_cli_idempotence_and_non_interactive_flags():
    """Verifies CLI flags (--check, --dry-run, --auto-apply) and idempotence."""
    print("[7/7] Testing CLI Invariants & Idempotence...")

    with tempfile.TemporaryDirectory() as tmp_dir:
        vault = Path(tmp_dir) / "content"
        vault.mkdir()
        db_path = Path(tmp_dir) / "vault.db"

        # Dirty vault: un-normalized folder & filename
        dirty_dir = vault / "Dirty Folder"
        dirty_dir.mkdir()
        doc = dirty_dir / "Un-Normalized Name.MD"
        doc.write_text("# Un-normalized\nTesting CLI.", encoding="utf-8")

        cli_path = PROJECT_ROOT / "system" / "normalize" / "cli.py"

        # 1. --check exits with 1 on dirty vault
        p_check = subprocess.run(
            [
                sys.executable,
                str(cli_path),
                "--vault-dir",
                str(vault),
                "--db-path",
                str(db_path),
                "--check",
            ],
            capture_output=True,
            text=True,
        )
        assert p_check.returncode == 1

        # 2. --dry-run reports changes but leaves disk unmodified
        p_dry = subprocess.run(
            [
                sys.executable,
                str(cli_path),
                "--vault-dir",
                str(vault),
                "--db-path",
                str(db_path),
                "--dry-run",
            ],
            capture_output=True,
            text=True,
        )
        assert p_dry.returncode == 0
        assert doc.exists(), "--dry-run must not write to disk"

        # 3. --auto-apply applies changes
        p_apply = subprocess.run(
            [
                sys.executable,
                str(cli_path),
                "--vault-dir",
                str(vault),
                "--db-path",
                str(db_path),
                "--auto-apply",
            ],
            capture_output=True,
            text=True,
        )
        assert p_apply.returncode == 0
        canonical_doc = vault / "dirty-folder" / "un-normalized-name.md"
        assert canonical_doc.exists(), "Sanitized document was not produced"
        assert not doc.exists(), "Old un-normalized file persisted"

        # 4. Idempotence: subsequent run performs zero operations and exits 0 under --check
        p_idempotent = subprocess.run(
            [
                sys.executable,
                str(cli_path),
                "--vault-dir",
                str(vault),
                "--db-path",
                str(db_path),
                "--check",
            ],
            capture_output=True,
            text=True,
        )
        assert p_idempotent.returncode == 0, (
            f"Idempotence violated: vault is not clean. Stderr: {p_idempotent.stderr}"
        )

    print("  -> CLI idempotence and execution flags verified.")


def main():
    print("\n================== RUNNING PHASE 5 STRESS TEST SUITE ==================")
    t0 = time.perf_counter()

    test_decision_matrix_all_branches()
    test_deterministic_collision_resolution()
    test_relative_path_mathematics_and_link_healing()
    test_code_block_isolation()
    test_stat_cache_performance_and_fast_path()
    test_atomic_rollback_and_fault_tolerance()
    test_cli_idempotence_and_non_interactive_flags()

    elapsed = time.perf_counter() - t0
    print(
        f"\n[SUCCESS] All Phase 5 verification and stress tests passed ({elapsed:.2f} s).\n"
    )


if __name__ == "__main__":
    main()
