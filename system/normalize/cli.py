# system/normalize/cli.py
"""
system/normalize/cli.py
"""

import argparse
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from system.normalize.db import FileRecord, VaultDB
from system.normalize.engine import ActionType, DiffPlan, compute_diff
from system.normalize.graph import (
    heal_markdown_links,
    parse_markdown_links,
    to_link_records,
)
from system.normalize.scanner import MARKDOWN_EXTENSIONS, scan_vault
from system.normalize.slugify import slugify_stem

# Terminal ANSI Color Constants
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"


class ContentBoundaryError(RuntimeError):
    """Raised when an operation attempts to target files outside content_root."""

    pass


def assert_within_content_root(target_path: Path, content_root: Path):
    """Enforces the strict boundary invariant: operations must stay inside content_root."""
    try:
        target_path.resolve().relative_to(content_root.resolve())
    except ValueError:
        raise ContentBoundaryError(
            f"Security Violation: Target path '{target_path}' lies outside vault root '{content_root}'."
        )


@dataclass
class TransactionManifest:
    """Discrete list of disk and ledger mutations staged for atomic execution."""

    disk_renames: List[Tuple[Path, Path]] = field(
        default_factory=list
    )  # (src_abs, dst_abs)
    text_rewrites: List[Tuple[Path, str]] = field(
        default_factory=list
    )  # (file_abs, new_content)
    files_to_upsert: List[FileRecord] = field(default_factory=list)
    files_to_delete: List[str] = field(default_factory=list)
    links_to_replace: Dict[str, list] = field(default_factory=dict)

    @property
    def has_changes(self) -> bool:
        return bool(
            self.disk_renames
            or self.text_rewrites
            or self.files_to_upsert
            or self.files_to_delete
            or self.links_to_replace
        )


def build_transaction_manifest(
    content_root: Path,
    diff_plan: DiffPlan,
    db: VaultDB,
) -> Tuple[TransactionManifest, List[str]]:
    """
    Translates a DiffPlan into an executable TransactionManifest.
    Plans all disk renames, path sanitizations, content link healing, and SQLite updates.
    """
    content_root = content_root.resolve()
    manifest = TransactionManifest()
    diagnostics: List[str] = []

    stem_to_new_rel_path: Dict[str, str] = {}

    for action in diff_plan.actions:
        if action.action_type in (
            ActionType.MOVE,
            ActionType.RENAME,
            ActionType.MOVE_AND_RENAME,
            ActionType.SANITIZE_STEM,
            ActionType.SANITIZE_PATH,
            ActionType.RESOLVE_COLLISION,
        ):
            if action.src_rel_path and action.dst_rel_path and action.old_stem:
                src_abs = (content_root / action.src_rel_path).resolve()
                dst_abs = (content_root / action.dst_rel_path).resolve()

                # Boundary invariant verification
                assert_within_content_root(src_abs, content_root)
                assert_within_content_root(dst_abs, content_root)

                manifest.disk_renames.append((src_abs, dst_abs))

                stem_to_new_rel_path[action.old_stem] = action.dst_rel_path
                stem_to_new_rel_path[slugify_stem(action.old_stem)] = (
                    action.dst_rel_path
                )
                if action.new_stem:
                    stem_to_new_rel_path[action.new_stem] = action.dst_rel_path
                    stem_to_new_rel_path[slugify_stem(action.new_stem)] = (
                        action.dst_rel_path
                    )

    # Evaluate all Markdown files on disk for link healing
    for item in content_root.rglob("*"):
        if (
            item.is_symlink()
            or not item.is_file()
            or item.suffix.lower() not in MARKDOWN_EXTENSIONS
        ):
            continue

        try:
            rel_path = item.relative_to(content_root).as_posix()
        except ValueError:
            continue

        try:
            content = item.read_text(encoding="utf-8")
        except OSError:
            continue

        healed_content, rewrites = heal_markdown_links(
            content=content,
            source_rel_path=rel_path,
            stem_to_new_rel_path=stem_to_new_rel_path,
        )

        if rewrites > 0 and healed_content != content:
            item_resolved = item.resolve()
            assert_within_content_root(item_resolved, content_root)
            manifest.text_rewrites.append((item_resolved, healed_content))

    return manifest, diagnostics


def prune_empty_directories(content_root: Path):
    """Recursively removes empty directory branches left behind after file renames, strictly within content_root."""
    content_root = content_root.resolve()
    for root, dirs, _ in os.walk(content_root, topdown=False):
        for d in dirs:
            dir_path = (Path(root) / d).resolve()
            if dir_path == content_root:
                continue
            try:
                assert_within_content_root(dir_path, content_root)
                if not any(dir_path.iterdir()):
                    dir_path.rmdir()
            except (OSError, ContentBoundaryError):
                pass


def execute_transaction(manifest: TransactionManifest, db: VaultDB) -> bool:
    """
    Applies the manifest atomically with rollback journaling.
    Phase 1: Stage text rewrites to .norm_tmp files.
    Phase 2: Apply renames in order, journaling executed steps.
    Phase 3: Atomically commit text rewrites via rename.
    """
    executed_renames: List[Tuple[Path, Path]] = []
    created_tmp_files: List[Path] = []

    try:
        # Phase 1: Stage text rewrites
        for abs_path, new_content in manifest.text_rewrites:
            tmp_path = abs_path.with_suffix(abs_path.suffix + ".norm_tmp")
            tmp_path.write_text(new_content, encoding="utf-8")
            created_tmp_files.append(tmp_path)

            # Phase 2: Execute disk renames
            for src, dst in manifest.disk_renames:
                if src == dst:
                    continue
                dst.parent.mkdir(parents=True, exist_ok=True)
                if src.parent == dst.parent and src.name.lower() == dst.name.lower():
                    case_tmp = (
                        dst.parent / f".norm_case_tmp_{os.urandom(4).hex()}_{dst.name}"
                    )
                    try:
                        src.rename(case_tmp)
                        case_tmp.rename(dst)
                    except Exception:
                        if case_tmp.exists() and not src.exists():
                            case_tmp.rename(src)
                        raise
                else:
                    src.rename(dst)
                executed_renames.append((dst, src))

        # Phase 3: Atomically swap text rewrites
        for abs_path, _ in manifest.text_rewrites:
            tmp_path = abs_path.with_suffix(abs_path.suffix + ".norm_tmp")
            tmp_path.replace(abs_path)
            if tmp_path in created_tmp_files:
                created_tmp_files.remove(tmp_path)

        return True

    except Exception as err:
        print(
            f"\n{RED}[FATAL] Error during execution: {err}. Initiating rollback...{RESET}",
            file=sys.stderr,
        )

        for tmp_file in created_tmp_files:
            try:
                if tmp_file.exists():
                    tmp_file.unlink()
            except OSError:
                pass

        for applied_dst, original_src in reversed(executed_renames):
            try:
                if applied_dst.exists():
                    original_src.parent.mkdir(parents=True, exist_ok=True)
                    if (
                        applied_dst.parent == original_src.parent
                        and applied_dst.name.lower() == original_src.name.lower()
                    ):
                        case_tmp = (
                            original_src.parent
                            / f".norm_rb_tmp_{os.urandom(4).hex()}_{original_src.name}"
                        )
                        applied_dst.rename(case_tmp)
                        case_tmp.rename(original_src)
                    else:
                        applied_dst.rename(original_src)
            except OSError as rb_err:
                print(
                    f"{RED}[CRITICAL] Failed to rollback {applied_dst} -> {original_src}: {rb_err}{RESET}",
                    file=sys.stderr,
                )

        print(
            f"{YELLOW}[ROLLBACK COMPLETE] Vault state restored.{RESET}", file=sys.stderr
        )
        raise


def sync_db_with_disk(content_root: Path, db: VaultDB):
    """Refreshes the SQLite ledger to match physical disk state after execution."""
    scan_res = scan_vault(content_root, db)
    current_paths = {f.rel_path for f in scan_res.files}
    current_canonicals = {f.canonical_filename for f in scan_res.files}

    for rel_path, rec in db.get_all_files().items():
        if rel_path not in current_paths:
            db.delete_file_by_path(rel_path)

    for f in scan_res.files:
        db.upsert_file(
            FileRecord(
                id=None,
                canonical_filename=f.canonical_filename,
                stem=f.stem,
                ext=f.ext,
                rel_path=f.rel_path,
                sha256=f.sha256,
                mtime=f.mtime,
                size=f.size,
                is_media=f.is_media,
                is_secure=f.is_secure,
            )
        )
        if not f.is_media and f.ext in MARKDOWN_EXTENSIONS:
            try:
                content = f.abs_path.read_text(encoding="utf-8")
                extracted = parse_markdown_links(content, f.canonical_filename)
                valid_links = [
                    l for l in extracted if l.target_canonical in current_canonicals
                ]
                db.replace_document_links(
                    f.canonical_filename, to_link_records(valid_links)
                )
            except OSError:
                pass


def audit_security_boundaries(
    scan_result: VaultScanResult,
) -> List[Tuple[str, str, int, str]]:
    """
    Validates media isolation boundaries between secure and public contexts.
    Cross-context document hyperlinks (Markdown -> Markdown) are permitted.
    Cross-context media embeds (e.g. secure note embedding public image or vice-versa)
    are flagged as fatal violations due to encryption runtime constraints.
    """
    violations = []
    canonical_map = {f.canonical_filename: f for f in scan_result.files}
    stem_map = {f.stem: f for f in scan_result.files if not f.is_media}

    for f in scan_result.files:
        if f.is_media or f.ext not in MARKDOWN_EXTENSIONS:
            continue
        try:
            content = f.abs_path.read_text(encoding="utf-8")
            links = parse_markdown_links(content, f.canonical_filename)
            for link in links:
                target_file = canonical_map.get(link.target_canonical)
                if not target_file:
                    target_file = stem_map.get(link.target_stem)

                if not target_file:
                    continue

                # Document-to-document navigation across boundaries is permitted.
                # Only enforce boundary separation on media asset embeds.
                if (
                    link.is_image or target_file.is_media
                ) and target_file.is_secure != f.is_secure:
                    s_ctx = "SECURE" if f.is_secure else "PUBLIC"
                    t_ctx = "SECURE" if target_file.is_secure else "PUBLIC"
                    violations.append(
                        (
                            f.rel_path,
                            target_file.rel_path,
                            link.line_number,
                            f"{s_ctx} document embeds {t_ctx} media asset",
                        )
                    )
        except OSError:
            pass

    return violations


def print_diff_report(
    diff_plan: DiffPlan,
    manifest: TransactionManifest,
    scan_time_ms: float,
    boundary_violations: List[Tuple[str, str, int, str]],
):
    """Outputs an ANSI-colorized summary table of planned mutations."""
    print(f"\n{BOLD}{CYAN}=== Kykloi Content Normalization Plan ==={RESET}")
    print(f"{DIM}Scan duration: {scan_time_ms:.2f} ms{RESET}\n")

    if boundary_violations:
        print(f"{BOLD}{RED}CRITICAL SECURITY BOUNDARY VIOLATIONS:{RESET}")
        for src, tgt, line, reason in boundary_violations:
            print(f"  {RED}[!] {src}:{line} -> {tgt} ({reason}){RESET}")
        print(
            f"\n  {YELLOW}Resolve security context mismatches by moving/duplicating assets.{RESET}\n"
        )

    if diff_plan.collisions:
        print(f"{BOLD}{RED}CRITICAL ANOMALIES (Filename Collisions Detected):{RESET}")
        for fname, paths in diff_plan.collisions.items():
            print(f"  {RED}Filename collision on '{fname}':{RESET}")
            for p in paths:
                print(f"    - {p}")
        print()

    mutations = [a for a in diff_plan.actions if a.action_type != ActionType.NOOP]

    if not mutations and not manifest.text_rewrites:
        print(f"{GREEN}[+] Vault is fully canonical. Zero mutations required.{RESET}\n")
        return

    print(f"{BOLD}{'Action':<18} {'Details':<60}{RESET}")
    print(f"{DIM}{'-' * 78}{RESET}")

    for a in mutations:
        color = YELLOW
        if a.action_type in (ActionType.SANITIZE_STEM, ActionType.SANITIZE_PATH):
            color = MAGENTA
        elif a.action_type == ActionType.CREATE:
            color = GREEN
        elif a.action_type == ActionType.DELETE:
            color = RED

        label = f"{color}{a.action_type.name:<18}{RESET}"
        if a.src_rel_path and a.dst_rel_path:
            details = f"{a.src_rel_path} -> {a.dst_rel_path}"
        elif a.dst_rel_path:
            details = a.dst_rel_path
        else:
            details = a.src_rel_path or ""
        print(f"{label} {details}")

    if manifest.text_rewrites:
        for p, _ in manifest.text_rewrites:
            label = f"{CYAN}{'HEAL_LINKS':<18}{RESET}"
            print(f"{label} Rewriting relative link targets in {p.name}")

    print(f"{DIM}{'-' * 78}{RESET}")
    print(
        f"Summary: {BOLD}{len(manifest.disk_renames)}{RESET} file rename(s), "
        f"{BOLD}{len(manifest.text_rewrites)}{RESET} document(s) with healed links.\n"
    )


def run_normalization_pipeline(
    content_root: Path,
    db_path: Path,
    dry_run: bool = False,
    auto_apply: bool = False,
    check_only: bool = False,
) -> int:
    """
    Programmatic entry point for running normalization.
    Returns:
      0 on success (or clean in check mode),
      1 on pending mutations (in check mode) or collision / error.
    """
    content_root = content_root.resolve()
    db_path = db_path.resolve()

    if not content_root.exists() or not content_root.is_dir():
        print(
            f"{RED}[FATAL] Content directory not found: {content_root}{RESET}",
            file=sys.stderr,
        )
        return 1

    t0 = time.perf_counter()
    with VaultDB(db_path) as db:
        db.init_schema()

        scan_result = scan_vault(content_root, db)
        boundary_violations = audit_security_boundaries(scan_result)
        diff_plan = compute_diff(scan_result, db)
        manifest, _ = build_transaction_manifest(content_root, diff_plan, db)
        scan_time_ms = (time.perf_counter() - t0) * 1000.0

        print_diff_report(diff_plan, manifest, scan_time_ms, boundary_violations)

        if boundary_violations:
            print(
                f"{RED}[FATAL] Execution halted: {len(boundary_violations)} security boundary violation(s) must be manually resolved.{RESET}\n",
                file=sys.stderr,
            )
            return 1

        has_work = manifest.has_changes or diff_plan.has_mutations

        if check_only:
            return 1 if (has_work or diff_plan.collisions) else 0

        if dry_run or not has_work:
            return 0

        if not auto_apply:
            if not sys.stdin.isatty():
                print(
                    f"{RED}[ERROR] Non-interactive environment. Re-run with --check or --auto-apply.{RESET}",
                    file=sys.stderr,
                )
                return 1

            try:
                answer = (
                    input(
                        f"{BOLD}Apply these transformations to disk and database? [y/N]: {RESET}"
                    )
                    .strip()
                    .lower()
                )
            except (KeyboardInterrupt, EOFError):
                print(f"\n{YELLOW}Aborted by user.{RESET}")
                return 1

            if answer not in ("y", "yes"):
                print(
                    f"{YELLOW}Operation cancelled. Zero modifications written.{RESET}"
                )
                return 0

        execute_transaction(manifest, db)
        prune_empty_directories(content_root)
        sync_db_with_disk(content_root, db)
        print(
            f"{GREEN}[SUCCESS] Transformations applied and ledger synchronized successfully.{RESET}"
        )
        return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deterministic Content Normalizer & Link Reconciler for Project Kykloi."
    )
    parser.add_argument(
        "--vault-dir",
        type=Path,
        default=PROJECT_ROOT / "content",
        help="Path to content vault directory (default: content/)",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=SCRIPT_DIR / "vault-index.db",
        help="Path to SQLite acceleration ledger (default: system/normalize/vault-index.db)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Lint mode: Exits with code 0 if vault is clean, 1 if mutations are planned.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate scan and report planned transformations without writing to disk.",
    )
    parser.add_argument(
        "--auto-apply",
        action="store_true",
        help="Apply planned transformations automatically without prompting.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    code = run_normalization_pipeline(
        content_root=args.vault_dir,
        db_path=args.db_path,
        dry_run=args.dry_run,
        auto_apply=args.auto_apply,
        check_only=args.check,
    )
    sys.exit(code)


if __name__ == "__main__":
    main()
