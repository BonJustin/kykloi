import argparse
import base64
import concurrent.futures
import getpass
import hashlib
import json
import logging
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# Optional Cryptography Import with User Diagnostics
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except ImportError:
    AESGCM = None

# ===========================================================================
# 1. GLOBAL PATH INITIALIZATION & VALIDATION
# ===========================================================================

try:
    PROJECT_ROOT = Path(__file__).parent.resolve().parent
    SRC = PROJECT_ROOT / "content"
    DST = PROJECT_ROOT / "dist"
    APP_DIR = PROJECT_ROOT / "build"

    DEFAULTS_YAML = APP_DIR / "pandoc_md_to_static_html.yaml"
    DEFAULT_TEMPLATE = APP_DIR / "templates" / "md_to_static_html.html"
    LUA_FILTER = APP_DIR / "translate_links.lua"
    MANIFEST_FILE = APP_DIR / ".build_manifest.json"
    SEARCH_INDEX_FILE = DST / "search_index.js"

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
    is_secure: bool
    passphrase: Optional[str]
    dry_run: bool
    verbose: bool


def parse_args():
    p = argparse.ArgumentParser(
        description="Deterministic Hash-Based Pandoc Static Site Generator (MiniSearch Offline)."
    )
    p.add_argument(
        "--clean",
        action="store_true",
        help="Purge destination directory and hash manifest for a complete rebuild.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate the build pipeline without modifying disk.",
    )
    p.add_argument(
        "--verbose",
        action="store_true",
        help="Output granular diagnostic logs.",
    )
    p.add_argument(
        "--workers",
        type=int,
        default=os.cpu_count() or 4,
        help="Worker process concurrency pool size (default: CPU core count).",
    )
    p.add_argument(
        "--password",
        type=str,
        default=os.environ.get("KYKLOI_ENCRYPT_KEY"),
        help="Passphrase for /secure/ content encryption (or set KYKLOI_ENCRYPT_KEY).",
    )
    return p.parse_args()


# ===========================================================================
# 3. CRYPTOGRAPHIC HASHING & ENCRYPTION UTILITIES
# ===========================================================================


def compute_file_hash(path: Path) -> str:
    """Computes a SHA-256 digest in 64 KiB chunks for flat memory allocation."""
    hasher = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()
    except (FileNotFoundError, PermissionError) as e:
        logging.warning("Unable to hash %s: %s", path, e)
        return ""


def compute_global_dependencies_hash() -> str:
    """Computes a collective digest of pandoc defaults, lua filters, and template."""
    hasher = hashlib.sha256()
    tracked_files: list[Path] = [DEFAULTS_YAML, LUA_FILTER, DEFAULT_TEMPLATE]

    for f in tracked_files:
        if f.is_file():
            hasher.update(f.name.encode("utf-8"))
            hasher.update(compute_file_hash(f).encode("utf-8"))

    return hasher.hexdigest()


def derive_key(passphrase: str, salt: bytes) -> bytes:
    """Derives a 256-bit key using PBKDF2-HMAC-SHA256 (600,000 iterations)."""
    return hashlib.pbkdf2_hmac(
        "sha256",
        passphrase.encode("utf-8"),
        salt,
        600000,
        dklen=32,
    )


def encrypt_payload(html_content: str, passphrase: str) -> str:
    """
    Encrypts HTML content using AES-256-GCM matching the WebCrypto API envelope:
    Format: Base64(Salt [16 bytes] + IV [12 bytes] + Ciphertext & Tag [N bytes])
    """
    if AESGCM is None:
        raise RuntimeError(
            "Missing required dependency: run 'pip install cryptography'"
        )

    salt = os.urandom(16)
    iv = os.urandom(12)
    key = derive_key(passphrase, salt)

    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(iv, html_content.encode("utf-8"), None)

    envelope = salt + iv + ciphertext
    return base64.b64encode(envelope).decode("ascii")


def load_manifest(manifest_path: Path) -> dict[str, str]:
    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except (json.JSONDecodeError, OSError) as e:
            logging.warning(
                "Corrupt manifest encountered (%s). Initializing empty manifest.", e
            )
    return {}


def save_manifest(manifest_path: Path, manifest: dict[str, str], dry_run: bool):
    if dry_run:
        return
    try:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, sort_keys=True)
    except OSError as e:
        logging.error("Failed to commit build manifest to disk: %s", e)


# ===========================================================================
# 4. METADATA EXTRACTION & SEARCH INDEX GENERATION
# ===========================================================================


def extract_metadata_from_markdown(md_path: Path) -> dict[str, str]:
    meta = {
        "title": "",
        "keywords": "",
        "date_edtf": "",
        "abstract": "",
    }

    try:
        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()

        match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if match:
            fm_text = match.group(1)

            t_match = re.search(
                r"^title:\s*[\"']?(.*?)[\"']?\s*$", fm_text, re.MULTILINE
            )
            if t_match:
                meta["title"] = t_match.group(1).strip()

            d_match = re.search(
                r"^date_edtf:\s*[\"']?(.*?)[\"']?\s*$", fm_text, re.MULTILINE
            )
            if d_match:
                meta["date_edtf"] = d_match.group(1).strip()

            k_match = re.search(
                r"^keywords:\s*(?:\[(.*?)\]|(.*))", fm_text, re.MULTILINE
            )
            if k_match:
                raw_keywords = k_match.group(1) or k_match.group(2) or ""
                meta["keywords"] = " ".join(
                    re.sub(r"[\"']", "", part).strip()
                    for part in raw_keywords.split(",")
                )

            a_match = re.search(
                r"^abstract:\s*(?:[|>]-?\s*\n)?((?:[ \t]+.*(?:\n|$))+|.*$)",
                fm_text,
                re.MULTILINE,
            )
            if a_match:
                raw_abstract = a_match.group(1)
                meta["abstract"] = " ".join(
                    line.strip() for line in raw_abstract.splitlines() if line.strip()
                )

    except Exception as e:
        logging.warning("Error reading frontmatter from %s: %s", md_path, e)

    if not meta["title"]:
        meta["title"] = md_path.stem.replace("-", " ").replace("_", " ").title()

    return meta


def write_minisearch_index(records: list[dict], out_path: Path, dry_run: bool):
    if dry_run:
        logging.info("[DRY RUN] Would write search index to %s", out_path)
        return

    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = f"window.__SEARCH_DOCS__ = {json.dumps(records, ensure_ascii=False, indent=2)};\n"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(payload)
    logging.info("MiniSearch index generated with %d documents.", len(records))


# ===========================================================================
# 5. WORKER COMPILATION SUBSYSTEM
# ===========================================================================


def compile_markdown_worker(task: CompileTask) -> tuple[Path, bool, Optional[str]]:
    """Compiles Markdown documents with conditional WebCrypto envelope wrapping."""
    if task.dry_run:
        return task.md_path, True, None

    css_files = ["assets/css/pico.css", "assets/css/style.css"]

    # ---------------------------------------------------------
    # CASE 1: Standard Unencrypted Document
    # ---------------------------------------------------------
    if not task.is_secure:
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
        for css in css_files:
            cmd.extend(["--css", f"{task.relative_root}{css}"])

        task.out_path.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return task.md_path, False, result.stderr.strip()
        return task.md_path, True, None

    # ---------------------------------------------------------
    # CASE 2: Secure Encrypted Document
    # ---------------------------------------------------------
    if not task.passphrase:
        return (
            task.md_path,
            False,
            "Cannot compile secure file: No passphrase provided.",
        )

    # 1. Compile the document body in isolation with embedded media data-URIs
    body_cmd = [
        "pandoc",
        str(task.md_path),
        "--defaults",
        str(task.defaults_yaml),
        "--lua-filter",
        str(task.lua_filter),
        f"--katex={task.relative_root}assets/katex/",
        "--embed-resources",
        "--resource-path",
        str(task.md_path.parent),
        "--metadata=title:",  # Suppresses internal title-block duplication
    ]

    body_result = subprocess.run(body_cmd, capture_output=True, text=True)
    if body_result.returncode != 0:
        return task.md_path, False, body_result.stderr.strip()

    # 2. Encrypt the compiled HTML body in Python memory
    try:
        ciphertext_b64 = encrypt_payload(body_result.stdout, task.passphrase)
    except Exception as e:
        return task.md_path, False, f"Encryption failed: {e}"

    # 3. Compile the standalone outer envelope WITHOUT the heavy payload argument
    envelope_cmd = [
        "pandoc",
        str(task.md_path),
        "--template",
        str(task.template_path),
        "-V",
        f"relative_root={task.relative_root}",
        "-V",
        "encrypted=true",
    ]
    for css in css_files:
        envelope_cmd.extend(["--css", f"{task.relative_root}{css}"])

    envelope_result = subprocess.run(envelope_cmd, capture_output=True, text=True)
    if envelope_result.returncode != 0:
        return task.md_path, False, envelope_result.stderr.strip()

    # 4. Stream ciphertext directly into file on disk
    try:
        # Inject raw base64 string directly inside the script block
        final_html = envelope_result.stdout.replace(
            "__KYKLOI_ENCRYPTED_PAYLOAD__", ciphertext_b64
        )
        task.out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(task.out_path, "w", encoding="utf-8") as f:
            f.write(final_html)
    except OSError as e:
        return task.md_path, False, f"Disk write error: {e}"

    return task.md_path, True, None


# ===========================================================================
# 6. ORPHAN PRUNING
# ===========================================================================


def prune_orphans(dst_dir: Path, expected_files: set[Path], dry_run: bool) -> int:
    if not dst_dir.exists():
        return 0

    orphans_removed = 0
    for item in list(dst_dir.rglob("*")):
        if item.is_file():
            if item.resolve() not in expected_files:
                if not dry_run:
                    item.unlink()
                orphans_removed += 1
                logging.debug("Pruned orphan file: %s", item)

    for dirpath in sorted(dst_dir.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if dirpath.is_dir():
            if not any(dirpath.iterdir()):
                if not dry_run:
                    dirpath.rmdir()
                logging.debug("Pruned empty dir: %s", dirpath)

    return orphans_removed


# ===========================================================================
# 7. PIPELINE ORCHESTRATION
# ===========================================================================


def main():
    args = parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    # 1. Critical Dependency Verification
    dependencies = [
        (SRC, "Source directory"),
        (DEFAULTS_YAML, "Pandoc defaults configuration"),
        (DEFAULT_TEMPLATE, "Content HTML template"),
        (LUA_FILTER, "Lua link translation filter"),
    ]
    for path, desc in dependencies:
        if not path.exists():
            logging.error("Configuration error: %s missing at %s", desc, path)
            sys.exit(1)

    # 2. Clean Execution Handling
    if args.clean:
        if DST.exists():
            logging.info("Flag --clean active: Purging %s", DST)
            if not args.dry_run:
                shutil.rmtree(DST)
        if MANIFEST_FILE.exists():
            logging.info("Flag --clean active: Removing manifest %s", MANIFEST_FILE)
            if not args.dry_run:
                MANIFEST_FILE.unlink()

    DST.mkdir(parents=True, exist_ok=True)

    # 3. Hash Manifest & Global Invalidation
    old_manifest = load_manifest(MANIFEST_FILE)
    new_manifest: dict[str, str] = {}

    current_global_hash = compute_global_dependencies_hash()
    new_manifest["__GLOBAL_DEPENDENCIES__"] = current_global_hash
    global_deps_changed = (
        old_manifest.get("__GLOBAL_DEPENDENCIES__") != current_global_hash
    )

    if global_deps_changed:
        logging.info(
            "Global dependencies/templates modified. Flagging all outputs for rebuild."
        )

    expected_outputs: set[Path] = set()
    compile_tasks: list[CompileTask] = []
    search_records: list[dict] = []

    # 4. Inventory, Security Scoping & Key Acquisition
    md_files = sorted(SRC.rglob("*.md"))
    has_secure_files = any("secure" in p.parts for p in md_files)

    passphrase = args.password
    if has_secure_files and not passphrase and not args.dry_run:
        if AESGCM is None:
            logging.error(
                "Cryptography module missing. Install via 'pip install cryptography'."
            )
            sys.exit(1)
        passphrase = getpass.getpass("Enter passphrase for /secure/ notes: ")
        if not passphrase:
            logging.error("Encryption passphrase cannot be empty.")
            sys.exit(1)

    # 5. Markdown Processing
    for idx, md in enumerate(md_files):
        rel = md.relative_to(SRC)
        manifest_key = f"content:{rel.as_posix()}"
        out = DST / rel.with_suffix(".html")
        expected_outputs.add(out.resolve())

        current_md_hash = compute_file_hash(md)
        new_manifest[manifest_key] = current_md_hash

        depth = len(rel.parent.parts) if rel.parent != Path(".") else 0
        relative_root = ("../" * depth) if depth > 0 else ""

        is_secure = "secure" in md.parts
        is_dirty = (
            not out.exists()
            or global_deps_changed
            or old_manifest.get(manifest_key) != current_md_hash
        )

        # Retain public search metadata for all documents, including secure ones
        meta = extract_metadata_from_markdown(md)
        clean_url = rel.with_suffix(".html").as_posix().lstrip("/")
        search_records.append(
            {
                "id": idx + 1,
                "title": meta["title"],
                "keywords": meta["keywords"],
                "date_edtf": meta["date_edtf"],
                "abstract": meta["abstract"],
                "url": clean_url,
            }
        )

        if is_dirty:
            compile_tasks.append(
                CompileTask(
                    md_path=md,
                    out_path=out,
                    template_path=DEFAULT_TEMPLATE,
                    relative_root=relative_root,
                    defaults_yaml=DEFAULTS_YAML,
                    lua_filter=LUA_FILTER,
                    is_secure=is_secure,
                    passphrase=passphrase,
                    dry_run=args.dry_run,
                    verbose=args.verbose,
                )
            )

    expected_outputs.add(SEARCH_INDEX_FILE.resolve())

    # 6. Inventory & Sync Assets (Explicitly exclude media inside secure directories)
    asset_sync_jobs: list[tuple[Path, Path]] = []

    # A. Content media assets (Leak prevention: skip copying any file under /secure/)
    for p in SRC.rglob("*"):
        if (
            p.is_file()
            and p.suffix.lower() != ".md"
            and not p.name.startswith(".")
            and "secure" not in p.parts
        ):
            target = DST / p.relative_to(SRC)
            expected_outputs.add(target.resolve())
            manifest_key = f"media:{p.relative_to(SRC).as_posix()}"
            h = compute_file_hash(p)
            new_manifest[manifest_key] = h
            if not target.exists() or old_manifest.get(manifest_key) != h:
                asset_sync_jobs.append((p, target))

    # B. Functional assets (build/assets -> dist/assets)
    assets_src = APP_DIR / "assets"
    if assets_src.exists():
        for p in assets_src.rglob("*"):
            if p.is_file() and not p.name.startswith("."):
                target = DST / "assets" / p.relative_to(assets_src)
                expected_outputs.add(target.resolve())
                manifest_key = (
                    f"functional_asset:{p.relative_to(assets_src).as_posix()}"
                )
                h = compute_file_hash(p)
                new_manifest[manifest_key] = h
                if not target.exists() or old_manifest.get(manifest_key) != h:
                    asset_sync_jobs.append((p, target))

    # C. Root assets (build/root -> dist)
    root_src = APP_DIR / "root"
    if root_src.exists():
        for p in root_src.rglob("*"):
            if p.is_file() and not p.name.startswith("."):
                target = DST / p.relative_to(root_src)
                expected_outputs.add(target.resolve())
                manifest_key = f"root_asset:{p.relative_to(root_src).as_posix()}"
                h = compute_file_hash(p)
                new_manifest[manifest_key] = h
                if not target.exists() or old_manifest.get(manifest_key) != h:
                    asset_sync_jobs.append((p, target))

    # 7. Execute Orphan Pruning
    orphans_pruned = prune_orphans(
        dst_dir=DST,
        expected_files=expected_outputs,
        dry_run=args.dry_run,
    )
    if orphans_pruned:
        logging.info("Pruned %d orphaned artifact(s).", orphans_pruned)

    # 8. Execute Asset Sync
    synced_assets = 0
    for src_file, target_file in asset_sync_jobs:
        if not args.dry_run:
            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, target_file)
        synced_assets += 1
    if synced_assets:
        logging.info("Synced %d modified/new asset(s).", synced_assets)

    # 9. Execute Concurrent Markdown Compilation
    total_md = len(md_files)
    to_compile = len(compile_tasks)
    failed = 0

    if to_compile > 0:
        logging.info(
            "Compiling %d of %d documents using %d workers...",
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
                        logging.error(
                            "Pandoc compilation error on %s:\n%s", md_path.name, err
                        )
                    elif args.verbose:
                        logging.info("Built: %s", md_path.name)
                except Exception as exc:
                    failed += 1
                    logging.error(
                        "Runtime exception compiling %s: %s", md_path.name, exc
                    )
    else:
        logging.info("All %d documents are verified current.", total_md)

    # 10. Update Search Index
    if (
        to_compile > 0 or orphans_pruned > 0 or not SEARCH_INDEX_FILE.exists()
    ) and failed == 0:
        write_minisearch_index(search_records, SEARCH_INDEX_FILE, dry_run=args.dry_run)

    # 11. Update Manifest Post-Build
    if failed == 0:
        save_manifest(MANIFEST_FILE, new_manifest, args.dry_run)
    else:
        logging.warning(
            "Build recorded failures. Manifest state will not be persisted."
        )

    if failed > 0:
        logging.error("Build completed with %d failure(s).", failed)
        sys.exit(1)

    logging.info(
        "Build complete. (%d compiled, %d assets synced, %d orphans pruned)",
        to_compile,
        synced_assets,
        orphans_pruned,
    )


if __name__ == "__main__":
    main()
