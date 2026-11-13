### 1. Locked Target Directory Topology

We will execute against the following frozen target structure (separating user content from internal system plumbing):

```text
kykloi/
│
├── content/                    <-- User space (Markdown notes & user media)
│   ├── index.md (or intro)
│   └── secure/
│
├── Start_Windows.vbs           <-- User entry point (silent execution)
├── Start_Mac.command           <-- User entry point (Finder double-click)
├── Start_Linux.sh              <-- User entry point (POSIX shell)
│
└── system/                    <-- Isolated appliance plumbing
    ├── admin/                  <-- Control hub (admin.html, app.js, styling)
    ├── build/                  <-- Compiler engine (build_site.py, templates, Lua filters)
    ├── dist/                   <-- Static build target (ephemeral output & search.db)
    ├── launch.py               <-- IPC orchestrator & admin server
    ├── serve.py                <-- Archival RFC 7233 HTTP server
    └── tools/                  <-- Hermetic binaries
        ├── python/             <-- Standalone Python runtimes (Win, Mac, Linux)
        └── pandoc/             <-- Standalone Pandoc executables (Win, Mac, Linux)
```

---

### 2. File Modification & Path Resolution Inventory

In the next session, edits will be applied systematically across four functional layers:

1.  **Orchestrator Pathing (`system/launch.py`):**
    *   Update `ROOT_DIR` to resolve relative to `kykloi` (one level up from `system/`).
    *   Re-map `ADMIN_DIR`, `BUILD_SCRIPT`, and `SERVE_SCRIPT` to their new locations inside `system/`.
    *   Ensure child process spawning (`subprocess.Popen`) sets working directories to `kykloi`.

2.  **Compiler Pathing (`system/build/build_site.py`):**
    *   Update `PROJECT_ROOT` to point to `kykloi`.
    *   Re-link source directory `SRC` to `kykloi/content/`.
    *   Re-link output directory `DST` to `kykloi/system/dist/`.
    *   Update relative dependencies: `DEFAULTS_YAML`, `DEFAULT_TEMPLATE`, `LUA_FILTER`, `MANIFEST_FILE`, and `SEARCH_DB_FILE`.
    *   Point `resolve_pandoc_binary()` to search `system/tools/pandoc/` before host `$PATH`.

3.  **Static Daemon Pathing (`system/serve.py`):**
    *   Update `DIST_DIR` to bind strictly to `system/dist/`.
    *   Verify jailbreak traversal guards against paths leaving `system/dist/`.

4.  **Client-Side UI & IPC Paths (`admin/app.js` & templates):**
    *   Verify the `/api/build` and `/api/view` fetch bridges operate across the redirected directory structure.
    *   Ensure the static site template (`md_to_static_html.html`) calculates relative root paths correctly when serving from `system/dist/`.

---

### 3. Verification & Testing Sequence

We will execute the following step-by-step verification pipeline to confirm zero regressions:

1.  **Path Resolution Dry Run:** Run `system/build/build_site.py --dry-run` to verify that all config files, filters, templates, and content trees resolve without `FileNotFoundError`.
2.  **Cryptographic Integrity Check:** Execute NIST KAT self-tests in isolation under the new path layout.
3.  **Live Site Build:** Execute a clean compilation to `system/dist/`, checking that:
    *   Relative asset links (`css`, `js`, `fonts`, `katex`) remain intact.
    *   Encrypted notes and `.enc` media compile to the correct target paths.
    *   `search.db` (FTS5 SQLite) populates and vacuum-seals inside `system/dist/`.
4.  **Daemon Smoke Tests:** Execute non-blocking socket bind and translation tests for `serve.py` and `launch.py`.

***

To begin with, **do not worry about platform launcher scripts**. Only consider the architectural changes and script edits needed to maintain the current function. Later refactoring and development can resolve the future issues.
