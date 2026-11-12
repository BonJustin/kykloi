#!/usr/bin/env python3
"""
launch.py - Autonomous Control Hub Daemon for Project Kykloi.
Features CLI argument parsing, defensive MIME registration, and IPC vault orchestration.
"""

import argparse
import http.server
import json
import mimetypes
import socket
import socketserver
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path

# ===========================================================================
# 1. PATH RESOLUTION & DEFENSIVE MIME REGISTRATION
# ===========================================================================

ROOT_DIR = Path(__file__).resolve().parent
ADMIN_DIR = ROOT_DIR / "admin"
BUILD_SCRIPT = ROOT_DIR / "build" / "build_site.py"
SERVE_SCRIPT = ROOT_DIR / "serve.py"

mimetypes.init()
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("font/woff2", ".woff2")
mimetypes.add_type("image/svg+xml", ".svg")

BUILD_LOCK = threading.Lock()
SERVE_PROC = None


# ===========================================================================
# 2. REQUEST HANDLER & IPC ENGINE
# ===========================================================================


class ControlHubHandler(http.server.SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ADMIN_DIR), **kwargs)

    def translate_path(self, path: str) -> str:
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
        if self.path == "/api/view":
            self._handle_view_ipc()
            return
        self.send_error(404, "Unknown API Endpoint")

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

            cmd = [sys.executable, str(BUILD_SCRIPT)] + flags

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

    def _handle_view_ipc(self):
        """Spawns serve.py if inactive and signals browser launch."""
        global SERVE_PROC
        reader_port = 8000

        # Test if serve.py is already active on port 8000
        is_running = False
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.2)
            if s.connect_ex(("127.0.0.1", reader_port)) == 0:
                is_running = True

        if not is_running:
            SERVE_PROC = subprocess.Popen(
                [sys.executable, str(SERVE_SCRIPT)],
                cwd=str(ROOT_DIR),
                stdin=subprocess.DEVNULL,
            )
            time.sleep(0.4)

        vault_url = f"http://127.0.0.1:{reader_port}/"
        threading.Thread(target=lambda: webbrowser.open(vault_url), daemon=True).start()

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(
            json.dumps({"status": "launched", "url": vault_url}).encode("utf-8")
        )


# ===========================================================================
# 3. CLI & INITIALIZATION
# ===========================================================================


class ThreadedServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


def parse_args():
    p = argparse.ArgumentParser(description="Kykloi Control Hub Appliance Daemon.")
    p.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Bind interface (default: 127.0.0.1)",
    )
    p.add_argument("--port", type=int, default=8040, help="Start port (default: 8040)")
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
            server = ThreadedServer((args.host, candidate_port), ControlHubHandler)
            port = candidate_port
            break
        except OSError as e:
            if e.errno in (98, 48, 10048):
                continue
            raise

    if server is None:
        sys.stderr.write("[FATAL] Could not bind to an open port.\n")
        sys.exit(1)

    url = f"http://{args.host}:{port}/"
    print("=" * 60)
    print("  Project Kykloi — Control Hub Daemon")
    print(f"  Root:   {ADMIN_DIR}")
    print(f"  URL:    {url}")
    print(f"  Mode:   {'Browser' if args.browser else 'Headless'}")
    print("=" * 60)

    if args.browser:
        threading.Thread(
            target=lambda: (time.sleep(0.3), webbrowser.open(url)), daemon=True
        ).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[Kykloi] Shutting down Control Hub...")
    finally:
        if SERVE_PROC:
            SERVE_PROC.terminate()
        server.server_close()


if __name__ == "__main__":
    main()
