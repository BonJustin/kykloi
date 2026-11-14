#!/usr/bin/env python3
"""
system/build/build_site.py - Zero-Dependency Deterministic SSG Compiler.
Part of Project Kykloi (v0.5.0).
"""

import argparse
import base64
import concurrent.futures
import getpass
import hashlib
import json
import logging
import os
import platform
import re
import shutil
import sqlite3
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# ===========================================================================
# 1. PURE-PYTHON AES-256-GCM ENGINE & TABLE-DRIVEN GHASH
# ===========================================================================

S_BOX = [
    0x63,
    0x7C,
    0x77,
    0x7B,
    0xF2,
    0x6B,
    0x6F,
    0xC5,
    0x30,
    0x01,
    0x67,
    0x2B,
    0xFE,
    0xD7,
    0xAB,
    0x76,
    0xCA,
    0x82,
    0xC9,
    0x7D,
    0xFA,
    0x59,
    0x47,
    0xF0,
    0xAD,
    0xD4,
    0xA2,
    0xAF,
    0x9C,
    0xA4,
    0x72,
    0xC0,
    0xB7,
    0xFD,
    0x93,
    0x26,
    0x36,
    0x3F,
    0xF7,
    0xCC,
    0x34,
    0xA5,
    0xE5,
    0xF1,
    0x71,
    0xD8,
    0x31,
    0x15,
    0x04,
    0xC7,
    0x23,
    0xC3,
    0x18,
    0x96,
    0x05,
    0x9A,
    0x07,
    0x12,
    0x80,
    0xE2,
    0xEB,
    0x27,
    0xB2,
    0x75,
    0x09,
    0x83,
    0x2C,
    0x1A,
    0x1B,
    0x6E,
    0x5A,
    0xA0,
    0x52,
    0x3B,
    0xD6,
    0xB3,
    0x29,
    0xE3,
    0x2F,
    0x84,
    0x53,
    0xD1,
    0x00,
    0xED,
    0x20,
    0xFC,
    0xB1,
    0x5B,
    0x6A,
    0xCB,
    0xBE,
    0x39,
    0x4A,
    0x4C,
    0x58,
    0xCF,
    0xD0,
    0xEF,
    0xAA,
    0xFB,
    0x43,
    0x4D,
    0x33,
    0x85,
    0x45,
    0xF9,
    0x02,
    0x7F,
    0x50,
    0x3C,
    0x9F,
    0xA8,
    0x51,
    0xA3,
    0x40,
    0x8F,
    0x92,
    0x9D,
    0x38,
    0xF5,
    0xBC,
    0xB6,
    0xDA,
    0x21,
    0x10,
    0xFF,
    0xF3,
    0xD2,
    0xCD,
    0x0C,
    0x13,
    0xEC,
    0x5F,
    0x97,
    0x44,
    0x17,
    0xC4,
    0xA7,
    0x7E,
    0x3D,
    0x64,
    0x5D,
    0x19,
    0x73,
    0x60,
    0x81,
    0x4F,
    0xDC,
    0x22,
    0x2A,
    0x90,
    0x88,
    0x46,
    0xEE,
    0xB8,
    0x14,
    0xDE,
    0x5E,
    0x0B,
    0xDB,
    0xE0,
    0x32,
    0x3A,
    0x0A,
    0x49,
    0x06,
    0x24,
    0x5C,
    0xC2,
    0xD3,
    0xAC,
    0x62,
    0x91,
    0x95,
    0xE4,
    0x79,
    0xE7,
    0xC8,
    0x37,
    0x6D,
    0x8D,
    0xD5,
    0x4E,
    0xA9,
    0x6C,
    0x56,
    0xF4,
    0xEA,
    0x65,
    0x7A,
    0xAE,
    0x08,
    0xBA,
    0x78,
    0x25,
    0x2E,
    0x1C,
    0xA6,
    0xB4,
    0xC6,
    0xE8,
    0xDD,
    0x74,
    0x1F,
    0x4B,
    0xBD,
    0x8B,
    0x8A,
    0x70,
    0x3E,
    0xB5,
    0x66,
    0x48,
    0x03,
    0xF6,
    0x0E,
    0x61,
    0x35,
    0x57,
    0xB9,
    0x86,
    0xC1,
    0x1D,
    0x9E,
    0xE1,
    0xF8,
    0x98,
    0x11,
    0x69,
    0xD9,
    0x8E,
    0x94,
    0x9B,
    0x1E,
    0x87,
    0xE9,
    0xCE,
    0x55,
    0x28,
    0xDF,
    0x8C,
    0xA1,
    0x89,
    0x0D,
    0xBF,
    0xE6,
    0x42,
    0x68,
    0x41,
    0x99,
    0x2D,
    0x0F,
    0xB0,
    0x54,
    0xBB,
    0x16,
]

RCON = [0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36]


def _xtime(a: int) -> int:
    return ((a << 1) ^ 0x1B) & 0xFF if (a & 0x80) else (a << 1)


def _key_expansion_256(key: bytes) -> list[int]:
    w = list(key)
    for i in range(8, 60):
        temp = w[(i - 1) * 4 : i * 4]
        if i % 8 == 0:
            temp = [S_BOX[temp[1]], S_BOX[temp[2]], S_BOX[temp[3]], S_BOX[temp[0]]]
            temp[0] ^= RCON[i // 8]
        elif i % 8 == 4:
            temp = [S_BOX[x] for x in temp]
        for j in range(4):
            w.append(w[(i - 8) * 4 + j] ^ temp[j])
    return w


def _cipher_block(state_in: bytes | list[int], round_keys: list[int]) -> bytes:
    state = list(state_in)
    for i in range(16):
        state[i] ^= round_keys[i]

    for r in range(1, 14):
        rk = r * 16
        s0, s1, s2, s3 = (
            S_BOX[state[0]],
            S_BOX[state[5]],
            S_BOX[state[10]],
            S_BOX[state[15]],
        )
        s4, s5, s6, s7 = (
            S_BOX[state[4]],
            S_BOX[state[9]],
            S_BOX[state[14]],
            S_BOX[state[3]],
        )
        s8, s9, s10, s11 = (
            S_BOX[state[8]],
            S_BOX[state[13]],
            S_BOX[state[2]],
            S_BOX[state[7]],
        )
        s12, s13, s14, s15 = (
            S_BOX[state[12]],
            S_BOX[state[1]],
            S_BOX[state[6]],
            S_BOX[state[11]],
        )

        state[0] = _xtime(s0 ^ s1) ^ s1 ^ s2 ^ s3 ^ round_keys[rk]
        state[1] = _xtime(s1 ^ s2) ^ s2 ^ s3 ^ s0 ^ round_keys[rk + 1]
        state[2] = _xtime(s2 ^ s3) ^ s3 ^ s0 ^ s1 ^ round_keys[rk + 2]
        state[3] = _xtime(s3 ^ s0) ^ s0 ^ s1 ^ s2 ^ round_keys[rk + 3]

        state[4] = _xtime(s4 ^ s5) ^ s5 ^ s6 ^ s7 ^ round_keys[rk + 4]
        state[5] = _xtime(s5 ^ s6) ^ s6 ^ s7 ^ s4 ^ round_keys[rk + 5]
        state[6] = _xtime(s6 ^ s7) ^ s7 ^ s4 ^ s5 ^ round_keys[rk + 6]
        state[7] = _xtime(s7 ^ s4) ^ s4 ^ s5 ^ s6 ^ round_keys[rk + 7]

        state[8] = _xtime(s8 ^ s9) ^ s9 ^ s10 ^ s11 ^ round_keys[rk + 8]
        state[9] = _xtime(s9 ^ s10) ^ s10 ^ s11 ^ s8 ^ round_keys[rk + 9]
        state[10] = _xtime(s10 ^ s11) ^ s11 ^ s8 ^ s9 ^ round_keys[rk + 10]
        state[11] = _xtime(s11 ^ s8) ^ s8 ^ s9 ^ s10 ^ round_keys[rk + 11]

        state[12] = _xtime(s12 ^ s13) ^ s13 ^ s14 ^ s15 ^ round_keys[rk + 12]
        state[13] = _xtime(s13 ^ s14) ^ s14 ^ s15 ^ s12 ^ round_keys[rk + 13]
        state[14] = _xtime(s14 ^ s15) ^ s15 ^ s12 ^ s13 ^ round_keys[rk + 14]
        state[15] = _xtime(s15 ^ s12) ^ s12 ^ s13 ^ s14 ^ round_keys[rk + 15]

    rk = 224
    out = bytearray(16)
    out[0] = S_BOX[state[0]] ^ round_keys[rk]
    out[1] = S_BOX[state[5]] ^ round_keys[rk + 1]
    out[2] = S_BOX[state[10]] ^ round_keys[rk + 2]
    out[3] = S_BOX[state[15]] ^ round_keys[rk + 3]
    out[4] = S_BOX[state[4]] ^ round_keys[rk + 4]
    out[5] = S_BOX[state[9]] ^ round_keys[rk + 5]
    out[6] = S_BOX[state[14]] ^ round_keys[rk + 6]
    out[7] = S_BOX[state[3]] ^ round_keys[rk + 7]
    out[8] = S_BOX[state[8]] ^ round_keys[rk + 8]
    out[9] = S_BOX[state[13]] ^ round_keys[rk + 9]
    out[10] = S_BOX[state[2]] ^ round_keys[rk + 10]
    out[11] = S_BOX[state[7]] ^ round_keys[rk + 11]
    out[12] = S_BOX[state[12]] ^ round_keys[rk + 12]
    out[13] = S_BOX[state[1]] ^ round_keys[rk + 13]
    out[14] = S_BOX[state[6]] ^ round_keys[rk + 14]
    out[15] = S_BOX[state[11]] ^ round_keys[rk + 15]

    return bytes(out)


def _ghash_mult(x: int, y: int) -> int:
    r = 0xE1000000000000000000000000000000
    z = 0
    v = x
    for i in range(128):
        if (y >> (127 - i)) & 1:
            z ^= v
        if v & 1:
            v = (v >> 1) ^ r
        else:
            v >>= 1
    return z


def _init_ghash_tables(h: int) -> list[list[int]]:
    tables: list[list[int]] = []
    for j in range(16):
        shift = 8 * (15 - j)
        basis = [_ghash_mult((1 << bit) << shift, h) for bit in range(8)]
        table = [0] * 256
        for b in range(1, 256):
            low_bit = (b & -b).bit_length() - 1
            table[b] = table[b & (b - 1)] ^ basis[low_bit]
        tables.append(table)
    return tables


def _ghash_block(t: list[list[int]], x: int) -> int:
    return (
        t[0][(x >> 120) & 0xFF]
        ^ t[1][(x >> 112) & 0xFF]
        ^ t[2][(x >> 104) & 0xFF]
        ^ t[3][(x >> 96) & 0xFF]
        ^ t[4][(x >> 88) & 0xFF]
        ^ t[5][(x >> 80) & 0xFF]
        ^ t[6][(x >> 72) & 0xFF]
        ^ t[7][(x >> 64) & 0xFF]
        ^ t[8][(x >> 56) & 0xFF]
        ^ t[9][(x >> 48) & 0xFF]
        ^ t[10][(x >> 40) & 0xFF]
        ^ t[11][(x >> 32) & 0xFF]
        ^ t[12][(x >> 24) & 0xFF]
        ^ t[13][(x >> 16) & 0xFF]
        ^ t[14][(x >> 8) & 0xFF]
        ^ t[15][x & 0xFF]
    )


def pure_aes_gcm_encrypt(
    key: bytes, iv: bytes, plaintext: bytes
) -> tuple[bytes, bytes]:
    if len(key) != 32 or len(iv) != 12:
        raise ValueError("Key must be 32 bytes and IV must be 12 bytes.")

    round_keys = _key_expansion_256(key)
    h_bytes = _cipher_block(bytes(16), round_keys)
    h = int.from_bytes(h_bytes, byteorder="big")
    ghash_tables = _init_ghash_tables(h)

    j0 = iv + b"\x00\x00\x00\x01"
    ciphertext = bytearray()
    num_blocks = (len(plaintext) + 15) // 16

    for i in range(num_blocks):
        ctr_val = (2 + i) & 0xFFFFFFFF
        ctr_block = iv + ctr_val.to_bytes(4, byteorder="big")
        keystream = _cipher_block(ctr_block, round_keys)
        chunk = plaintext[i * 16 : (i + 1) * 16]
        for p_b, k_b in zip(chunk, keystream):
            ciphertext.append(p_b ^ k_b)

    ciphertext_bytes = bytes(ciphertext)
    pad_len = (16 - (len(ciphertext_bytes) % 16)) % 16
    padded_ct = ciphertext_bytes + (b"\x00" * pad_len)

    s = 0
    for i in range(0, len(padded_ct), 16):
        block_int = int.from_bytes(padded_ct[i : i + 16], byteorder="big")
        s = _ghash_block(ghash_tables, s ^ block_int)

    len_block_int = len(ciphertext_bytes) * 8
    s = _ghash_block(ghash_tables, s ^ len_block_int)

    tag_mask = _cipher_block(j0, round_keys)
    tag = bytes(a ^ b for a, b in zip(s.to_bytes(16, "big"), tag_mask))

    return ciphertext_bytes, tag


def verify_cryptographic_engine():
    kat_key = bytes.fromhex("00" * 32)
    kat_iv = bytes.fromhex("00" * 12)
    kat_pt = bytes.fromhex("00" * 16)
    expected_ct = bytes.fromhex("cea7403d4d606b6e074ec5d3baf39d18")
    expected_tag = bytes.fromhex("d0d1c8a799996bf0265b98b5d48ab919")

    ct, tag = pure_aes_gcm_encrypt(kat_key, kat_iv, kat_pt)
    if ct != expected_ct or tag != expected_tag:
        raise RuntimeError("CRITICAL: NIST KAT verification failed for AES-GCM engine.")


# ===========================================================================
# 2. PATHS & HYGIENE
# ===========================================================================

JUNK_DIR_NAMES = {
    ".obsidian",
    ".trash",
    ".zettlr",
    ".logseq",
    "logseq",
    ".git",
    ".vscode",
    ".idea",
}

JUNK_FILE_EXTENSIONS = {".ztr-directory", ".ds_store", "thumbs.db", "desktop.ini"}


def is_junk_path(path: Path, root: Optional[Path] = None) -> bool:
    base = root if root is not None else PROJECT_ROOT
    try:
        rel_parts = path.relative_to(base).parts
    except ValueError:
        rel_parts = path.parts
    for part in rel_parts:
        if part.lower() in JUNK_DIR_NAMES or part.startswith("."):
            return True
    return path.name.lower() in JUNK_FILE_EXTENSIONS


APP_DIR = Path(__file__).resolve().parent
SYSTEM_DIR = APP_DIR.parent
PROJECT_ROOT = SYSTEM_DIR.parent
SRC = PROJECT_ROOT / "content"
DST = PROJECT_ROOT / "dist"

DEFAULTS_YAML = APP_DIR / "pandoc_md_to_static_html.yaml"
DEFAULT_TEMPLATE = APP_DIR / "templates" / "md_to_static_html.html"
LUA_FILTER = APP_DIR / "translate_links.lua"
MANIFEST_FILE = APP_DIR / ".build_manifest.json"
SEARCH_DB_FILE = DST / "search.db"

CITATION_PATTERN = re.compile(
    r"(?:\[@[a-zA-Z0-9_:.#$%&-]+|(?<!\w)@[a-zA-Z0-9_:.#$%&-]+)"
)


@dataclass(frozen=True)
class CompileTask:
    md_path: Path
    out_path: Path
    template_path: Path
    relative_root: str
    doc_title: str
    defaults_yaml: Path
    lua_filter: Path
    bibliography_path: Optional[Path]
    is_secure: bool
    passphrase: Optional[str]
    dry_run: bool
    pandoc_bin: str


@dataclass(frozen=True)
class EncryptBlobTask:
    src_path: Path
    dst_path: Path
    passphrase: str
    dry_run: bool


def parse_args():
    p = argparse.ArgumentParser(
        description="Deterministic Archival Static Site Generator (Zero-Dependency Cryptography & SQLite FTS5)."
    )
    p.add_argument(
        "--clean", action="store_true", help="Purge destination directory and manifest."
    )
    p.add_argument("--dry-run", action="store_true", help="Simulate build pipeline.")
    p.add_argument(
        "--verbose", action="store_true", help="Output granular diagnostic logs."
    )
    p.add_argument(
        "--workers",
        type=int,
        default=os.cpu_count() or 4,
        help="Worker concurrency pool.",
    )
    p.add_argument(
        "--password",
        type=str,
        default=os.environ.get("KYKLOI_ENCRYPT_KEY"),
        help="Secure passphrase.",
    )
    return p.parse_args()


# ===========================================================================
# 3. BINARY RESOLUTION & CRYPTOGRAPHIC UTILITIES
# ===========================================================================


def resolve_pandoc_binary(root_dir: Path) -> str:
    """Resolves the Pandoc executable.
    Prioritizes local bundled binaries in system/tools/pandoc/ over host system PATH.
    Includes defensive fallback for Linux systems mounting exFAT with noexec.
    """
    system = platform.system().lower()
    machine = platform.machine().lower()

    if machine in ("x86_64", "amd64"):
        arch = "x86_64"
    elif machine in ("arm64", "aarch64"):
        arch = "arm64"
    else:
        arch = machine

    base_bin = root_dir / "system" / "tools" / "pandoc"
    candidate = None

    if system == "linux" and arch == "x86_64":
        candidate = base_bin / "linux-x86_64" / "pandoc"
    elif system == "darwin":
        candidate = base_bin / f"macos-{arch}" / "pandoc"
        if not candidate.exists() and arch == "arm64":
            candidate = base_bin / "macos-x86_64" / "pandoc"
    elif system == "windows":
        candidate = base_bin / "windows-x86_64" / "pandoc.exe"

    if candidate and candidate.is_file():
        # Defensive Linux exFAT noexec mitigation
        if system == "linux":
            if not os.access(candidate, os.X_OK):
                try:
                    candidate.chmod(0o755)
                except OSError:
                    pass

            if not os.access(candidate, os.X_OK):
                tmp_dir = Path("/tmp/kykloi_bin")
                tmp_dir.mkdir(parents=True, exist_ok=True)
                shadow_bin = tmp_dir / "pandoc"
                if (
                    not shadow_bin.exists()
                    or shadow_bin.stat().st_size != candidate.stat().st_size
                ):
                    shutil.copy2(candidate, shadow_bin)
                    shadow_bin.chmod(0o755)
                return str(shadow_bin.resolve())

        return str(candidate.resolve())

    # Fall back to host system PATH
    sys_pandoc = shutil.which("pandoc")
    if sys_pandoc:
        return sys_pandoc

    raise FileNotFoundError(
        f"Pandoc executable not found. Checked local directory '{base_bin}' and system PATH."
    )


def compute_file_hash(path: Path) -> str:
    hasher = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()
    except OSError:
        return ""


def compute_global_dependencies_hash(bibliography_file: Optional[Path] = None) -> str:
    hasher = hashlib.sha256()
    tracked = [DEFAULTS_YAML, LUA_FILTER, DEFAULT_TEMPLATE, Path(__file__).resolve()]
    if bibliography_file and bibliography_file.is_file():
        tracked.append(bibliography_file)

    for f in tracked:
        if f.is_file():
            hasher.update(f.name.encode("utf-8"))
            hasher.update(compute_file_hash(f).encode("utf-8"))
    return hasher.hexdigest()


def is_secure_path(path: Path, src_root: Path) -> bool:
    try:
        rel = path.relative_to(src_root)
        return "secure" in rel.parts
    except ValueError:
        return False


def compute_passphrase_fingerprint(passphrase: str) -> str:
    salt = b"kykloi:key_rotation_fingerprint:v1"
    return hashlib.sha256(salt + passphrase.encode("utf-8")).hexdigest()


def derive_key(passphrase: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac(
        "sha256", passphrase.encode("utf-8"), salt, 100_000, dklen=32
    )


def encrypt_payload(html_content: str, passphrase: str) -> str:
    salt = os.urandom(16)
    iv = os.urandom(12)
    key = derive_key(passphrase, salt)
    pt_bytes = html_content.encode("utf-8")
    ciphertext, tag = pure_aes_gcm_encrypt(key, iv, pt_bytes)
    envelope = salt + iv + ciphertext + tag
    return base64.b64encode(envelope).decode("ascii")


def encrypt_binary_file(src_path: Path, dst_path: Path, passphrase: str) -> None:
    with open(src_path, "rb") as f:
        plaintext = f.read()

    salt = os.urandom(16)
    iv = os.urandom(12)
    key = derive_key(passphrase, salt)
    ciphertext, tag = pure_aes_gcm_encrypt(key, iv, plaintext)
    envelope = salt + iv + ciphertext + tag

    dst_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = dst_path.with_suffix(dst_path.suffix + ".tmp")
    with open(tmp_path, "wb") as f:
        f.write(envelope)
    tmp_path.replace(dst_path)


def load_manifest(manifest_path: Path) -> dict:
    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def save_manifest(manifest_path: Path, manifest: dict, dry_run: bool):
    if dry_run:
        return
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = manifest_path.with_suffix(".json.tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
    tmp_path.replace(manifest_path)


# ===========================================================================
# 4. FRONTMATTER & METADATA-ONLY SQLITE FTS5
# ===========================================================================


def parse_frontmatter_robust(text: str) -> dict:
    if not text.startswith("---"):
        return {}

    lines = text.splitlines()
    yaml_lines = []
    for line in lines[1:]:
        if line.strip() in ("---", "..."):
            break
        yaml_lines.append(line)

    result = {}
    current_key = None
    multiline_mode = None
    multiline_accumulator = []

    def commit_multiline():
        nonlocal current_key, multiline_mode, multiline_accumulator
        if current_key and multiline_mode:
            val = (
                "\n".join(multiline_accumulator)
                if multiline_mode == "|"
                else " ".join(" ".join(multiline_accumulator).split())
            )
            result[current_key] = val
        multiline_mode = None
        multiline_accumulator = []

    for line in yaml_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip())

        if multiline_mode and indent > 0:
            multiline_accumulator.append(stripped)
            continue
        elif multiline_mode and indent == 0:
            commit_multiline()

        if stripped.startswith("- ") and current_key:
            item = stripped[2:].strip().strip("'\"")
            if not isinstance(result.get(current_key), list):
                result[current_key] = []
            result[current_key].append(item)
            continue

        if ":" in stripped:
            key, raw_val = stripped.split(":", 1)
            key = key.strip()
            raw_val = raw_val.strip()
            current_key = key

            if raw_val in ("|", ">"):
                multiline_mode = raw_val
                multiline_accumulator = []
                continue

            if raw_val.startswith("[") and raw_val.endswith("]"):
                inner = raw_val[1:-1].strip()
                result[key] = (
                    [x.strip().strip("'\"") for x in inner.split(",") if x.strip()]
                    if inner
                    else []
                )
                continue

            if (raw_val.startswith('"') and raw_val.endswith('"')) or (
                raw_val.startswith("'") and raw_val.endswith("'")
            ):
                raw_val = raw_val[1:-1]

            result[key] = raw_val

    commit_multiline()
    return result


def extract_metadata_fast(md_path: Path) -> tuple[Path, dict[str, str], bool]:
    meta = {"title": "", "keywords": "", "date_edtf": ""}
    has_citations = False
    try:
        with open(md_path, "r", encoding="utf-8") as f:
            full_content = f.read()

        parsed = parse_frontmatter_robust(full_content[:16384])
        meta["title"] = str(parsed.get("title", "")).strip()
        meta["date_edtf"] = str(
            parsed.get("date_edtf") or parsed.get("date", "")
        ).strip()

        keywords_val = parsed.get("keywords", "")
        if isinstance(keywords_val, list):
            meta["keywords"] = " ".join(str(k).strip() for k in keywords_val)
        elif isinstance(keywords_val, str):
            meta["keywords"] = keywords_val.strip()

        has_citations = bool(CITATION_PATTERN.search(full_content))

    except OSError as err:
        logging.warning("Error reading %s: %s", md_path.name, err)

    if not meta["title"]:
        clean_stem = md_path.stem
        parts = clean_stem.split(maxsplit=1)
        if len(parts) > 1 and parts[0].isdigit() and len(parts[0]) in (8, 12, 14):
            clean_stem = parts[1]
        meta["title"] = clean_stem.replace("-", " ").replace("_", " ").title()

    return md_path, meta, has_citations


def build_sqlite_search_index(
    records: list[dict], out_path: Path, dry_run: bool
) -> None:
    if dry_run:
        return

    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = out_path.with_suffix(".tmp.db")
    if tmp_path.exists():
        tmp_path.unlink()

    try:
        conn = sqlite3.connect(tmp_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA page_size = 4096;")
        cursor.execute("PRAGMA journal_mode = OFF;")
        cursor.execute("PRAGMA synchronous = OFF;")

        cursor.execute(
            """
            CREATE VIRTUAL TABLE docs_fts USING fts5(
                title,
                keywords,
                date_edtf,
                url UNINDEXED,
                tokenize='porter unicode61'
            );
            """
        )

        cursor.executemany(
            """
            INSERT INTO docs_fts (title, keywords, date_edtf, url)
            VALUES (?, ?, ?, ?);
            """,
            [
                (
                    r.get("title", ""),
                    r.get("keywords", ""),
                    r.get("date_edtf", ""),
                    r.get("url", ""),
                )
                for r in records
            ],
        )

        conn.commit()
        cursor.execute("INSERT INTO docs_fts(docs_fts) VALUES('optimize');")
        conn.commit()
        cursor.execute("VACUUM;")
        conn.close()

        tmp_path.replace(out_path)
        logging.info(
            "Compiled SQLite FTS5 index (%d records, %d bytes).",
            len(records),
            out_path.stat().st_size,
        )

    except Exception:
        if tmp_path.exists():
            tmp_path.unlink()
        raise


# ===========================================================================
# 5. COMPILATION WORKERS
# ===========================================================================


def compile_markdown_worker(task: CompileTask) -> tuple[Path, bool, Optional[str]]:
    if task.dry_run:
        return task.md_path, True, None

    css_files = ["assets/css/pico.css", "assets/css/style.css"]

    if not task.is_secure:
        cmd = [
            task.pandoc_bin,
            str(task.md_path),
            "--defaults",
            str(task.defaults_yaml),
            "--template",
            str(task.template_path),
            "--lua-filter",
            str(task.lua_filter),
            "-V",
            f"relative_root={task.relative_root}",
            "-V",
            f"pagetitle={task.doc_title}",
            f"--katex={task.relative_root}assets/katex/",
            "-o",
            str(task.out_path),
        ]
        if task.bibliography_path:
            cmd.extend(
                [
                    "--citeproc",
                    f"--bibliography={str(task.bibliography_path.resolve())}",
                ]
            )

        for css in css_files:
            cmd.extend(["--css", f"{task.relative_root}{css}"])

        task.out_path.parent.mkdir(parents=True, exist_ok=True)
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            return task.md_path, False, res.stderr.strip()
        return task.md_path, True, None

    if not task.passphrase:
        return (
            task.md_path,
            False,
            "Cannot compile secure file: No passphrase provided.",
        )

    env = os.environ.copy()
    env["KYKLOI_SECURE_BUILD"] = "1"

    body_cmd = [
        task.pandoc_bin,
        str(task.md_path),
        "--defaults",
        str(task.defaults_yaml),
        "--lua-filter",
        str(task.lua_filter),
        f"--katex={task.relative_root}assets/katex/",
    ]
    if task.bibliography_path:
        body_cmd.extend(
            ["--citeproc", f"--bibliography={str(task.bibliography_path.resolve())}"]
        )

    body_res = subprocess.run(body_cmd, capture_output=True, text=True, env=env)
    if body_res.returncode != 0:
        return task.md_path, False, f"Body compilation error: {body_res.stderr.strip()}"

    try:
        ciphertext_b64 = encrypt_payload(body_res.stdout, task.passphrase)
    except Exception as e:
        return task.md_path, False, f"Encryption failed: {e}"

    envelope_cmd = [
        task.pandoc_bin,
        str(task.md_path),
        "--defaults",
        str(task.defaults_yaml),
        "--template",
        str(task.template_path),
        f"--katex={task.relative_root}assets/katex/",
        "-V",
        f"relative_root={task.relative_root}",
        "-V",
        f"pagetitle={task.doc_title}",
        "-V",
        "encrypted=true",
    ]
    for css in css_files:
        envelope_cmd.extend(["--css", f"{task.relative_root}{css}"])

    envelope_res = subprocess.run(envelope_cmd, capture_output=True, text=True)
    if envelope_res.returncode != 0:
        return (
            task.md_path,
            False,
            f"Envelope generation error: {envelope_res.stderr.strip()}",
        )

    try:
        final_html = envelope_res.stdout.replace(
            "__KYKLOI_ENCRYPTED_PAYLOAD__", ciphertext_b64
        )
        task.out_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_out = task.out_path.with_suffix(task.out_path.suffix + ".tmp")
        with open(tmp_out, "w", encoding="utf-8") as f:
            f.write(final_html)
        tmp_out.replace(task.out_path)
    except OSError as e:
        return task.md_path, False, f"Disk write error: {e}"

    return task.md_path, True, None


def encrypt_blob_worker(task: EncryptBlobTask) -> tuple[Path, bool, Optional[str]]:
    if task.dry_run:
        return task.src_path, True, None

    try:
        encrypt_binary_file(task.src_path, task.dst_path, task.passphrase)
        return task.src_path, True, None
    except Exception as exc:
        return task.src_path, False, str(exc)


def prune_orphans(dst_dir: Path, expected_files: set[Path], dry_run: bool) -> int:
    if not dst_dir.exists():
        return 0

    orphans_removed = 0
    for item in list(dst_dir.rglob("*")):
        if item.is_file() and item.resolve() not in expected_files:
            if not dry_run:
                item.unlink()
            orphans_removed += 1

    for dirpath in sorted(dst_dir.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if dirpath.is_dir() and not any(dirpath.iterdir()):
            if not dry_run:
                dirpath.rmdir()

    return orphans_removed


# ===========================================================================
# 6. PIPELINE ORCHESTRATION
# ===========================================================================


def find_vault_bibliography(src_root: Path) -> Optional[Path]:
    for candidate in ["references.bib", "library.bib", "bibliography.bib"]:
        p = src_root / candidate
        if p.is_file():
            return p
    return None


def main():
    args = parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    try:
        verify_cryptographic_engine()
    except RuntimeError as err:
        logging.critical(str(err))
        sys.exit(1)

    try:
        pandoc_bin = resolve_pandoc_binary(PROJECT_ROOT)
        logging.info("Resolved Pandoc executable: %s", pandoc_bin)
    except FileNotFoundError as err:
        logging.critical(str(err))
        sys.exit(1)

    for path, desc in [
        (SRC, "Source directory"),
        (DEFAULTS_YAML, "Pandoc defaults configuration"),
        (DEFAULT_TEMPLATE, "Content template"),
        (LUA_FILTER, "Lua link translation filter"),
    ]:
        if not path.exists():
            logging.error("Configuration error: %s missing at %s", desc, path)
            sys.exit(1)

    if args.clean:
        if DST.exists() and not args.dry_run:
            shutil.rmtree(DST)
        if MANIFEST_FILE.exists() and not args.dry_run:
            MANIFEST_FILE.unlink()

    DST.mkdir(parents=True, exist_ok=True)

    old_manifest = load_manifest(MANIFEST_FILE)
    new_manifest: dict = {}

    central_bib = find_vault_bibliography(SRC)
    current_global_hash = compute_global_dependencies_hash(central_bib)
    new_manifest["__GLOBAL_DEPENDENCIES__"] = current_global_hash
    global_deps_changed = (
        old_manifest.get("__GLOBAL_DEPENDENCIES__") != current_global_hash
    )

    if global_deps_changed:
        logging.info("Core templates/configurations modified. Recompiling site.")

    expected_outputs: set[Path] = set()
    compile_tasks: list[CompileTask] = []
    encrypt_blob_tasks: list[EncryptBlobTask] = []

    all_content_files = [
        p for p in SRC.rglob("*") if p.is_file() and not is_junk_path(p)
    ]
    md_files = sorted([p for p in all_content_files if p.suffix.lower() == ".md"])

    has_secure_files = any(is_secure_path(p, SRC) for p in all_content_files)

    passphrase = args.password
    if has_secure_files and not passphrase and not args.dry_run:
        if not sys.stdin.isatty():
            logging.error(
                "Passphrase required for /secure/ notes in non-interactive environment. "
                "Provide --password or set KYKLOI_ENCRYPT_KEY."
            )
            sys.exit(1)

        try:
            passphrase = getpass.getpass("Enter passphrase for /secure/ notes: ")
        except (OSError, EOFError):
            logging.error("Terminal disconnected: Unable to prompt for passphrase.")
            sys.exit(1)

        if not passphrase:
            logging.error("Passphrase required for secure notes.")
            sys.exit(1)

    passphrase_changed = False
    if has_secure_files and passphrase:
        current_key_fingerprint = compute_passphrase_fingerprint(passphrase)
        new_manifest["__PASSPHRASE_FINGERPRINT__"] = current_key_fingerprint
        old_key_fingerprint = old_manifest.get("__PASSPHRASE_FINGERPRINT__")
        if old_manifest and old_key_fingerprint != current_key_fingerprint:
            passphrase_changed = True
            logging.info("Passphrase rotation detected. Re-encrypting payloads.")

    asset_sync_jobs: list[tuple[Path, Path]] = []

    for p in all_content_files:
        if p.suffix.lower() == ".md":
            continue

        rel_src = p.relative_to(SRC)
        h = compute_file_hash(p)

        if is_secure_path(p, SRC):
            target = DST / rel_src.with_name(rel_src.name + ".enc")
            expected_outputs.add(target.resolve())
            manifest_key = f"secure_blob:{rel_src.as_posix()}"
            new_manifest[manifest_key] = h

            if (
                not target.exists()
                or passphrase_changed
                or old_manifest.get(manifest_key) != h
            ):
                encrypt_blob_tasks.append(
                    EncryptBlobTask(
                        src_path=p,
                        dst_path=target,
                        passphrase=passphrase or "",
                        dry_run=args.dry_run,
                    )
                )
        else:
            target = DST / rel_src
            expected_outputs.add(target.resolve())
            manifest_key = f"media:{rel_src.as_posix()}"
            new_manifest[manifest_key] = h
            if not target.exists() or old_manifest.get(manifest_key) != h:
                asset_sync_jobs.append((p, target))

    metadata_extraction_jobs: list[Path] = []
    file_metadata_map: dict[Path, dict[str, str]] = {}
    doc_has_citations_map: dict[Path, bool] = {}

    for md in md_files:
        rel = md.relative_to(SRC)
        manifest_key = f"content:{rel.as_posix()}"
        meta_cache_key = f"meta:{rel.as_posix()}"
        out = DST / rel.with_suffix(".html")
        expected_outputs.add(out.resolve())

        current_md_hash = compute_file_hash(md)
        new_manifest[manifest_key] = current_md_hash

        depth = len(rel.parent.parts) if rel.parent != Path(".") else 0
        relative_root = ("../" * depth) if depth > 0 else ""

        is_secure = is_secure_path(md, SRC)
        md_content_changed = old_manifest.get(manifest_key) != current_md_hash

        is_dirty = (
            not out.exists()
            or global_deps_changed
            or md_content_changed
            or (is_secure and passphrase_changed)
        )

        cached_meta = old_manifest.get(meta_cache_key)
        meta_is_dirty = (
            global_deps_changed
            or md_content_changed
            or not isinstance(cached_meta, dict)
        )

        if not meta_is_dirty and isinstance(cached_meta, dict):
            file_metadata_map[md] = cached_meta
            doc_has_citations_map[md] = cached_meta.get("__has_citations__", False)
            new_manifest[meta_cache_key] = cached_meta
        else:
            metadata_extraction_jobs.append(md)

        if is_dirty:
            compile_tasks.append(
                CompileTask(
                    md_path=md,
                    out_path=out,
                    template_path=DEFAULT_TEMPLATE,
                    relative_root=relative_root,
                    doc_title="",
                    defaults_yaml=DEFAULTS_YAML,
                    lua_filter=LUA_FILTER,
                    bibliography_path=None,
                    is_secure=is_secure,
                    passphrase=passphrase,
                    dry_run=args.dry_run,
                    pandoc_bin=pandoc_bin,
                )
            )

    if metadata_extraction_jobs:
        for md_path in metadata_extraction_jobs:
            _, extracted_meta, has_cites = extract_metadata_fast(md_path)
            extracted_meta["__has_citations__"] = has_cites
            file_metadata_map[md_path] = extracted_meta
            doc_has_citations_map[md_path] = has_cites
            rel = md_path.relative_to(SRC)
            new_manifest[f"meta:{rel.as_posix()}"] = extracted_meta

    final_compile_tasks: list[CompileTask] = []
    for t in compile_tasks:
        needs_bib = (
            central_bib
            if (central_bib and doc_has_citations_map.get(t.md_path, False))
            else None
        )
        meta = file_metadata_map[t.md_path]
        final_compile_tasks.append(
            CompileTask(
                md_path=t.md_path,
                out_path=t.out_path,
                template_path=t.template_path,
                relative_root=t.relative_root,
                doc_title=meta["title"],
                defaults_yaml=t.defaults_yaml,
                lua_filter=t.lua_filter,
                bibliography_path=needs_bib,
                is_secure=t.is_secure,
                passphrase=t.passphrase,
                dry_run=t.dry_run,
                pandoc_bin=pandoc_bin,
            )
        )
    compile_tasks = final_compile_tasks

    search_records: list[dict] = []
    for idx, md in enumerate(md_files):
        rel = md.relative_to(SRC)
        clean_url = rel.with_suffix(".html").as_posix().lstrip("/")
        meta = file_metadata_map[md]
        search_records.append(
            {
                "id": idx + 1,
                "title": meta["title"],
                "keywords": meta["keywords"],
                "date_edtf": meta["date_edtf"],
                "url": clean_url,
            }
        )

    expected_outputs.add(SEARCH_DB_FILE.resolve())

    # Static Assets
    for folder_name, manifest_prefix in [
        ("assets", "functional_asset"),
        ("root", "root_asset"),
    ]:
        src_dir = APP_DIR / folder_name
        if not src_dir.exists():
            continue
        for p in src_dir.rglob("*"):
            if p.is_file() and not is_junk_path(p):
                rel_p = p.relative_to(src_dir)
                target = DST / ("assets" / rel_p if folder_name == "assets" else rel_p)
                expected_outputs.add(target.resolve())
                manifest_key = f"{manifest_prefix}:{rel_p.as_posix()}"
                h = compute_file_hash(p)
                new_manifest[manifest_key] = h
                if not target.exists() or old_manifest.get(manifest_key) != h:
                    asset_sync_jobs.append((p, target))

    orphans_pruned = prune_orphans(
        dst_dir=DST, expected_files=expected_outputs, dry_run=args.dry_run
    )
    if orphans_pruned:
        logging.info("Pruned %d orphaned artifact(s).", orphans_pruned)

    for src_file, target_file in asset_sync_jobs:
        if not args.dry_run:
            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, target_file)

    failed = 0

    if encrypt_blob_tasks:
        logging.info("Encrypting %d media blob(s)...", len(encrypt_blob_tasks))
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=args.workers
        ) as executor:
            futures = [
                executor.submit(encrypt_blob_worker, t) for t in encrypt_blob_tasks
            ]
            for future in concurrent.futures.as_completed(futures):
                path, ok, err = future.result()
                if not ok:
                    failed += 1
                    logging.error("Failed to encrypt blob %s: %s", path.name, err)

    if compile_tasks:
        logging.info("Compiling %d documents...", len(compile_tasks))
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=args.workers
        ) as executor:
            futures = [
                executor.submit(compile_markdown_worker, t) for t in compile_tasks
            ]
            for future in concurrent.futures.as_completed(futures):
                path, ok, err = future.result()
                if not ok:
                    failed += 1
                    logging.error("Error compiling %s: %s", path.name, err)
    else:
        logging.info("All documents are up-to-date.")

    if failed == 0:
        search_index_needed = (
            not SEARCH_DB_FILE.exists()
            or bool(metadata_extraction_jobs)
            or orphans_pruned > 0
        )
        if search_index_needed:
            build_sqlite_search_index(
                search_records, SEARCH_DB_FILE, dry_run=args.dry_run
            )
            if SEARCH_DB_FILE.exists() and not args.dry_run:
                new_manifest["__SEARCH_DB_HASH__"] = compute_file_hash(SEARCH_DB_FILE)
        else:
            new_manifest["__SEARCH_DB_HASH__"] = old_manifest.get(
                "__SEARCH_DB_HASH__", ""
            )

        save_manifest(MANIFEST_FILE, new_manifest, args.dry_run)
        logging.info("Pipeline completed successfully.")
    else:
        logging.error("Build failed with %d error(s). Manifest retained.", failed)
        sys.exit(1)


if __name__ == "__main__":
    main()
