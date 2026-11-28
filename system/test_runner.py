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

from launch import KykloiVaultHandler, ThreadedServer

from system.backup import (
    create_vault_backup,
    find_previous_backups,
    prune_previous_backups,
)
from system.build.build import (
    ACTIVE_ENGINE_NAME,
    probe_pandoc_version,
    resolve_pandoc_binary,
)
from system.normalize.cli import run_normalization_pipeline
from system.normalize.scanner import is_junk_path

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
    try:
        resolved_pandoc = resolve_pandoc_binary(PROJECT_ROOT)
        pandoc_ver = probe_pandoc_version(resolved_pandoc)
        ver_str = ".".join(str(x) for x in pandoc_ver) if pandoc_ver else "unknown"
        is_bundled = "runtime_" in resolved_pandoc or "kykloi_pandoc" in resolved_pandoc
        source_tag = "bundled archive" if is_bundled else "host system"
        print(f"Pandoc Runtime:        {resolved_pandoc} (v{ver_str}, {source_tag})")
    except Exception as exc:
        print(f"Pandoc Runtime:        Failed to resolve ({exc})")
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


def hydrate_fixtures_to(target_dir: Path) -> int:
    """Clones test-content/ into specified target directory."""
    if not TEST_CONTENT_DIR.exists():
        raise FileNotFoundError(f"Fixture directory missing: {TEST_CONTENT_DIR}")

    count = 0
    for src in TEST_CONTENT_DIR.rglob("*"):
        if src.is_file() and not is_junk_path(src, TEST_CONTENT_DIR):
            rel = src.relative_to(TEST_CONTENT_DIR)
            dst = target_dir / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            count += 1
    return count


def run_pipeline_step(name: str, fn) -> tuple[bool, float, str]:
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
    import tempfile

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    host_slug = platform.node().replace(" ", "_")
    plat_slug = f"{platform.system().lower()}_{platform.machine().lower()}"
    log_file = LOGS_DIR / f"test_{stamp}_{host_slug}_{plat_slug}.log"

    tee = TestReportLogger(log_file)
    old_stdout, old_stderr = sys.stdout, sys.stderr
    sys.stdout = tee
    sys.stderr = tee

    results: list[tuple[str, bool, float, str]] = []

    with tempfile.TemporaryDirectory(prefix="kykloi_test_") as temp_workspace_str:
        temp_workspace = Path(temp_workspace_str).resolve()
        isolated_content = temp_workspace / "content"
        isolated_dist = temp_workspace / "dist"
        isolated_db = temp_workspace / "vault-index.db"

        isolated_content.mkdir(parents=True, exist_ok=True)

        try:
            print_environment_report()

            # Step 1: Isolated Environment Initialization
            def step_init():
                if not isolated_content.is_dir():
                    raise RuntimeError("Failed to create isolated content sandbox.")

            results.append(
                (
                    "Initialize Isolated Sandbox",
                    *run_pipeline_step("Initialize Isolated Sandbox", step_init)[0:2],
                    "",
                )
            )

            # Step 2: Empty Vault Handling
            def step_empty_vault():
                code = run_normalization_pipeline(
                    content_root=isolated_content,
                    db_path=isolated_db,
                    auto_apply=True,
                )
                if code != 0:
                    raise RuntimeError(
                        f"Normalization failed on empty content directory (exit code {code})"
                    )

            ok, dur, err = run_pipeline_step(
                "Empty Vault Normalization", step_empty_vault
            )
            results.append(("Empty Vault Normalization", ok, dur, err))

            # Step 3: Fixture Hydration
            def step_hydrate():
                c = hydrate_fixtures_to(isolated_content)
                if c == 0:
                    raise RuntimeError("test-content/ contained zero files to hydrate.")

            ok, dur, err = run_pipeline_step(
                "Hydrate Fixtures to Sandbox", step_hydrate
            )
            results.append(("Hydrate Fixtures", ok, dur, err))

            # Step 4: Vault Normalization & Sanitization
            def step_normalize():
                code = run_normalization_pipeline(
                    content_root=isolated_content,
                    db_path=isolated_db,
                    auto_apply=True,
                )
                if code != 0:
                    raise RuntimeError(
                        f"Normalization pipeline returned error code {code}"
                    )

            ok, dur, err = run_pipeline_step(
                "Execute Normalization & Link Healing", step_normalize
            )
            results.append(("Execute Normalization", ok, dur, err))

            # Step 5: Full Compilation
            def step_build():
                env = os.environ.copy()
                env["KYKLOI_ENCRYPT_KEY"] = TEST_PASSPHRASE
                cmd = [
                    sys.executable,
                    str(BUILD_SCRIPT),
                    "--src",
                    str(isolated_content),
                    "--dst",
                    str(isolated_dist),
                    "--db-path",
                    str(isolated_db),
                ]
                res = subprocess.run(
                    cmd, cwd=str(PROJECT_ROOT), env=env, capture_output=True, text=True
                )
                if res.returncode != 0:
                    raise RuntimeError(f"Build failed:\n{res.stderr}\n{res.stdout}")

                # Verify build artifacts
                if not (isolated_dist / "index.html").is_file():
                    raise FileNotFoundError("Missing dist/index.html")
                if not (isolated_dist / "search.db").is_file():
                    raise FileNotFoundError("Missing dist/search.db")

                # Verify secure note encryption: assert plaintext is not leaked in dist/
                secure_out = isolated_dist / "secure" / "secret-vault-entry.html"
                if not secure_out.is_file():
                    raise FileNotFoundError(
                        f"Missing encrypted secure document: {secure_out}"
                    )
                secure_html = secure_out.read_text(encoding="utf-8")
                if "PBKDF2-HMAC-SHA256" in secure_html:
                    raise AssertionError(
                        "CRITICAL SECURITY LEAK: Plaintext found inside encrypted output document."
                    )
                if "kykloi-encrypted-payload" not in secure_html:
                    raise AssertionError(
                        "Encrypted envelope script tag missing from secure document."
                    )

                # Verify SQLite FTS5 index contains searchable records
                conn = sqlite3.connect(isolated_dist / "search.db")
                cur = conn.cursor()
                cur.execute("SELECT count(*) FROM docs_fts;")
                cnt = cur.fetchone()[0]
                conn.close()
                if cnt < 4:
                    raise ValueError(
                        f"docs_fts table indexed {cnt} documents; expected at least 4."
                    )

            ok, dur, err = run_pipeline_step(
                "Full Compilation & Cryptographic Packaging", step_build
            )
            results.append(("Full Compilation", ok, dur, err))

            # Step 6: Stat-Cache Incremental Compilation Verification
            def step_stat_cache():
                env = os.environ.copy()
                env["KYKLOI_ENCRYPT_KEY"] = TEST_PASSPHRASE
                cmd = [
                    sys.executable,
                    str(BUILD_SCRIPT),
                    "--src",
                    str(isolated_content),
                    "--dst",
                    str(isolated_dist),
                    "--db-path",
                    str(isolated_db),
                ]
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
                target = isolated_content / "20261116170353-sample-intro.md"
                referencing = isolated_content / "20261117053719-sample-crypto.md"

                if not target.is_file() or not referencing.is_file():
                    raise FileNotFoundError(
                        "Mutation target or referencing fixture note missing in sandbox."
                    )

                mutated_name = "20261116170353-sample-intro-renamed.md"
                mutated = target.with_name(mutated_name)
                target.rename(mutated)

                code = run_normalization_pipeline(
                    content_root=isolated_content,
                    db_path=isolated_db,
                    auto_apply=True,
                )
                if code != 0:
                    raise RuntimeError(
                        f"Normalization failed during link mutation step (code {code})"
                    )

                referencing_content = referencing.read_text(encoding="utf-8")
                if mutated_name not in referencing_content:
                    raise AssertionError(
                        f"Link healing failed: Referencing document '{referencing.name}' "
                        f"was not updated with new target '{mutated_name}'."
                    )

            ok, dur, err = run_pipeline_step(
                "Dynamic Mutation & Automatic Link Repair", step_mutation
            )
            results.append(("Mutation Link Repair", ok, dur, err))

            # Step 8: Crash Recovery & Uncommitted Mutation Roll-Forward
            def step_crash_recovery():
                import json

                from system.normalize.cli import recover_uncommitted_journal
                from system.normalize.db import VaultDB

                test_file = isolated_content / "20261118120000-sample-note-3.md"
                if not test_file.is_file():
                    raise FileNotFoundError(
                        "Fixture note missing for crash recovery test."
                    )

                target_recovered = (
                    isolated_content / "20261118120000-sample-note-recovered.md"
                )
                if target_recovered.exists():
                    target_recovered.unlink()

                with VaultDB(isolated_db) as db:
                    renames_json = json.dumps([(str(test_file), str(target_recovered))])
                    db.record_journal(
                        session_id="test_crash_session",
                        stage="STAGED",
                        file_renames_json=renames_json,
                        content_patches_json="{}",
                        created_at="2026-11-28T00:00:00Z",
                    )
                    uncommitted = db.get_uncommitted_journal()
                    if not uncommitted:
                        raise AssertionError(
                            "Failed to record simulated crash journal."
                        )

                    recovered = recover_uncommitted_journal(isolated_content, db)
                    if not recovered:
                        raise AssertionError(
                            "recover_uncommitted_journal returned False."
                        )

                    remaining = db.get_uncommitted_journal()
                    if remaining is not None:
                        raise AssertionError(
                            "Uncommitted journal was not cleared after recovery."
                        )

                    if not target_recovered.is_file():
                        raise AssertionError("File was not rolled forward to new path.")
                    if test_file.exists():
                        raise AssertionError(
                            "Original file still exists after roll-forward."
                        )

                    db_files = db.get_all_files()
                    rel_p = target_recovered.relative_to(isolated_content).as_posix()
                    if rel_p not in db_files:
                        raise AssertionError(
                            f"Recovered file '{rel_p}' not present in synchronized ledger."
                        )

            ok, dur, err = run_pipeline_step(
                "Crash Recovery & Interrupted Journal Roll-Forward",
                step_crash_recovery,
            )
            results.append(("Crash Journal Recovery", ok, dur, err))

            # Step 9: Static HTTP Server & RFC 7233 Byte-Range Testing
            def step_server():
                class SandboxVaultHandler(KykloiVaultHandler):
                    dist_dir = isolated_dist

                server = None
                port = 8990
                max_attempts = 10
                for offset in range(max_attempts):
                    candidate_port = 8990 + offset
                    try:
                        server = ThreadedServer(
                            ("127.0.0.1", candidate_port), SandboxVaultHandler
                        )
                        port = candidate_port
                        break
                    except OSError:
                        continue

                if not server:
                    raise RuntimeError(
                        "Could not bind test server to open ephemeral port."
                    )

                import threading

                th = threading.Thread(target=server.serve_forever, daemon=True)
                th.start()

                try:
                    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
                    conn.request("GET", "/index.html")
                    r1 = conn.getresponse()
                    if r1.status != 200:
                        raise AssertionError(
                            f"Expected 200 OK on /index.html, got {r1.status}"
                        )
                    r1.read()

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

            # Step 9: Archival Backup & Integrity Verification
            def step_backup():
                isolated_backups = temp_workspace / "backups"

                # Inject junk files to verify they are filtered out
                junk_dir = isolated_content / ".obsidian"
                junk_dir.mkdir(parents=True, exist_ok=True)
                junk_file = junk_dir / "workspace.json"
                junk_file.write_text('{"junk": true}', encoding="utf-8")
                ds_store_file = isolated_content / ".DS_Store"
                ds_store_file.write_bytes(b"\x00\x01\x02")

                try:
                    zip_p, sha_p, count, _ = create_vault_backup(
                        content_dir=isolated_content,
                        output_dir=isolated_backups,
                        archive_name="test-backup.zip",
                    )

                    if not zip_p.is_file():
                        raise AssertionError("ZIP archive was not created.")
                    if not sha_p.is_file():
                        raise AssertionError("SHA-256 sidecar file was not created.")

                    import zipfile

                    if not zipfile.is_zipfile(zip_p):
                        raise AssertionError("Created file is not a valid ZIP archive.")

                    with zipfile.ZipFile(zip_p, "r") as zf:
                        namelist = zf.namelist()
                        for name in namelist:
                            if ".obsidian" in name or ".DS_Store" in name:
                                raise AssertionError(
                                    f"Junk file was not excluded from archive: {name}"
                                )
                        if count != len(namelist):
                            raise AssertionError(
                                f"Reported count {count} does not match archive entries {len(namelist)}"
                            )

                    # Verify SHA-256 sidecar digest
                    import hashlib

                    with open(zip_p, "rb") as zf:
                        calculated_hash = hashlib.sha256(zf.read()).hexdigest()
                    with open(sha_p, "r", encoding="utf-8") as sf:
                        sidecar_content = sf.read().strip()
                    if not sidecar_content.startswith(calculated_hash):
                        raise AssertionError(
                            f"SHA-256 sidecar mismatch: expected {calculated_hash}"
                        )

                    # Verify discovery and safe pruning of previous backups
                    old_zip = (
                        isolated_backups / "kykloi-backup-content-20261120T000000Z.zip"
                    )
                    old_sha = (
                        isolated_backups
                        / "kykloi-backup-content-20261120T000000Z.zip.sha256"
                    )
                    old_zip.write_bytes(b"PK\x05\x06" + b"\x00" * 18)
                    old_sha.write_text("dummy_hash  old.zip\n", encoding="utf-8")

                    new_zip, new_sha, _, _ = create_vault_backup(
                        content_dir=isolated_content,
                        output_dir=isolated_backups,
                        archive_name="kykloi-backup-content-20261125T000000Z.zip",
                    )

                    found_old = find_previous_backups(
                        isolated_backups, exclude_paths={new_zip, new_sha}
                    )
                    found_names = {p.name for p in found_old}
                    if (
                        old_zip.name not in found_names
                        or old_sha.name not in found_names
                    ):
                        raise AssertionError(
                            f"Previous backups not found by discovery: {found_names}"
                        )
                    if new_zip.name in found_names or new_sha.name in found_names:
                        raise AssertionError(
                            "Newly generated backup was not excluded from previous backup candidates."
                        )

                    pruned = prune_previous_backups(
                        isolated_backups, exclude_paths={new_zip, new_sha}
                    )
                    if len(pruned) != 2:
                        raise AssertionError(
                            f"Expected 2 pruned artifacts, got {len(pruned)}"
                        )
                    if old_zip.exists() or old_sha.exists():
                        raise AssertionError("Old backup files were not unlinked.")
                    if not new_zip.exists() or not new_sha.exists():
                        raise AssertionError(
                            "New backup was erroneously removed during pruning."
                        )
                finally:
                    shutil.rmtree(junk_dir, ignore_errors=True)
                    if ds_store_file.exists():
                        ds_store_file.unlink()

            ok, dur, err = run_pipeline_step(
                "Archival Backup & SHA-256 Integrity Verification", step_backup
            )
            results.append(("Archival Backup & Integrity", ok, dur, err))

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
                cleaned_paths = purge_ephemeral_runtimes()
                for cp in cleaned_paths:
                    print(f"  Purged: {cp}")
                print("[CLEANUP] Ephemeral runtime caches purged.")

            sys.stdout = old_stdout
            sys.stderr = old_stderr
            tee.close()

    return 1 if failed_tests else 0


if __name__ == "__main__":
    auto_clean = "--clean" in sys.argv or "--cleanup" in sys.argv
    code = execute_field_test_suite(auto_cleanup=auto_clean)
    sys.exit(code)
