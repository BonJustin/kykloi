import argparse
import concurrent.futures
import logging
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml

# ===========================================================================
# 1. GLOBAL PATH INITIALIZATION
# ===========================================================================

try:
    PROJECT_ROOT = Path(__file__).parent.resolve().parent
    SRC = PROJECT_ROOT / "content"
    DST = PROJECT_ROOT / "dist"
    APP_DIR = PROJECT_ROOT / "build"

    DEFAULTS_YAML = APP_DIR / "pandoc_md_to_static_html.yaml"
    DEFAULT_TEMPLATE = APP_DIR / "templates" / "md_to_static_html.html"
    LUA_FILTER = APP_DIR / "translate_links.lua"

except Exception as err:
    print(f"CRITICAL CONFIGURATION ERROR: {err}", file=sys.stderr)
    sys.exit(1)


# ===========================================================================
# 2. DATA STRUCTURES & ARGUMENT PARSING
# ===========================================================================


@dataclass(frozen=True)
class CompileTask:
    md_path: Path
    out_path: Path
    template_path: Path
    relative_root: str
    defaults_yaml: Path
    lua_filter: Path
    dry_run: bool
    verbose: bool


def parse_args():
    p = argparse.ArgumentParser(
        description="High-performance Pandoc static site generator."
    )
    p.add_argument(
        "--clean",
        action="store_true",
        help="Purge the output directory before running for a clean rebuild.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate the build without writing files.",
    )
    p.add_argument(
        "--verbose",
        action="store_true",
        help="Display detailed commands and file-by-file status.",
    )
    p.add_argument(
        "--workers",
        type=int,
        default=os.cpu_count() or 4,
        help="Number of concurrent worker processes for Pandoc (default: CPU core count).",
    )
    return p.parse_args()


# ===========================================================================
# 3. TEMPLATE PARSING & DIRTY-CHECKING
# ===========================================================================


def extract_custom_template_stream(
    md_path: Path, app_dir: Path, default_template: Path
) -> Path:
    """Fast stream-based frontmatter scan for custom HTML templates."""
    try:
        with open(md_path, "r", encoding="utf-8") as f:
            first_line = f.readline()
            if not first_line:
                return default_template

            if first_line.startswith("\ufeff"):
                first_line = first_line[1:]

            if first_line.strip() != "---":
                return default_template

            yaml_lines = []
            closed = False
            for _ in range(150):
                line = f.readline()
                if not line:
                    break
                if line.strip() == "---":
                    closed = True
                    break
                yaml_lines.append(line)

        if closed and yaml_lines:
            yaml_block = "".join(yaml_lines)
            if "html_template" not in yaml_block:
                return default_template

            meta = yaml.safe_load(yaml_block)
            if isinstance(meta, dict):
                custom_tpl = meta.get("html_template")
                if custom_tpl:
                    resolved = app_dir / str(custom_tpl)
                    if not resolved.exists():
                        resolved = app_dir / "templates" / str(custom_tpl)
                    if resolved.is_file():
                        return resolved

                    logging.warning(
                        "Template '%s' in '%s' not found. Falling back to default.",
                        custom_tpl,
                        md_path.name,
                    )
    except Exception as error:
        logging.debug("Frontmatter parse error on %s: %s", md_path.name, error)

    return default_template


def get_global_dependency_mtime() -> float:
    """Returns the latest modification time among all global configuration files and templates."""
    tracked_files = [DEFAULTS_YAML, LUA_FILTER]
    templates_dir = APP_DIR / "templates"
    if templates_dir.exists():
        tracked_files.extend(templates_dir.glob("*.html"))

    existing_mtimes = [f.stat().st_mtime for f in tracked_files if f.is_file()]
    return max(existing_mtimes) if existing_mtimes else 0.0


# ===========================================================================
# 4. COMPILATION WORKER (PARALLEL EXECUTION)
# ===========================================================================


def compile_markdown_worker(task: CompileTask) -> tuple[Path, bool, Optional[str]]:
    """Worker function executed across multiple CPU cores."""
    cmd = [
        "pandoc",
        str(task.md_path),
        "--defaults",
        str(task.defaults_yaml),
        "--template",
        str(task.template_path),
        "--lua-filter",
        str(task.lua_filter),
        "-V",
        f"relative_root={task.relative_root}",
        f"--katex={task.relative_root}assets/katex/",
        "-o",
        str(task.out_path),
    ]

    css_files = ["assets/css/pico.css", "assets/css/style.css"]
    for css in css_files:
        cmd.extend(["--css", f"{task.relative_root}{css}"])

    if task.dry_run:
        return task.md_path, True, None

    # Ensure target subdirectory exists
    task.out_path.parent.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return task.md_path, False, result.stderr.strip()

    return task.md_path, True, None


# ===========================================================================
# 5. RECONCILIATION & ORPHAN PRUNING
# ===========================================================================


def prune_orphans(
    dst_dir: Path, expected_files: set[Path], preserve_dirs: set[str], dry_run: bool
) -> int:
    """
    Deletes any file or directory in dst_dir that is not part of expected_files.
    Preserves specialized directories like 'pagefind'.
    """
    if not dst_dir.exists():
        return 0

    orphans_removed = 0

    # 1. Prune orphaned files
    for item in list(dst_dir.rglob("*")):
        if item.is_file():
            # Check if file resides inside a preserved directory
            rel_parts = item.relative_to(dst_dir).parts
            if any(part in preserve_dirs for part in rel_parts):
                continue

            if item.resolve() not in expected_files:
                if not dry_run:
                    item.unlink()
                orphans_removed += 1
                logging.debug("Pruned orphan file: %s", item)

    # 2. Prune empty directories (bottom-up traversal)
    for dirpath in sorted(dst_dir.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if dirpath.is_dir():
            rel_parts = dirpath.relative_to(dst_dir).parts
            if any(part in preserve_dirs for part in rel_parts):
                continue
            if not any(dirpath.iterdir()):
                if not dry_run:
                    dirpath.rmdir()
                logging.debug("Pruned empty dir: %s", dirpath)

    return orphans_removed


# ===========================================================================
# 6. ASSET SYNCING (INCREMENTAL DIFFING)
# ===========================================================================


def sync_file_if_modified(src: Path, dst: Path, dry_run: bool) -> bool:
    """Copies src to dst only if dst doesn't exist or src was updated."""
    if not dst.exists() or src.stat().st_mtime > dst.stat().st_mtime:
        if not dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        return True
    return False


def sync_assets_incremental(src_dir: Path, dst_dir: Path, dry_run: bool) -> int:
    """Synchronizes non-markdown files preserving hierarchy."""
    if not src_dir.exists():
        return 0
    synced = 0
    for p in src_dir.rglob("*"):
        if p.is_file() and p.suffix.lower() != ".md" and not p.name.startswith("."):
            target = dst_dir / p.relative_to(src_dir)
            if sync_file_if_modified(p, target, dry_run):
                synced += 1
    return synced


def sync_directory_incremental(src_dir: Path, dst_dir: Path, dry_run: bool) -> int:
    """Mirrors a folder incrementally."""
    if not src_dir.exists():
        return 0
    synced = 0
    for p in src_dir.rglob("*"):
        if p.is_file() and not p.name.startswith("."):
            target = dst_dir / p.relative_to(src_dir)
            if sync_file_if_modified(p, target, dry_run):
                synced += 1
    return synced


# ===========================================================================
# 7. SEARCH INDEXING
# ===========================================================================


def run_pagefind(site_dir: Path, dry_run: bool, verbose: bool):
    """Executes Pagefind indexer."""
    if dry_run:
        logging.info("[DRY RUN] Would execute Pagefind search indexing.")
        return

    cmd = ["pagefind", "--site", str(site_dir)]
    if verbose:
        logging.info("Running: %s", " ".join(cmd))

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if res.returncode != 0:
            logging.error(
                "Pagefind failed (Exit %d):\n%s", res.returncode, res.stderr.strip()
            )
        else:
            logging.info("Pagefind index updated successfully.")
    except Exception as err:
        logging.error("Failed to run Pagefind: %s", err)


# ===========================================================================
# 8. MAIN EXECUTION PIPELINE
# ===========================================================================


def main():
    args = parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    # Validate essential configurations
    for path, desc in [
        (SRC, "Source directory"),
        (DEFAULTS_YAML, "Pandoc defaults"),
        (LUA_FILTER, "Lua filter"),
    ]:
        if not path.exists():
            logging.error("%s missing: %s", desc, path)
            sys.exit(1)

    # 1. Handle Explicit Clean Flag
    if args.clean and DST.exists():
        logging.info("Flag --clean passed. Purging entire destination: %s", DST)
        if not args.dry_run:
            shutil.rmtree(DST)

    DST.mkdir(parents=True, exist_ok=True)

    # 2. Inventory Expected Outputs & Identify Dirty Markdown Files
    expected_outputs: set[Path] = set()
    compile_tasks: list[CompileTask] = []
    global_dep_mtime = get_global_dependency_mtime()

    md_files = list(SRC.rglob("*.md"))
    if not md_files:
        logging.warning("No markdown files detected in %s.", SRC)
        sys.exit(0)

    for md in md_files:
        rel = md.relative_to(SRC)
        out = DST / rel.with_suffix(".html")
        expected_outputs.add(out.resolve())

        # Determine relative root
        depth = len(rel.parent.parts) if rel.parent != Path(".") else 0
        relative_root = "../" * depth if depth > 0 else "./"

        # Resolve template
        template = extract_custom_template_stream(md, APP_DIR, DEFAULT_TEMPLATE)
        template_mtime = template.stat().st_mtime if template.exists() else 0.0

        # Dirty Check Logic
        out_exists = out.exists()
        out_mtime = out.stat().st_mtime if out_exists else 0.0

        is_dirty = (
            not out_exists
            or md.stat().st_mtime > out_mtime
            or global_dep_mtime > out_mtime
            or template_mtime > out_mtime
        )

        if is_dirty:
            compile_tasks.append(
                CompileTask(
                    md_path=md,
                    out_path=out,
                    template_path=template,
                    relative_root=relative_root,
                    defaults_yaml=DEFAULTS_YAML,
                    lua_filter=LUA_FILTER,
                    dry_run=args.dry_run,
                    verbose=args.verbose,
                )
            )

    # 3. Inventory Expected Assets
    # Content media
    for p in SRC.rglob("*"):
        if p.is_file() and p.suffix.lower() != ".md" and not p.name.startswith("."):
            expected_outputs.add((DST / p.relative_to(SRC)).resolve())

    # Functional assets (CSS, JS, Fonts, KaTeX)
    assets_src = APP_DIR / "assets"
    if assets_src.exists():
        for p in assets_src.rglob("*"):
            if p.is_file():
                expected_outputs.add(
                    (DST / "assets" / p.relative_to(assets_src)).resolve()
                )

    # Root assets (favicons, manifests, etc.)
    root_src = APP_DIR / "root"
    if root_src.exists():
        for p in root_src.rglob("*"):
            if p.is_file():
                expected_outputs.add((DST / p.relative_to(root_src)).resolve())

    # 4. Prune Dead Orphans (Before Compiling & Indexing)
    orphans_pruned = prune_orphans(
        DST, expected_outputs, preserve_dirs={"pagefind"}, dry_run=args.dry_run
    )
    if orphans_pruned:
        logging.info("Pruned %d orphaned file(s).", orphans_pruned)

    # 5. Concurrent Compilation Phase
    total_md = len(md_files)
    to_compile = len(compile_tasks)
    failed = 0

    if to_compile > 0:
        logging.info(
            "Compiling %d of %d notes using %d workers...",
            to_compile,
            total_md,
            args.workers,
        )

        with concurrent.futures.ProcessPoolExecutor(
            max_workers=args.workers
        ) as executor:
            future_to_file = {
                executor.submit(compile_markdown_worker, t): t.md_path
                for t in compile_tasks
            }

            for future in concurrent.futures.as_completed(future_to_file):
                md_path = future_to_file[future]
                try:
                    _, success, err = future.result()
                    if not success:
                        failed += 1
                        logging.error("Pandoc error on %s:\n%s", md_path.name, err)
                    elif args.verbose:
                        logging.info("Built: %s", md_path.name)
                except Exception as exc:
                    failed += 1
                    logging.error("Exception compiling %s: %s", md_path.name, exc)
    else:
        logging.info(
            "All %d notes are up to date. No HTML recompilation required.", total_md
        )

    # 6. Incremental Asset Sync
    synced_assets = sync_directory_incremental(
        assets_src, DST / "assets", dry_run=args.dry_run
    )
    synced_media = sync_assets_incremental(SRC, DST, dry_run=args.dry_run)
    synced_root = sync_directory_incremental(root_src, DST, dry_run=args.dry_run)

    total_synced = synced_assets + synced_media + synced_root
    if total_synced > 0:
        logging.info("Synced %d updated asset(s).", total_synced)

    # 7. Update Search Index
    # Re-run Pagefind if any notes were compiled or orphans were pruned
    if (to_compile > 0 or orphans_pruned > 0) and not failed:
        run_pagefind(DST, dry_run=args.dry_run, verbose=args.verbose)

    # Summary
    if failed:
        logging.error("Build completed with %d failure(s).", failed)
        sys.exit(1)

    logging.info(
        "Build complete. (%d compiled, %d pruned, %d synced)",
        to_compile,
        orphans_pruned,
        total_synced,
    )


if __name__ == "__main__":
    main()
