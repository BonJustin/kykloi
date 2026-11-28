#!/usr/bin/env python3
"""
system/tools/fetch_tools.py - Autonomous Toolchain Archive Fetcher & Verifier.
Part of Project Kykloi.
Retrieves and validates offline toolchain archives using only Python standard libraries.
"""

import argparse
import hashlib
import json
import platform
import sys
import urllib.error
import urllib.request
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
MANIFEST_PATH = TOOLS_DIR / "tools-manifest.json"
ARCHIVES_DIR = TOOLS_DIR / "archives"


def detect_host_targets() -> tuple[str, str]:
    """
    Detects (pandoc_target, python_target) identifiers matching manifest keys.
    """
    sys_name = platform.system().lower()
    machine = platform.machine().lower()

    arch = (
        "x86_64"
        if machine in ("x86_64", "amd64")
        else ("arm64" if machine in ("arm64", "aarch64") else machine)
    )

    if sys_name == "darwin":
        base_target = f"macos-{arch}"
        return base_target, base_target

    if sys_name == "windows":
        py_target = "windows-arm64" if arch == "arm64" else "windows-x86_64"
        # Pandoc runs via x86_64 emulation on Windows ARM64
        return "windows-x86_64", py_target

    if sys_name == "linux":
        # Check for musl vs glibc
        is_musl = False
        try:
            import subprocess

            res = subprocess.run(["ldd", "--version"], capture_output=True, text=True)
            if "musl" in (res.stdout + res.stderr).lower():
                is_musl = True
        except Exception:
            pass

        suffix = "-musl" if is_musl else ""
        py_target = f"linux-{arch}{suffix}"
        # Upstream pandoc builds do not distribute separate musl targets
        pandoc_target = f"linux-{arch}"
        return pandoc_target, py_target

    raise RuntimeError(f"Unsupported operational platform: {sys_name} ({machine})")


def compute_sha256(file_path: Path) -> str:
    """Computes SHA-256 hexadecimal hash of a file."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def download_file(url: str, dest_path: Path, expected_sha256: str) -> bool:
    """
    Downloads an archive from url to dest_path via a temporary file,
    validating SHA-256 before staging.
    """
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = dest_path.with_name(dest_path.name + ".download")
    print(f"[*] Downloading: {dest_path.name}")
    print(f"    Source: {url}")

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Kykloi-Toolchain-Bootstrap/1.0"},
    )

    try:
        with (
            urllib.request.urlopen(req, timeout=45) as response,
            open(temp_path, "wb") as out_file,
        ):
            total_size = response.getheader("Content-Length")
            total_bytes = int(total_size) if total_size else 0
            downloaded = 0
            block_size = 65536

            while True:
                buffer = response.read(block_size)
                if not buffer:
                    break
                out_file.write(buffer)
                downloaded += len(buffer)
                if total_bytes > 0:
                    percent = (downloaded / total_bytes) * 100.0
                    mb_down = downloaded / (1024 * 1024)
                    mb_total = total_bytes / (1024 * 1024)
                    sys.stdout.write(
                        f"\r    Progress: {percent:6.2f}% ({mb_down:6.2f} / {mb_total:6.2f} MB)"
                    )
                    sys.stdout.flush()
            sys.stdout.write("\n")
    except Exception as exc:
        if temp_path.exists():
            temp_path.unlink()
        print(f"[!] Network error downloading {url}: {exc}", file=sys.stderr)
        return False

    print(f"[*] Verifying SHA-256 for {dest_path.name}...")
    actual_hash = compute_sha256(temp_path)
    if actual_hash.lower() != expected_sha256.lower():
        print(
            f"[!] Checksum mismatch for {dest_path.name}!\n"
            f"    Expected: {expected_sha256}\n"
            f"    Actual:   {actual_hash}",
            file=sys.stderr,
        )
        temp_path.unlink()
        return False

    temp_path.replace(dest_path)
    print(f"[+] Verified and saved: {dest_path.name}")
    return True


def ensure_host_pandoc(
    manifest_path: Path = MANIFEST_PATH,
    archives_dir: Path = ARCHIVES_DIR,
    force: bool = False,
    quiet: bool = False,
) -> tuple[bool, Path | None]:
    """
    Ensures that the Pandoc archive for the current host platform is present
    and verified in archives_dir. If not present, attempts to download it.
    Returns (success, archive_path).
    """
    if not manifest_path.is_file():
        if not quiet:
            print(f"[!] Manifest missing at: {manifest_path}", file=sys.stderr)
        return False, None

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
    except Exception as exc:
        if not quiet:
            print(f"[!] Failed to parse manifest: {exc}", file=sys.stderr)
        return False, None

    try:
        host_pandoc, _ = detect_host_targets()
    except Exception as exc:
        if not quiet:
            print(f"[!] Host target detection failed: {exc}", file=sys.stderr)
        return False, None

    pandoc_meta = (
        manifest.get("tools", {}).get("pandoc", {}).get("targets", {}).get(host_pandoc)
    )
    if not pandoc_meta:
        if not quiet:
            print(
                f"[!] No manifest target found for host Pandoc: {host_pandoc}",
                file=sys.stderr,
            )
        return False, None

    archive_name = pandoc_meta["archive"]
    expected_sha = pandoc_meta["sha256"]
    url = pandoc_meta.get("url")
    dest_path = archives_dir / archive_name

    archives_dir.mkdir(parents=True, exist_ok=True)

    if dest_path.is_file() and not force:
        actual_sha = compute_sha256(dest_path)
        if actual_sha.lower() == expected_sha.lower():
            if not quiet:
                print(f"[+] Host Pandoc archive verified: {dest_path.name}")
            return True, dest_path
        else:
            if not quiet:
                print(
                    f"[!] Checksum mismatch for existing {dest_path.name}. Re-downloading...",
                    file=sys.stderr,
                )

    if not url:
        if not quiet:
            print(
                f"[!] No download URL in manifest for {archive_name}", file=sys.stderr
            )
        return False, None

    if not quiet:
        print(f"[*] Pre-staging Pandoc archive for {host_pandoc}...")
    success = download_file(url, dest_path, expected_sha)
    if success:
        return True, dest_path
    return False, None


def fetch_binaries(
    all_platforms: bool = False,
    force: bool = False,
    manifest_path: Path = MANIFEST_PATH,
    archives_dir: Path = ARCHIVES_DIR,
) -> int:
    """
    Downloads and verifies toolchain archives from manifest into archives_dir.
    If all_platforms is False, only fetches archives for the host architecture.
    Returns 0 on success, non-zero on failure.
    """
    if not manifest_path.is_file():
        print(f"[!] Manifest missing at: {manifest_path}", file=sys.stderr)
        return 1

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    archives_dir.mkdir(parents=True, exist_ok=True)
    try:
        host_pandoc, host_python = detect_host_targets()
    except Exception as exc:
        print(f"[!] Failed to detect host architecture: {exc}", file=sys.stderr)
        host_pandoc, host_python = "", ""

    queue: list[
        tuple[str, str, Path, str, str]
    ] = []  # (tool, target, dest_file, expected_sha256, url)

    tools_dict = manifest.get("tools", {})
    for tool_name, tool_data in tools_dict.items():
        targets = tool_data.get("targets", {})
        for tgt_key, meta in targets.items():
            if not all_platforms:
                if tool_name == "pandoc" and tgt_key != host_pandoc:
                    continue
                if tool_name == "python" and tgt_key != host_python:
                    continue

            archive_name = meta["archive"]
            target_file = archives_dir / archive_name
            expected_sha = meta["sha256"]
            download_url = meta["url"]

            queue.append((tool_name, tgt_key, target_file, expected_sha, download_url))

    if not queue:
        print("[!] No eligible targets resolved from manifest.", file=sys.stderr)
        return 1

    print(f"[*] Processing {len(queue)} toolchain asset(s)...")
    failed = 0

    for tool_name, tgt_key, dest_path, expected_sha, url in queue:
        if dest_path.is_file() and not force:
            actual_sha = compute_sha256(dest_path)
            if actual_sha.lower() == expected_sha.lower():
                print(
                    f"[+] Already present and verified: {dest_path.name} ({tool_name}:{tgt_key})"
                )
                continue
            else:
                print(
                    f"[!] Checksum invalid for existing {dest_path.name}. Re-downloading..."
                )

        success = download_file(url, dest_path, expected_sha)
        if not success:
            failed += 1

    if failed > 0:
        print(
            f"\n[!] Failed to download or verify {failed} archive(s).",
            file=sys.stderr,
        )
        return 1

    print("\n[+] All requested toolchain archives are verified and staged.")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Retrieve and verify offline toolchain binaries for Project Kykloi."
    )
    parser.add_argument(
        "--host-only",
        action="store_true",
        help="Download only the binaries required for the current host architecture.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download and overwrite existing archives even if checksums match.",
    )
    args = parser.parse_args()

    # Default to fetching all platforms unless --host-only is explicitly provided
    fetch_all = not args.host_only
    sys.exit(fetch_binaries(all_platforms=fetch_all, force=args.force))


if __name__ == "__main__":
    main()
