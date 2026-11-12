#!/usr/bin/env python3
"""
launch.py - Autonomous Control Hub Daemon for Project Kykloi.
Serves exclusively from admin/ and provides streaming IPC for build tasks.
"""

import http.server
import json
import socketserver
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path

HOST = "127.0.0.1"
START_PORT = 8000
MAX_PORT_ATTEMPTS = 15

ROOT_DIR = Path(__file__).resolve().parent
ADMIN_DIR = ROOT_DIR / "admin"
BUILD_SCRIPT = ROOT_DIR / "build" / "build_site.py"


class ControlHubHandler(http.server.SimpleHTTPRequestHandler):
    """
    Standard static server rooted in admin/ with dynamic IPC hooks.
    All GET/HEAD requests are natively handled by SimpleHTTPRequestHandler.
    """

    protocol_version = "HTTP/1.1"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ADMIN_DIR), **kwargs)

    def translate_path(self, path: str) -> str:
        """Route root requests to admin.html if index.html does not exist."""
        clean_path = path.split("?", 1)[0].split("#", 1)[0]
        if clean_path in ("/", "/index.html"):
            admin_target = ADMIN_DIR / "admin.html"
            if admin_target.is_file():
                return str(admin_target)
        return super().translate_path(path)

    def do_POST(self):
        if self.path == "/api/build":
            self._handle_build_ipc()
            return
        self.send_error(404, "Unknown API Endpoint")

    def _send_chunk(self, data: bytes):
        """Transmits a standard HTTP/1.1 chunk."""
        if not data:
            return
        chunk = f"{len(data):X}\r\n".encode("ascii") + data + b"\r\n"
        self.wfile.write(chunk)
        self.wfile.flush()

    def _handle_build_ipc(self):
        """Executes build_site.py and streams stdout/stderr back in real time."""
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

        cmd = [sys.executable, str(BUILD_SCRIPT)] + flags

        # Initialize chunked response
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Transfer-Encoding", "chunked")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()

        self._send_chunk(f"[Kykloi IPC] Running: {' '.join(cmd)}\n\n".encode("utf-8"))

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=str(ROOT_DIR),
            text=True,
            bufsize=1,
        )

        try:
            for line in iter(proc.stdout.readline, ""):
                self._send_chunk(line.encode("utf-8"))
            proc.stdout.close()
            exit_code = proc.wait()
            self._send_chunk(
                f"\n[Kykloi IPC] Completed with exit code {exit_code}.\n".encode(
                    "utf-8"
                )
            )
        except (BrokenPipeError, ConnectionResetError):
            proc.kill()
        finally:
            # Terminate HTTP chunk stream
            self.wfile.write(b"0\r\n\r\n")
            self.wfile.flush()


class ThreadedServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    if not ADMIN_DIR.exists():
        sys.stderr.write(f"[FATAL] Admin directory not found: {ADMIN_DIR}\n")
        sys.exit(1)

    server = None
    port = START_PORT

    for offset in range(MAX_PORT_ATTEMPTS):
        candidate_port = START_PORT + offset
        try:
            server = ThreadedServer((HOST, candidate_port), ControlHubHandler)
            port = candidate_port
            break
        except OSError as e:
            if e.errno in (98, 48, 10048):
                continue
            raise

    if server is None:
        sys.stderr.write("[FATAL] Could not bind to an open port.\n")
        sys.exit(1)

    url = f"http://{HOST}:{port}/"
    print("=" * 60)
    print("  Project Kykloi — Control Hub (Model 1 Architecture)")
    print(f"  Root:  {ADMIN_DIR}")
    print(f"  URL:   {url}")
    print("=" * 60)

    threading.Thread(
        target=lambda: (time.sleep(0.3), webbrowser.open(url)), daemon=True
    ).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[Kykloi] Shutting down Control Hub...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
