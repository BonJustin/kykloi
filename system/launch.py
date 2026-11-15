#!/usr/bin/env python3
"""
system/launch.py - Autonomous Control Hub Daemon for Project Kykloi.
Features CLI argument parsing, defensive MIME registration, and IPC vault orchestration.
"""

import argparse
import http.server
import json
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
import time
import urllib.parse
import webbrowser
from pathlib import Path

SYSTEM_DIR = Path(__file__).resolve().parent
ROOT_DIR = SYSTEM_DIR.parent
ADMIN_DIR = SYSTEM_DIR / "admin"
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

BUILD_LOCK = threading.Lock()
RANGE_REGEX = re.compile(r"^bytes=(\d*)-(\d*)$")

# ===========================================================================
# 2. UNIFIED REQUEST HANDLER & IPC ENGINE
# ===========================================================================


class KykloiApplianceHandler(http.server.BaseHTTPRequestHandler):
    server_version = "KykloiAppliance/0.5"
    protocol_version = "HTTP/1.1"

    def guess_mime(self, filepath: str) -> str:
        mime, _ = mimetypes.guess_type(filepath)
        return mime or "application/octet-stream"

    # -----------------------------------------------------------------------
    # ROUTING DISPATCH
    # -----------------------------------------------------------------------
    def do_HEAD(self):
        self._dispatch_get(send_body=False)

    def do_GET(self):
        self._dispatch_get(send_body=True)

    def do_POST(self):
        clean_path = urllib.parse.urlsplit(self.path).path
        if clean_path == "/api/build":
            self._handle_build_ipc()
            return
        if clean_path == "/api/shutdown":
            self._handle_shutdown_ipc()
            return
        self.send_error(404, "Unknown API Endpoint")

    def _dispatch_get(self, send_body: bool):
        parsed = urllib.parse.urlsplit(self.path)
        clean_path = urllib.parse.unquote(parsed.path)

        # 1. Admin UI Namespace
        if clean_path == "/admin":
            self.send_response(302)
            self.send_header("Location", "/admin/")
            self.end_headers()
            return

        if clean_path.startswith("/admin/"):
            rel_admin = clean_path[len("/admin/") :]
            if rel_admin in ("", "index.html"):
                target = ADMIN_DIR / "admin.html"
            else:
                target = (ADMIN_DIR / rel_admin).resolve()

            try:
                target.relative_to(ADMIN_DIR.resolve())
            except ValueError:
                self.send_error(403, "Forbidden")
                return

            if not target.is_file():
                self.send_error(404, "Admin Asset Not Found")
                return

            self._serve_static_file(str(target), send_body)
            return

        # 2. Vault Dist Namespace
        if not DIST_DIR.exists() or not any(DIST_DIR.iterdir()):
            self.send_response(302)
            self.send_header("Location", "/admin/")
            self.end_headers()
            return

        target_file = self._translate_dist_path(clean_path)
        if target_file is None or not os.path.isfile(target_file):
            self.send_error(404, "File Not Found")
            return

        self._serve_static_file(target_file, send_body)

    # -----------------------------------------------------------------------
    # DIST FILE RESOLUTION & RFC 7233 RANGE STREAMING
    # -----------------------------------------------------------------------
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

    # -----------------------------------------------------------------------
    # COMPILATION IPC
    # -----------------------------------------------------------------------
    def _send_chunk(self, data: bytes):
        if not data:
            return
        chunk = f"{len(data):X}\r\n".encode("ascii") + data + b"\r\n"
        self.wfile.write(chunk)
        self.wfile.flush()

    def _handle_build_ipc(self):
        if not BUILD_LOCK.acquire(blocking=False):
            self.send_response(409)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            msg = b"Conflict: A build process is already active. Request rejected.\n"
            self.send_header("Content-Length", str(len(msg)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(msg)
            return

        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = (
                self.rfile.read(content_length).decode("utf-8")
                if content_length > 0
                else "{}"
            )

            try:
                params = json.loads(body)
            except json.JSONDecodeError:
                params = {}

            flags = []
            if params.get("clean"):
                flags.append("--clean")
            if params.get("verbose"):
                flags.append("--verbose")
            if params.get("password"):
                flags.extend(["--password", str(params["password"])])

            cmd = [sys.executable, "-u", str(BUILD_SCRIPT)] + flags

            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Transfer-Encoding", "chunked")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()

            self._send_chunk(
                f"[Kykloi IPC] Executing: {' '.join(cmd)}\n\n".encode("utf-8")
            )

            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                cwd=str(ROOT_DIR),
                text=True,
                bufsize=1,
            )

            try:
                for line in iter(proc.stdout.readline, ""):
                    self._send_chunk(line.encode("utf-8"))
                proc.stdout.close()
                code = proc.wait()
                self._send_chunk(
                    f"\n[Kykloi IPC] Build finished with exit code {code}.\n".encode(
                        "utf-8"
                    )
                )
            except (BrokenPipeError, ConnectionResetError):
                proc.kill()
            finally:
                self.wfile.write(b"0\r\n\r\n")
                self.wfile.flush()

        finally:
            BUILD_LOCK.release()

    def _handle_shutdown_ipc(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(b'{"status":"shutting_down"}')
        threading.Thread(target=self.server.shutdown, daemon=True).start()


# ===========================================================================
# 3. CLI & INITIALIZATION
# ===========================================================================


class ThreadedServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


def parse_args():
    p = argparse.ArgumentParser(description="Kykloi Appliance Daemon.")
    p.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Bind interface (default: 127.0.0.1)",
    )
    p.add_argument("--port", type=int, default=8000, help="Start port (default: 8000)")
    p.add_argument(
        "--browser",
        action="store_true",
        help="Launch browser upon startup (defaults to headless).",
    )
    return p.parse_args()


def main():
    args = parse_args()

    if not ADMIN_DIR.exists() or not (ADMIN_DIR / "admin.html").is_file():
        sys.stderr.write(f"[FATAL] Admin UI missing in {ADMIN_DIR}\n")
        sys.exit(1)

    server = None
    port = args.port
    max_attempts = 15

    for offset in range(max_attempts):
        candidate_port = port + offset
        try:
            server = ThreadedServer((args.host, candidate_port), KykloiApplianceHandler)
            port = candidate_port
            break
        except OSError as e:
            if e.errno in (98, 48, 10048):
                continue
            raise

    if server is None:
        sys.stderr.write("[FATAL] Could not bind to an open port.\n")
        sys.exit(1)

    admin_url = f"http://{args.host}:{port}/admin/"
    vault_url = f"http://{args.host}:{port}/"

    print("=" * 64)
    print("  Project Kykloi — Unified Appliance Daemon")
    print(f"  Admin:  {admin_url}")
    print(f"  Vault:  {vault_url}")
    print(f"  Mode:   {'Browser' if args.browser else 'Headless'}")
    print("=" * 64)

    if args.browser:
        threading.Thread(
            target=lambda: (time.sleep(0.3), webbrowser.open(admin_url)), daemon=True
        ).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[Kykloi] Shutting down appliance daemon...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
