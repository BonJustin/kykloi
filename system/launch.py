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
BUILD_SCRIPT = SYSTEM_DIR / "build" / "build_site.py"
NORM_DB_PATH = SYSTEM_DIR / "normalize" / "vault_index.db"

# Ensure the root project repository and internal subsystems are on sys.path
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(SYSTEM_DIR) not in sys.path:
    sys.path.insert(0, str(SYSTEM_DIR))
if str(SYSTEM_DIR / "build") not in sys.path:
    sys.path.insert(0, str(SYSTEM_DIR / "build"))

from build_site import ACTIVE_ENGINE_NAME, _resolve_active_crypto_engine
from logger import get_logger, setup_logging

from system.normalize.cli import run_normalization_pipeline
from system.normalize.db import VaultDB

mimetypes.init()
mimetypes.add_type("application/wasm", ".wasm")
mimetypes.add_type("font/woff2", ".woff2")
mimetypes.add_type("application/manifest+json", ".webmanifest")
mimetypes.add_type("application/octet-stream", ".enc")
mimetypes.add_type("image/svg+xml", ".svg")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("application/javascript", ".js")

RANGE_REGEX = re.compile(r"^bytes=(\d*)-(\d*)$")

# ===========================================================================
# 2. VAULT STATIC SERVER HANDLER
# ===========================================================================


class KykloiVaultHandler(http.server.BaseHTTPRequestHandler):
    server_version = "KykloiServer/0.6"
    protocol_version = "HTTP/1.1"

    def guess_mime(self, filepath: str) -> str:
        mime, _ = mimetypes.guess_type(filepath)
        return mime or "application/octet-stream"

    def log_message(self, format: str, *args):
        logger = get_logger("server")
        msg = format % args
        code_match = re.search(r'"\s+(\d{3})\s+', msg)
        status_code = int(code_match.group(1)) if code_match else 200

        if status_code >= 500:
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

        if not DIST_DIR.exists() or not any(DIST_DIR.iterdir()):
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
        stripped = clean_path.lstrip("/")
        target = (DIST_DIR / stripped).resolve()

        try:
            target.relative_to(DIST_DIR.resolve())
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

        # Full Request (200 OK)
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

        # RFC 7233 Range Request (206 Partial Content)
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


def execute_build(
    clean: bool = False,
    passphrase: str | None = None,
    log_file: str | None = None,
) -> int:
    logger = get_logger("launcher")
    cmd = [sys.executable, str(BUILD_SCRIPT)]
    if clean:
        cmd.append("--clean")
    if passphrase:
        cmd.extend(["--password", passphrase])
    if log_file:
        cmd.extend(["--log-file", log_file])

    masked_cmd = [
        "********" if i > 0 and cmd[i - 1] == "--password" else arg
        for i, arg in enumerate(cmd)
    ]
    logger.info("Executing build: %s", " ".join(masked_cmd))

    res = subprocess.run(cmd, cwd=str(ROOT_DIR))
    if res.returncode == 0:
        logger.info("Compilation process exited normally (code 0).")
    else:
        logger.error("Compilation process failed with exit code %d.", res.returncode)
    return res.returncode


def get_ledger_status_tag() -> str:
    """Returns a short formatted string detailing the state of vault_index.db."""
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
        print("    To enable hardware acceleration:")
        print(
            "    1. Ensure a standard host Python (>=3.10) is installed on your path."
        )
        print(
            "    2. Install the optional compiled primitive package in that environment:"
        )
        print("         pip install cryptography")
        print("       or:")
        print("         pip install pycryptodome\n")
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
        "--normalize",
        action="store_true",
        help="Run interactive content normalization and exit.",
    )
    p.add_argument(
        "--auto-normalize",
        action="store_true",
        help="Run normalization automatically without confirmation prompts.",
    )
    p.add_argument(
        "--check-normalize",
        action="store_true",
        help="Audit vault: returns 0 if clean, 1 if anomalies/mutations are detected.",
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
    return p.parse_args()


def interactive_menu(
    vault_url: str,
    initial_password: str | None,
    log_file: str | None = None,
):
    session_password = initial_password
    logger = get_logger("menu")

    while True:
        vault_ready = DIST_DIR.exists() and any(DIST_DIR.iterdir())
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
        print("  [3] Normalize Vault (Reconcile Links & Filenames)")
        print("  [4] Audit Vault Health (Check & Collision Audit)")
        print("  [5] Set / Update Secure Passphrase")
        print("  [6] Open Vault in Default Browser")
        print("  [7] Cryptographic Acceleration Diagnostics")
        print("  [0] Exit")
        print("==============================================================")

        try:
            choice = input("Select an option [0-7]: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n")
            break

        if choice == "1":
            execute_build(clean=False, passphrase=session_password, log_file=log_file)
        elif choice == "2":
            execute_build(clean=True, passphrase=session_password, log_file=log_file)
        elif choice == "3":
            logger.info("Initiating vault normalization pipeline...")
            run_normalization_pipeline(
                content_root=CONTENT_DIR,
                db_path=NORM_DB_PATH,
                dry_run=False,
                auto_apply=False,
                check_only=False,
            )
        elif choice == "4":
            logger.info("Auditing vault structure and links...")
            run_normalization_pipeline(
                content_root=CONTENT_DIR,
                db_path=NORM_DB_PATH,
                dry_run=True,
                auto_apply=False,
                check_only=True,
            )
        elif choice == "5":
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
        elif choice == "6":
            if not vault_ready:
                logger.warning("Vault must be compiled before opening in browser.")
            else:
                logger.info("Opening browser target: %s", vault_url)
                webbrowser.open(vault_url)
        elif choice == "7":
            print_crypto_diagnostics()
        elif choice == "0":
            break
        else:
            logger.warning("Unrecognized menu option: %s", choice)


def main():
    args = parse_args()

    if args.crypto_info:
        print_crypto_diagnostics()
        sys.exit(0)

    log_file_path = Path(args.log_file).resolve() if args.log_file else None
    logger = setup_logging(
        subsystem="launcher",
        verbose=args.verbose,
        log_file=log_file_path,
        enable_console=True,
    )

    # CLI direct execution routes
    if args.normalize or args.auto_normalize or args.check_normalize:
        code = run_normalization_pipeline(
            content_root=CONTENT_DIR,
            db_path=NORM_DB_PATH,
            dry_run=False,
            auto_apply=args.auto_normalize,
            check_only=args.check_normalize,
        )
        sys.exit(code)

    if args.build:
        code = execute_build(
            clean=args.clean,
            passphrase=args.password,
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
