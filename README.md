# Kykloi

## 1. Project Overview & Core Architecture

* **Archival Philosophy**: Offline-first, deterministic knowledge vault compiler transforming plain-text Markdown repositories into self-contained, client-side searchable static HTML distributions.
* **Zero External Dependencies**: Core engine operates exclusively on the Python standard library (no third-party `pip` dependencies; `dependencies = []`).
* **Document Compilation**: Uses Pandoc (>= 3.0) via Lua filters to compile CommonMark Markdown to semantic, accessible HTML.
* **Deterministic Ledger**: SQLite catalog (`vault-index.db`) indexes document metadata, cryptographic SHA-256 digests, citation keys, and relative link graphs.
* **Client-Side Search**: Compiles an offline SQLite FTS5 database (`search.db`) queried in the browser via SQLite WASM and Web Workers.
* **Selective Vault Encryption**: Content placed in `content/secure/` is compiled to AES-256-GCM encrypted payloads (`.enc`) and decrypted client-side via the browser Web Cryptography API (`window.crypto.subtle`).
* **Hardware Acceleration**: Automatic C-ABI crypto acceleration via native system libraries (macOS CommonCrypto, Windows CNG/BCrypt, POSIX OpenSSL `libcrypto`) with a pure-Python fallback.
* **Portable Appliance**: Portable toolchain bootstrapping enables running entirely off air-gapped removable media (flash drives) across Linux, macOS, and Windows without host installation.

---

## 2. Workspace & Filesystem Layout

```text
kykloi/
├── content/                    # Source archival vault (Markdown notes and media)
│   └── secure/                 # Encrypted subtree (compiled to client-side encrypted blobs)
├── dist/                       # Compiled static site distribution (web root)
├── backups/                    # Default destination for deterministic vault zip archives
├── logs/                       # Rotating application telemetry and test reports
├── test-content/               # Test fixtures and reference integration content
├── launch.sh                   # POSIX launcher wrapper (Linux & macOS)
├── launch.bat                  # Windows batch launcher wrapper
├── pyproject.toml              # Standard Python packaging metadata
└── system/                     # Kykloi engine subsystem
    ├── launch.py               # Main daemon, HTTP server, and interactive CLI/TUI
    ├── backup.py               # Archival backup generator (hardened ZIP + SHA-256 sidecar)
    ├── config.json             # Vault identity configuration (title, brand, tab prefix)
    ├── logger.py               # Centralized rotating file and console telemetry
    ├── test_runner.py          # Field test harness and environment diagnostic suite
    ├── build/                  # SSG compilation pipeline
    │   ├── build.py            # Static compiler script
    │   ├── html-config.yaml    # Pandoc metadata configuration
    │   ├── translate-links.lua # AST link translation filter (maps .md -> .html)
    │   ├── templates/          # Base Pandoc HTML templates
    │   ├── root/               # Static site root assets (manifest, favicons, root index)
    │   └── assets/             # CSS (Pico), JS (SQLite WASM), fonts, KaTeX math bundle
    ├── normalize/              # Vault ledger, sanitization, and link healing
    │   ├── cli.py              # Standalone ledger/audit CLI tool
    │   ├── db.py               # SQLite ledger interface
    │   ├── engine.py           # Diff and rename computation engine
    │   ├── graph.py            # AST relative link parser and validator
    │   ├── scanner.py          # Vault filesystem scanner and junk filter
    │   ├── slugify.py          # Deterministic stem slugification routines
    │   └── vault-index.db      # SQLite ledger index file
    └── tools/                  # Offline runtime management
        ├── fetch-tools.py      # Portable toolchain fetcher script
        ├── fetch_tools.py      # Toolchain download and hash verification routines
        ├── verify-manifest.py  # Checksum integrity auditor for downloaded archives
        ├── tools-manifest.json # Cryptographic manifest of portable Python & Pandoc archives
        └── archives/           # Local staging cache for pre-packaged toolchain tarballs
```

---

## 3. Vault Invariants & Conventions

* **Low-Mutation Archival Standard**: Kykloi never modifies the internal text of user Markdown files with the sole exception of internal link healing to prevent maintenance nightmares when re-organizing personal repositories.
* **Deterministic File Stem Slugs**: `YYYYMMDDHHMMSS-kebab-case-title.ext`
  * Leading 14-digit UTC/local timestamp prefix.
  * Hyphen-separated lowercase alphanumeric stem.
  * Preserved extension (`.md`, `.png`, `.jpg`, `.pdf`, etc.).
* **Standard Frontmatter**: Canonical YAML block at file origin:
  ```yaml
  ---
  title: "Document Title"
  date_edtf: "YYYY-MM-DD"
  keywords: ["tag1", "tag2"]
  ---
  ```
* **Relative Link Architecture**:
  * **Explicitly Disallowed**: Proprietary wikilinks (`[[target]]`) are deliberately unsupported to ensure total repository legibility without an active indexer or proprietary application.
  * **Standard Markdown Links**: `[Label](path/to/20261116170353-target-note.md)`
  * **Media Embeds**: `![Alt Text](media/diagram.png)`
  * **Pandoc Citations**: `[@citation_key]`
  * **Link Translation**: The compiler translates relative `.md` and `.markdown` paths to `.html` in distribution artifacts while leaving source documents intact.
* **Security Boundaries**:
  * Root boundary: Relative paths escaping `content/` (`../`) trigger critical boundary errors.
  * Context boundary: Public documents embedding `/secure/` media (or vice-versa) trigger isolation boundary violations.
* **Junk Path Filtering**: Automatic exclusion of OS/editor artifacts:
  * `.DS_Store`, `Thumbs.db`, `desktop.ini`
  * Version control directories (`.git/`, `.svn/`, `.hg/`)
  * Editor swap and backup files (`*~`, `.*.swp`, `.#*`)

---

## 4. Prerequisites & Runtime Hydration Model

### 4.1 System Requirements
1. **Python**: Version `>= 3.10` (tested through `3.15`).
2. **Pandoc**: Version `>= 3.0` (compiled against pandoc AST v1.23+).

### 4.2 Runtime Resolution Hierarchy
When launched via `launch.sh` or `launch.bat`:
1. **Host Probing**: Probes system `$PATH` and standard system trees (`/opt/homebrew`, `/usr/local`, `%LOCALAPPDATA%`, `py -3`). If a compatible Python is found, it is executed directly.
2. **Portable Fallback**: If no compatible host runtime exists, the launcher extracts a pre-packaged portable standalone Python archive from `system/tools/archives/` into an executable runtime cache.
3. **Execution Partition Resolution**: Probes target directories in order to bypass `noexec` mounts:
   * `$KYKLOI_RUNTIME_DIR` (explicit user override)
   * `${XDG_CACHE_HOME:-~/.cache}/kykloi` (POSIX) or `%TEMP%\kykloi_runtime_*` (Windows)
   * `/var/tmp/kykloi`
   * `/tmp/kykloi`
   * *Aborts with diagnostic guidance if all available partitions reject execution.*
4. **Integrity Verification**: Portable archives are verified against `system/tools/tools-manifest.json` via SHA-256 before extraction.

---

## 5. Interactive Control Plane (CLI / TUI)

Invoking `./launch.sh`, `launch.bat`, or `python3 system/launch.py` without action flags starts an embedded background HTTP server and displays the interactive control plane:

```text
==================== KYKLOI CONTROL PLANE ====================
  Status:     Vault: Ready (http://127.0.0.1:8000/) | Not Compiled
  Passphrase: [Set] | [Not Set]
  Ledger:     [Indexed (X notes, Y assets)] | [Uninitialized] | [Degraded]
  Crypto:     [OpenSSL (C-ABI libcrypto.so.3)] | [Pure-Python (SLOW)]
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
 [10] Configure Vault Identity (Title & Brand)
 [11] Pre-Package Portable Toolchain (Download Multi-Platform Archives)
  [0] Exit
==============================================================
```

### Menu Action Breakdown
* `[1] Compile Site (Incremental)`: Runs vault audit, prompts for unresolved normalizations or broken links, prompts for `/secure/` passphrase if encrypted content exists, and compiles modified files using stat caching.
* `[2] Rebuild Site (Clean Purge)`: Purges `dist/` and build manifests, rebuilding all assets and documents from scratch.
* `[3] Audit Vault Health`: Non-destructive, read-only analysis of filenames, directory structure, dead relative links, unanchored citations, and security boundary violations.
* `[4] Normalize Vault Filenames`: Interactively calculates and applies on-disk physical renames to align file stems with the `YYYYMMDDHHMMSS-slug` convention.
* `[5] Scaffold New Archival Note`: Interactive wizard generating a new note with slugified stem, valid EDTF date, and standard frontmatter.
* `[6] Set / Update Secure Passphrase`: Prompts for passphrase held strictly in volatile daemon memory (never persisted to disk) for `/secure/` compilation.
* `[7] Open Vault in Default Browser`: Triggers OS default browser to open the bound daemon URL (offers compilation if unbuilt).
* `[8] Cryptographic Acceleration Diagnostics`: Displays active AES-GCM engine, C-ABI bindings, and hardware instruction set acceleration status.
* `[9] Create Archival Vault Backup (.zip)`: Compresses `content/` into a timestamped zip archive with a companion SHA-256 verification sidecar.
* `[10] Configure Vault Identity`: Prompts to update `vault_title`, `brand_text`, and browser `title_prefix` in `system/config.json`.
* `[11] Pre-Package Portable Toolchain`: Sub-menu to fetch offline Python and Pandoc archives for multi-platform USB deployment:
  * `[1] Download complete multi-platform toolchain` (All targets: Linux x86_64/arm64 gnu/musl, macOS x86_64/arm64, Windows x86_64/arm64; ~330 MB).
  * `[2] Download host toolchain only` (Current operating system/architecture only; ~50 MB).
* `[0] Exit`: Terminates background HTTP server daemon and exits cleanly.

---

## 6. Command-Line Invocation Reference

### 6.1 Root Launchers (`launch.sh` / `launch.bat`)

Shell wrappers performing host probing, fallback hydration, and process delegation.

```sh
# POSIX (Linux / macOS)
./launch.sh [LAUNCHER_FLAGS] [PASSTHROUGH_ARGS...]

# Windows
launch.bat [LAUNCHER_FLAGS] [PASSTHROUGH_ARGS...]
```

* **Launcher Flags**:
  * `--force-fallback`: Bypasses host system Python probing; forces hydration and execution of bundled portable standalone Python runtime.
* **Passthrough**: Any additional arguments or flags are forwarded directly to `system/launch.py`.

---

### 6.2 Control Hub Daemon (`system/launch.py`)

Primary operational hub supporting interactive server mode and direct CLI batch invocation.

```sh
python3 system/launch.py [OPTIONS]
```

#### Networking & Daemon Options
* `--host STR`: Bind interface address for embedded HTTP server (default: `127.0.0.1`).
* `--port INT`: Starting base TCP port (default: `8000`). Automatically tests up to 15 successive ports if occupied.

#### Build & Compilation Flags
* `--build`: Compiles the static site and exits immediately without launching the interactive menu.
* `--clean`: Purges `dist/` and rebuilds the static site from scratch (must be paired with `--build`).
* `--password STR`: Passphrase used for AES-256-GCM encryption of `/secure/` documents (defaults to environment variable `KYKLOI_ENCRYPT_KEY`).

#### Vault Maintenance & Health Flags
* `--audit`: Runs non-destructive vault health analysis (broken relative links, un-normalized filenames, security boundaries) and exits with code `0` (clean) or `1` (issues detected).
* `--normalize`: Interactively stages and applies filename normalizations on disk.
* `--auto-normalize`: Applies all staged filename normalizations automatically without confirmation prompts.
* `--new`: Launches interactive note scaffolding wizard and exits.

#### Vault Branding & Configuration Flags
* `--set-title STR`: Updates `vault_title` in `system/config.json`.
* `--set-brand STR`: Updates `brand_text` (monogram/header label) in `system/config.json`.
* `--set-title-prefix STR`: Updates `title_prefix` for browser document tabs in `system/config.json`.
*(Exits immediately after writing unless `--build` is specified).*

#### Backup & Archival Flags
* `--backup`: Triggers an automated zip backup of `content/` with SHA-256 checksum sidecar.
* `--backup-dest DIR`: Target destination directory for backup archive (default: `backups/`).
* `--backup-name STR`: Explicit filename for archive (default: `kykloi-backup-content-YYYYMMDDTHHMMSSZ.zip`).
* `--prune-old`: Purges older backup archives and sidecars in target destination after creating new backup.

#### Toolchain & Maintenance Flags
* `--fetch-host`: Downloads offline Python and Pandoc archives for current host architecture to `system/tools/archives/` and exits.
* `--fetch-all`: Downloads complete multi-platform offline toolchain archives and exits.
* `--fetch-force`: Forces re-download of toolchain archives even if local archive hashes match.
* `--purge-cache`: Purges temporary extracted runtimes and sandbox caches from system temp/cache directories.

#### Telemetry, Testing & Diagnostic Flags
* `--crypto-info`: Prints active cryptographic acceleration backend diagnostics and exits.
* `--test`: Runs end-to-end automated field integration test suite in an isolated sandbox.
* `--clean-test`: Runs field integration test suite and automatically cleans up ephemeral test sandboxes.
* `--verbose`: Enables granular `DEBUG` telemetry output in console.
* `--log-file PATH`: Sets path for persistent diagnostic log file on disk.

---

### 6.3 Standalone Compiler Engine (`system/build/build.py`)

Static site compiler invoked by the control plane or directly in scripted/CI pipelines.

```sh
python3 system/build/build.py [OPTIONS]
```

* `--clean`: Purges destination directory and build manifest before compiling.
* `--dry-run`: Executes build pipeline in simulation mode without writing files.
* `--verbose`: Emits detailed step-by-step diagnostic telemetry.
* `--workers INT`: Worker thread pool size for parallel compilation (default: system CPU count or `4`).
* `--password STR`: Passphrase for encrypting `/secure/` content (defaults to `$KYKLOI_ENCRYPT_KEY`).
* `--src PATH`: Overrides source content directory path (default: `content/`).
* `--dst PATH`: Overrides distribution output directory path (default: `dist/`).
* `--db-path PATH`: Overrides SQLite ledger path (default: `system/normalize/vault-index.db`).
* `--config-path PATH`: Overrides JSON site identity configuration path (default: `system/config.json`).
* `--log-file PATH`: Destination path for persistent compilation logs.

---

### 6.4 Vault Normalizer & Ledger CLI (`system/normalize/cli.py`)

Low-level ledger indexing, link healing, and filename sanitization utility.

```sh
python3 system/normalize/cli.py [OPTIONS]
```

* `--audit`: Read-only health analysis; inspects file stems, relative links, and vault root boundaries. Default behavior when invoked without flags.
* `--normalize`: Interactively prompts before applying calculated filename renames to disk.
* `--auto-apply`: Automatically applies calculated disk renames without confirmation prompts.
* `--new`: Scaffolds a new note with valid slug, EDTF date, and frontmatter.
* `--vault-dir PATH`: Target content vault directory (default: `content/`).
* `--db-path PATH`: Target SQLite ledger file (default: `system/normalize/vault-index.db`).

---

### 6.5 Offline Toolchain Downloader (`system/tools/fetch-tools.py`)

Retrieves portable toolchain archives based on `system/tools/tools-manifest.json`.

```sh
python3 system/tools/fetch-tools.py [OPTIONS]
```

* *(no flags)*: Downloads complete multi-platform toolchain archives (Linux, macOS, Windows; x86_64 and ARM64).
* `--host-only`: Downloads only the archives required for the current host OS and architecture.
* `--force`: Forces re-download of archives even if local checksums match the manifest.

---

### 6.6 Toolchain Manifest Integrity Verifier (`system/tools/verify-manifest.py`)

Audits staged offline toolchain archives against SHA-256 checksums in `tools-manifest.json`.

```sh
python3 system/tools/verify-manifest.py [OPTIONS]
```

* `--manifest PATH`: Path to manifest file (default: `system/tools/tools-manifest.json`).
* `--archives PATH`: Path to archives directory (default: `system/tools/archives`).
* `--update`: Recomputes SHA-256 hashes of physical archives on disk and updates `tools-manifest.json`.

---

## 7. Environment Variables Reference

| Variable | Type | Description | Default |
| :--- | :--- | :--- | :--- |
| `KYKLOI_ENCRYPT_KEY` | String | Passphrase for encrypting and decrypting `/secure/` vault notes. | `None` |
| `KYKLOI_FORCE_FALLBACK` | `1` / `0` | If `1`, bypasses host Python/Pandoc probing and forces portable runtime extraction. | `0` |
| `KYKLOI_RUNTIME_DIR` | Path | Explicit directory for extracting portable toolchain runtimes (bypasses `noexec` mounts). | OS cache / temp |
| `KYKLOI_LIBC` | `gnu` / `musl` | Overrides Linux libc auto-detection for portable toolchain selection. | Auto-detected |
| `KYKLOI_CRYPTO_ENGINE` | `pure` | If set to `pure`, forces pure-Python AES-GCM engine, bypassing hardware C-ABI libraries. | Auto-selected |
| `KYKLOI_CONTENT_DIR` | Path | Overrides source directory for notes and media. | `<repo>/content` |
| `KYKLOI_DIST_DIR` | Path | Overrides output directory for static site compilation. | `<repo>/dist` |
| `KYKLOI_DB_PATH` | Path | Overrides path to SQLite ledger database. | `<repo>/system/normalize/vault-index.db` |
| `KYKLOI_CONFIG_PATH` | Path | Overrides path to vault identity configuration file. | `<repo>/system/config.json` |
| `KYKLOI_LOG_MAX_BYTES` | Integer | Maximum byte threshold before rotating log files. | `5242880` (5 MB) |
| `REQ_MAJ` | Integer | Minimum required Python major version evaluated by launcher scripts. | `3` |
| `REQ_MIN` | Integer | Minimum required Python minor version evaluated by launcher scripts. | `10` |

---

## 8. Cryptography & Security Model

* **Cipher Suite**: AES-256-GCM (Authenticated Encryption with Associated Data).
* **Key Derivation (KDF)**: PBKDF2-HMAC-SHA256:
  * 100,000 iterations.
  * 16-byte random salt generated per-file via `os.urandom()`.
  * 256-bit derived key.
* **Payload Structure (`.enc`)**:
  * Bytes 0–15: Salt (16 bytes)
  * Bytes 16–27: Initialization Vector / Nonce (12 bytes)
  * Bytes 28 to `N-16`: Ciphertext
  * Last 16 bytes: GCM Authentication Tag (16 bytes)
* **Client-Side Decryption**: Handled via browser `window.crypto.subtle` (`decrypt.js`). Passphrases are never written to disk or included in static distribution artifacts.
* **Metadata vs. Content Boundary**:
  * Unencrypted: Note title, slug, EDTF date, keyword tags (indexed in `search.db` to allow full discoverability).
  * Encrypted: Document body HTML, embedded code blocks, and sensitive binary media located inside `/secure/`.
* **Hardware Acceleration Priority**:
  1. macOS: `CommonCrypto` via `ctypes` (`kCCAlgorithmAES`, `kCCModeGCM`).
  2. Windows: Windows Cryptography API: Next Generation (`bcrypt.dll` CNG) via `ctypes`.
  3. POSIX: OpenSSL C-ABI via `ctypes` (`libcrypto.so.3` / `libcrypto.so.1.1`).
  4. Fallback: Pure-Python AES-GCM baseline (~1 MB/s throughput; emits warning).
* **Threat Model Limitations**: Protects confidentiality of static distribution artifacts at rest. Does not protect against side-channel/cache-timing attacks or nation-state adversaries.

---

## 9. Embedded HTTP Server Specifications

* **Daemon Implementation**: Threaded HTTP server based on `http.server.BaseHTTPRequestHandler` and `socketserver.ThreadingMixIn`.
* **Default Socket Binding**: `127.0.0.1:8000` (iterates up to port `8015` on collision).
* **RFC 7233 Byte-Range Compliance**: Supports `Range: bytes=start-end` requests for streaming media and partial chunk fetching of `search.db` and WebAssembly binaries.
* **MIME Mapping**:
  * `.wasm` -> `application/wasm`
  * `.woff2` -> `font/woff2`
  * `.webmanifest` -> `application/manifest+json`
  * `.enc` -> `application/octet-stream`
  * `.svg` -> `image/svg+xml`
* **Compilation Lock Concurrency**: Emits HTTP `503 Service Unavailable` with `Retry-After: 1` if a client requests assets while a compilation process is active.

---

## 10. Automated Field Testing & Diagnostics

Kykloi includes an end-to-end field testing suite exercising all components in an isolated temporary sandbox:

```sh
# Run field test suite:
python3 system/launch.py --test

# Run field test suite and clean ephemeral artifacts:
python3 system/launch.py --clean-test
```

### Test Pipeline Execution Steps
1. **Isolated Sandbox Initialization**: Establishes sandboxed directory partitions.
2. **Empty Vault Handling**: Confirms graceful normalization and indexing on empty trees.
3. **Fixture Hydration**: Populates sandbox from `test-content/`.
4. **Vault Normalization**: Validates filename sanitization and SQLite ledger population.
5. **Full Site Compilation**: Tests Pandoc compilation, asset bundling, and SQLite FTS5 database creation.
6. **Stat-Cache Verification**: Confirms incremental compilation skips unmodified files.
7. **Graph Healing & Mutation**: Modifies file stems and verifies link repair graph updates.
8. **Static HTTP & Byte-Range Testing**: Tests daemon header dispatch and RFC 7233 range requests.
9. **Archival Backup Verification**: Validates deterministic ZIP creation and SHA-256 sidecar checksums.
