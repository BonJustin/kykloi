#!/usr/bin/env python3
"""
launch.py - Minimal, isolated viability prototype for Kykloi Control Hub.
Runs entirely in memory; makes zero modifications to existing project files.
"""

import http.server
import socketserver
import sys
import threading
import time
import webbrowser

HOST = "127.0.0.1"
START_PORT = 8000
MAX_PORT_ATTEMPTS = 15

# Minimal embedded HTML for Milestone 1 (Zero disk dependencies)
HTML_PAYLOAD = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Kykloi Control Hub (Test)</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {
      font-family: system-ui, -apple-system, sans-serif;
      max-width: 600px;
      margin: 4rem auto;
      padding: 0 1rem;
      line-height: 1.5;
      background-color: #f9f9f9;
      color: #222;
    }
    .card {
      background: #fff;
      border: 1px solid #ddd;
      border-radius: 8px;
      padding: 2rem;
      box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    h1 { margin-top: 0; color: #0066cc; }
    .status { color: #28a745; font-weight: bold; }
  </style>
</head>
<body>
  <div class="card">
    <h1>Kykloi Control Hub</h1>
    <p class="status">● Status: Connection Established</p>
    <p>Hello World. Localhost interface is active and accessible.</p>
  </div>
</body>
</html>
"""


class DashboardRequestHandler(http.server.BaseHTTPRequestHandler):
    """Minimal request handler serving the in-memory test page."""

    server_version = "KykloiPrototype/0.1"

    def do_GET(self):
        # Serve the test interface for root or any path
        body = HTML_PAYLOAD.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        # Clean terminal logging
        sys.stderr.write(f"[Kykloi Hub] {self.address_string()} - {format % args}\n")


class ThreadedServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


def open_default_browser(url: str):
    """Open the URL in the system's default browser without vendor lock-in."""
    time.sleep(0.3)
    webbrowser.open(url)


def main():
    server = None
    port = START_PORT

    # Port hunting logic identical to serve.py
    for offset in range(MAX_PORT_ATTEMPTS):
        candidate_port = START_PORT + offset
        try:
            server = ThreadedServer((HOST, candidate_port), DashboardRequestHandler)
            port = candidate_port
            break
        except OSError as e:
            if e.errno in (98, 48, 10048):  # Port already in use
                continue
            raise

    if server is None:
        sys.stderr.write(f"[ERROR] Could not bind to an open port between {START_PORT} and {START_PORT + MAX_PORT_ATTEMPTS}.\n")
        sys.exit(1)

    url = f"http://{HOST}:{port}/"
    print("=" * 60)
    print("  Kykloi Dashboard Prototype Initialized")
    print(f"  Target URL: {url}")
    print("  Press Ctrl+C to terminate server.")
    print("=" * 60)

    # Launch system default browser in background thread
    threading.Thread(target=open_default_browser, args=(url,), daemon=True).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[Kykloi Hub] Shutting down cleanly...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
