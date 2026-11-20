#!/usr/bin/env python3
"""
system/test_runner.py - Rapid Cross-Platform Field Testing & Diagnostics Suite.
Part of Project Kykloi.
Executes end-to-end lifecycle verification, captures environment telemetry,
and writes comprehensive reports to logs/.
"""

import datetime
import http.client
import os
import platform
import shutil
import socket
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SYSTEM_DIR = PROJECT_ROOT / "system"
CONTENT_DIR = PROJECT_ROOT / "content"
TEST_CONTENT_DIR = PROJECT_ROOT / "test-content"
DIST_DIR = PROJECT_ROOT / "dist"
LOGS_DIR = PROJECT_ROOT / "logs"
NORM_DB_PATH = SYSTEM_DIR / "normalize" / "vault-index.db"
BUILD_SCRIPT = SYSTEM_DIR / "build" / "build.py"

for p in (PROJECT_ROOT, SYSTEM_DIR, SYSTEM_DIR / "build"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from build import ACTIVE_ENGINE_NAME
from launch import KykloiVaultHandler, ThreadedServer

from system.normalize.cli import run_normalization_pipeline

TEST_PASSPHRASE = "kykloi-field-test-passphrase-2026"


class TestReportLogger:
    """Tees console output directly into an archival report file."""

    def __init__(self, log_path: Path):
        self.log_path = log_path
        self.terminal = sys.stdout
        self.file = open(log_path, "w", encoding="utf-8")

    def write(self, message: str):
        self.terminal.write(message)
        self.file.write(message)
        self.file.flush()

    def flush(self):
        self.terminal.flush()
        self.file.flush()

    def close(self):
        if not self.file.closed:
            self.file.close()


def detect_filesystem_type(path: Path) -> str:
    """Detects the underlying filesystem type of the directory."""
    if sys.platform == "win32":
        try:
            import ctypes

            kernel32 = ctypes.windll.kernel32
            root_drive = path.resolve().drive + "\\"
            fs_name_buf = ctypes.create_unicode_buffer(256)
            success = kernel32.GetVolumeInformationW(
                ctypes.c_wchar_p(root_drive),
                None,
                0,
                None,
                None,
                None,
                fs_name_buf,
                ctypes.sizeof(fs_name_buf),
            )
            if success:
                return fs_name_buf.value
        except Exception:
            pass
        return "Windows-FS"
    else:
        try:
            import subprocess

            res = subprocess.run(
                ["df", "-T", str(path)], capture_output=True, text=True
            )
            if res.returncode == 0:
                lines = res.stdout.strip().splitlines()
                if len(lines) >= 2:
                    parts = lines[1].split()
                    if len(parts) >= 2:
                        return parts[1]
        except Exception:
            pass
        return "POSIX-FS"


def detect_linux_libc() -> str:
    """Probes libc implementation on Linux."""
    if sys.platform != "linux":
        return "N/A"
    try:
        res = subprocess.run(
            ["getconf", "GNU_LIBC_VERSION"], capture_output=True, text=True
        )
        if res.returncode == 0 and res.stdout.strip():
            return f"glibc {res.stdout.strip()}"
    except Exception:
        pass
    try:
        res = subprocess.run(["ldd", "--version"], capture_output=True, text=True)
        output = (res.stdout + res.stderr).lower()
        if "musl" in output:
            return "musl"
        elif "glibc" in output or "gnu" in output:
            return "glibc"
    except Exception:
        pass
    return "unknown"


def print_environment_report():
    print(
        "================================================================================"
    )
    print(
        "                   PROJECT KYKLOI - FIELD TEST DIAGNOSTICS                      "
    )
    print(
        "================================================================================"
    )
    print(
        f"Timestamp (UTC):       {datetime.datetime.now(datetime.timezone.utc).isoformat()}"
    )
    print(f"Hostname:              {socket.gethostname()}")
    print(
        f"Operating System:      {platform.system()} {platform.release()} ({platform.version()})"
    )
    print(
        f"Architecture:          {platform.machine()} / {platform.processor() or 'unknown'}"
    )
    if sys.platform == "linux":
        print(f"C Library:             {detect_linux_libc()}")
    print(f"Filesystem Type:       {detect_filesystem_type(PROJECT_ROOT)}")
    print(f"Project Location:      {PROJECT_ROOT}")
    print(f"Python Executable:     {sys.executable}")
    print(
        f"Python Version:        {platform.python_version()} ({platform.python_implementation()})"
    )
    print(f"Crypto Accelerator:    {ACTIVE_ENGINE_NAME}")
    print(
        f"Pandoc on PATH:        {shutil.which('pandoc') or 'None (using bundled archive)'}"
    )
    print(
        "================================================================================\n"
    )


def purge_ephemeral_runtimes():
    """Purges extracted runtime caches in temporary directories."""
    cleaned = []
    candidates = []

    if sys.platform == "win32":
        temp_dir = Path(
            os.environ.get("TEMP", os.environ.get("LOCALAPPDATA", "C:\\Temp"))
        )
        candidates.extend(temp_dir.glob("kykloi_runtime_*"))
        candidates.extend(temp_dir.glob("kykloi_pandoc_*"))
    else:
        for base in [
            Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "kykloi",
            Path("/var/tmp/kykloi"),
            Path("/tmp/kykloi"),
        ]:
            if base.exists():
                candidates.append(base)

    for item in candidates:
        try:
            if item.is_dir():
                shutil.rmtree(item)
                cleaned.append(str(item))
            elif item.is_file():
                item.unlink()
                cleaned.append(str(item))
        except OSError:
            pass

    return cleaned


def reset_vault_state():
    """Wipes content/, dist/, and vault-index.db."""
    if CONTENT_DIR.exists():
        shutil.rmtree(CONTENT_DIR)
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)

    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)

    if NORM_DB_PATH.exists():
        NORM_DB_PATH.unlink()
    for ext in ("-wal", "-shm"):
        wal = NORM_DB_PATH.with_name(NORM_DB_PATH.name + ext)
        if wal.exists():
            wal.unlink()


def hydrate_fixtures() -> int:
    """Clones test-content/ into content/."""
    if not TEST_CONTENT_DIR.exists():
        raise FileNotFoundError(f"Fixture directory missing: {TEST_CONTENT_DIR}")

    count = 0
    for src in TEST_CONTENT_DIR.rglob("*"):
        if src.is_file():
            rel = src.relative_to(TEST_CONTENT_DIR)
            dst = CONTENT_DIR / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            count += 1
    return count


def run_pipeline_step(name: str, fn) -> Tuple[bool, float, str]:
    print(f"[TEST STEP] {name} ... ", end="", flush=True)
    t0 = time.perf_counter()
    try:
        fn()
        elapsed = (time.perf_counter() - t0) * 1000.0
        print(f"PASSED ({elapsed:.2f} ms)")
        return True, elapsed, ""
    except Exception as exc:
        elapsed = (time.perf_counter() - t0) * 1000.0
        print(f"FAILED ({elapsed:.2f} ms)")
        print(f"            Error: {exc}")
        return False, elapsed, str(exc)


def execute_field_test_suite(auto_cleanup: bool = False) -> int:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    host_slug = platform.node().replace(" ", "_")
    plat_slug = f"{platform.system().lower()}_{platform.machine().lower()}"
    log_file = LOGS_DIR / f"test_{stamp}_{host_slug}_{plat_slug}.log"

    tee = TestReportLogger(log_file)
    old_stdout, old_stderr = sys.stdout, sys.stderr
    sys.stdout = tee
    sys.stderr = tee

    results: List[Tuple[str, bool, float, str]] = []

    try:
        print_environment_report()

        # Step 1: Pre-test reset
        def step_reset():
            reset_vault_state()

        results.append(
            (
                "Reset Workspace State",
                *run_pipeline_step("Reset Workspace State", step_reset)[0:2],
                "",
            )
        )

        # Step 2: Empty Vault Handling
        def step_empty_vault():
            code = run_normalization_pipeline(
                content_root=CONTENT_DIR,
                db_path=NORM_DB_PATH,
                dry_run=False,
                auto_apply=True,
                check_only=False,
            )
            if code != 0:
                raise RuntimeError(
                    f"Normalization failed on empty content directory (exit code {code})"
                )

        ok, dur, err = run_pipeline_step("Empty Vault Normalization", step_empty_vault)
        results.append(("Empty Vault Normalization", ok, dur, err))

        # Step 3: Fixture Hydration
        def step_hydrate():
            c = hydrate_fixtures()
            if c == 0:
                raise RuntimeError("test-content/ contained zero files to hydrate.")

        ok, dur, err = run_pipeline_step(
            "Hydrate Fixtures from test-content/", step_hydrate
        )
        results.append(("Hydrate Fixtures", ok, dur, err))

        # Step 4: Vault Normalization & Sanitization
        def step_normalize():
            code = run_normalization_pipeline(
                content_root=CONTENT_DIR,
                db_path=NORM_DB_PATH,
                dry_run=False,
                auto_apply=True,
                check_only=False,
            )
            if code != 0:
                raise RuntimeError(f"Normalization pipeline returned error code {code}")

        ok, dur, err = run_pipeline_step(
            "Execute Normalization & Link Healing", step_normalize
        )
        results.append(("Execute Normalization", ok, dur, err))

        # Step 5: Full Compilation
        def step_build():
            env = os.environ.copy()
            env["KYKLOI_ENCRYPT_KEY"] = TEST_PASSPHRASE
            cmd = [sys.executable, str(BUILD_SCRIPT)]
            res = subprocess.run(
                cmd, cwd=str(PROJECT_ROOT), env=env, capture_output=True, text=True
            )
            if res.returncode != 0:
                raise RuntimeError(f"Build failed:\n{res.stderr}\n{res.stdout}")

            # Verify build artifacts
            if not (DIST_DIR / "index.html").is_file():
                raise FileNotFoundError("Missing dist/index.html")
            if not (DIST_DIR / "search.db").is_file():
                raise FileNotFoundError("Missing dist/search.db")

            # Verify SQLite FTS5 index contains searchable records
            conn = sqlite3.connect(DIST_DIR / "search.db")
            cur = conn.cursor()
            cur.execute("SELECT count(*) FROM docs_fts;")
            cnt = cur.fetchone()[0]
            conn.close()
            if cnt == 0:
                raise ValueError("docs_fts table contains 0 indexed documents.")

        ok, dur, err = run_pipeline_step(
            "Full Compilation & Cryptographic Packaging", step_build
        )
        results.append(("Full Compilation", ok, dur, err))

        # Step 6: Stat-Cache Incremental Compilation Verification
        def step_stat_cache():
            env = os.environ.copy()
            env["KYKLOI_ENCRYPT_KEY"] = TEST_PASSPHRASE
            cmd = [sys.executable, str(BUILD_SCRIPT)]
            res = subprocess.run(
                cmd, cwd=str(PROJECT_ROOT), env=env, capture_output=True, text=True
            )
            if res.returncode != 0:
                raise RuntimeError(f"Incremental build failed:\n{res.stderr}")
            if "Document compilation cache hit. All" not in res.stdout:
                raise AssertionError(
                    "Stat-cache failed to register complete cache hit on unchanged vault."
                )

        ok, dur, err = run_pipeline_step(
            "Stat-Cache 100% Hit Verification", step_stat_cache
        )
        results.append(("Stat-Cache Hit", ok, dur, err))

        # Step 7: Graph Healing on Dynamic File Mutation
        def step_mutation():
            # Find a markdown file in content/ to rename
            candidates = list(CONTENT_DIR.glob("*.md"))
            if not candidates:
                raise FileNotFoundError(
                    "No markdown files in content/ to perform mutation test."
                )
            target = candidates[0]
            mutated = target.with_name(f"mutated-{target.name}")
            target.rename(mutated)

            code = run_normalization_pipeline(
                content_root=CONTENT_DIR,
                db_path=NORM_DB_PATH,
                dry_run=False,
                auto_apply=True,
                check_only=False,
            )
            if code != 0:
                raise RuntimeError(
                    f"Normalization failed during link mutation step (code {code})"
                )

        ok, dur, err = run_pipeline_step(
            "Dynamic Mutation & Automatic Link Repair", step_mutation
        )
        results.append(("Mutation Link Repair", ok, dur, err))

        # Step 8: Static HTTP Server & RFC 7233 Byte-Range Testing
        def step_server():
            server, port, url = None, 0, ""
            max_attempts = 10
            for offset in range(max_attempts):
                candidate_port = 8990 + offset
                try:
                    server = ThreadedServer(
                        ("127.0.0.1", candidate_port), KykloiVaultHandler
                    )
                    port = candidate_port
                    break
                except OSError:
                    continue

            if not server:
                raise RuntimeError("Could not bind test server to open ephemeral port.")

            import threading

            th = threading.Thread(target=server.serve_forever, daemon=True)
            th.start()

            try:
                # 1. Test 200 OK
                conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
                conn.request("GET", "/index.html")
                r1 = conn.getresponse()
                if r1.status != 200:
                    raise AssertionError(
                        f"Expected 200 OK on /index.html, got {r1.status}"
                    )
                r1.read()

                # 2. Test 206 Partial Content (Range: bytes=0-15)
                conn.request("GET", "/index.html", headers={"Range": "bytes=0-15"})
                r2 = conn.getresponse()
                if r2.status != 206:
                    raise AssertionError(
                        f"Expected 206 Partial Content, got {r2.status}"
                    )
                chunk = r2.read()
                if len(chunk) != 16:
                    raise AssertionError(
                        f"Expected 16 bytes for range 0-15, received {len(chunk)}"
                    )

                # 3. Test 404 File Not Found
                conn.request("GET", "/non_existent_file_xyz.html")
                r3 = conn.getresponse()
                if r3.status != 404:
                    raise AssertionError(
                        f"Expected 404 File Not Found, got {r3.status}"
                    )
                r3.read()
                conn.close()
            finally:
                server.shutdown()
                server.server_close()

        ok, dur, err = run_pipeline_step(
            "Local HTTP Server & Byte-Range Verification", step_server
        )
        results.append(("Server Protocol Check", ok, dur, err))

    finally:
        total_time = sum(d for _, _, d, _ in results)
        failed_tests = [name for name, passed, _, _ in results if not passed]

        print(
            "\n================================================================================"
        )
        print(
            "                            TEST SUITE SCORECARD                                "
        )
        print(
            "================================================================================"
        )
        for name, passed, dur, err in results:
            status = "PASS" if passed else "FAIL"
            print(f"  [{status}] {name:<46} ({dur:>8.2f} ms)")
            if err:
                print(f"         Reason: {err}")
        print(
            "--------------------------------------------------------------------------------"
        )
        print(f"Total Operational Duration: {total_time:.2f} ms")
        print(f"Log Archive Written:        {log_file.resolve()}")

        if failed_tests:
            print(f"OVERALL STATUS: FAILED ({len(failed_tests)} step(s) failed)")
        else:
            print("OVERALL STATUS: SUCCESS (All verification invariants satisfied)")
        print(
            "================================================================================\n"
        )

        if auto_cleanup:
            print("[CLEANUP] Resetting vault state and purging ephemeral runtimes...")
            reset_vault_state()
            cleaned_paths = purge_ephemeral_runtimes()
            for cp in cleaned_paths:
                print(f"  Purged: {cp}")
            print("[CLEANUP] Workspace restored to clean baseline.")

        sys.stdout = old_stdout
        sys.stderr = old_stderr
        tee.close()

    return 1 if failed_tests else 0


if __name__ == "__main__":
    auto_clean = "--clean" in sys.argv or "--cleanup" in sys.argv
    code = execute_field_test_suite(auto_cleanup=auto_clean)
    sys.exit(code)
