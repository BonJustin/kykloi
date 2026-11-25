"""
system/normalize/cli.py - Filename Normalizer, Ledger Sync, and Vault Diagnostics.
Strict Zero-Mutation Archival Standard: Never alters the text inside user Markdown files.
"""

import argparse
import datetime
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from system.normalize.db import DocMetadataRecord, FileRecord, VaultDB
from system.normalize.engine import ActionType, DiffPlan, compute_diff
from system.normalize.graph import (
    BrokenLinkDiagnostic,
    LinkHealingPlan,
    LinkPatch,
    parse_markdown_links,
    plan_link_healing,
    to_link_records,
)
from system.normalize.scanner import (
    MARKDOWN_EXTENSIONS,
    VaultScanResult,
    scan_vault,
)
from system.normalize.slugify import slugify_stem

CITATION_PATTERN = re.compile(
    r"(?:\[@[a-zA-Z0-9_:.#$%&-]+|(?<!\w)@[a-zA-Z0-9_:.#$%&-]+)"
)

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


def assert_within_content_root(target_path: Path, content_root: Path):
    """Enforces boundary invariant: operations must stay strictly inside content_root."""
    try:
        target_path.resolve().relative_to(content_root.resolve())
    except ValueError:
        raise ContentBoundaryError(
            f"Security Violation: Target path '{target_path}' lies outside vault root '{content_root}'."
        )


@dataclass
class NormalizationPlan:
    """Discrete list of physical disk renames staged for user review."""

    disk_renames: list[tuple[Path, Path, str]] = field(
        default_factory=list
    )  # (src_abs, dst_abs, reason)

    @property
    def has_changes(self) -> bool:
        return bool(self.disk_renames)


def build_normalization_plan(
    content_root: Path, diff_plan: DiffPlan
) -> NormalizationPlan:
    """Collects physical disk renames needed to normalize invalid file stems or paths."""
    content_root = content_root.resolve()
    plan = NormalizationPlan()

    for action in diff_plan.actions:
        if action.action_type in (
            ActionType.SANITIZE_STEM,
            ActionType.SANITIZE_PATH,
            ActionType.RESOLVE_COLLISION,
        ):
            if (
                action.src_rel_path
                and action.dst_rel_path
                and action.src_rel_path != action.dst_rel_path
            ):
                src_abs = (content_root / action.src_rel_path).resolve()
                dst_abs = (content_root / action.dst_rel_path).resolve()

                assert_within_content_root(src_abs, content_root)
                assert_within_content_root(dst_abs, content_root)

                if src_abs.exists():
                    plan.disk_renames.append((src_abs, dst_abs, action.reason))

    return plan


def execute_normalization_plan(plan: NormalizationPlan) -> bool:
    """Executes staged disk renames in-place with directory creation and case-safety."""
    for src, dst, _ in plan.disk_renames:
        if src == dst or not src.exists():
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)

        # Case-only rename safety for case-insensitive filesystems (macOS/Windows)
        if src.parent == dst.parent and src.name.lower() == dst.name.lower():
            tmp = dst.parent / f".norm_case_tmp_{os.urandom(4).hex()}_{dst.name}"
            src.rename(tmp)
            tmp.rename(dst)
        else:
            src.rename(dst)

    return True


def apply_file_patches(file_abs: Path, patches: list[LinkPatch]) -> None:
    """Applies character-slice substitutions in descending order using atomic temp file replacement."""
    if not patches:
        return

    content = file_abs.read_text(encoding="utf-8")
    sorted_patches = sorted(patches, key=lambda p: p.start_char, reverse=True)

    for patch in sorted_patches:
        content = (
            content[: patch.start_char] + patch.new_target + content[patch.end_char :]
        )

    tmp_path = file_abs.with_name(f".tmp_patch_{os.urandom(6).hex()}_{file_abs.name}")
    tmp_path.write_text(content, encoding="utf-8")
    os.replace(tmp_path, file_abs)


def execute_link_healing_plan(content_root: Path, healing_plan: LinkHealingPlan) -> int:
    """Applies all staged link patches across affected Markdown documents."""
    patched_count = 0
    content_root = content_root.resolve()

    for rel_path, patches in healing_plan.patches_by_file.items():
        if not patches:
            continue
        file_abs = content_root / rel_path
        if file_abs.is_file():
            apply_file_patches(file_abs, patches)
            patched_count += len(patches)

    return patched_count


def prune_empty_directories(content_root: Path):
    """Recursively removes empty directory branches left behind after file renames."""
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


def parse_frontmatter_dict(text: str) -> dict:
    clean_text = text.lstrip("\ufeff")
    if not clean_text.startswith("---"):
        return {}

    lines = text.splitlines()
    yaml_lines = []
    for line in lines[1:]:
        if line.strip() in ("---", "..."):
            break
        yaml_lines.append(line)

    result = {}
    current_key = None
    multiline_mode = None
    multiline_accumulator = []

    def commit_multiline():
        nonlocal current_key, multiline_mode, multiline_accumulator
        if current_key and multiline_mode:
            val = (
                "\n".join(multiline_accumulator)
                if multiline_mode == "|"
                else " ".join(" ".join(multiline_accumulator).split())
            )
            result[current_key] = val
        multiline_mode = None
        multiline_accumulator = []

    for line in yaml_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip())

        if multiline_mode and indent > 0:
            multiline_accumulator.append(stripped)
            continue
        elif multiline_mode and indent == 0:
            commit_multiline()

        if stripped.startswith("- ") and current_key:
            item = stripped[2:].strip().strip("'\"")
            if not isinstance(result.get(current_key), list):
                result[current_key] = []
            result[current_key].append(item)
            continue

        if ":" in stripped:
            key, raw_val = stripped.split(":", 1)
            key = key.strip()
            raw_val = raw_val.strip()
            current_key = key

            if raw_val in ("|", ">"):
                multiline_mode = raw_val
                multiline_accumulator = []
                continue

            if raw_val.startswith("[") and raw_val.endswith("]"):
                inner = raw_val[1:-1].strip()
                result[key] = (
                    [x.strip().strip("'\"") for x in inner.split(",") if x.strip()]
                    if inner
                    else []
                )
                continue

            if (raw_val.startswith('"') and raw_val.endswith('"')) or (
                raw_val.startswith("'") and raw_val.endswith("'")
            ):
                raw_val = raw_val[1:-1]

            result[key] = raw_val

    commit_multiline()
    return result


def extract_frontmatter_metadata(content: str, stem: str) -> tuple[str, str, str, bool]:
    parsed = parse_frontmatter_dict(content)
    title = str(parsed.get("title", "")).strip()
    date_edtf = str(parsed.get("date_edtf") or parsed.get("date", "")).strip()

    keywords_val = parsed.get("keywords", "")
    if isinstance(keywords_val, list):
        keywords = " ".join(str(k).strip() for k in keywords_val)
    elif isinstance(keywords_val, str):
        keywords = keywords_val.strip()
    else:
        keywords = ""

    has_citations = bool(CITATION_PATTERN.search(content))

    if not title:
        clean_stem = stem
        ts_match = re.match(r"^(\d{8}|\d{12}|\d{14})[-_\s]+(.+)$", clean_stem)
        if ts_match:
            clean_stem = ts_match.group(2)
        title = clean_stem.replace("-", " ").replace("_", " ").title()

    return title, date_edtf, keywords, has_citations


def sync_db_with_disk(content_root: Path, db: VaultDB):
    """Atomically refreshes the SQLite ledger to match physical disk state."""
    scan_res = scan_vault(content_root, db)
    current_paths = {f.rel_path for f in scan_res.files}
    current_canonicals = {f.canonical_filename for f in scan_res.files}
    canonical_to_rel = {f.canonical_filename: f.rel_path for f in scan_res.files}

    existing_db_files = db.get_all_files()
    paths_to_delete = [
        rel_path
        for rel_path in existing_db_files.keys()
        if rel_path not in current_paths
    ]
    if paths_to_delete:
        db.delete_files_by_paths_batch(paths_to_delete)

    files_to_upsert = [
        FileRecord(
            id=None,
            canonical_filename=f.canonical_filename,
            stem=f.stem,
            ext=f.ext,
            rel_path=f.rel_path,
            sha256=f.sha256,
            mtime=f.mtime,
            mtime_ns=f.mtime_ns,
            size=f.size,
            is_media=f.is_media,
            is_secure=f.is_secure,
        )
        for f in scan_res.files
    ]
    db.upsert_files_batch(files_to_upsert)

    metadata_to_upsert: list[DocMetadataRecord] = []
    links_by_source: dict[str, list] = {}

    for f in scan_res.files:
        if not f.is_media and f.ext in MARKDOWN_EXTENSIONS:
            try:
                content = f.abs_path.read_text(encoding="utf-8")
                extracted = parse_markdown_links(content, f.canonical_filename)
                all_links = to_link_records(
                    extracted,
                    target_rel_map=canonical_to_rel,
                    current_canonicals=current_canonicals,
                )
                links_by_source[f.canonical_filename] = all_links

                title, date_edtf, keywords, has_cites = extract_frontmatter_metadata(
                    content, f.stem
                )
                metadata_to_upsert.append(
                    DocMetadataRecord(
                        canonical_filename=f.canonical_filename,
                        title=title,
                        date_edtf=date_edtf,
                        keywords=keywords,
                        has_citations=has_cites,
                    )
                )
            except (OSError, UnicodeDecodeError):
                pass

    if metadata_to_upsert:
        db.upsert_doc_metadata_batch(metadata_to_upsert)
    if links_by_source:
        db.replace_all_links_batch(links_by_source)


def audit_security_boundaries(
    scan_result: VaultScanResult,
) -> list[tuple[str, str, int, str]]:
    """Validates media isolation boundaries between secure and public contexts."""
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
        except (OSError, UnicodeDecodeError):
            pass

    return violations


def print_audit_report(
    norm_plan: NormalizationPlan,
    boundary_violations: list[tuple[str, str, int, str]],
    broken_links: list[BrokenLinkDiagnostic],
    collisions: dict[str, list[str]],
    scan_time_ms: float,
):
    """Outputs an ANSI-colorized diagnostic scorecard of the vault state."""
    print(f"\n{BOLD}{CYAN}=== Kykloi Vault Audit & Health Report ==={RESET}")
    print(f"{DIM}Scan duration: {scan_time_ms:.2f} ms{RESET}\n")

    has_issues = False

    # 1. Filename Sanitization Requirements
    if norm_plan.has_changes:
        has_issues = True
        print(
            f"{BOLD}{YELLOW}Un-normalized Filenames Requiring Normalization ({len(norm_plan.disk_renames)}):{RESET}"
        )
        for src, dst, reason in norm_plan.disk_renames:
            print(f"  {YELLOW}[RENAME]{RESET} {src.name} -> {BOLD}{dst.name}{RESET}")
            print(f"           {DIM}Target: {dst}{RESET}")
        print()

    # 2. Filename Collisions
    if collisions:
        has_issues = True
        print(
            f"{BOLD}{RED}CRITICAL: Stem Collisions Detected ({len(collisions)}):{RESET}"
        )
        for fname, paths in collisions.items():
            print(f"  {RED}[COLLISION]{RESET} '{fname}':")
            for p in paths:
                print(f"    - {p}")
        print()

    # 3. Security Boundary Violations
    if boundary_violations:
        has_issues = True
        print(
            f"{BOLD}{RED}CRITICAL: Security Boundary Violations ({len(boundary_violations)}):{RESET}"
        )
        for src, tgt, line, reason in boundary_violations:
            print(f"  {RED}[BOUNDARY]{RESET} {src}:{line} -> {tgt} ({reason})")
        print()

    # 4. Broken Link Diagnostics
    if broken_links:
        has_issues = True
        print(
            f"{BOLD}{MAGENTA}Broken References Requiring Author Attention ({len(broken_links)}):{RESET}"
        )
        for diag in broken_links:
            print(
                f"  {MAGENTA}[BROKEN LINK]{RESET} {diag.source_rel_path}:{diag.line_number}"
            )
            print(f"                Target:   {diag.raw_target}")
            if diag.suggested_fix:
                print(f"                {GREEN}Fix with: {diag.suggested_fix}{RESET}")
            else:
                print(f"                {RED}Status:   {diag.reason}{RESET}")
        print()

    if not has_issues:
        print(
            f"{GREEN}[+] Vault is in pristine archival health. Zero anomalies detected.{RESET}\n"
        )


def scaffold_new_document(content_root: Path) -> Path | None:
    """Interactive wizard for generating archival notes with valid slugs and frontmatter."""
    print(f"\n{BOLD}{CYAN}=== Create New Archival Document ==={RESET}")
    try:
        title = input(f"{BOLD}Document Title: {RESET}").strip()
        if not title:
            print(f"{YELLOW}Operation cancelled: Title cannot be empty.{RESET}")
            return None

        sub_dir = input(
            f"{BOLD}Subdirectory relative to content/ (press Enter for root): {RESET}"
        ).strip()
        is_secure_input = (
            input(f"{BOLD}Is this document encrypted /secure/? [y/N]: {RESET}")
            .strip()
            .lower()
        )
        is_secure = is_secure_input in ("y", "yes")

        date_stamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        slug_title = slugify_stem(title)
        filename = f"{date_stamp}-{slug_title}.md"

        target_dir = content_root
        if is_secure:
            target_dir = target_dir / "secure"
        if sub_dir:
            target_dir = target_dir / sub_dir

        target_dir.mkdir(parents=True, exist_ok=True)
        file_path = target_dir / filename

        if file_path.exists():
            print(f"{RED}Error: File '{file_path}' already exists.{RESET}")
            return None

        today_edtf = datetime.date.today().isoformat()
        frontmatter = f"""---
title: "{title}"
date_edtf: "{today_edtf}"
keywords: []
---

# {title}

"""
        file_path.write_text(frontmatter, encoding="utf-8")
        print(
            f"\n{GREEN}[+] Created document: {file_path.relative_to(content_root)}{RESET}\n"
        )
        return file_path

    except (KeyboardInterrupt, EOFError):
        print(f"\n{YELLOW}Aborted by user.{RESET}")
        return None


def write_broken_links_report(
    boundary_violations: list[tuple[str, str, int, str]],
    broken_links: list[BrokenLinkDiagnostic],
    quarantined: list[tuple[str, str]],
    collisions: dict[str, list[str]],
    log_path: Path,
):
    """Writes a comprehensive diagnostic report to logs/broken-links.log."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    lines = [
        "=" * 80,
        "                    KYKLOI VAULT AUDIT & BROKEN REFERENCES",
        "=" * 80,
        f"Timestamp (UTC): {stamp}",
        f"Total Boundary Violations: {len(boundary_violations)}",
        f"Total Broken / Dead References: {len(broken_links)}",
        f"Total Quarantined Discontinuities: {len(quarantined)}",
        f"Total Stem Collisions: {len(collisions)}",
        "",
    ]

    # Section 1: Security Boundary Violations
    lines.append("-" * 80)
    lines.append(
        "1. SECURITY BOUNDARY VIOLATIONS (Action Required: Relocate asset or update link)"
    )
    lines.append("-" * 80)
    if boundary_violations:
        for idx, (src, tgt, line, reason) in enumerate(boundary_violations, 1):
            lines.append(f"[BOUNDARY-{idx:02d}]")
            lines.append(f"  Source Note:   {src} (Line {line})")
            lines.append(f"  Target Asset:  {tgt}")
            lines.append(f"  Violation:     {reason}")
            lines.append(
                "  Remediation:   Ensure markdown document and embedded media share the same security profile."
            )
            lines.append("")
    else:
        lines.append("  None detected.")
        lines.append("")

    # Section 2: Quarantined Discontinuities
    lines.append("-" * 80)
    lines.append(
        "2. QUARANTINED UNRESOLVED DISCONTINUITIES (Case 6: Path, Name & Content Changed)"
    )
    lines.append("-" * 80)
    if quarantined:
        for idx, (db_p, disk_p) in enumerate(quarantined, 1):
            lines.append(f"[QUARANTINE-{idx:02d}]")
            lines.append(f"  Unmatched DB Record:   {db_p}")
            lines.append(f"  Unmatched Disk File:   {disk_p}")
            lines.append(
                "  Status:                Ambiguous identity. File content, path, and name were all altered."
            )
            lines.append(
                "  Remediation:           Verify file identity and update links manually if needed."
            )
            lines.append("")
    else:
        lines.append("  None detected.")
        lines.append("")

    # Section 3: Dead Links
    lines.append("-" * 80)
    lines.append("3. MISSING ASSETS & DEAD REFERENCES (404 Not Found)")
    lines.append("-" * 80)
    dead_links = [d for d in broken_links if d.category == "DEAD_LINK"]
    if dead_links:
        for idx, diag in enumerate(dead_links, 1):
            lines.append(f"[DEAD-LINK-{idx:02d}]")
            lines.append(
                f"  Source Note:   {diag.source_rel_path} (Line {diag.line_number})"
            )
            lines.append(f"  Raw Target:    {diag.raw_target}")
            lines.append(f"  Reason:        {diag.reason}")
            if diag.suggested_fix:
                lines.append(f"  Suggested Fix: {diag.suggested_fix}")
            lines.append(
                "  Remediation:   Supply the missing file or remove/update the Markdown link."
            )
            lines.append("")
    else:
        lines.append("  None detected.")
        lines.append("")

    # Section 4: Stem Collisions
    lines.append("-" * 80)
    lines.append("4. STEM COLLISIONS (Files with identical canonical filenames)")
    lines.append("-" * 80)
    if collisions:
        for fname, paths in collisions.items():
            lines.append(f"[COLLISION] '{fname}':")
            for p in paths:
                lines.append(f"  - {p}")
            lines.append(
                "  Remediation: Disambiguate file names to maintain globally unique stems."
            )
            lines.append("")
    else:
        lines.append("  None detected.")
        lines.append("")

    lines.append("=" * 80)
    log_path.write_text("\n".join(lines), encoding="utf-8")


def run_audit(
    content_root: Path, db_path: Path
) -> tuple[int, NormalizationPlan, list[BrokenLinkDiagnostic]]:
    """Runs a complete read-only health audit of the vault and writes logs/broken-links.log."""
    t0 = time.perf_counter()
    with VaultDB(db_path) as db:
        db.init_schema()
        scan_result = scan_vault(content_root, db)
        boundary_violations = audit_security_boundaries(scan_result)
        diff_plan = compute_diff(scan_result, db)
        norm_plan = build_normalization_plan(content_root, diff_plan)

        healing_plan, diagnostics = plan_link_healing(
            content_root=content_root,
            scanned_files=scan_result.files,
            relocation_map=diff_plan.relocation_map,
            canonical_to_final_rel=diff_plan.canonical_to_final_rel,
            boundary_violations=boundary_violations,
        )

        broken_links_log_path = PROJECT_ROOT / "logs" / "broken-links.log"
        write_broken_links_report(
            boundary_violations=boundary_violations,
            broken_links=diagnostics,
            quarantined=diff_plan.quarantined_discontinuities,
            collisions=diff_plan.collisions,
            log_path=broken_links_log_path,
        )

        scan_time_ms = (time.perf_counter() - t0) * 1000.0

        print_audit_report(
            norm_plan=norm_plan,
            boundary_violations=boundary_violations,
            broken_links=diagnostics,
            collisions=diff_plan.collisions,
            scan_time_ms=scan_time_ms,
        )

        has_critical = bool(
            boundary_violations or diff_plan.collisions or norm_plan.has_changes
        )
        exit_code = 1 if has_critical else (2 if diagnostics else 0)
        return exit_code, norm_plan, diagnostics


def run_normalization_pipeline(
    content_root: Path,
    db_path: Path,
    auto_apply: bool = False,
) -> int:
    """Normalizes filenames on disk, applies in-place link healing, and updates the SQLite ledger."""
    content_root = content_root.resolve()
    db_path = db_path.resolve()

    if not content_root.exists() or not content_root.is_dir():
        print(
            f"{RED}[FATAL] Content directory not found: {content_root}{RESET}",
            file=sys.stderr,
        )
        return 1

    with VaultDB(db_path) as db:
        db.init_schema()
        scan_result = scan_vault(content_root, db)
        boundary_violations = audit_security_boundaries(scan_result)
        diff_plan = compute_diff(scan_result, db)
        norm_plan = build_normalization_plan(content_root, diff_plan)

        healing_plan, diagnostics = plan_link_healing(
            content_root=content_root,
            scanned_files=scan_result.files,
            relocation_map=diff_plan.relocation_map,
            canonical_to_final_rel=diff_plan.canonical_to_final_rel,
            boundary_violations=boundary_violations,
        )

        broken_links_log_path = PROJECT_ROOT / "logs" / "broken-links.log"
        write_broken_links_report(
            boundary_violations=boundary_violations,
            broken_links=diagnostics,
            quarantined=diff_plan.quarantined_discontinuities,
            collisions=diff_plan.collisions,
            log_path=broken_links_log_path,
        )

        if not norm_plan.has_changes and not healing_plan.has_patches:
            sync_db_with_disk(content_root, db)
            return 0

        if norm_plan.has_changes:
            print(
                f"\n{BOLD}{YELLOW}Planned Filename Normalizations ({len(norm_plan.disk_renames)} files):{RESET}"
            )
            for src, dst, _ in norm_plan.disk_renames:
                print(
                    f"  {src.relative_to(content_root)} -> {BOLD}{dst.relative_to(content_root)}{RESET}"
                )
            print()

        if healing_plan.has_patches:
            print(
                f"\n{BOLD}{CYAN}Planned In-Place Link Updates ({healing_plan.total_patch_count} links in {len(healing_plan.patches_by_file)} files):{RESET}"
            )
            for rel_p, patches in healing_plan.patches_by_file.items():
                print(f"  {BOLD}{rel_p}:{RESET}")
                for patch in patches:
                    print(
                        f"    {DIM}{patch.old_target}{RESET} -> {GREEN}{patch.new_target}{RESET}"
                    )
            print()

        if not auto_apply:
            if not sys.stdin.isatty():
                print(
                    f"{RED}[ERROR] Non-interactive environment. Use --auto-apply.{RESET}",
                    file=sys.stderr,
                )
                return 1

            try:
                answer = (
                    input(
                        f"{BOLD}Apply these renames and link updates on disk now? [y/N]: {RESET}"
                    )
                    .strip()
                    .lower()
                )
            except (KeyboardInterrupt, EOFError):
                print(f"\n{YELLOW}Aborted by user.{RESET}")
                return 1

            if answer not in ("y", "yes"):
                print(f"{YELLOW}Operation cancelled. Files remain unchanged.{RESET}")
                return 0

        # Phase 1: Write-ahead journal
        session_id = f"norm_{os.urandom(6).hex()}_{int(time.time())}"
        renames_json = json.dumps(
            [(str(s), str(d)) for s, d, _ in norm_plan.disk_renames]
        )
        patches_json = json.dumps(
            {
                k: [
                    {"start": p.start_char, "end": p.end_char, "new": p.new_target}
                    for p in v
                ]
                for k, v in healing_plan.patches_by_file.items()
            }
        )
        jid = db.record_journal(
            session_id=session_id,
            stage="STAGED",
            file_renames_json=renames_json,
            content_patches_json=patches_json,
            created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        )

        # Phase 2: Physical renames
        execute_normalization_plan(norm_plan)
        db.update_journal_stage(jid, "RENAMED")
        prune_empty_directories(content_root)

        # Phase 3: In-place link healing
        if healing_plan.has_patches:
            execute_link_healing_plan(content_root, healing_plan)
            db.update_journal_stage(jid, "PATCHED")

        # Phase 4: Synchronize database and commit journal
        sync_db_with_disk(content_root, db)
        db.update_journal_stage(jid, "COMMITTED")
        db.clear_committed_journals()

        print(
            f"{GREEN}[SUCCESS] Vault normalized, links healed, and ledger updated.{RESET}\n"
        )
        return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deterministic Content Normalizer & Vault Diagnostics for Project Kykloi."
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
        help="Path to SQLite ledger (default: system/normalize/vault-index.db)",
    )
    parser.add_argument(
        "--audit",
        action="store_true",
        help="Run read-only vault health check, diagnosing filenames, broken links, and boundaries.",
    )
    parser.add_argument(
        "--normalize",
        action="store_true",
        help="Interactively normalize invalid file stems and directory names on disk.",
    )
    parser.add_argument(
        "--auto-apply",
        action="store_true",
        help="Automatically apply filename normalizations without confirmation prompts.",
    )
    parser.add_argument(
        "--new",
        action="store_true",
        help="Scaffold a new note with valid slug, frontmatter, and EDTF timestamp.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if args.new:
        scaffold_new_document(args.vault_dir)
        sys.exit(0)

    if args.audit:
        code, _, _ = run_audit(args.vault_dir, args.db_path)
        sys.exit(code)

    if args.normalize:
        code = run_normalization_pipeline(
            args.vault_dir, args.db_path, auto_apply=args.auto_apply
        )
        sys.exit(code)

    # Default action if invoked directly without flags: run audit
    code, _, _ = run_audit(args.vault_dir, args.db_path)
    sys.exit(code)


if __name__ == "__main__":
    main()
