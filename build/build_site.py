import argparse
import logging
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

# ===========================================================================
# 1. GLOBAL INITIALIZATION
# ===========================================================================

try:
    PROJECT_ROOT = Path(__file__).parent.resolve().parent

    SRC = PROJECT_ROOT / "content"
    DST = PROJECT_ROOT / "dist"
    app_dir = PROJECT_ROOT / "build"

    DEFAULTS_YAML = app_dir / "pandoc_md_to_static_html.yaml"
    TEMPLATE_HTML = app_dir / "templates" / "md_to_static_html.html"
    LUA_FILTER = app_dir / "translate_links.lua"


except (FileNotFoundError, KeyError) as error:
    print(
        f"CRITICAL CONFIGURATION ERROR: Missing value or file: {error}", file=sys.stderr
    )
    sys.exit(1)

# ===========================================================================
# 2. FUNCTION DEFINITIONS
# ===========================================================================


def parse_args():
    p = argparse.ArgumentParser(description="Build HTML site from markdown folder.")
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would happen without doing it.",
    )
    p.add_argument(
        "--verbose",
        action="store_true",
        help="Show each pandoc command before running it.",
    )
    return p.parse_args()


def extract_custom_template_stream(
    md_path: Path, app_dir: Path, default_template: Path
) -> Path:
    """
    Parses the YAML frontmatter of a markdown file strictly within the start
    and end delimiters ('---'). Fast-paths the template check and resolves
    the template path against the 'app' directory.
    """
    try:
        with open(md_path, "r", encoding="utf-8") as f:
            first_line = f.readline()
            if not first_line:
                return default_template

            # Handle UTF-8 Byte Order Mark (BOM) if present
            if first_line.startswith("\ufeff"):
                first_line = first_line[1:]

            # Standard YAML frontmatter must start on the absolute first line
            if first_line.strip() != "---":
                return default_template

            yaml_lines = []
            closed_properly = False
            # Limit scan to 150 lines to prevent reading entire massive files
            for _ in range(150):
                line = f.readline()
                if not line:
                    break
                if line.strip() == "---":
                    closed_properly = True
                    break
                yaml_lines.append(line)

        # Only parse if we isolated a completely closed, valid frontmatter block
        if closed_properly and yaml_lines:
            yaml_block = "".join(yaml_lines)

            # Fast-path lookup: check if our custom tag exists in the isolated block
            if "html_template" not in yaml_block:
                return default_template

            # Safely load the isolated YAML snippet
            metadata = yaml.safe_load(yaml_block)
            if isinstance(metadata, dict):
                custom_tpl = metadata.get("html_template")
                if custom_tpl:
                    resolved_path = app_dir / str(custom_tpl)
                    if resolved_path.exists() and resolved_path.is_file():
                        return resolved_path

                    logging.warning(
                        "Custom template '%s' declared in '%s' does not exist in '%s'. "
                        "Falling back to default template.",
                        custom_tpl,
                        md_path.name,
                        app_dir,
                    )
    except Exception as error:
        logging.debug(
            "Stream-based template extraction failed for %s: %s", md_path.name, error
        )

    return default_template


def convert_file(
    md: Path,
    out: Path,
    defaults_yaml: Path,
    template_html: Path,
    lua_filter: Path,
    relative_root: str,
    dry_run: bool,
    verbose: bool,
) -> bool:
    """Run pandoc on a single markdown file with dynamic variables. Returns True on success."""
    cmd = [
        "pandoc",
        str(md),
        "--defaults",
        str(defaults_yaml),
        "--template",
        str(template_html),
        "--lua-filter",
        str(lua_filter),
        "-V",
        f"relative_root={relative_root}",
        f"--katex={relative_root}assets/katex/",
        "-o",
        str(out),
    ]

    # Inject relative paths to CSS stylesheets dynamically
    css_files = [
        "assets/css/pico.css",
        "assets/css/style.css",
        "assets/katex/katex.min.css",
    ]
    for css in css_files:
        cmd.extend(["--css", f"{relative_root}{css}"])

    if verbose or dry_run:
        logging.info("  cmd: %s", " ".join(cmd))
    if dry_run:
        return True

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logging.error("pandoc failed on %s:\n%s", md, result.stderr.strip())
        return False
    return True


def sync_functional_assets(
    app_assets: Path, dst_assets: Path, dry_run: bool, verbose: bool
):
    """Mirror the functional assets folder (CSS, JS, KaTeX) to the destination assets directory."""
    if not app_assets.exists():
        logging.warning(
            "Functional assets folder not found at: %s — skipping.", app_assets
        )
        return
    if verbose or dry_run:
        logging.info("Syncing functional assets: %s → %s", app_assets, dst_assets)
    if dry_run:
        return
    shutil.copytree(app_assets, dst_assets, dirs_exist_ok=True)
    logging.info("Functional assets synced.")


def sync_media_assets(src_dir: Path, dst_dir: Path, dry_run: bool, verbose: bool):
    """Find and copy all non-markdown files (media, etc.) from SRC to DST, preserving folder structure."""
    if verbose or dry_run:
        logging.info(
            "Syncing media assets (non-markdown files) from %s → %s", src_dir, dst_dir
        )
    if dry_run:
        return

    copied_count = 0
    # Walk through src_dir to find non-markdown files
    for p in src_dir.rglob("*"):
        # Copy files that are not markdown (.md) and not system/hidden files
        if p.is_file() and p.suffix.lower() != ".md" and not p.name.startswith("."):
            rel = p.relative_to(src_dir)
            target = dst_dir / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, target)
            copied_count += 1

    if verbose:
        logging.info("Copied %d media asset file(s).", copied_count)


def sync_root_assets(root_src: Path, dst_dir: Path, dry_run: bool, verbose: bool):
    """Copy files from the app root directory (favicon, .htaccess, robots.txt, etc.) directly into DST root."""
    if not root_src.exists():
        logging.warning(
            "App root configuration folder not found at: %s — skipping.", root_src
        )
        return
    if verbose or dry_run:
        logging.info("Syncing root assets: %s → %s", root_src, dst_dir)
    if dry_run:
        return
    shutil.copytree(root_src, dst_dir, dirs_exist_ok=True)
    logging.info("Root assets synced.")


def run_pagefind(site_dir: Path, dry_run: bool, verbose: bool):
    """Run Pagefind indexing on the compiled output directory."""
    if dry_run:
        logging.info("[DRY RUN] Would run Pagefind indexing on: %s", site_dir)
        return

    logging.info("Running Pagefind search indexer...")

    cmd = ["pagefind", "--site", str(site_dir)]

    if verbose:
        logging.info("  cmd: %s", " ".join(cmd))

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            logging.error(
                "Pagefind indexing failed (Exit code %d).\n"
                "Ensure pagefind is installed.\n"
                "Stderr:\n%s",
                result.returncode,
                result.stderr.strip(),
            )
        else:
            if verbose and result.stdout:
                logging.info("Pagefind Output:\n%s", result.stdout.strip())
            logging.info("Pagefind indexing completed successfully.")

    except Exception as error:
        logging.error("An unexpected error occurred executing Pagefind: %s", error)


def main():
    args = parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    # Validate configuration and assets path dependencies
    for label, path in [
        ("SRC", SRC),
        ("DEFAULTS_YAML", DEFAULTS_YAML),
        ("TEMPLATE_HTML", TEMPLATE_HTML),
        ("LUA_FILTER", LUA_FILTER),
    ]:
        if not path.exists():
            logging.error("Config path not found (%s): %s", label, path)
            sys.exit(1)

    if DST.exists():
        shutil.rmtree(DST)
    DST.mkdir(parents=True, exist_ok=True)

    # Collect all .md files (all assets folders inside SRC have been migrated)
    md_files = list(SRC.rglob("*.md"))

    if not md_files:
        logging.warning("No .md files found under %s", SRC)
        sys.exit(0)

    total = len(md_files)
    built = failed = 0

    for md in sorted(md_files):
        rel = md.relative_to(SRC)
        out = DST / rel.with_suffix(".html")

        # Determine relative root based on path depth
        rel_parent = rel.parent
        depth = len(rel_parent.parts) if rel_parent != Path(".") else 0
        relative_root = "../" * depth if depth > 0 else "./"

        out.parent.mkdir(parents=True, exist_ok=True)
        logging.info("BUILD: %s → %s", rel, out.relative_to(DST))

        # Dynamically resolve template path using high-performance stream parsing
        current_template = extract_custom_template_stream(md, app_dir, TEMPLATE_HTML)

        ok = convert_file(
            md=md,
            out=out,
            defaults_yaml=DEFAULTS_YAML,
            template_html=current_template,
            lua_filter=LUA_FILTER,
            relative_root=relative_root,
            dry_run=args.dry_run,
            verbose=args.verbose,
        )

        if ok:
            built += 1
        else:
            failed += 1

    # 1. Sync functional assets (CSS, JS, Katex) from app/assets to dst/assets
    sync_functional_assets(
        app_dir / "assets", DST / "assets", dry_run=args.dry_run, verbose=args.verbose
    )

    # 2. Sync media assets (non-markdown files) from SRC to DST
    sync_media_assets(SRC, DST, dry_run=args.dry_run, verbose=args.verbose)

    # 3. Sync root assets (favicon, robots.txt, .htaccess, etc.) from app/root to DST root
    sync_root_assets(app_dir / "root", DST, dry_run=args.dry_run, verbose=args.verbose)

    # Run Pagefind Indexer on raw unencrypted text (if no build failures occur)
    if not failed:
        run_pagefind(DST, dry_run=args.dry_run, verbose=args.verbose)

    # Summary
    mode = "[DRY RUN] " if args.dry_run else ""
    logging.info(
        "%sDone. %d/%d built, %d failed.",
        mode,
        built,
        total,
        failed,
    )
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
