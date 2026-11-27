#!/usr/bin/env python3
"""
system/launch.py - Autonomous Control Hub Daemon for Project Kykloi.
Features CLI argument parsing, defensive MIME registration, centralized telemetry,
cryptographic engine inspection, interactive vault normalization, and IPC server orchestration.
"""

import argparse
import http.server
import mimetypes
import os
import re
import socketserver
import subprocess
import sys
import threading
import urllib.parse
import webbrowser
from pathlib import Path

# ===========================================================================
# 1. PATH RESOLUTION, MODULE SETUP & DEFENSIVE MIME REGISTRATION
# ===========================================================================
SYSTEM_DIR = Path(__file__).resolve().parent
ROOT_DIR = SYSTEM_DIR.parent
CONTENT_DIR = ROOT_DIR / "content"
DIST_DIR = ROOT_DIR / "dist"
BUILD_SCRIPT = SYSTEM_DIR / "build" / "build.py"
NORM_DB_PATH = SYSTEM_DIR / "normalize" / "vault-index.db"

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(SYSTEM_DIR) not in sys.path:
    sys.path.insert(0, str(SYSTEM_DIR))
if str(SYSTEM_DIR / "build") not in sys.path:
    sys.path.insert(0, str(SYSTEM_DIR / "build"))

from logger import get_logger, setup_logging

from system.backup import (
    create_vault_backup,
    prune_previous_backups,
    run_interactive_backup,
)
from system.build import (
    ACTIVE_ENGINE_NAME,
    CONFIG_PATH,
    _resolve_active_crypto_engine,
    load_vault_config,
    save_vault_config,
)
from system.normalize.cli import (
    run_audit,
    run_normalization_pipeline,
    scaffold_new_document,
)
from system.normalize.db import VaultDB
from system.normalize.scanner import is_junk_path

mimetypes.init()
mimetypes.add_type("application/wasm", ".wasm")
mimetypes.add_type("font/woff2", ".woff2")
mimetypes.add_type("application/manifest+json", ".webmanifest")
mimetypes.add_type("application/octet-stream", ".enc")
mimetypes.add_type("image/svg+xml", ".svg")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("application/javascript", ".js")

RANGE_REGEX = re.compile(r"^bytes=(\d*)-(\d*)$")
IS_COMPILING: bool = False

# ===========================================================================
# 2. VAULT STATIC SERVER HANDLER
# ===========================================================================


class KykloiVaultHandler(http.server.BaseHTTPRequestHandler):
    server_version = "KykloiServer/0.7.0"
    protocol_version = "HTTP/1.1"
    dist_dir: Path = DIST_DIR

    def guess_mime(self, filepath: str) -> str:
        mime, _ = mimetypes.guess_type(filepath)
        return mime or "application/octet-stream"

    def log_message(self, format: str, *args):
        logger = get_logger("server")
        msg = format % args
        code_match = re.search(r'"\s+(\d{3})\s+', msg)
        status_code = int(code_match.group(1)) if code_match else 200

        if status_code >= 500:
            if IS_COMPILING:
                logger.debug("%s - %s", self.address_string(), msg)
            else:
                logger.error("%s - %s", self.address_string(), msg)
        elif status_code >= 400:
            logger.warning("%s - %s", self.address_string(), msg)
        else:
            logger.debug("%s - %s", self.address_string(), msg)

    def do_HEAD(self):
        self._dispatch_get(send_body=False)

    def do_GET(self):
        self._dispatch_get(send_body=True)

    def _dispatch_get(self, send_body: bool):
        parsed = urllib.parse.urlsplit(self.path)
        clean_path = urllib.parse.unquote(parsed.path)

        if IS_COMPILING:
            body = b"Vault compilation in progress. Please refresh in a moment.\n"
            self.send_response(503)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Retry-After", "1")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Connection", "close")
            self.end_headers()
            if send_body:
                self.wfile.write(body)
            return

        active_dist = getattr(self, "dist_dir", DIST_DIR)
        if not active_dist.exists() or not (active_dist / "index.html").is_file():
            body = b"Vault unbuilt. Run compilation in CLI.\n"
            self.send_response(503)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Connection", "close")
            self.end_headers()
            if send_body:
                self.wfile.write(body)
            return

        target_file = self._translate_dist_path(clean_path)
        if target_file is None or not os.path.isfile(target_file):
            self.send_error(404, "File Not Found")
            return

        self._serve_static_file(target_file, send_body)

    def _translate_dist_path(self, clean_path: str) -> str | None:
        active_dist = getattr(self, "dist_dir", DIST_DIR).resolve()
        stripped = clean_path.lstrip("/")
        target = (active_dist / stripped).resolve()

        try:
            target.relative_to(active_dist)
        except ValueError:
            return None

        if target.is_dir():
            index_candidate = target / "index.html"
            if index_candidate.is_file():
                return str(index_candidate)

        return str(target) if target.exists() else None

    def _serve_static_file(self, filepath: str, send_body: bool):
        try:
            file_size = os.path.getsize(filepath)
        except OSError:
            self.send_error(404, "File Inaccessible")
            return

        mime_type = self.guess_mime(filepath)
        range_header = self.headers.get("Range")

        if not range_header:
            self.send_response(200)
            self.send_header("Content-Type", mime_type)
            self.send_header("Content-Length", str(file_size))
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()

            if send_body:
                self._stream_slice(filepath, start=0, length=file_size)
            return

        match = RANGE_REGEX.match(range_header.strip())
        if not match:
            self._send_416(file_size)
            return

        raw_start, raw_end = match.groups()
        if raw_start and raw_end:
            start = int(raw_start)
            end = int(raw_end)
        elif raw_start:
            start = int(raw_start)
            end = file_size - 1
        elif raw_end:
            suffix_len = int(raw_end)
            start = max(0, file_size - suffix_len)
            end = file_size - 1
        else:
            self._send_416(file_size)
            return

        if start > end or start >= file_size or start < 0:
            self._send_416(file_size)
            return

        end = min(end, file_size - 1)
        content_length = (end - start) + 1

        self.send_response(206)
        self.send_header("Content-Type", mime_type)
        self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
        self.send_header("Content-Length", str(content_length))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()

        if send_body:
            self._stream_slice(filepath, start=start, length=content_length)

    def _send_416(self, file_size: int):
        self.send_response(416)
        self.send_header("Content-Range", f"bytes */{file_size}")
        self.send_header("Content-Length", "0")
        self.send_header("Connection", "close")
        self.end_headers()

    def _stream_slice(self, filepath: str, start: int, length: int):
        chunk_size = 65536
        remaining = length
        try:
            with open(filepath, "rb") as f:
                f.seek(start)
                while remaining > 0:
                    read_len = min(chunk_size, remaining)
                    data = f.read(read_len)
                    if not data:
                        break
                    self.wfile.write(data)
                    remaining -= len(data)
        except (BrokenPipeError, ConnectionResetError):
            pass


# ===========================================================================
# 3. BACKGROUND SERVER ORCHESTRATION
# ===========================================================================


class ThreadedServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


def start_background_server(
    host: str, start_port: int
) -> tuple[ThreadedServer, int, str]:
    max_attempts = 15
    for offset in range(max_attempts):
        candidate_port = start_port + offset
        try:
            server = ThreadedServer((host, candidate_port), KykloiVaultHandler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            url = f"http://{host}:{candidate_port}/"
            return server, candidate_port, url
        except OSError as e:
            if e.errno in (98, 48, 10048):
                continue
            raise
    raise RuntimeError(
        f"Unable to bind to an open port between {start_port} and {start_port + max_attempts - 1}"
    )


# ===========================================================================
# 4. COMPILER & NORMALIZER INVOCATION
# ===========================================================================


def vault_has_secure_content() -> bool:
    if not CONTENT_DIR.exists():
        return False
    for path in CONTENT_DIR.rglob("*"):
        if (
            path.is_file()
            and not is_junk_path(path, CONTENT_DIR)
            and "secure" in path.relative_to(CONTENT_DIR).parts
        ):
            return True
    return False


def ensure_build_prerequisites(session_password: str | None) -> tuple[bool, str | None]:
    """
    Verifies that ledger normalization and security credentials are satisfied before compilation.
    Returns (can_proceed, effective_passphrase).
    """
    logger = get_logger("launcher")

    # 1. Run audit recipe first
    code, norm_plan, broken_links = run_audit(CONTENT_DIR, NORM_DB_PATH)

    # 2. If un-normalized filenames exist, prompt user to normalize them
    if norm_plan.has_changes:
        logger.warning("Un-normalized filenames detected.")
        try:
            ans = input("Normalize filenames on disk now? [Y/n]: ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print()
            return False, session_password

        if ans in ("", "y", "yes"):
            norm_code = run_normalization_pipeline(
                CONTENT_DIR, NORM_DB_PATH, auto_apply=True
            )
            if norm_code != 0:
                logger.error("Normalization failed. Build halted.")
                return False, session_password
        else:
            logger.error(
                "Compilation halted: Un-normalized filenames must be reconciled."
            )
            return False, session_password

    # 3. If broken links exist, notify and prompt user
    if broken_links:
        logger.warning("Vault contains %d broken reference(s).", len(broken_links))
        try:
            ans = (
                input("Proceed with site compilation despite broken links? [Y/n]: ")
                .strip()
                .lower()
            )
        except (KeyboardInterrupt, EOFError):
            print()
            return False, session_password

        if ans not in ("", "y", "yes"):
            logger.info("Compilation cancelled to allow link correction.")
            return False, session_password

    # 4. Secure passphrase acquisition
    effective_pw = session_password
    if vault_has_secure_content() and not effective_pw:
        import getpass

        try:
            pw = getpass.getpass("Enter passphrase for /secure/ notes: ")
            effective_pw = pw.strip() or None
            if not effective_pw:
                logger.error("Passphrase required to compile secure vault documents.")
                return False, None
        except (KeyboardInterrupt, EOFError):
            print()
            logger.warning("Passphrase entry cancelled.")
            return False, session_password

    return True, effective_pw


def execute_build(
    clean: bool = False,
    passphrase: str | None = None,
    log_file: str | None = None,
) -> int:
    global IS_COMPILING
    logger = get_logger("launcher")
    cmd = [sys.executable, str(BUILD_SCRIPT)]
    if clean:
        cmd.append("--clean")
    if log_file:
        cmd.extend(["--log-file", log_file])

    env = os.environ.copy()
    if passphrase:
        env["KYKLOI_ENCRYPT_KEY"] = passphrase

    logger.info("Executing build: %s", " ".join(cmd))

    IS_COMPILING = True
    try:
        res = subprocess.run(cmd, cwd=str(ROOT_DIR), env=env)
        if res.returncode == 0:
            logger.info("Compilation process exited normally (code 0).")
        else:
            logger.error(
                "Compilation process failed with exit code %d.", res.returncode
            )
        return res.returncode
    except KeyboardInterrupt:
        logger.warning("\nBuild cancelled by user.")
        return 130
    finally:
        IS_COMPILING = False


def get_ledger_status_tag() -> str:
    if not NORM_DB_PATH.exists():
        return "Uninitialized"
    try:
        with VaultDB(NORM_DB_PATH) as db:
            files = db.get_all_files().values()
            docs = sum(1 for f in files if not f.is_media)
            media = sum(1 for f in files if f.is_media)
            return f"Indexed ({docs} notes, {media} assets)"
    except Exception:
        return "Degraded"


def print_crypto_diagnostics():
    engine_name, _ = _resolve_active_crypto_engine()
    is_pure_python = "Pure-Python" in engine_name

    print("\n================== KYKLOI CRYPTOGRAPHIC STATUS ==================")
    print(f"  Current Engine:     {engine_name}")
    print(
        f"  Execution Mode:     {'BASELINE FALLBACK (Unaccelerated)' if is_pure_python else 'HARDWARE ACCELERATED'}"
    )
    print(f"  Active Interpreter: {sys.executable}")
    print("=================================================================")

    if is_pure_python:
        print("\n[!] Pure-Python fallback is active. Build operations on large secure")
        print("    media files will experience reduced throughput (~1 MB/s).\n")
    else:
        print("\n[+] System is fully optimized. Cryptographic operations will use")
        print("    native C-ABI / hardware intrinsics (AES-NI / NEON).\n")


def parse_args():
    p = argparse.ArgumentParser(description="Kykloi Vault Engine & Local Appliance.")
    p.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Bind interface (default: 127.0.0.1)",
    )
    p.add_argument("--port", type=int, default=8000, help="Base port (default: 8000)")
    p.add_argument("--build", action="store_true", help="Compile and exit immediately.")
    p.add_argument(
        "--clean",
        action="store_true",
        help="Perform clean rebuild when combined with --build.",
    )
    p.add_argument(
        "--password",
        type=str,
        default=os.environ.get("KYKLOI_ENCRYPT_KEY"),
        help="Passphrase for /secure/ notes.",
    )
    p.add_argument(
        "--audit",
        action="store_true",
        help="Run vault health check and diagnostic link report.",
    )
    p.add_argument(
        "--normalize",
        action="store_true",
        help="Interactively normalize filenames on disk.",
    )
    p.add_argument(
        "--auto-normalize",
        action="store_true",
        help="Normalize filenames automatically without prompting.",
    )
    p.add_argument(
        "--new", action="store_true", help="Interactively scaffold a new archival note."
    )
    p.add_argument(
        "--log-file",
        type=str,
        default=None,
        help="Path to persistent log file on disk.",
    )
    p.add_argument(
        "--verbose",
        action="store_true",
        help="Enable granular debug telemetry in console output.",
    )
    p.add_argument(
        "--crypto-info",
        action="store_true",
        help="Inspect active cryptographic acceleration engine and exit.",
    )
    p.add_argument("--test", action="store_true", help="Execute automated test suite.")
    p.add_argument(
        "--clean-test",
        action="store_true",
        help="Execute test suite and clean up workspace.",
    )
    p.add_argument(
        "--purge-cache",
        action="store_true",
        help="Purge temporary runtime binaries and reset workspace.",
    )
    p.add_argument(
        "--backup",
        action="store_true",
        help="Create a timestamped zip archive backup of content/.",
    )
    p.add_argument(
        "--backup-dest",
        type=str,
        default=None,
        help="Destination directory for backup archive (default: backups/).",
    )
    p.add_argument(
        "--backup-name",
        type=str,
        default=None,
        help="Optional explicit archive filename (default: timestamped).",
    )
    p.add_argument(
        "--prune-old",
        action="store_true",
        help="Delete previous backups from destination after creating new archive.",
    )
    p.add_argument(
        "--set-title",
        type=str,
        default=None,
        help="Update vault title in system/config.json.",
    )
    p.add_argument(
        "--set-brand",
        type=str,
        default=None,
        help="Update vault brand / monogram in system/config.json.",
    )
    p.add_argument(
        "--set-title-prefix",
        type=str,
        default=None,
        help="Update browser note title prefix in system/config.json.",
    )
    return p.parse_args()


def configure_identity_interactive():
    config = load_vault_config()
    print("\n================== CONFIGURE VAULT IDENTITY ==================")
    print("  Press Enter to retain the current value in brackets.")
    print("==============================================================")

    cur_title = config.get("vault_title", "Κύκλοι")
    try:
        new_title = input(f"  Vault Title [{cur_title}]: ").strip()
    except (KeyboardInterrupt, EOFError):
        print()
        return

    cur_brand = config.get("brand_text", "JmB²")
    try:
        new_brand = input(f"  Brand / Header Monogram [{cur_brand}]: ").strip()
    except (KeyboardInterrupt, EOFError):
        print()
        return

    cur_prefix = config.get("title_prefix", "")
    prefix_display = cur_prefix if cur_prefix else "(none)"
    try:
        new_prefix = input(f"  Note Tab Prefix [{prefix_display}]: ").strip()
    except (KeyboardInterrupt, EOFError):
        print()
        return

    final_title = new_title if new_title else cur_title
    final_brand = new_brand if new_brand else cur_brand
    final_prefix = new_prefix if new_prefix else cur_prefix

    save_vault_config(final_title, final_brand, final_prefix)
    print(f"\n[+] Saved identity configuration to {CONFIG_PATH.name}.")
    print("    Run [1] Compile Site or [2] Rebuild Site to apply changes.\n")


def interactive_menu(
    vault_url: str,
    initial_password: str | None,
    log_file: str | None = None,
):
    session_password = initial_password
    logger = get_logger("menu")

    while True:
        vault_ready = (DIST_DIR / "index.html").is_file()
        status_line = (
            f"Vault: Ready ({vault_url})" if vault_ready else "Vault: Not Compiled"
        )
        pw_status = "Set" if session_password else "Not Set"

        is_fallback = "Pure-Python" in ACTIVE_ENGINE_NAME
        crypto_tag = (
            f"{ACTIVE_ENGINE_NAME} [SLOW]" if is_fallback else ACTIVE_ENGINE_NAME
        )
        ledger_tag = get_ledger_status_tag()

        print("\n==================== KYKLOI CONTROL PLANE ====================")
        print(f"  Status:     {status_line}")
        print(f"  Passphrase: [{pw_status}]")
        print(f"  Ledger:     [{ledger_tag}]")
        print(f"  Crypto:     [{crypto_tag}]")
        print("==============================================================")
        print("  [1] Compile Site (Incremental)")
        print("  [2] Rebuild Site (Clean Purge)")
        print("  [3] Audit Vault Health (Dead Links & Filename Check)")
        print("  [4] Normalize Vault Filenames (Renames On Disk)")
        print("  [5] Scaffold New Archival Note")
        print("  [6] Set / Update Secure Passphrase")
        print("  [7] Open Vault in Default Browser")
        print("  [8] Cryptographic Acceleration Diagnostics")
        print("  [9] Create Archival Vault Backup (.zip)")
        print(" [10] Configure Vault Identity (Title & Brand)")
        print("  [0] Exit")
        print("==============================================================")

        try:
            choice = input("Select an option [0-10]: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n")
            break

        if choice == "1":
            ok, session_password = ensure_build_prerequisites(session_password)
            if ok:
                execute_build(
                    clean=False, passphrase=session_password, log_file=log_file
                )
        elif choice == "2":
            ok, session_password = ensure_build_prerequisites(session_password)
            if ok:
                execute_build(
                    clean=True, passphrase=session_password, log_file=log_file
                )
        elif choice == "3":
            logger.info("Executing comprehensive vault audit...")
            try:
                run_audit(CONTENT_DIR, NORM_DB_PATH)
            except KeyboardInterrupt:
                logger.warning("\nAudit interrupted by user.")
        elif choice == "4":
            logger.info("Initiating filename normalization...")
            try:
                run_normalization_pipeline(CONTENT_DIR, NORM_DB_PATH, auto_apply=False)
            except KeyboardInterrupt:
                logger.warning("\nNormalization interrupted by user.")
        elif choice == "5":
            try:
                scaffold_new_document(CONTENT_DIR)
            except KeyboardInterrupt:
                logger.warning("\nNote scaffolding cancelled.")
        elif choice == "6":
            import getpass

            try:
                pw = getpass.getpass(
                    "Enter passphrase for /secure/ notes (leave empty to clear): "
                )
                session_password = pw.strip() or None
                if session_password:
                    logger.info("Passphrase stored in active session memory.")
                else:
                    logger.info("Passphrase cleared.")
            except (KeyboardInterrupt, EOFError):
                print()
                logger.warning("Passphrase input aborted by user.")
        elif choice == "7":
            if not vault_ready:
                logger.warning("Vault is not compiled.")
                try:
                    ans = input("Compile vault now? [Y/n]: ").strip().lower()
                except (KeyboardInterrupt, EOFError):
                    ans = "n"

                if ans in ("", "y", "yes"):
                    ok, session_password = ensure_build_prerequisites(session_password)
                    if (
                        ok
                        and execute_build(
                            clean=False, passphrase=session_password, log_file=log_file
                        )
                        == 0
                    ):
                        logger.info("Opening browser target: %s", vault_url)
                        webbrowser.open(vault_url)
            else:
                logger.info("Opening browser target: %s", vault_url)
                webbrowser.open(vault_url)
        elif choice == "8":
            print_crypto_diagnostics()
        elif choice == "9":
            logger.info("Initiating archival backup workflow...")
            try:
                run_interactive_backup(
                    content_dir=CONTENT_DIR,
                    default_backup_dir=ROOT_DIR / "backups",
                )
            except KeyboardInterrupt:
                logger.warning("\nBackup workflow interrupted by user.")
        elif choice == "10":
            configure_identity_interactive()
        elif choice == "0":
            break
        else:
            logger.warning("Unrecognized menu option: %s", choice)


def main():
    args = parse_args()

    if (
        args.set_title is not None
        or args.set_brand is not None
        or args.set_title_prefix is not None
    ):
        cfg = load_vault_config()
        new_title = (
            args.set_title
            if args.set_title is not None
            else cfg.get("vault_title", "Κύκλοι")
        )
        new_brand = (
            args.set_brand
            if args.set_brand is not None
            else cfg.get("brand_text", "JmB²")
        )
        new_prefix = (
            args.set_title_prefix
            if args.set_title_prefix is not None
            else cfg.get("title_prefix", "")
        )
        save_vault_config(new_title, new_brand, new_prefix)
        print(
            f"[+] Updated identity configuration: title='{new_title}', brand='{new_brand}', prefix='{new_prefix}'"
        )
        if not args.build:
            sys.exit(0)

    if args.crypto_info:
        print_crypto_diagnostics()
        sys.exit(0)

    if args.backup:
        if args.backup_dest:
            dest = Path(os.path.expanduser(args.backup_dest)).resolve()
            print(f"Creating automated backup in {dest}...")
            try:
                zip_p, sha_p, count, total_b = create_vault_backup(
                    content_dir=CONTENT_DIR,
                    output_dir=dest,
                    archive_name=args.backup_name,
                )
                print(f"[+] Archive created: {zip_p} ({count} files)")
                print(f"[+] SHA-256 sidecar: {sha_p}")
                if args.prune_old:
                    pruned = prune_previous_backups(dest, exclude_paths={zip_p, sha_p})
                    print(f"[+] Pruned {len(pruned)} previous backup artifact(s).")
                sys.exit(0)
            except Exception as err:
                print(f"[-] Automated backup failed: {err}", file=sys.stderr)
                sys.exit(1)
        else:
            ok = run_interactive_backup(
                content_dir=CONTENT_DIR,
                default_backup_dir=ROOT_DIR / "backups",
            )
            sys.exit(0 if ok else 1)

    if args.purge_cache:
        from test_runner import purge_ephemeral_runtimes

        purged = purge_ephemeral_runtimes()
        for p in purged:
            print(f"Purged: {p}")
        print("Ephemeral caches and vault state cleared.")
        sys.exit(0)

    if args.test or args.clean_test:
        from test_runner import execute_field_test_suite

        code = execute_field_test_suite(auto_cleanup=args.clean_test)
        sys.exit(code)

    if args.new:
        scaffold_new_document(CONTENT_DIR)
        sys.exit(0)

    if args.audit:
        code, _, _ = run_audit(CONTENT_DIR, NORM_DB_PATH)
        sys.exit(code)

    if args.normalize or args.auto_normalize:
        code = run_normalization_pipeline(
            CONTENT_DIR,
            NORM_DB_PATH,
            auto_apply=args.auto_normalize,
        )
        sys.exit(code)

    log_file_path = Path(args.log_file).resolve() if args.log_file else None
    logger = setup_logging(
        subsystem="launcher",
        verbose=args.verbose,
        log_file=log_file_path,
        enable_console=True,
    )

    if args.build:
        ok, effective_pw = ensure_build_prerequisites(args.password)
        if not ok:
            sys.exit(1)
        code = execute_build(
            clean=args.clean,
            passphrase=effective_pw,
            log_file=args.log_file,
        )
        sys.exit(code)

    try:
        server, port, vault_url = start_background_server(args.host, args.port)
        logger.info("Vault daemon online at %s (bound to port %d)", vault_url, port)
    except Exception as err:
        logger.critical("Local static server failed to bind: %s", err)
        sys.exit(1)

    try:
        interactive_menu(vault_url, args.password, log_file=args.log_file)
    finally:
        logger.info("Shutting down vault server daemon...")
        server.shutdown()
        server.server_close()
        logger.info("Daemon cleanly terminated.")


if __name__ == "__main__":
    main()
