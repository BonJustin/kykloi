#!/usr/bin/env python3
"""
system/build/build.py - Zero-Dependency Deterministic SSG Compiler.
Part of Project Kykloi (v0.7.0).
Leverages vault_index.db SQLite ledger for O(1) stat-cached incremental builds.
Features Tiered Multi-Engine AES-256-GCM Acceleration with Deterministic Fallback.
Priority Order:
  1. Native OS C-ABI Shared Libraries (CommonCrypto / CNG / OpenSSL EVP)
  2. Host Python Compiled Packages (cryptography / pycryptodome)
  3. Pure-Python Baseline Engine (Zero-Dependency Fallback)
"""

import argparse
import base64
import concurrent.futures
import ctypes
import ctypes.util
import getpass
import hashlib
import json
import logging
import multiprocessing
import os
import platform
import shutil
import sqlite3
import subprocess
import sys
import urllib.parse
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional, Tuple

APP_DIR = Path(__file__).resolve().parent
SYSTEM_DIR = APP_DIR.parent
PROJECT_ROOT = SYSTEM_DIR.parent

# Register project root and system subsystems on sys.path
for path_entry in (PROJECT_ROOT, SYSTEM_DIR, APP_DIR):
    if str(path_entry) not in sys.path:
        sys.path.insert(0, str(path_entry))

from logger import get_logger, setup_logging, timed_step

from system.normalize.cli import sync_db_with_disk
from system.normalize.db import BuildArtifactRecord, VaultDB
from system.normalize.scanner import is_junk_path

# ===========================================================================
# 1. PURE-PYTHON AES-256-GCM ENGINE & TABLE-DRIVEN GHASH (TIER 3 BASELINE)
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


_GHASH_TABLES_CACHE: dict[int, list[list[int]]] = {}


def _init_ghash_tables(h: int) -> list[list[int]]:
    if h in _GHASH_TABLES_CACHE:
        return _GHASH_TABLES_CACHE[h]
    tables: list[list[int]] = []
    for j in range(16):
        shift = 8 * (15 - j)
        basis = [_ghash_mult((1 << bit) << shift, h) for bit in range(8)]
        table = [0] * 256
        for b in range(1, 256):
            low_bit = (b & -b).bit_length() - 1
            table[b] = table[b & (b - 1)] ^ basis[low_bit]
        tables.append(table)
    _GHASH_TABLES_CACHE[h] = tables
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
) -> Tuple[bytes, bytes]:
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


# ===========================================================================
# 2. ACCELERATED CRYPTO ENGINES
# ===========================================================================


def _init_darwin_commoncrypto() -> Optional[
    Callable[[bytes, bytes, bytes], Tuple[bytes, bytes]]
]:
    if sys.platform != "darwin":
        return None

    try:
        lib = ctypes.CDLL("/usr/lib/libSystem.B.dylib")
        if not hasattr(lib, "CCCryptorGCMOneshotEncrypt"):
            return None

        fn = lib.CCCryptorGCMOneshotEncrypt
        fn.restype = ctypes.c_int32
        fn.argtypes = [
            ctypes.c_uint32,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_size_t,
        ]

        def _encrypt_commoncrypto(
            key: bytes, iv: bytes, plaintext: bytes
        ) -> Tuple[bytes, bytes]:
            pt_len = len(plaintext)
            ct = ctypes.create_string_buffer(max(1, pt_len))
            tag = ctypes.create_string_buffer(16)

            st = fn(
                0,
                key,
                len(key),
                iv,
                len(iv),
                None,
                0,
                plaintext if pt_len > 0 else None,
                pt_len,
                ct,
                tag,
                16,
            )
            if st != 0:
                raise RuntimeError(f"CommonCrypto error code: {st}")

            return bytes(ct.raw[:pt_len]), bytes(tag.raw)

        return _encrypt_commoncrypto
    except Exception:
        return None


class _BCRYPT_AUTHENTICATED_CIPHER_MODE_INFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_ulong),
        ("dwInfoVersion", ctypes.c_ulong),
        ("pbNonce", ctypes.c_void_p),
        ("cbNonce", ctypes.c_ulong),
        ("pbAuthData", ctypes.c_void_p),
        ("cbAuthData", ctypes.c_ulong),
        ("pbTag", ctypes.c_void_p),
        ("cbTag", ctypes.c_ulong),
        ("pbMacContext", ctypes.c_void_p),
        ("cbMacContext", ctypes.c_ulong),
        ("cbAAD", ctypes.c_ulong),
        ("cbData", ctypes.c_ulonglong),
        ("dwFlags", ctypes.c_ulong),
    ]


_CNG_ALG_HANDLE: Optional[ctypes.c_void_p] = None


def _init_windows_cng() -> Optional[
    Callable[[bytes, bytes, bytes], Tuple[bytes, bytes]]
]:
    global _CNG_ALG_HANDLE
    if sys.platform != "win32":
        return None

    try:
        bcrypt = ctypes.windll.bcrypt  # type: ignore[attr-defined]

        alg_handle = ctypes.c_void_p()
        status = bcrypt.BCryptOpenAlgorithmProvider(
            ctypes.byref(alg_handle),
            ctypes.c_wchar_p("AES"),
            None,
            ctypes.c_ulong(0),
        )
        if status != 0:
            return None

        chain_mode = "ChainingModeGCM\0".encode("utf-16le")
        status = bcrypt.BCryptSetProperty(
            alg_handle,
            ctypes.c_wchar_p("ChainingMode"),
            chain_mode,
            ctypes.c_ulong(len(chain_mode)),
            ctypes.c_ulong(0),
        )
        if status != 0:
            bcrypt.BCryptCloseAlgorithmProvider(alg_handle, ctypes.c_ulong(0))
            return None

        _CNG_ALG_HANDLE = alg_handle

        def _encrypt_cng(
            key: bytes, iv: bytes, plaintext: bytes
        ) -> Tuple[bytes, bytes]:
            key_handle = ctypes.c_void_p()
            st = bcrypt.BCryptGenerateSymmetricKey(
                _CNG_ALG_HANDLE,
                ctypes.byref(key_handle),
                None,
                ctypes.c_ulong(0),
                ctypes.c_char_p(key),
                ctypes.c_ulong(len(key)),
                ctypes.c_ulong(0),
            )
            if st != 0:
                raise RuntimeError(f"BCryptGenerateSymmetricKey error: {hex(st)}")

            try:
                c_iv = ctypes.create_string_buffer(iv, len(iv))
                c_tag = ctypes.create_string_buffer(16)

                auth_info = _BCRYPT_AUTHENTICATED_CIPHER_MODE_INFO()
                auth_info.cbSize = ctypes.sizeof(_BCRYPT_AUTHENTICATED_CIPHER_MODE_INFO)
                auth_info.dwInfoVersion = 1
                auth_info.pbNonce = ctypes.cast(c_iv, ctypes.c_void_p)
                auth_info.cbNonce = len(iv)
                auth_info.pbTag = ctypes.cast(c_tag, ctypes.c_void_p)
                auth_info.cbTag = 16

                pt_len = len(plaintext)
                out_buf = ctypes.create_string_buffer(max(1, pt_len))
                bytes_done = ctypes.c_ulong(0)

                st = bcrypt.BCryptEncrypt(
                    key_handle,
                    ctypes.c_char_p(plaintext) if pt_len > 0 else None,
                    ctypes.c_ulong(pt_len),
                    ctypes.byref(auth_info),
                    None,
                    ctypes.c_ulong(0),
                    out_buf,
                    ctypes.c_ulong(pt_len),
                    ctypes.byref(bytes_done),
                    ctypes.c_ulong(0),
                )
                if st != 0:
                    raise RuntimeError(f"BCryptEncrypt error: {hex(st)}")

                return bytes(out_buf.raw[: bytes_done.value]), bytes(c_tag.raw)
            finally:
                bcrypt.BCryptDestroyKey(key_handle)

        return _encrypt_cng
    except Exception:
        return None


def _is_safe_posix_libcrypto_path(path: str) -> bool:
    if sys.platform == "darwin":
        clean = path.strip()
        if clean in ("crypto", "libcrypto", "libcrypto.dylib", "libcrypto.35.dylib"):
            return False
        try:
            resolved = str(Path(clean).resolve())
        except Exception:
            resolved = clean
        if resolved.startswith(("/usr/lib/", "/System/", "/Library/Apple/")):
            return False
    return True


def _find_posix_libcrypto() -> Optional[ctypes.CDLL]:
    candidates: list[str] = []

    py_lib_dir = Path(sys.prefix) / "lib"
    if py_lib_dir.is_dir():
        for pattern in ("libcrypto*.dylib", "libcrypto*.so*"):
            for found in sorted(py_lib_dir.glob(pattern)):
                candidates.append(str(found))

    if sys.platform == "darwin":
        candidates.extend(
            [
                "/opt/homebrew/opt/openssl@3/lib/libcrypto.dylib",
                "/opt/homebrew/opt/openssl@1.1/lib/libcrypto.dylib",
                "/opt/homebrew/lib/libcrypto.dylib",
                "/usr/local/opt/openssl@3/lib/libcrypto.dylib",
                "/usr/local/opt/openssl@1.1/lib/libcrypto.dylib",
                "/usr/local/lib/libcrypto.dylib",
                "/opt/local/lib/libcrypto.dylib",
                "/opt/local/lib/openssl-3/libcrypto.dylib",
                "/opt/local/lib/openssl-1.1/libcrypto.dylib",
            ]
        )
    else:
        for name in ("crypto", "libcrypto"):
            path = ctypes.util.find_library(name)
            if path:
                candidates.append(path)

        candidates.extend(
            [
                "libcrypto.so.3",
                "libcrypto.so.1.1",
                "libcrypto.so",
                "/lib/libcrypto.so.3",
                "/lib/libcrypto.so.1.1",
                "/lib64/libcrypto.so.3",
                "/lib64/libcrypto.so.1.1",
                "/usr/lib/x86_64-linux-gnu/libcrypto.so.3",
                "/usr/lib/aarch64-linux-gnu/libcrypto.so.3",
                "/usr/lib/x86_64-linux-gnu/libcrypto.so.1.1",
                "/usr/lib/aarch64-linux-gnu/libcrypto.so.1.1",
                "/usr/lib64/libcrypto.so.3",
                "/usr/lib64/libcrypto.so.1.1",
                "/usr/lib/libcrypto.so.3",
                "/usr/lib/libcrypto.so.1.1",
                "/usr/lib/libcrypto.so",
                "/usr/local/lib/libcrypto.so.3",
                "/usr/local/lib/libcrypto.so.1.1",
                "/usr/local/lib/libcrypto.so",
                "/usr/local/lib64/libcrypto.so",
            ]
        )

    required_symbols = (
        "EVP_CIPHER_CTX_new",
        "EVP_CIPHER_CTX_free",
        "EVP_aes_256_gcm",
        "EVP_EncryptInit_ex",
        "EVP_CIPHER_CTX_ctrl",
        "EVP_EncryptUpdate",
        "EVP_EncryptFinal_ex",
    )

    for p in candidates:
        if not _is_safe_posix_libcrypto_path(p):
            continue
        if "/" in p and not os.path.isfile(p):
            continue
        try:
            lib = ctypes.CDLL(p)
            if all(hasattr(lib, sym) for sym in required_symbols):
                return lib
        except OSError:
            continue

    return None


def _init_posix_openssl() -> Optional[
    Callable[[bytes, bytes, bytes], Tuple[bytes, bytes]]
]:
    lib = _find_posix_libcrypto()
    if not lib:
        return None

    try:
        lib.EVP_CIPHER_CTX_new.restype = ctypes.c_void_p
        lib.EVP_CIPHER_CTX_new.argtypes = []

        lib.EVP_CIPHER_CTX_free.restype = None
        lib.EVP_CIPHER_CTX_free.argtypes = [ctypes.c_void_p]

        lib.EVP_aes_256_gcm.restype = ctypes.c_void_p
        lib.EVP_aes_256_gcm.argtypes = []

        lib.EVP_EncryptInit_ex.restype = ctypes.c_int
        lib.EVP_EncryptInit_ex.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
        ]

        lib.EVP_CIPHER_CTX_ctrl.restype = ctypes.c_int
        lib.EVP_CIPHER_CTX_ctrl.argtypes = [
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_void_p,
        ]

        lib.EVP_EncryptUpdate.restype = ctypes.c_int
        lib.EVP_EncryptUpdate.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_int),
            ctypes.c_char_p,
            ctypes.c_int,
        ]

        lib.EVP_EncryptFinal_ex.restype = ctypes.c_int
        lib.EVP_EncryptFinal_ex.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_int),
        ]

        EVP_CTRL_GCM_SET_IVLEN = 0x9
        EVP_CTRL_GCM_GET_TAG = 0x10

        def _encrypt_openssl(
            key: bytes, iv: bytes, plaintext: bytes
        ) -> Tuple[bytes, bytes]:
            ctx = lib.EVP_CIPHER_CTX_new()
            if not ctx:
                raise RuntimeError("EVP_CIPHER_CTX_new allocation failure.")

            try:
                cipher = lib.EVP_aes_256_gcm()
                if lib.EVP_EncryptInit_ex(ctx, cipher, None, None, None) != 1:
                    raise RuntimeError("EVP_EncryptInit_ex cipher bind failed.")

                if (
                    lib.EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, len(iv), None)
                    != 1
                ):
                    raise RuntimeError(
                        "EVP_CIPHER_CTX_ctrl IV length assignment failed."
                    )

                if lib.EVP_EncryptInit_ex(ctx, None, None, key, iv) != 1:
                    raise RuntimeError(
                        "EVP_EncryptInit_ex key/iv initialization failed."
                    )

                pt_len = len(plaintext)
                c_ct = ctypes.create_string_buffer(max(1, pt_len + 16))
                out_len = ctypes.c_int(0)

                if pt_len > 0:
                    if (
                        lib.EVP_EncryptUpdate(
                            ctx, c_ct, ctypes.byref(out_len), plaintext, pt_len
                        )
                        != 1
                    ):
                        raise RuntimeError("EVP_EncryptUpdate failed.")

                total_len = out_len.value
                final_buf = ctypes.create_string_buffer(16)
                final_len = ctypes.c_int(0)
                if (
                    lib.EVP_EncryptFinal_ex(ctx, final_buf, ctypes.byref(final_len))
                    != 1
                ):
                    raise RuntimeError("EVP_EncryptFinal_ex failed.")

                tag = ctypes.create_string_buffer(16)
                if lib.EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_GET_TAG, 16, tag) != 1:
                    raise RuntimeError("EVP_CIPHER_CTX_ctrl tag extraction failed.")

                return bytes(c_ct.raw[:total_len]), bytes(tag.raw)
            finally:
                lib.EVP_CIPHER_CTX_free(ctx)

        return _encrypt_openssl
    except Exception:
        return None


def _init_py_cryptography() -> Optional[
    Callable[[bytes, bytes, bytes], Tuple[bytes, bytes]]
]:
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM

        def _encrypt(key: bytes, iv: bytes, plaintext: bytes) -> Tuple[bytes, bytes]:
            ct_tag = AESGCM(key).encrypt(iv, plaintext, None)
            return ct_tag[:-16], ct_tag[-16:]

        return _encrypt
    except ImportError:
        return None


def _init_py_cryptodome() -> Optional[
    Callable[[bytes, bytes, bytes], Tuple[bytes, bytes]]
]:
    try:
        from Cryptodome.Cipher import AES  # type: ignore[import-not-found]

        def _encrypt(key: bytes, iv: bytes, plaintext: bytes) -> Tuple[bytes, bytes]:
            cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
            ct, tag = cipher.encrypt_and_digest(plaintext)
            return ct, tag

        return _encrypt
    except ImportError:
        return None


# ===========================================================================
# 3. ENGINE DISPATCHER & NIST KAT VERIFICATION
# ===========================================================================

KAT_KEY = bytes.fromhex("00" * 32)
KAT_IV = bytes.fromhex("00" * 12)
KAT_PT = bytes.fromhex("00" * 16)
KAT_EXPECTED_CT = bytes.fromhex("cea7403d4d606b6e074ec5d3baf39d18")
KAT_EXPECTED_TAG = bytes.fromhex("d0d1c8a799996bf0265b98b5d48ab919")


def _test_engine_kat(fn: Callable[[bytes, bytes, bytes], Tuple[bytes, bytes]]) -> bool:
    try:
        ct, tag = fn(KAT_KEY, KAT_IV, KAT_PT)
        return ct == KAT_EXPECTED_CT and tag == KAT_EXPECTED_TAG
    except Exception:
        return False


def _resolve_active_crypto_engine() -> Tuple[
    str, Callable[[bytes, bytes, bytes], Tuple[bytes, bytes]]
]:
    if os.environ.get("KYKLOI_CRYPTO_ENGINE") == "pure":
        if _test_engine_kat(pure_aes_gcm_encrypt):
            return "Pure-Python AES-GCM (Forced Fallback)", pure_aes_gcm_encrypt

    # Priority Tier 1: Native OS C-ABI via ctypes
    if sys.platform == "darwin":
        darwin_fn = _init_darwin_commoncrypto()
        if darwin_fn and _test_engine_kat(darwin_fn):
            return "Apple CommonCrypto (libSystem / NEON / AES-NI)", darwin_fn

        openssl_fn = _init_posix_openssl()
        if openssl_fn and _test_engine_kat(openssl_fn):
            return "Safe OpenSSL EVP (MacPorts / Homebrew / sys.prefix)", openssl_fn

    elif sys.platform == "win32":
        cng_fn = _init_windows_cng()
        if cng_fn and _test_engine_kat(cng_fn):
            return "Windows CNG (bcrypt.dll / AES-NI)", cng_fn
    else:
        openssl_fn = _init_posix_openssl()
        if openssl_fn and _test_engine_kat(openssl_fn):
            return "System OpenSSL EVP (libcrypto / AES-NI / NEON)", openssl_fn

    # Priority Tier 2: Compiled Site Packages
    crypto_fn = _init_py_cryptography()
    if crypto_fn and _test_engine_kat(crypto_fn):
        return "Python cryptography (OpenSSL C-Extension)", crypto_fn

    cryptodome_fn = _init_py_cryptodome()
    if cryptodome_fn and _test_engine_kat(cryptodome_fn):
        return "Python pycryptodome (Hardware Accelerated)", cryptodome_fn

    # Priority Tier 3: Pure-Python Fallback Baseline
    if _test_engine_kat(pure_aes_gcm_encrypt):
        return "Pure-Python AES-GCM (Zero-Dependency Fallback)", pure_aes_gcm_encrypt

    raise RuntimeError("CRITICAL: All cryptographic engines failed NIST KAT self-test.")


ACTIVE_ENGINE_NAME, ACTIVE_ENCRYPT_FN = _resolve_active_crypto_engine()


def aes_gcm_encrypt(key: bytes, iv: bytes, plaintext: bytes) -> Tuple[bytes, bytes]:
    return ACTIVE_ENCRYPT_FN(key, iv, plaintext)


def verify_cryptographic_engine():
    if not _test_engine_kat(ACTIVE_ENCRYPT_FN):
        raise RuntimeError(
            f"CRITICAL: NIST KAT verification failed for active engine: {ACTIVE_ENGINE_NAME}"
        )


# ===========================================================================
# 4. PATHS & PIPELINE DEFINITIONS
# ===========================================================================

SRC = Path(os.environ.get("KYKLOI_CONTENT_DIR", PROJECT_ROOT / "content")).resolve()
DST = Path(os.environ.get("KYKLOI_DIST_DIR", PROJECT_ROOT / "dist")).resolve()
NORM_DB_PATH = Path(
    os.environ.get("KYKLOI_DB_PATH", SYSTEM_DIR / "normalize" / "vault-index.db")
).resolve()

DEFAULTS_YAML = APP_DIR / "html-config.yaml"
DEFAULT_TEMPLATE = APP_DIR / "templates" / "pandoc-template.html"
LUA_FILTER = APP_DIR / "translate-links.lua"
SEARCH_DB_FILE = DST / "search.db"


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
    p.add_argument(
        "--log-file",
        type=str,
        default=None,
        help="Destination path for persistent diagnostic logs.",
    )
    p.add_argument(
        "--src",
        type=Path,
        default=None,
        help="Override source content directory.",
    )
    p.add_argument(
        "--dst",
        type=Path,
        default=None,
        help="Override output destination directory.",
    )
    p.add_argument(
        "--db-path",
        type=Path,
        default=None,
        help="Override SQLite ledger path.",
    )
    return p.parse_args()


# ===========================================================================
# 5. BINARY RESOLUTION & CRYPTOGRAPHIC UTILITIES
# ===========================================================================


def resolve_pandoc_binary(root_dir: Path) -> str:
    system = platform.system().lower()
    machine = platform.machine().lower()
    arch = (
        "x86_64"
        if machine in ("x86_64", "amd64")
        else ("arm64" if machine in ("arm64", "aarch64") else machine)
    )
    target = f"{'macos' if system == 'darwin' else system}-{arch}"
    pandoc_target = "windows-x86_64" if target == "windows-arm64" else target

    archives_dir = root_dir / "system" / "tools" / "archives"
    manifest_path = root_dir / "system" / "tools" / "tools-manifest.json"

    if system == "windows":
        base_runtime = Path(
            os.environ.get("TEMP", os.environ.get("LOCALAPPDATA", "C:\\Temp"))
        )
        runtime_dir = base_runtime / f"kykloi_pandoc_{pandoc_target}"
        pandoc_bin = runtime_dir / "pandoc.exe"
    else:

        def _probe_exec(target_dir: Path) -> bool:
            try:
                target_dir.mkdir(parents=True, exist_ok=True)
                probe = target_dir / f".probe_{os.getpid()}"
                probe.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
                probe.chmod(0o700)
                res = subprocess.run([str(probe)], capture_output=True)
                probe.unlink(missing_ok=True)
                return res.returncode == 0
            except Exception:
                return False

        candidates = []
        if "KYKLOI_RUNTIME_DIR" in os.environ:
            candidates.append(Path(os.environ["KYKLOI_RUNTIME_DIR"]))

        xdg_cache = os.environ.get("XDG_CACHE_HOME")
        if xdg_cache:
            candidates.append(Path(xdg_cache) / "kykloi")
        elif Path.home().exists():
            candidates.append(Path.home() / ".cache" / "kykloi")

        candidates.append(Path("/var/tmp/kykloi"))
        candidates.append(Path("/tmp/kykloi"))

        valid_base = next((c for c in candidates if _probe_exec(c)), None)
        if valid_base is None:
            sys_pandoc = shutil.which("pandoc")
            if sys_pandoc:
                return sys_pandoc
            raise PermissionError(
                "Execution boundary restriction: Cannot locate a writable, executable directory "
                "to extract bundled Pandoc (all probed cache and temp mounts enforce 'noexec'). "
                "Remediation: Install Pandoc natively via host package manager or define an "
                "executable target via export KYKLOI_RUNTIME_DIR='/path/to/exec_dir'."
            )

        runtime_dir = valid_base / f"runtime_{pandoc_target}"
        pandoc_bin = runtime_dir / "bin" / "pandoc"

    stamp_file = runtime_dir / ".verified_sha256"

    if (
        pandoc_bin.is_file()
        and stamp_file.is_file()
        and (system == "windows" or os.access(pandoc_bin, os.X_OK))
    ):
        return str(pandoc_bin.resolve())

    # Probe host system for native Pandoc before uncompressing archives
    pandoc_candidates = [
        shutil.which("pandoc"),
        "/opt/homebrew/bin/pandoc",
        "/usr/local/bin/pandoc",
        "/opt/local/bin/pandoc",
        "/usr/pkg/bin/pandoc",
        str(
            Path(os.environ.get("ProgramFiles", "C:\\Program Files"))
            / "Pandoc"
            / "pandoc.exe"
        ),
        str(
            Path(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"))
            / "Pandoc"
            / "pandoc.exe"
        ),
        str(Path(os.environ.get("LOCALAPPDATA", "")) / "Pandoc" / "pandoc.exe"),
        str(Path.home() / ".local" / "bin" / "pandoc"),
    ]

    for candidate in pandoc_candidates:
        if candidate and os.path.isfile(candidate):
            if system == "windows" or os.access(candidate, os.X_OK):
                return str(Path(candidate).resolve())

    if not manifest_path.is_file():
        raise FileNotFoundError(f"Tools manifest missing at {manifest_path}")

    try:
        with open(manifest_path, "r", encoding="utf-8") as mf:
            tools_manifest = json.load(mf)
        target_info = tools_manifest["tools"]["pandoc"]["targets"][pandoc_target]
        archive_name = target_info["archive"]
        expected_hash = target_info["sha256"]
    except (KeyError, json.JSONDecodeError) as err:
        raise ValueError(
            f"Failed to read Pandoc manifest definition for {pandoc_target}: {err}"
        )

    archive_path = archives_dir / archive_name
    ext = "zip" if archive_name.endswith(".zip") else "tar.gz"
    log = get_logger("pandoc")

    if archive_path.is_file():
        log.info("Verifying integrity checksum for %s...", archive_path.name)
        actual_hash = compute_file_hash(archive_path)
        if actual_hash != expected_hash:
            raise ValueError(
                f"SHA-256 mismatch for {archive_path.name}:\n"
                f"  Expected: {expected_hash}\n"
                f"  Actual:   {actual_hash}"
            )

        log.info(
            "Extracting isolated Pandoc runtime: %s -> %s",
            archive_path.name,
            runtime_dir,
        )
        runtime_dir.mkdir(parents=True, exist_ok=True)

        if ext == "zip":
            import zipfile

            with zipfile.ZipFile(archive_path, "r") as zf:
                for member in zf.namelist():
                    filename = Path(member).name
                    if filename in ("pandoc", "pandoc.exe"):
                        target_file = (
                            (runtime_dir / "bin" / filename)
                            if system != "windows"
                            else (runtime_dir / filename)
                        )
                        target_file.parent.mkdir(parents=True, exist_ok=True)
                        with zf.open(member) as src, open(target_file, "wb") as dst:
                            shutil.copyfileobj(src, dst)
                        target_file.chmod(0o755)
                        if system == "darwin":
                            subprocess.run(
                                [
                                    "xattr",
                                    "-dr",
                                    "com.apple.quarantine",
                                    str(runtime_dir),
                                ],
                                capture_output=True,
                            )
                        stamp_file.write_text(actual_hash, encoding="utf-8")
                        return str(target_file.resolve())
        else:
            import tarfile

            with tarfile.open(archive_path, "r:gz") as tf:
                for member in tf.getmembers():
                    filename = Path(member.name).name
                    if filename == "pandoc":
                        target_file = runtime_dir / "bin" / "pandoc"
                        target_file.parent.mkdir(parents=True, exist_ok=True)
                        src = tf.extractfile(member)
                        if src:
                            with open(target_file, "wb") as dst:
                                shutil.copyfileobj(src, dst)
                            target_file.chmod(0o755)
                            if system == "darwin":
                                subprocess.run(
                                    [
                                        "xattr",
                                        "-dr",
                                        "com.apple.quarantine",
                                        str(runtime_dir),
                                    ],
                                    capture_output=True,
                                )
                            stamp_file.write_text(actual_hash, encoding="utf-8")
                            return str(target_file.resolve())

    sys_pandoc = shutil.which("pandoc")
    if sys_pandoc:
        return sys_pandoc

    raise FileNotFoundError(
        f"Pandoc executable not found on host and archive missing at {archive_path}"
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
    ciphertext, tag = aes_gcm_encrypt(key, iv, pt_bytes)
    envelope = salt + iv + ciphertext + tag
    return base64.b64encode(envelope).decode("ascii")


def encrypt_binary_file(src_path: Path, dst_path: Path, passphrase: str) -> None:
    with open(src_path, "rb") as f:
        plaintext = f.read()

    salt = os.urandom(16)
    iv = os.urandom(12)
    key = derive_key(passphrase, salt)
    ciphertext, tag = aes_gcm_encrypt(key, iv, plaintext)
    envelope = salt + iv + ciphertext + tag

    dst_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = dst_path.with_suffix(dst_path.suffix + ".tmp")
    with open(tmp_path, "wb") as f:
        f.write(envelope)
    tmp_path.replace(dst_path)


# ===========================================================================
# 6. SQLITE FTS5 SEARCH GENERATION
# ===========================================================================


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
        get_logger("search").info(
            "Generated search index: %d record(s) indexed (%d bytes) at %s",
            len(records),
            out_path.stat().st_size,
            out_path.name,
        )

    except Exception:
        if tmp_path.exists():
            tmp_path.unlink()
        raise


# ===========================================================================
# 7. COMPILATION WORKERS
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
            f"--math-method=katex:{task.relative_root}assets/katex/",
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
        f"--math-method=katex:{task.relative_root}assets/katex/",
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
        f"--math-method=katex:{task.relative_root}assets/katex/",
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


def find_vault_bibliography(src_root: Path) -> Optional[Path]:
    for candidate in ["references.bib", "library.bib", "bibliography.bib"]:
        p = src_root / candidate
        if p.is_file():
            return p
    return None


# ===========================================================================
# 8. PIPELINE ORCHESTRATION (LEDGER INTEGRATED)
# ===========================================================================


def main():
    global SRC, DST, NORM_DB_PATH, SEARCH_DB_FILE
    args = parse_args()
    if args.src:
        SRC = args.src.resolve()
    if args.dst:
        DST = args.dst.resolve()
        SEARCH_DB_FILE = DST / "search.db"
    if args.db_path:
        NORM_DB_PATH = args.db_path.resolve()
    log_file_path = Path(args.log_file).resolve() if args.log_file else None
    log = setup_logging(
        subsystem="compiler",
        verbose=args.verbose,
        log_file=log_file_path,
        enable_console=True,
    )

    with timed_step(
        log, "Cryptographic Self-Test (NIST AES-256-GCM KAT)", logging.DEBUG
    ):
        try:
            verify_cryptographic_engine()
            log.info("Cryptographic accelerator active: [%s]", ACTIVE_ENGINE_NAME)
        except RuntimeError as err:
            log.critical("Cryptographic verification failure: %s", err)
            sys.exit(1)

    with timed_step(log, "Pandoc Binary Resolution", logging.DEBUG):
        try:
            pandoc_bin = resolve_pandoc_binary(PROJECT_ROOT)
            log.info("Resolved Pandoc executable: %s", pandoc_bin)
        except FileNotFoundError as err:
            log.critical("Toolchain dependency error: %s", err)
            sys.exit(1)

    for path, desc in [
        (SRC, "Source directory"),
        (DEFAULTS_YAML, "Pandoc defaults configuration"),
        (DEFAULT_TEMPLATE, "Content template"),
        (LUA_FILTER, "Lua link translation filter"),
    ]:
        if not path.exists():
            log.error("Missing required pipeline dependency: %s at %s", desc, path)
            sys.exit(1)

    if not NORM_DB_PATH.is_file():
        log.critical(
            "Vault ledger missing at '%s'. Normalization is required before building.\n"
            "Run: python system/launch.py --normalize (or select option [3] in the control menu).",
            NORM_DB_PATH,
        )
        sys.exit(1)

    with VaultDB(NORM_DB_PATH) as db:
        db.init_schema()

        central_bib = find_vault_bibliography(SRC)
        current_global_hash = compute_global_dependencies_hash(central_bib)
        old_global_hash = db.get_meta("__GLOBAL_DEPENDENCIES__")
        global_deps_changed = old_global_hash != current_global_hash

        if global_deps_changed:
            log.info(
                "Core templates/toolchain modified. Triggering full re-compilation."
            )

        with timed_step(log, "Ledger Synchronization & Fast Stat Check"):
            sync_db_with_disk(SRC, db)
            vault_records = list(db.get_all_files().values())
            doc_metadata_map = db.get_all_doc_metadata()
            existing_artifacts = db.get_all_build_artifacts()

        md_records = [r for r in vault_records if not r.is_media]
        media_records = [r for r in vault_records if r.is_media]
        has_secure_files = any(r.is_secure for r in vault_records)

        passphrase = args.password
        if has_secure_files and not passphrase and not args.dry_run:
            if not sys.stdin.isatty():
                log.error(
                    "Passphrase required for /secure/ notes in non-interactive environment. "
                    "Provide --password or set KYKLOI_ENCRYPT_KEY."
                )
                sys.exit(1)

            try:
                passphrase = getpass.getpass("Enter passphrase for /secure/ notes: ")
            except (OSError, EOFError):
                log.error("Terminal disconnected: Unable to prompt for passphrase.")
                sys.exit(1)

            if not passphrase:
                log.error("Passphrase required for secure notes.")
                sys.exit(1)

        # Defer directory purging until after passphrase acquisition succeeds
        if args.clean:
            if DST.exists() and not args.dry_run:
                shutil.rmtree(DST)
            if not args.dry_run:
                db.clear_build_state()

        DST.mkdir(parents=True, exist_ok=True)

        passphrase_changed = False
        current_key_fingerprint = ""
        if has_secure_files and passphrase:
            current_key_fingerprint = compute_passphrase_fingerprint(passphrase)
            old_key_fingerprint = db.get_meta("__PASSPHRASE_FINGERPRINT__")
            if old_key_fingerprint and old_key_fingerprint != current_key_fingerprint:
                passphrase_changed = True
                log.info(
                    "Passphrase rotation detected. Invalidating encrypted document cache."
                )

        expected_outputs: set[Path] = set()
        compile_tasks: list[CompileTask] = []
        encrypt_blob_tasks: list[EncryptBlobTask] = []
        asset_sync_jobs: list[tuple[Path, Path]] = []
        staged_artifacts: list[BuildArtifactRecord] = []

        # -------------------------------------------------------------------
        # Media & Binary Assets Dispatch
        # -------------------------------------------------------------------
        for rec in media_records:
            src_path = SRC / rec.rel_path
            rel_posix = Path(rec.rel_path)

            if rec.is_secure:
                target = DST / rel_posix.with_name(rel_posix.name + ".enc")
                rel_target_str = target.relative_to(DST).as_posix()
                expected_outputs.add(target.resolve())
                staged_artifacts.append(
                    BuildArtifactRecord(rel_target_str, rec.sha256, "encrypted_blob")
                )

                cached_art = existing_artifacts.get(rel_target_str)
                if (
                    not target.exists()
                    or passphrase_changed
                    or not cached_art
                    or cached_art.source_sha256 != rec.sha256
                ):
                    encrypt_blob_tasks.append(
                        EncryptBlobTask(
                            src_path=src_path,
                            dst_path=target,
                            passphrase=passphrase or "",
                            dry_run=args.dry_run,
                        )
                    )
            else:
                target = DST / rel_posix
                rel_target_str = target.relative_to(DST).as_posix()
                expected_outputs.add(target.resolve())
                staged_artifacts.append(
                    BuildArtifactRecord(rel_target_str, rec.sha256, "media")
                )

                cached_art = existing_artifacts.get(rel_target_str)
                if (
                    not target.exists()
                    or not cached_art
                    or cached_art.source_sha256 != rec.sha256
                ):
                    asset_sync_jobs.append((src_path, target))

        # -------------------------------------------------------------------
        # Markdown Documents Dispatch
        # -------------------------------------------------------------------
        for rec in md_records:
            src_path = SRC / rec.rel_path
            rel = Path(rec.rel_path)
            out = DST / rel.with_suffix(".html")
            rel_out_str = out.relative_to(DST).as_posix()
            expected_outputs.add(out.resolve())

            staged_artifacts.append(
                BuildArtifactRecord(
                    rel_out_str,
                    rec.sha256,
                    "encrypted_html" if rec.is_secure else "html",
                )
            )

            depth = len(rel.parent.parts) if rel.parent != Path(".") else 0
            relative_root = ("../" * depth) if depth > 0 else ""

            cached_art = existing_artifacts.get(rel_out_str)
            md_content_changed = (
                not cached_art or cached_art.source_sha256 != rec.sha256
            )

            is_dirty = (
                not out.exists()
                or global_deps_changed
                or md_content_changed
                or (rec.is_secure and passphrase_changed)
            )

            meta = doc_metadata_map.get(rec.canonical_filename)
            doc_title = meta.title if meta else rec.stem.replace("-", " ").title()
            has_cites = meta.has_citations if meta else False

            if is_dirty:
                needs_bib = central_bib if (central_bib and has_cites) else None
                compile_tasks.append(
                    CompileTask(
                        md_path=src_path,
                        out_path=out,
                        template_path=DEFAULT_TEMPLATE,
                        relative_root=relative_root,
                        doc_title=doc_title,
                        defaults_yaml=DEFAULTS_YAML,
                        lua_filter=LUA_FILTER,
                        bibliography_path=needs_bib,
                        is_secure=rec.is_secure,
                        passphrase=passphrase,
                        dry_run=args.dry_run,
                        pandoc_bin=pandoc_bin,
                    )
                )

        # -------------------------------------------------------------------
        # Search Records Generation
        # -------------------------------------------------------------------
        search_records: list[dict] = []
        for idx, rec in enumerate(md_records):
            raw_url = Path(rec.rel_path).with_suffix(".html").as_posix().lstrip("/")
            clean_url = urllib.parse.quote(raw_url, safe="/")
            meta = doc_metadata_map.get(rec.canonical_filename)
            search_records.append(
                {
                    "id": idx + 1,
                    "title": meta.title if meta else rec.stem.replace("-", " ").title(),
                    "keywords": meta.keywords if meta else "",
                    "date_edtf": meta.date_edtf if meta else "",
                    "url": clean_url,
                }
            )

        expected_outputs.add(SEARCH_DB_FILE.resolve())

        # -------------------------------------------------------------------
        # Static Assets Sync (UI Functional & Root Icons)
        # -------------------------------------------------------------------
        for folder_name, cat in [("assets", "asset"), ("root", "asset")]:
            src_dir = APP_DIR / folder_name
            if not src_dir.exists():
                continue
            for p in src_dir.rglob("*"):
                if p.is_file() and not is_junk_path(p, src_dir):
                    rel_p = p.relative_to(src_dir)
                    target = DST / (
                        "assets" / rel_p if folder_name == "assets" else rel_p
                    )
                    rel_target_str = target.relative_to(DST).as_posix()
                    expected_outputs.add(target.resolve())

                    h = compute_file_hash(p)
                    staged_artifacts.append(BuildArtifactRecord(rel_target_str, h, cat))

                    cached_art = existing_artifacts.get(rel_target_str)
                    if (
                        not target.exists()
                        or not cached_art
                        or cached_art.source_sha256 != h
                    ):
                        asset_sync_jobs.append((p, target))

        with timed_step(log, "Artifact Pruning", logging.DEBUG):
            orphans_pruned = prune_orphans(
                dst_dir=DST, expected_files=expected_outputs, dry_run=args.dry_run
            )
            if orphans_pruned:
                log.info("Pruned %d orphaned artifact(s) from target.", orphans_pruned)

        if asset_sync_jobs:
            log.info("Synchronizing %d static/media asset(s)...", len(asset_sync_jobs))
            for src_file, target_file in asset_sync_jobs:
                if not args.dry_run:
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_file, target_file)
                log.debug(
                    "Synchronized asset: %s -> %s", src_file.name, target_file.name
                )

        failed = 0
        mp_context = multiprocessing.get_context("spawn")

        if encrypt_blob_tasks:
            log.info("Encrypting %d binary blob(s)...", len(encrypt_blob_tasks))
            with timed_step(
                log, f"Binary Blob Encryption ({len(encrypt_blob_tasks)} items)"
            ):
                with concurrent.futures.ProcessPoolExecutor(
                    max_workers=args.workers, mp_context=mp_context
                ) as executor:
                    futures = [
                        executor.submit(encrypt_blob_worker, t)
                        for t in encrypt_blob_tasks
                    ]
                    for future in concurrent.futures.as_completed(futures):
                        path, ok, err = future.result()
                        if not ok:
                            failed += 1
                            log.error("Failed to encrypt blob %s: %s", path.name, err)
                        else:
                            log.debug("Encrypted binary asset: %s", path.name)

        if compile_tasks:
            log.info("Compiling %d Markdown document(s)...", len(compile_tasks))
            with timed_step(
                log, f"Markdown Compilation ({len(compile_tasks)} documents)"
            ):
                with concurrent.futures.ProcessPoolExecutor(
                    max_workers=args.workers, mp_context=mp_context
                ) as executor:
                    futures = [
                        executor.submit(compile_markdown_worker, t)
                        for t in compile_tasks
                    ]
                    for future in concurrent.futures.as_completed(futures):
                        path, ok, err = future.result()
                        if not ok:
                            failed += 1
                            log.error("Compilation error in %s: %s", path.name, err)
                        else:
                            log.debug("Compiled: %s", path.name)
        else:
            log.info(
                "Document compilation cache hit. All %d documents are up-to-date.",
                len(md_records),
            )

        if failed == 0:
            search_index_needed = (
                not SEARCH_DB_FILE.exists()
                or len(compile_tasks) > 0
                or orphans_pruned > 0
            )
            if search_index_needed:
                build_sqlite_search_index(
                    search_records, SEARCH_DB_FILE, dry_run=args.dry_run
                )

            if not args.dry_run:
                valid_target_paths = {r.target_rel_path for r in staged_artifacts}
                db.upsert_build_artifacts(staged_artifacts)
                db.prune_build_artifacts(valid_target_paths)
                db.set_meta("__GLOBAL_DEPENDENCIES__", current_global_hash)
                if passphrase and current_key_fingerprint:
                    db.set_meta("__PASSPHRASE_FINGERPRINT__", current_key_fingerprint)
                if SEARCH_DB_FILE.exists():
                    db.set_meta("__SEARCH_DB_HASH__", compute_file_hash(SEARCH_DB_FILE))

            log.info("Build pipeline completed successfully.")
        else:
            log.error(
                "Build failed with %d error(s). Ledger build artifacts retained in prior state.",
                failed,
            )
            sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.stderr.write("\n[Kykloi] Build process cancelled by user.\n")
        sys.exit(130)
