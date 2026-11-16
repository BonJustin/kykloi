#!/usr/bin/env python3
"""
system/launch.py - Autonomous Control Hub Daemon for Project Kykloi.
Features CLI argument parsing, defensive MIME registration, and IPC vault orchestration.
"""

import argparse
import http.server
import mimetypes

# ===========================================================================
# 1. PATH RESOLUTION & DEFENSIVE MIME REGISTRATION
# ===========================================================================
import os
import re
import socketserver
import subprocess
import sys
import threading
import urllib.parse
import webbrowser
from pathlib import Path

SYSTEM_DIR = Path(__file__).resolve().parent
ROOT_DIR = SYSTEM_DIR.parent
DIST_DIR = ROOT_DIR / "dist"
BUILD_SCRIPT = SYSTEM_DIR / "build" / "build_site.py"

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
        # Silence access logs to keep the interactive CLI uncluttered
        pass

    def do_HEAD(self):
        self._dispatch_get(send_body=False)

    def do_GET(self):
        self._dispatch_get(send_body=True)

    def _dispatch_get(self, send_body: bool):
        parsed = urllib.parse.urlsplit(self.path)
        clean_path = urllib.parse.unquote(parsed.path)

        if not DIST_DIR.exists() or not any(DIST_DIR.iterdir()):
            self.send_response(503)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            if send_body:
                self.wfile.write(b"Vault unbuilt. Run compilation in CLI.\n")
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
# 4. COMPILER INVOCATION & INTERACTIVE CLI
# ===========================================================================


def execute_build(clean: bool = False, passphrase: str | None = None) -> int:
    cmd = [sys.executable, str(BUILD_SCRIPT)]
    if clean:
        cmd.append("--clean")
    if passphrase:
        cmd.extend(["--password", passphrase])

    print("\n" + "-" * 60)
    print(f"[Compiler] Executing: {' '.join(cmd)}")
    print("-" * 60)

    res = subprocess.run(cmd, cwd=str(ROOT_DIR))
    print("-" * 60)
    return res.returncode


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
    return p.parse_args()


def interactive_menu(vault_url: str, initial_password: str | None):
    session_password = initial_password

    while True:
        vault_ready = DIST_DIR.exists() and any(DIST_DIR.iterdir())
        status_line = (
            f"Vault: Ready ({vault_url})" if vault_ready else "Vault: Not Compiled"
        )
        pw_status = "Set" if session_password else "Not Set"

        print("\n==================== KYKLOI CONTROL PLANE ====================")
        print(f"  Status:     {status_line}")
        print(f"  Passphrase: [{pw_status}]")
        print("==============================================================")
        print("  [1] Compile Site (Incremental)")
        print("  [2] Rebuild Site (Clean Purge)")
        print("  [3] Set / Update Secure Passphrase")
        print("  [4] Open Vault in Default Browser")
        print("  [0] Exit")
        print("==============================================================")

        try:
            choice = input("Select an option [0-4]: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n")
            break

        if choice == "1":
            execute_build(clean=False, passphrase=session_password)
        elif choice == "2":
            execute_build(clean=True, passphrase=session_password)
        elif choice == "3":
            import getpass

            try:
                pw = getpass.getpass(
                    "Enter passphrase for /secure/ notes (leave empty to clear): "
                )
                session_password = pw.strip() or None
                if session_password:
                    print("[Config] Passphrase stored in active session memory.")
                else:
                    print("[Config] Passphrase cleared.")
            except (KeyboardInterrupt, EOFError):
                print("\n[Config] Passphrase entry cancelled.")
        elif choice == "4":
            if not vault_ready:
                print("\n[!] Vault must be compiled before opening in browser.")
            else:
                print(f"\n[Browser] Opening {vault_url} ...")
                webbrowser.open(vault_url)
        elif choice == "0":
            break
        else:
            print("\n[!] Invalid selection.")


def main():
    args = parse_args()

    # Headless execution bypass
    if args.build:
        code = execute_build(clean=args.clean, passphrase=args.password)
        sys.exit(code)

    # Start background daemon
    try:
        server, port, vault_url = start_background_server(args.host, args.port)
    except Exception as err:
        sys.stderr.write(f"[FATAL] Server initialization failed: {err}\n")
        sys.exit(1)

    try:
        interactive_menu(vault_url, args.password)
    finally:
        print("\n[Kykloi] Shutting down local server and closing ports...")
        server.shutdown()
        server.server_close()
        print("[Kykloi] Shutdown complete.")


if __name__ == "__main__":
    main()
