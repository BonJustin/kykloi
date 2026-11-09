import argparse
import base64
import concurrent.futures
import getpass
import hashlib
import json
import logging
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# ===========================================================================
# 1. PURE-PYTHON AES-256-GCM ENGINE & 8-BIT TABLE-DRIVEN GHASH
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


def _cipher_block(state: list[int], round_keys: list[int]) -> bytes:
    for i in range(16):
        state[i] ^= round_keys[i]

    for r in range(1, 14):
        rk_offset = r * 16
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

        state[0] = _xtime(s0 ^ s1) ^ s1 ^ s2 ^ s3 ^ round_keys[rk_offset]
        state[1] = _xtime(s1 ^ s2) ^ s2 ^ s3 ^ s0 ^ round_keys[rk_offset + 1]
        state[2] = _xtime(s2 ^ s3) ^ s3 ^ s0 ^ s1 ^ round_keys[rk_offset + 2]
        state[3] = _xtime(s3 ^ s0) ^ s0 ^ s1 ^ s2 ^ round_keys[rk_offset + 3]

        state[4] = _xtime(s4 ^ s5) ^ s5 ^ s6 ^ s7 ^ round_keys[rk_offset + 4]
        state[5] = _xtime(s5 ^ s6) ^ s6 ^ s7 ^ s4 ^ round_keys[rk_offset + 5]
        state[6] = _xtime(s6 ^ s7) ^ s7 ^ s4 ^ s5 ^ round_keys[rk_offset + 6]
        state[7] = _xtime(s7 ^ s4) ^ s4 ^ s5 ^ s6 ^ round_keys[rk_offset + 7]

        state[8] = _xtime(s8 ^ s9) ^ s9 ^ s10 ^ s11 ^ round_keys[rk_offset + 8]
        state[9] = _xtime(s9 ^ s10) ^ s10 ^ s11 ^ s8 ^ round_keys[rk_offset + 9]
        state[10] = _xtime(s10 ^ s11) ^ s11 ^ s8 ^ s9 ^ round_keys[rk_offset + 10]
        state[11] = _xtime(s11 ^ s8) ^ s8 ^ s9 ^ s10 ^ round_keys[rk_offset + 11]

        state[12] = _xtime(s12 ^ s13) ^ s13 ^ s14 ^ s15 ^ round_keys[rk_offset + 12]
        state[13] = _xtime(s13 ^ s14) ^ s14 ^ s15 ^ s12 ^ round_keys[rk_offset + 13]
        state[14] = _xtime(s14 ^ s15) ^ s15 ^ s12 ^ s13 ^ round_keys[rk_offset + 14]
        state[15] = _xtime(s15 ^ s12) ^ s12 ^ s13 ^ s14 ^ round_keys[rk_offset + 15]

    rk_offset = 224
    out = bytearray(16)
    out[0] = S_BOX[state[0]] ^ round_keys[rk_offset]
    out[1] = S_BOX[state[5]] ^ round_keys[rk_offset + 1]
    out[2] = S_BOX[state[10]] ^ round_keys[rk_offset + 2]
    out[3] = S_BOX[state[15]] ^ round_keys[rk_offset + 3]
    out[4] = S_BOX[state[4]] ^ round_keys[rk_offset + 4]
    out[5] = S_BOX[state[9]] ^ round_keys[rk_offset + 5]
    out[6] = S_BOX[state[14]] ^ round_keys[rk_offset + 6]
    out[7] = S_BOX[state[3]] ^ round_keys[rk_offset + 7]
    out[8] = S_BOX[state[8]] ^ round_keys[rk_offset + 8]
    out[9] = S_BOX[state[13]] ^ round_keys[rk_offset + 9]
    out[10] = S_BOX[state[2]] ^ round_keys[rk_offset + 10]
    out[11] = S_BOX[state[7]] ^ round_keys[rk_offset + 11]
    out[12] = S_BOX[state[12]] ^ round_keys[rk_offset + 12]
    out[13] = S_BOX[state[1]] ^ round_keys[rk_offset + 13]
    out[14] = S_BOX[state[6]] ^ round_keys[rk_offset + 14]
    out[15] = S_BOX[state[11]] ^ round_keys[rk_offset + 15]

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
    if len(key) != 32:
        raise ValueError("Key must be 32 bytes (256 bits).")
    if len(iv) != 12:
        raise ValueError("Initialization vector must be 12 bytes (96 bits).")

    round_keys = _key_expansion_256(key)
    h_bytes = _cipher_block([0] * 16, round_keys)
    h = int.from_bytes(h_bytes, byteorder="big")
    ghash_tables = _init_ghash_tables(h)

    j0 = iv + b"\x00\x00\x00\x01"
    ciphertext = bytearray()
    num_blocks = (len(plaintext) + 15) // 16

    for i in range(num_blocks):
        ctr_val = (1 + 1 + i) & 0xFFFFFFFF
        ctr_block = iv + ctr_val.to_bytes(4, byteorder="big")
        keystream = _cipher_block(list(ctr_block), round_keys)
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

    tag_mask = _cipher_block(list(j0), round_keys)
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
        raise RuntimeError(
            "CRITICAL: Pure-Python AES-GCM engine failed NIST KAT verification."
        )


# ===========================================================================
# 2. GLOBAL PATH INITIALIZATION & VALIDATION
# ===========================================================================

try:
    PROJECT_ROOT = Path(__file__).parent.resolve().parent
    SRC = PROJECT_ROOT / "content"
    DST = PROJECT_ROOT / "dist"
    APP_DIR = PROJECT_ROOT / "build"

    DEFAULTS_YAML = APP_DIR / "pandoc_md_to_static_html.yaml"
    DEFAULT_TEMPLATE = APP_DIR / "templates" / "md_to_static_html.html"
    METADATA_TEMPLATE = APP_DIR / "templates" / "metadata.json"
    LUA_FILTER = APP_DIR / "translate_links.lua"
    MANIFEST_FILE = APP_DIR / ".build_manifest.json"
    SEARCH_INDEX_FILE = DST / "search_index.js"

except Exception as err:
    print(f"CRITICAL CONFIGURATION ERROR: {err}", file=sys.stderr)
    sys.exit(1)


# ===========================================================================
# 3. DATA STRUCTURES & ARGUMENT PARSING
# ===========================================================================


@dataclass(frozen=True)
class CompileTask:
    md_path: Path
    out_path: Path
    template_path: Path
    relative_root: str
    defaults_yaml: Path
    lua_filter: Path
    is_secure: bool
    passphrase: Optional[str]
    dry_run: bool
    verbose: bool
    secure_root: Optional[Path] = None


def parse_args():
    p = argparse.ArgumentParser(
        description="Deterministic Archival Static Site Generator (Zero-Dependency Cryptography)."
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
    p.add_argument(
        "--test-frontmatter",
        action="store_true",
        help="Run comprehensive unit tests on the YAML scanner.",
    )
    return p.parse_args()


# ===========================================================================
# 4. CRYPTOGRAPHIC HASHING & ENVELOPE UTILITIES
# ===========================================================================


def compute_file_hash(path: Path) -> str:
    hasher = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()
    except (FileNotFoundError, PermissionError) as e:
        logging.warning("Unable to hash %s: %s", path, e)
        return ""


def compute_global_dependencies_hash() -> str:
    hasher = hashlib.sha256()
    tracked_files: list[Path] = [
        DEFAULTS_YAML,
        LUA_FILTER,
        DEFAULT_TEMPLATE,
        METADATA_TEMPLATE,
        Path(
            __file__
        ).resolve(),  # Self-tracking ensures build script changes invalidate cache
    ]
    for f in tracked_files:
        if f.is_file():
            hasher.update(f.name.encode("utf-8"))
            hasher.update(compute_file_hash(f).encode("utf-8"))
    return hasher.hexdigest()


def find_enclosing_secure_root(path: Path, src_root: Path) -> Optional[Path]:
    try:
        rel = path.relative_to(src_root)
    except ValueError:
        return None
    if "secure" not in rel.parts:
        return None
    idx = rel.parts.index("secure")
    return src_root.joinpath(*rel.parts[: idx + 1])


def compute_secure_tree_assets_hash(assets: list[tuple[str, str]]) -> str:
    hasher = hashlib.sha256()
    for rel_path_str, file_hash in sorted(assets):
        hasher.update(rel_path_str.encode("utf-8"))
        hasher.update(file_hash.encode("utf-8"))
    return hasher.hexdigest()


def compute_passphrase_fingerprint(passphrase: str) -> str:
    salt = b"kykloi:key_rotation_fingerprint:v1"
    return hashlib.sha256(salt + passphrase.encode("utf-8")).hexdigest()


# Iterations calibrated for permacomputing & low-power ARM responsiveness
DEFAULT_PBKDF2_ITERATIONS = 100_000


def derive_key(passphrase: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac(
        "sha256", passphrase.encode("utf-8"), salt, DEFAULT_PBKDF2_ITERATIONS, dklen=32
    )


def encrypt_payload(html_content: str, passphrase: str) -> str:
    salt = os.urandom(16)
    iv = os.urandom(12)
    key = derive_key(passphrase, salt)
    pt_bytes = html_content.encode("utf-8")

    # Opportunistic acceleration via system openssl CLI if present
    if shutil.which("openssl"):
        try:
            cmd = ["openssl", "enc", "-aes-256-gcm", "-K", key.hex(), "-iv", iv.hex()]
            proc = subprocess.run(cmd, input=pt_bytes, capture_output=True, check=True)
            envelope = salt + iv + proc.stdout
            return base64.b64encode(envelope).decode("ascii")
        except Exception as err:
            logging.debug("OpenSSL accelerator fallback triggered: %s", err)

    # Permacomputing Fallback: Pure-Python Engine
    ciphertext, tag = pure_aes_gcm_encrypt(key, iv, pt_bytes)
    envelope = salt + iv + ciphertext + tag
    return base64.b64encode(envelope).decode("ascii")


def load_manifest(manifest_path: Path) -> dict:
    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except (json.JSONDecodeError, OSError) as e:
            logging.warning(
                "Corrupt manifest encountered (%s). Initializing fresh manifest.", e
            )
    return {}


def save_manifest(manifest_path: Path, manifest: dict, dry_run: bool):
    if dry_run:
        return
    try:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, sort_keys=True)
    except OSError as e:
        logging.error("Failed to commit build manifest to disk: %s", e)


# ===========================================================================
# 5. ZERO-DEPENDENCY IN-MEMORY YAML FRONTMATTER PARSER
# ===========================================================================


def parse_frontmatter_robust(text: str) -> dict:
    """
    Zero-dependency, state-machine YAML frontmatter parser.
    Handles:
      - Colons in titles and quoted strings.
      - Multiline block scalars (folded '>' and literal '|').
      - Both list styles: inline arrays `[a, b]` and bulleted `- item`.
      - Comment stripping and nested indent boundary tracking.
    """
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
    multiline_mode = None  # '|' or '>'
    multiline_accumulator = []

    def commit_multiline():
        nonlocal current_key, multiline_mode, multiline_accumulator
        if current_key and multiline_mode:
            if multiline_mode == "|":
                val = "\n".join(multiline_accumulator)
            else:  # '>' folded style
                val = " ".join(" ".join(multiline_accumulator).split())
            result[current_key] = val
        multiline_mode = None
        multiline_accumulator = []

    for line in yaml_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip())

        # 1. Accumulate multiline blocks
        if multiline_mode and indent > 0:
            multiline_accumulator.append(stripped)
            continue
        elif multiline_mode and indent == 0:
            commit_multiline()

        # 2. Accumulate bulleted lists
        if stripped.startswith("- ") and current_key:
            item = stripped[2:].strip().strip("'\"")
            if not isinstance(result.get(current_key), list):
                result[current_key] = []
            result[current_key].append(item)
            continue

        # 3. Key-Value Extraction
        if ":" in stripped:
            key, raw_val = stripped.split(":", 1)
            key = key.strip()
            raw_val = raw_val.strip()
            current_key = key

            # Check for folded (>) or literal (|) block scalars
            if raw_val in ("|", ">"):
                multiline_mode = raw_val
                multiline_accumulator = []
                continue

            # Check for inline list [a, b, c]
            if raw_val.startswith("[") and raw_val.endswith("]"):
                inner = raw_val[1:-1].strip()
                if not inner:
                    result[key] = []
                else:
                    result[key] = [
                        x.strip().strip("'\"") for x in inner.split(",") if x.strip()
                    ]
                continue

            # Quoted or unquoted scalar
            if (raw_val.startswith('"') and raw_val.endswith('"')) or (
                raw_val.startswith("'") and raw_val.endswith("'")
            ):
                raw_val = raw_val[1:-1]

            result[key] = raw_val

    commit_multiline()
    return result


def extract_metadata_fast(md_path: Path) -> tuple[Path, dict[str, str]]:
    """In-memory extraction executing in microseconds per file."""
    meta = {
        "title": "",
        "keywords": "",
        "date_edtf": "",
    }

    try:
        with open(md_path, "r", encoding="utf-8") as f:
            header = f.read(16384)  # Read opening 16 KB for frontmatter

        parsed = parse_frontmatter_robust(header)

        title_val = parsed.get("title", "")
        meta["title"] = str(title_val).strip()

        date_val = parsed.get("date_edtf") or parsed.get("date", "")
        meta["date_edtf"] = str(date_val).strip()

        keywords_val = parsed.get("keywords", "")
        if isinstance(keywords_val, list):
            meta["keywords"] = " ".join(str(k).strip() for k in keywords_val)
        elif isinstance(keywords_val, str):
            meta["keywords"] = keywords_val.strip()

    except OSError as err:
        logging.warning("Error reading %s: %s", md_path.name, err)

    if not meta["title"]:
        meta["title"] = md_path.stem.replace("-", " ").replace("_", " ").title()

    return md_path, meta


def test_frontmatter_suite():
    """Deterministic validation test suite verifying frontmatter edge cases."""
    test_yaml = """---
title: "Project Kykloi: Advanced Archival Systems"
date_edtf: 2026-11-08
keywords:
  - permacomputing
  - "offline-first"
  - static-site
abstract: >
  This is a multiline folded abstract intended to verify
  that line continuation and word spacing fold correctly into
  a single continuous string without line breaks.
---
# Document content begins here
"""
    parsed = parse_frontmatter_robust(test_yaml)
    assert parsed["title"] == "Project Kykloi: Advanced Archival Systems", (
        "Title with colon failed"
    )
    assert parsed["date_edtf"] == "2026-11-08", "Date extraction failed"
    assert parsed["keywords"] == ["permacomputing", "offline-first", "static-site"], (
        "Bulleted list failed"
    )
    assert "single continuous string" in parsed["abstract"], "Folded abstract failed"
    print("ALL FRONTMATTER PARSER UNIT TESTS PASSED SUCCESSFULLY.")


def write_minisearch_index(records: list[dict], out_path: Path, dry_run: bool):
    if dry_run:
        logging.info("[DRY RUN] Would write search index to %s", out_path)
        return

    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = f"window.__SEARCH_DOCS__ = {json.dumps(records, ensure_ascii=False, indent=2)};\n"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(payload)
    logging.info("MiniSearch index generated with %d documents.", len(records))


# ===========================================================================
# 6. WORKER COMPILATION SUBSYSTEM
# ===========================================================================


def compile_markdown_worker(task: CompileTask) -> tuple[Path, bool, Optional[str]]:
    if task.dry_run:
        return task.md_path, True, None

    css_files = ["assets/css/pico.css", "assets/css/style.css"]

    # CASE 1: Standard Unencrypted Document
    if not task.is_secure:
        cmd = [
            "pandoc",
            str(task.md_path),
            "--defaults",
            str(task.defaults_yaml),
            "--template",
            str(task.template_path),
            "--lua-filter",
            str(task.lua_filter),
            "-V",
            f"relative_root={task.relative_root}",
            f"--katex={task.relative_root}assets/katex/",
            "-o",
            str(task.out_path),
        ]
        for css in css_files:
            cmd.extend(["--css", f"{task.relative_root}{css}"])

        task.out_path.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return task.md_path, False, result.stderr.strip()
        return task.md_path, True, None

    # CASE 2: Secure Encrypted Document
    if not task.passphrase:
        return (
            task.md_path,
            False,
            "Cannot compile secure file: No passphrase provided.",
        )

    resource_paths = [str(task.md_path.parent)]
    if task.secure_root and task.secure_root != task.md_path.parent:
        resource_paths.append(str(task.secure_root))

    body_cmd = [
        "pandoc",
        str(task.md_path),
        "--defaults",
        str(task.defaults_yaml),
        "--lua-filter",
        str(task.lua_filter),
        f"--katex={task.relative_root}assets/katex/",
        "--embed-resources",
        "--resource-path",
        os.pathsep.join(resource_paths),
    ]

    body_result = subprocess.run(body_cmd, capture_output=True, text=True)
    if body_result.returncode != 0:
        return task.md_path, False, body_result.stderr.strip()

    try:
        ciphertext_b64 = encrypt_payload(body_result.stdout, task.passphrase)
    except Exception as e:
        return task.md_path, False, f"Encryption failed: {e}"

    envelope_cmd = [
        "pandoc",
        str(task.md_path),
        "--template",
        str(task.template_path),
        "-V",
        f"relative_root={task.relative_root}",
        "-V",
        "encrypted=true",
    ]
    for css in css_files:
        envelope_cmd.extend(["--css", f"{task.relative_root}{css}"])

    envelope_result = subprocess.run(envelope_cmd, capture_output=True, text=True)
    if envelope_result.returncode != 0:
        return task.md_path, False, envelope_result.stderr.strip()

    try:
        final_html = envelope_result.stdout.replace(
            "__KYKLOI_ENCRYPTED_PAYLOAD__", ciphertext_b64
        )
        task.out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(task.out_path, "w", encoding="utf-8") as f:
            f.write(final_html)
    except OSError as e:
        return task.md_path, False, f"Disk write error: {e}"

    return task.md_path, True, None


# ===========================================================================
# 7. ORPHAN PRUNING
# ===========================================================================


def prune_orphans(dst_dir: Path, expected_files: set[Path], dry_run: bool) -> int:
    if not dst_dir.exists():
        return 0

    orphans_removed = 0
    for item in list(dst_dir.rglob("*")):
        if item.is_file() and item.resolve() not in expected_files:
            if not dry_run:
                item.unlink()
            orphans_removed += 1
            logging.debug("Pruned orphan file: %s", item)

    for dirpath in sorted(dst_dir.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if dirpath.is_dir() and not any(dirpath.iterdir()):
            if not dry_run:
                dirpath.rmdir()
            logging.debug("Pruned empty dir: %s", dirpath)

    return orphans_removed


# ===========================================================================
# 8. PIPELINE ORCHESTRATION
# ===========================================================================


def main():
    args = parse_args()
    if args.test_frontmatter:
        test_frontmatter_suite()
        return

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    try:
        verify_cryptographic_engine()
    except RuntimeError as err:
        logging.critical(str(err))
        sys.exit(1)

    dependencies = [
        (SRC, "Source directory"),
        (DEFAULTS_YAML, "Pandoc defaults configuration"),
        (DEFAULT_TEMPLATE, "Content HTML template"),
        (METADATA_TEMPLATE, "Metadata JSON template"),
        (LUA_FILTER, "Lua link translation filter"),
    ]
    for path, desc in dependencies:
        if not path.exists():
            logging.error("Configuration error: %s missing at %s", desc, path)
            sys.exit(1)

    if args.clean:
        if DST.exists():
            logging.info("Flag --clean active: Purging %s", DST)
            if not args.dry_run:
                shutil.rmtree(DST)
        if MANIFEST_FILE.exists():
            logging.info("Flag --clean active: Removing manifest %s", MANIFEST_FILE)
            if not args.dry_run:
                MANIFEST_FILE.unlink()

    DST.mkdir(parents=True, exist_ok=True)

    old_manifest = load_manifest(MANIFEST_FILE)
    new_manifest: dict = {}

    current_global_hash = compute_global_dependencies_hash()
    new_manifest["__GLOBAL_DEPENDENCIES__"] = current_global_hash
    global_deps_changed = (
        old_manifest.get("__GLOBAL_DEPENDENCIES__") != current_global_hash
    )

    if global_deps_changed:
        logging.info(
            "Global dependencies/templates modified. Flagging all outputs for rebuild."
        )

    expected_outputs: set[Path] = set()
    compile_tasks: list[CompileTask] = []

    md_files = sorted(SRC.rglob("*.md"))
    has_secure_files = any("secure" in p.relative_to(SRC).parts for p in md_files)

    passphrase = args.password
    if has_secure_files and not passphrase and not args.dry_run:
        passphrase = getpass.getpass("Enter passphrase for /secure/ notes: ")
        if not passphrase:
            logging.error("Encryption passphrase cannot be empty.")
            sys.exit(1)

    passphrase_changed = False
    if has_secure_files and passphrase:
        current_key_fingerprint = compute_passphrase_fingerprint(passphrase)
        new_manifest["__PASSPHRASE_FINGERPRINT__"] = current_key_fingerprint
        old_key_fingerprint = old_manifest.get("__PASSPHRASE_FINGERPRINT__")

        if old_manifest and old_key_fingerprint is None:
            passphrase_changed = True
        elif old_key_fingerprint != current_key_fingerprint:
            passphrase_changed = True

        if passphrase_changed:
            logging.info(
                "Passphrase rotation detected. Flagging secure documents for re-encryption."
            )

    secure_tree_assets: dict[Path, list[tuple[str, str]]] = {}
    asset_sync_jobs: list[tuple[Path, Path]] = []

    for p in SRC.rglob("*"):
        if not p.is_file() or p.name.startswith(".") or p.suffix.lower() == ".md":
            continue

        rel_src = p.relative_to(SRC)
        secure_root = find_enclosing_secure_root(p, SRC)

        if secure_root is not None:
            h = compute_file_hash(p)
            rel_to_root = p.relative_to(secure_root).as_posix()
            secure_tree_assets.setdefault(secure_root, []).append((rel_to_root, h))
            new_manifest[f"secure_asset:{rel_src.as_posix()}"] = h
        else:
            target = DST / rel_src
            expected_outputs.add(target.resolve())
            manifest_key = f"media:{rel_src.as_posix()}"
            h = compute_file_hash(p)
            new_manifest[manifest_key] = h
            if not target.exists() or old_manifest.get(manifest_key) != h:
                asset_sync_jobs.append((p, target))

    all_secure_roots: set[Path] = set(secure_tree_assets.keys())
    for md in md_files:
        s_root = find_enclosing_secure_root(md, SRC)
        if s_root is not None:
            all_secure_roots.add(s_root)

    current_secure_tree_hashes: dict[Path, str] = {}
    for s_root in all_secure_roots:
        assets = secure_tree_assets.get(s_root, [])
        tree_hash = compute_secure_tree_assets_hash(assets)
        current_secure_tree_hashes[s_root] = tree_hash
        rel_root = s_root.relative_to(SRC).as_posix()
        new_manifest[f"secure_tree_assets:{rel_root}"] = tree_hash

    metadata_extraction_jobs: list[Path] = []
    file_metadata_map: dict[Path, dict[str, str]] = {}

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

        is_secure = "secure" in rel.parts
        secure_root = find_enclosing_secure_root(md, SRC) if is_secure else None

        secure_assets_changed = False
        if is_secure and secure_root is not None:
            rel_root = secure_root.relative_to(SRC).as_posix()
            old_tree_hash = old_manifest.get(f"secure_tree_assets:{rel_root}")
            current_tree_hash = current_secure_tree_hashes[secure_root]
            if old_tree_hash != current_tree_hash:
                secure_assets_changed = True

        md_content_changed = old_manifest.get(manifest_key) != current_md_hash

        is_dirty = (
            not out.exists()
            or global_deps_changed
            or md_content_changed
            or (is_secure and (passphrase_changed or secure_assets_changed))
        )

        cached_meta = old_manifest.get(meta_cache_key)
        meta_is_dirty = (
            global_deps_changed
            or md_content_changed
            or not isinstance(cached_meta, dict)
        )

        if not meta_is_dirty and isinstance(cached_meta, dict):
            file_metadata_map[md] = cached_meta
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
                    defaults_yaml=DEFAULTS_YAML,
                    lua_filter=LUA_FILTER,
                    is_secure=is_secure,
                    passphrase=passphrase,
                    dry_run=args.dry_run,
                    verbose=args.verbose,
                    secure_root=secure_root,
                )
            )

    # In-memory metadata scanning for changed documents
    if metadata_extraction_jobs:
        logging.info(
            "Extracting metadata from %d file(s) in-memory...",
            len(metadata_extraction_jobs),
        )
        for md_path in metadata_extraction_jobs:
            _, extracted_meta = extract_metadata_fast(md_path)
            file_metadata_map[md_path] = extracted_meta
            rel = md_path.relative_to(SRC)
            new_manifest[f"meta:{rel.as_posix()}"] = extracted_meta

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

    expected_outputs.add(SEARCH_INDEX_FILE.resolve())

    assets_src = APP_DIR / "assets"
    if assets_src.exists():
        for p in assets_src.rglob("*"):
            if p.is_file() and not p.name.startswith("."):
                target = DST / "assets" / p.relative_to(assets_src)
                expected_outputs.add(target.resolve())
                manifest_key = (
                    f"functional_asset:{p.relative_to(assets_src).as_posix()}"
                )
                h = compute_file_hash(p)
                new_manifest[manifest_key] = h
                if not target.exists() or old_manifest.get(manifest_key) != h:
                    asset_sync_jobs.append((p, target))

    root_src = APP_DIR / "root"
    if root_src.exists():
        for p in root_src.rglob("*"):
            if p.is_file() and not p.name.startswith("."):
                target = DST / p.relative_to(root_src)
                expected_outputs.add(target.resolve())
                manifest_key = f"root_asset:{p.relative_to(root_src).as_posix()}"
                h = compute_file_hash(p)
                new_manifest[manifest_key] = h
                if not target.exists() or old_manifest.get(manifest_key) != h:
                    asset_sync_jobs.append((p, target))

    orphans_pruned = prune_orphans(
        dst_dir=DST, expected_files=expected_outputs, dry_run=args.dry_run
    )
    if orphans_pruned:
        logging.info("Pruned %d orphaned artifact(s).", orphans_pruned)

    synced_assets = 0
    for src_file, target_file in asset_sync_jobs:
        if not args.dry_run:
            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, target_file)
        synced_assets += 1
    if synced_assets:
        logging.info("Synced %d modified/new asset(s).", synced_assets)

    total_md = len(md_files)
    to_compile = len(compile_tasks)
    failed = 0

    if to_compile > 0:
        logging.info(
            "Compiling %d of %d documents using %d workers...",
            to_compile,
            total_md,
            args.workers,
        )
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=args.workers
        ) as executor:
            future_to_file = {
                executor.submit(compile_markdown_worker, t): t.md_path
                for t in compile_tasks
            }
            for future in concurrent.futures.as_completed(future_to_file):
                md_path = future_to_file[future]
                try:
                    _, success, err = future.result()
                    if not success:
                        failed += 1
                        logging.error(
                            "Pandoc compilation error on %s:\n%s", md_path.name, err
                        )
                    elif args.verbose:
                        logging.info("Built: %s", md_path.name)
                except Exception as exc:
                    failed += 1
                    logging.error(
                        "Runtime exception compiling %s: %s", md_path.name, exc
                    )
    else:
        logging.info("All %d documents are verified current.", total_md)

    if (
        to_compile > 0 or orphans_pruned > 0 or not SEARCH_INDEX_FILE.exists()
    ) and failed == 0:
        write_minisearch_index(search_records, SEARCH_INDEX_FILE, dry_run=args.dry_run)

    if failed == 0:
        save_manifest(MANIFEST_FILE, new_manifest, args.dry_run)
    else:
        logging.warning(
            "Build recorded failures. Manifest state will not be persisted."
        )
        sys.exit(1)

    logging.info(
        "Build complete. (%d compiled, %d assets synced, %d orphans pruned)",
        to_compile,
        synced_assets,
        orphans_pruned,
    )


if __name__ == "__main__":
    main()
