A comprehensive audit of the codebase reveals several **remaining issues and operational edge cases**. 

They are categorized below by subsystem, severity, and failure mechanics, along with their targeted resolutions.

---

### Category 1: Subsystem-Specific Architectural Gaps

#### 1. Collision Deadlock in the Normalization Engine
* **Location:** `system/normalize/engine.py` (inside `matched_pairs` loop, lines 145–210)
* **Mechanics:** 
  In Step 1 of `compute_diff`, duplicate stems across directories are flagged in `diff_plan.collisions`. However, inside the `matched_pairs` loop, if two files on disk already share a stem (for example, `archive/notes.md` and `current/notes.md`), the engine tests:
  ```python
  needs_stem_sanitize = (
      not is_valid_stem(disk_rec.stem) or disk_rec.stem != canonical_stem
  )
  ```
  Because `notes` is already a valid canonical stem, `needs_stem_sanitize` evaluates to `False`. The engine takes the `else` branch, yields `ActionType.NOOP`, and adds `notes` to `allocated_stems` without checking if it was already allocated.
* **Failure Mode:** 
  The normalization plan reports a collision anomaly in the terminal output, but **generates zero actions to resolve it**. Running `--auto-apply` completes with `NOOP`, yet running `--check` continues to fail with exit code `1`. The vault enters a perpetual "dirty" state where the engine identifies the collision but cannot autonomously resolve it.
* **Resolution:**
  In `engine.py`, check `disk_rec.stem in allocated_stems` *even if* `needs_stem_sanitize` is false. If already allocated, force `ActionType.RESOLVE_COLLISION` to append a `-1` suffix.

---

#### 2. Collisions Between Notes and Media Assets
* **Location:** `system/normalize/db.py` (Line 20)
* **Mechanics:**
  The schema defines:
  ```sql
  CREATE TABLE IF NOT EXISTS files (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      stem TEXT UNIQUE NOT NULL,
      ...
  );
  ```
* **Failure Mode:**
  If a Markdown document is named `system-overview.md` and an associated diagram is saved alongside it as `system-overview.png`, both share the stem `system-overview`. In `sync_db_with_disk()`, the file inserted second will overwrite the first via `ON CONFLICT(stem) DO UPDATE`. If the image overwrites the note, the note vanishes from the ledger and will not be indexed or compiled.
* **Resolution:**
  Scope stem uniqueness by file category in SQLite:
  ```sql
  UNIQUE(stem, is_media)
  ```
  Update the conflict clause to `ON CONFLICT(stem, is_media) DO UPDATE ...`.

---

#### 3. Secure Note Media Encryption Disconnect
* **Location:** `system/build/build_site.py` vs. `system/build/translate_links.lua`
* **Mechanics:**
  * In `build_site.py`, binary encryption only triggers for files where `rec.is_secure == True` (meaning the asset physically resides in a `/secure/` directory).
  * In `translate_links.lua`, the image filter checks `if is_secure` (which is set globally whenever a secure Markdown document is compiling) and appends `.enc` to **all** image links.
* **Failure Mode:**
  If an encrypted note in `content/secure/report.md` includes an image located in public media `content/media/chart.png`, `build_site.py` copies it to `dist/media/chart.png` unencrypted. However, Pandoc compiles the link to `chart.png.enc`. The browser runtime searches for `chart.png.enc`, receives an HTTP 404, and the image fails to load.
* **Resolution:**
  In `translate_links.lua`, ensure `.enc` is only appended if the image target URL actually points to a path containing `/secure/`.

---

### Category 2: Parsing & Lexing Edge Cases

#### 4. Inline Code Span False-Link Extraction
* **Location:** `system/normalize/graph.py` (Line 22)
* **Mechanics:**
  `graph.py` attempts to sanitize lines before running link regex by masking inline code spans:
  ```python
  INLINE_CODE_PATTERN = re.compile(r"`+[^`]+`+")
  ```
* **Failure Mode:**
  In CommonMark, inline code delimited by multiple backticks can contain single backticks (e.g., `` `code with ` backtick` ``). The negated set `[^`]+` terminates at the *first* inner backtick. The remaining segment of the code span is unmasked. If that unmasked text resembles Markdown link syntax (common in programming notes or documentation), it is parsed as a real document link and corrupted during link healing.
* **Resolution:**
  Replace with a delimiter-matched backreference pattern:
  ```python
  INLINE_CODE_PATTERN = re.compile(r"(`+)(?:(?!\1).)+?\1")
  ```

---

#### 5. Extension Case Mismatch in Lua Filter
* **Location:** `system/build/translate_links.lua` (Line 18)
* **Mechanics:**
  The Pandoc Lua filter converts internal links from `.md` to `.html`:
  ```lua
  if path:match("%.md$") then
    path = path:gsub("%.md$", ".html")
    el.target = path .. separator .. suffix
  end
  ```
* **Failure Mode:**
  If a link is authored as `[Chapter](chapter.MD)` or `[Chapter](chapter.markdown)` and compiled prior to running normalization, the Lua pattern `%.md$` fails to match. Pandoc outputs `<a href="chapter.MD">`, breaking the link in the static HTML build.
* **Resolution:**
  Make the Lua pattern case-insensitive and support `.markdown`:
  ```lua
  if path:match("%.[mM][dD]$") or path:match("%.[mM][aA][rR][kK][dD][oO][wW][nN]$") then
    path = path:gsub("%.%a+$", ".html")
    el.target = path .. separator .. suffix
  end
  ```

---

### Category 3: Security & Operational Invariants

#### 6. Passphrase Exposure via Process Arguments
* **Location:** `system/launch.py` (Line 233)
* **Mechanics:**
  `launch.py` executes the compilation subprocess with the passphrase passed on the command line:
  ```python
  cmd = [sys.executable, str(BUILD_SCRIPT)]
  if passphrase:
      cmd.extend(["--password", passphrase])
  res = subprocess.run(cmd, cwd=str(ROOT_DIR))
  ```
* **Failure Mode:**
  Although `launch.py` masks the passphrase in terminal log strings, passing it via `sys.argv` exposes it to the OS process table. On shared multi-user systems, any local user or background monitoring daemon running `ps aux` or inspecting `/proc/<PID>/cmdline` can read the plaintext encryption passphrase.
* **Resolution:**
  Pass the passphrase strictly via an environment variable:
  ```python
  env = os.environ.copy()
  if passphrase:
      env["KYKLOI_ENCRYPT_KEY"] = passphrase
  res = subprocess.run(cmd, cwd=str(ROOT_DIR), env=env)
  ```
  `build_site.py` already supports reading `KYKLOI_ENCRYPT_KEY` from `os.environ` natively.

---

### Current Defect & Resolution Matrix

| # | Issue | Impact Area | Likelihood | Complexity to Fix |
| :--- | :--- | :--- | :--- | :--- |
| **1** | Normalizer Collision Deadlock | Vault Normalizer | Moderate (on duplicate names) | **Low** (~8 lines in `engine.py`) |
| **2** | Media vs. Note Stem Collision | SQLite Ledger | High (e.g. `doc.md` & `doc.png`) | **Low** (Composite Unique index) |
| **3** | Secure Note Media 404 Gap | Static Output | High (if public media linked) | **Low** (~2 lines in `translate_links.lua`) |
| **4** | Inline Code Masking Breakage | Link Healer | Low (requires backtick in code) | **Low** (Regex update in `graph.py`) |
| **5** | Uppercase Extension Skipping | Pandoc Filter | Moderate (un-normalized markdown) | **Low** (Pattern update in Lua) |
| **6** | Passphrase in `ps aux` | Local Security | Moderate (multi-user systems) | **Low** (Pass via `env` in `launch.py`) |
