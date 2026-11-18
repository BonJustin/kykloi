# Project Kykloi — Content Normalization Layer Architecture Specification

**Module Scope:** Isolated development in `system/normalize/`  
**Status:** Pre-Implementation Architectural Blueprint  
**Primary Directive:** Strict archival determinism, cross-platform portability, zero-dependency execution, and preservation of canonical plain-text Markdown as the sole source of truth.

---

## 1. Architectural Philosophy & Core Invariants

### 1.1 The Source-of-Truth Invariant
* **`content/` is Canonical:** Content files must remain human-readable, portable, and standard-compliant (CommonMark) without requiring proprietary runtime software.
* **No Database Lock-in:** The normalization SQLite database (`vault_index.db`) is strictly a **disposable acceleration cache and forensic ledger**. Deleting `vault_index.db` must cause zero information loss; the system must be capable of reconstructing its entire index from a cold scan of `content/`.
* **Explicit Relative Links:** Links within Markdown documents must remain standard, explicit relative POSIX paths (e.g., `[Title](../notes/target-stem.md)`). The system **rejects** runtime-dependent Wikilinks or bare stem links (`[[stem]]`), ensuring notes can be navigated in any basic text viewer, terminal pager, or web browser.

### 1.2 The Filename Stem as Globally Unique Identifier (UID)
* **Global Stem Uniqueness:** No two files within `content/` may share the same filename stem, regardless of subfolder nesting depth (e.g., `content/math/matrix.md` and `content/physics/matrix.md` constitutes a collision).
* **Strict Portability Standard:** All stems must strictly adhere to a deterministic, cross-platform POSIX and Windows safe subset:
  $$\text{Regex: } \mathtt{\wedge[a-z0-9][a-z0-9\-_]*\$}$$
  * All characters lowercased.
  * Spaces, underscores, and punctuation converted to hyphens or stripped.
  * Windows-forbidden characters (`< > : " / \ | ? *`) strictly disallowed.
  * Unicode normalized to NFC form before ASCII/slug conversion.
* **The UID Guarantee:** Because each stem is globally unique and immutable across folder moves, it serves as the durable semantic anchor for link graph reconciliation.

### 1.3 User Consent & Non-Destructive Operation
* **No Silent Source Mutation:** Standard build pipelines must never silently rename files or rewrite contents without explicit user interaction.
* **The Normalization Gate:** When invoked, the tool detects anomalies, plans a batch of atomic operations, presents a formatted terminal diff, and requests confirmation before modifying any file on disk.
* **Idempotence:** 
  $$\text{Normalize}(\text{Normalize}(\text{vault})) \equiv \text{Normalize}(\text{vault})$$
  Running the normalizer on an already clean vault must execute in $< 0.1\text{ s}$ and perform zero writes.

---

## 2. Isolated Module Scope (`system/normalize/`)

During isolated development, the module will have zero dependencies on other Kykloi scripts and will not be imported by `launch.py` or `build_site.py`.

```text
system/normalize/
├── __init__.py
├── db.py               # SQLite schema setup, ledger transactions, stat-cache queries
├── scanner.py          # Fast-path filesystem traversal & SHA-256 computation
├── slugify.py          # Deterministic cross-platform filename/path sanitizer
├── graph.py            # CommonMark relative link extractor, validator & path calculator
├── engine.py           # Core reconciliation state machine & move/rename heuristics
└── cli.py              # Standalone CLI entry point with terminal diff & opt-in prompt
```

---

## 3. Database Schema & Ledger Architecture

The database is housed at `system/normalize/vault_index.db`. It consists of two primary relational tables and one metadata table:

```sql
-- Schema Version & Integrity Marker
CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- Master File State Ledger
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stem TEXT UNIQUE NOT NULL,           -- Normalized unique identifier
    rel_path TEXT UNIQUE NOT NULL,       -- Relative POSIX path from content/
    sha256 TEXT NOT NULL,                -- Content hash
    mtime REAL NOT NULL,                 -- Last modified timestamp (stat cache)
    size INTEGER NOT NULL,               -- File size in bytes (stat cache)
    is_media INTEGER NOT NULL DEFAULT 0, -- 1 = Binary media, 0 = Markdown document
    is_secure INTEGER NOT NULL DEFAULT 0 -- 1 = Nested in /secure/, 0 = Public
);

CREATE INDEX IF NOT EXISTS idx_files_stem ON files(stem);
CREATE INDEX IF NOT EXISTS idx_files_sha256 ON files(sha256);
CREATE INDEX IF NOT EXISTS idx_files_rel_path ON files(rel_path);

-- Inverted Link Graph (for O(1) Dependency Resolution)
CREATE TABLE IF NOT EXISTS links (
    source_stem TEXT NOT NULL,           -- Originating document stem
    target_stem TEXT NOT NULL,           -- Target document/media stem
    raw_target TEXT NOT NULL,            -- Literal target string in Markdown AST
    line_number INTEGER,                 -- Source file line for forensic diagnostics
    FOREIGN KEY(source_stem) REFERENCES files(stem) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_links_target ON links(target_stem);
CREATE INDEX IF NOT EXISTS idx_links_source ON links(source_stem);
```

### 3.1 Stat-Cache Optimization Invariant
To ensure linear scalability up to 50,000+ files:
1. File traversal queries `os.stat()`: retrieves `(mtime, size)`.
2. Compares directly against `files.mtime` and `files.size` in SQLite.
3. If matches: **Bypass SHA-256 calculation and content reading entirely.**
4. If mismatch or new path: Read bytes, compute SHA-256, parse Markdown AST links.

---

## 4. State Transition & Identity Decision Matrix

A file is identified by the tuple $(P, S, H)$: Path, Stem, and SHA-256 Hash.

| Transition State | Event Type | Detection Logic | Planned Engine Action |
| :--- | :--- | :--- | :--- |
| **$P \to P'$, $S = S$, $H = H$** | Clean Move | $H_{\text{new}} == H_{\text{db}} \land S_{\text{new}} == S_{\text{db}}$ | Register path move. Recalculate relative paths for all referring documents using `os.path.relpath`. |
| **$P = P$, $S \to S'$, $H = H$** | Clean Rename | $H_{\text{new}} == H_{\text{db}} \land P_{\text{dir}} == P_{\text{dir, db}}$ | Register rename. Update referring links from old target string to new sanitized target string. |
| **$P \to P'$, $S \to S'$, $H = H$** | Move + Rename | $H_{\text{new}} == H_{\text{db}} \land P_{\text{new}} \ne P_{\text{db}}$ | Confirm identity via hash match. Propose unified move + rename; update all referring relative links. |
| **$P \to P'$, $S = S$, $H \to H'$** | Move + Content Edit | Old path gone, new path has identical unique stem $S$, but hash changed. | Anchor identity via **Stem UID**. Update hash and path in DB; recalculate relative links in referring files. |
| **$P = P$, $S \to S'$, $H \to H'$** | Rename + Content Edit | Path gone, new file in same folder with non-matching stem and hash. | **Ambiguous.** Treat as `DELETE(old)` and `CREATE(new)`. Flag incoming links to old stem as **Broken/Orphaned**. |
| **$P \to P'$, $S \to S'$, $H \to H'$** | Move + Rename + Edit | Complete divergence of all three attributes. | Information-theoretically uncorrelatable. Treat as atomic `DELETE` + `CREATE`. Emit broken link diagnostics. |

---

## 5. Projected Edge Cases & Proposed Resolutions

### 5.1 Deterministic Collision Resolution
* **Scenario:** A user creates `content/physics/energy.md` while `content/economics/energy.md` already exists.
* **Resolution:** 
  1. The existing entry in `vault_index.db` retains the un-suffixed canonical stem `energy`.
  2. The new colliding file is deterministically assigned the lowest available positive integer suffix: `energy-1.md`.
  3. If both files are completely new (e.g., cold import of an external folder), sort by creation timestamp (`ctime`/`mtime`), falling back to lexicographical path order.

### 5.2 Atomic Vault Mutations & Rollback
* **Scenario:** Normalization requires renaming 15 files and updating 40 links across 10 documents. The process crashes or is terminated (SIGINT/Ctrl+C) halfway through.
* **Resolution:**
  1. All operations are planned in memory as a discrete `TransactionManifest`:
     * List of disk renames (`src -> dst`).
     * List of file text edits (`filepath -> new_content`).
  2. Text edits are written to `.tmp` files alongside originals.
  3. Execution phase applies renames in a strict sequence with rollback journaling. If an error occurs, the rollback journal restores original names and removes `.tmp` artifacts.
  4. SQLite commit is executed **only after all filesystem changes complete successfully**.

### 5.3 Non-Interactive / Headless Operation
* **Scenario:** The normalization script is invoked in CI/CD, headless automated tests, or without a TTY (`sys.stdin.isatty() == False`).
* **Resolution:**
  * Add explicit execution flags:
    * `--check`: Lint mode. Exits with code `0` if vault is normalized; code `1` with a formatted report if drift or anomalies exist.
    * `--auto-apply`: Automatically applies changes without prompting (for scripted pipelines).
    * `--dry-run`: Prints planned transformations without writing to disk or database.
  * Default behavior in non-interactive mode without flags: Fail-fast with diagnostic error output.

### 5.4 Media Files with Large Binaries
* **Scenario:** Moving or adding large video, audio, or high-resolution image files.
* **Resolution:**
  * Media files are identified by extension (`.png`, `.jpg`, `.jpeg`, `.webp`, `.svg`, `.mp4`, `.pdf`, etc.).
  * Media entries are populated in the `files` table with `is_media = 1`.
  * The stat-cache invariant strictly guards media files. Hashing is bypassed completely on subsequent runs if `(mtime, size)` remain unchanged.

---

## 6. Implementation Stages (Isolated Module)

1. **Phase 1: DB Schema & Utilities (`db.py`, `slugify.py`)**  
   Create SQLite connection handlers, schema setup, and the deterministic slugification and validation functions.
2. **Phase 2: Scanner & State Differ (`scanner.py`, `engine.py`)**  
   Implement directory traversal, stat-cache checking, SHA-256 calculation, and identity diffing against SQLite.
3. **Phase 3: Link Extraction & Relative Path Mathematics (`graph.py`)**  
   Parse Markdown files for CommonMark links/images, store edges in `links`, and implement `os.path.relpath` healing logic.
4. **Phase 4: CLI, Interactive Terminal Diff & Transaction Engine (`cli.py`)**  
   Build the terminal interface with formatted change tables, user confirmation flow, atomic execution, and rollback safeguards.
5. **Phase 5: Verification & Stress Testing**  
   Construct an isolated test suite simulating moves, edits, collisions, and non-portable filenames to ensure complete determinism before wiring into Kykloi core.
