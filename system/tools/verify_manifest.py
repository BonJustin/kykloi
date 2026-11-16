#!/usr/bin/env python3
"""
system/tools/verify_manifest.py - Archive Checksum Integrity Verifier.
Validates tools_manifest.json against physical archives in system/tools/archives/.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
MANIFEST_PATH = TOOLS_DIR / "tools_manifest.json"
ARCHIVES_DIR = TOOLS_DIR / "archives"


def compute_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def main():
    parser = argparse.ArgumentParser(
        description="Verify archive checksums against tools_manifest.json"
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=MANIFEST_PATH,
        help="Path to tools_manifest.json",
    )
    parser.add_argument(
        "--archives",
        type=Path,
        default=ARCHIVES_DIR,
        help="Path to archives directory",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Update manifest with actual computed SHA-256 values on disk",
    )
    args = parser.parse_args()

    manifest_file = args.manifest.resolve()
    archives_dir = args.archives.resolve()

    if not manifest_file.is_file():
        sys.stderr.write(f"Error: Manifest not found at {manifest_file}\n")
        sys.exit(1)

    if not archives_dir.is_dir():
        sys.stderr.write(f"Error: Archives directory not found at {archives_dir}\n")
        sys.exit(1)

    with open(manifest_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    tools = data.get("tools", {})
    records = []
    has_mismatch = False
    has_missing = False

    for tool_name, tool_data in tools.items():
        targets = tool_data.get("targets", {})
        for target_name, target_info in targets.items():
            archive_name = target_info.get("archive", "")
            expected_sha = target_info.get("sha256", "").strip().lower()
            archive_path = archives_dir / archive_name

            if not archive_path.is_file():
                status = "MISSING"
                actual_sha = "N/A"
                has_missing = True
            else:
                actual_sha = compute_sha256(archive_path)
                if actual_sha == expected_sha:
                    status = "OK"
                else:
                    status = "MISMATCH"
                    has_mismatch = True
                    if args.update:
                        target_info["sha256"] = actual_sha

            records.append(
                {
                    "tool": tool_name,
                    "target": target_name,
                    "archive": archive_name,
                    "expected": expected_sha,
                    "actual": actual_sha,
                    "status": status,
                }
            )

    # Render summary table
    print(f"\nTarget Manifest: {manifest_file.relative_to(TOOLS_DIR.parent.parent)}")
    print(f"Archives Source: {archives_dir.relative_to(TOOLS_DIR.parent.parent)}\n")
    print(f"{'STATUS':<10} {'TOOL/TARGET':<30} {'ARCHIVE':<45}")
    print("-" * 85)

    for r in records:
        target_label = f"{r['tool']}:{r['target']}"
        print(f"[{r['status']:<8}] {target_label:<30} {r['archive']:<45}")
        if r["status"] == "MISMATCH":
            print(f"  Expected: {r['expected']}")
            print(f"  Actual:   {r['actual']}")

    print("-" * 85)
    matched_count = sum(1 for r in records if r["status"] == "OK")
    mismatch_count = sum(1 for r in records if r["status"] == "MISMATCH")
    missing_count = sum(1 for r in records if r["status"] == "MISSING")
    print(
        f"Summary: {matched_count} Valid, {mismatch_count} Mismatch, {missing_count} Missing (Total: {len(records)})\n"
    )

    if args.update and (has_mismatch or has_missing):
        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
        print(
            "[Manifest] Successfully updated tools_manifest.json with verified hashes."
        )

    if has_mismatch or has_missing:
        sys.exit(1)


if __name__ == "__main__":
    main()
