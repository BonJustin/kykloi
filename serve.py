#!/usr/bin/env python3
"""
serve.py - Zero-Dependency Archival HTTP Daemon with RFC 7233 Range Support.
Part of Project Kykloi (v0.5.0).
"""

import argparse
import http.server
import mimetypes
import os
import re
import socket
import socketserver
import sys
import threading
import time
import urllib.parse
import webbrowser
from pathlib import Path

# ===========================================================================
# 1. PATH RESOLUTION & DEFENSIVE MIME REGISTRATION
# ===========================================================================

ROOT_DIR = Path(__file__).resolve().parent
DIST_DIR = ROOT_DIR / "dist"

# Hardcode MIME overrides to protect against stripped/minimal host OS registries
mimetypes.init()
mimetypes.add_type("application/wasm", ".wasm")
mimetypes.add_type("font/woff2", ".woff2")
mimetypes.add_type("application/manifest+json", ".webmanifest")
mimetypes.add_type("application/octet-stream", ".enc")
mimetypes.add_type("image/svg+xml", ".svg")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("application/javascript", ".js")


# ===========================================================================
# 2. RFC 7233 RANGE-CAPABLE REQUEST HANDLER
# ===========================================================================

RANGE_REGEX = re.compile(r"^bytes=(\d*)-(\d*)$")


class KykloiHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    """
    HTTP handler serving strictly from the dist/ directory.
    Implements RFC 7233 partial content (206) for media streaming/scrubbing
    and enforces jailbreak checks against directory traversal.
    """

    server_version = "KykloiDaemon/0.5"

    def translate_path(self, path: str) -> str | None:
        """Translate a URL path into an absolute file system path inside dist/."""
        parsed_url = urllib.parse.urlsplit(path)
        clean_path = urllib.parse.unquote(parsed_url.path).lstrip("/")

        target = (DIST_DIR / clean_path).resolve()

        # Jail enforcement: Ensure resolved path lives within DIST_DIR
        try:
            target.relative_to(DIST_DIR.resolve())
        except ValueError:
            return None

        if target.is_dir():
            index_candidate = target / "index.html"
            if index_candidate.is_file():
                return str(index_candidate)

        return str(target) if target.exists() else None

    def guess_mime(self, filepath: str) -> str:
        mime, _ = mimetypes.guess_type(filepath)
        return mime or "application/octet-stream"

    def do_HEAD(self):
        self._handle_request(send_body=False)

    def do_GET(self):
        self._handle_request(send_body=True)

    def _handle_request(self, send_body: bool):
        filepath = self.translate_path(self.path)

        if filepath is None or not os.path.isfile(filepath):
            self.send_error(404, "File Not Found")
            return

        try:
            file_size = os.path.getsize(filepath)
        except OSError:
            self.send_error(404, "File Inaccessible")
            return

        mime_type = self.guess_mime(filepath)
        range_header = self.headers.get("Range")

        # -------------------------------------------------------------
        # CASE 1: Standard Full File Request (HTTP 200 OK)
        # -------------------------------------------------------------
        if not range_header:
            self.send_response(200)
            self.send_header("Content-Type", mime_type)
            self.send_header("Content-Length", str(file_size))
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()

            if send_body:
                self._stream_file_slice(filepath, start=0, length=file_size)
            return

        # -------------------------------------------------------------
        # CASE 2: RFC 7233 Range Request (HTTP 206 Partial Content)
        # -------------------------------------------------------------
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

        # Validate range boundary bounds
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
            self._stream_file_slice(filepath, start=start, length=content_length)

    def _send_416(self, file_size: int):
        self.send_response(416)
        self.send_header("Content-Range", f"bytes */{file_size}")
        self.end_headers()

    def _stream_file_slice(self, filepath: str, start: int, length: int):
        """Stream chunks of 64 KB from disk to socket without bloating RAM."""
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
            # Client closed tab or cancelled download
            pass


# ===========================================================================
# 3. SERVER ORCHESTRATION & CLI
# ===========================================================================


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


def parse_args():
    p = argparse.ArgumentParser(
        description="Zero-Dependency Local HTTP Daemon for Project Kykloi."
    )
    p.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Network interface to bind (default: 127.0.0.1; use 0.0.0.0 for LAN).",
    )
    p.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Preferred port number (default: 8000).",
    )
    p.add_argument(
        "--browser",
        action="store_true",
        help="Automatically launch system browser upon startup.",
    )
    return p.parse_args()


def open_browser_delayed(url: str):
    time.sleep(0.4)
    try:
        webbrowser.open(url)
    except Exception:
        pass


def main():
    args = parse_args()

    if not DIST_DIR.exists() or not any(DIST_DIR.iterdir()):
        print("\n[ERROR] Compiled artifacts directory not found or empty:")
        print(f"        {DIST_DIR}")
        print("\nPlease build the static site first using:")
        print("  python3 build/build_site.py\n")
        sys.exit(1)

    port = args.port
    server = None
    max_attempts = 15

    for offset in range(max_attempts):
        candidate_port = port + offset
        try:
            server = ThreadedTCPServer(
                (args.host, candidate_port), KykloiHTTPRequestHandler
            )
            port = candidate_port
            break
        except OSError as e:
            if e.errno in (98, 48, 10048):  # EADDRINUSE across Linux, macOS, Windows
                continue
            raise

    if server is None:
        print(
            f"[FATAL] Could not bind to an open port between {port} and {port + max_attempts}."
        )
        sys.exit(1)

    url = f"http://{args.host}:{port}/"
    print("=" * 64)
    print("  Project Kykloi — Archival HTTP Daemon")
    print(f"  Root:   {DIST_DIR}")
    print(f"  URL:    {url}")
    print("  Status: Listening (Press Ctrl+C to stop)")
    print("=" * 64)

    if args.browser:
        threading.Thread(target=open_browser_delayed, args=(url,), daemon=True).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[Kykloi] Shutting down daemon gracefully...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
