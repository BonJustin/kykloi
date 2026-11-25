# Kykloi

Deterministic Archival Knowledge Management and Static Site Generator (SSG).

Kykloi is an offline-first knowledge vault compiler that normalizes Markdown documents, maintains a deterministic SQLite ledger, builds client-side SQLite WASM search indices, and optionally encrypts `/secure/` entries using AES-256-GCM.

---

## Prerequisites

Kykloi requires:

1. **Python >= 3.10** (no external `pip` dependencies required; uses standard library exclusively).
2. **Pandoc** (required for compiling Markdown to HTML).

### Installing Prerequisites

#### 1. Host Installation (Recommended)

Installing Python and Pandoc via your system package manager is the recommended approach, bypassing all binary extraction and `noexec` temporary filesystem restrictions:

* **macOS**:

  ```sh
  brew install python pandoc
  ```

* **Debian / Ubuntu**:

  ```sh
  sudo apt update && sudo apt install -y python3 pandoc
  ```

* **Fedora / RHEL**:

  ```sh
  sudo dnf install -y python3 pandoc
  ```

* **Arch Linux**:

  ```sh
  sudo pacman -S python pandoc-cli
  ```

* **Windows** (via WinGet or Scoop):

  ```powershell
  winget install Python.Python.3.12 JohnMacFarlane.Pandoc
  ```

#### 2. Standalone Toolchain Bootstrapping

If Pandoc is not installed globally on your machine, Kykloi includes an autonomous toolchain fetcher to download and verify portable binaries for your host architecture:

```sh
# Fetch Pandoc (and fallback Python) for the current host architecture:
python3 system/tools/fetch-tools.py --host-only

# Or fetch all multi-platform archives:
python3 system/tools/fetch-tools.py
```

Downloaded archives are cryptographically verified against `system/tools/tools-manifest.json` using SHA-256 digests and staged in `system/tools/archives/`.

---

## Quick Start

### 1. Launching the Control Plane

You can start Kykloi using the provided launcher scripts or by directly invoking Python:

* **Linux / macOS**:

  ```sh
  ./launch.sh
  ```

  *(Or: `python3 system/launch.py`)*

* **Windows**:

  ```cmd
  launch.bat
  ```

  *(Or: `python system\launch.py`)*

The launcher will bind an HTTP daemon (default: `http://127.0.0.1:8000`) and display the interactive control plane menu:

```text
==================== KYKLOI CONTROL PLANE ====================
  Status:     Vault: Not Compiled
  Passphrase: [Not Set]
  Ledger:     [Uninitialized]
  Crypto:     [OpenSSL (C-ABI libcrypto.so.3)]
==============================================================
  [1] Compile Site (Incremental)
  [2] Rebuild Site (Clean Purge)
  [3] Audit Vault Health (Dead Links & Filename Check)
  [4] Normalize Vault Filenames (Renames On Disk)
  [5] Scaffold New Archival Note
  [6] Set / Update Secure Passphrase
  [7] Open Vault in Default Browser
  [8] Cryptographic Acceleration Diagnostics
  [9] Create Archival Vault Backup (.zip)
  [0] Exit
==============================================================
```

### 2. Adding & Compiling Content

1. Place Markdown documents and media assets into the `content/` folder (or select `[5] Scaffold New Archival Note` from the menu).
2. Documents placed in `content/secure/` are encrypted with AES-256-GCM. Set a passphrase via menu option `[6]` or via the `KYKLOI_ENCRYPT_KEY` environment variable.
3. Select `[1] Compile Site` (or run `python3 system/launch.py --build`).
4. Select `[7] Open Vault in Default Browser` to view the generated static site.

### 3. Running Field Tests & Diagnostics

To verify your environment, cryptographic acceleration, ledger normalization, and static server functionality:

```sh
# Run comprehensive end-to-end integration test suite:
python3 system/launch.py --test

# Run tests and clean up ephemeral caches:
python3 system/launch.py --clean-test
```

---

## Architecture & Security Model

* **Launcher Scripts (`launch.sh` / `launch.bat`)**: These shell wrappers probe for host Python installations across standard paths. If Python >= 3.10 is installed, they directly execute `system/launch.py`. If host Python is unavailable, they unpack bundled portable Python binaries from `system/tools/archives/` (if present) to an authorized executable partition (`KYKLOI_RUNTIME_DIR` or cache).
* **Zero External Dependencies**: The core compiler, normalizer, link-repair graph, and HTTP server do not require third-party Python packages (`dependencies = []`).
* **Cryptographic Acceleration**: Hardware-accelerated AES-256-GCM is automatically selected using OS-native libraries (macOS CommonCrypto, Windows CNG/BCrypt, POSIX OpenSSL via `ctypes`) with a pure-Python fallback.
* **Threat Model**: Kykloi is **not** designed to resist cache-timing attacks or nation-state adversaries. It provides single-user or limited-audience privacy for distribution artifacts (`dist/`), allowing the static site to be hosted without exposing the raw archival source repository (`content/`).
* **Search & Metadata**: Notes within `dist/` remain discoverable via SQLite WASM full-text search. Metadata (titles, EDTF dates, keywords) remain unencrypted for searchability, while sensitive note bodies and secure media blobs require the passphrase to decrypt client-side via `window.crypto.subtle`.
