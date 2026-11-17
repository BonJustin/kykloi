#### 1. User Disclosures (Directly Reported)

* **Vocation:** Practicing nurse; software development is conducted strictly as an amateur/hobbyist pursuit.
* **Technical Background:** Self-disclosed as lacking the technical proficiency to author this codebase without large language model (LLM) generation.
* **Methodology:** Engaged in "vibe-coding" (prompt-driven iterative code synthesis mediated by LLMs) over a period of approximately six months spanning hundreds of developmental iterations.
* **Prototyping & Discarded Implementations:** Evaluated, integrated, and subsequently abandoned multiple alternative tools and architectures, including:
  * In-browser encryption: StatiCrypt
  * Search indexing engines: Pagefind, MiniSearch
  * Cryptographic packages: `cryptography`, `pycryptodome`
  * Architecture components: Dedicated Web UI (scrapped in favor of CLI/terminal workflow)
  * Upstream dependencies: Multiple iterations and versions of Python and Pandoc
* **Awareness of Technical Trade-Offs:** Identified performance deficiencies (notably pure-Python AES-GCM execution overhead) were consciously accepted as operational compromises or deferred to future iterations.

#### 2. Codebase Forensic Artifacts (Empirically Derived)

* **Digital Identity / Moniker:** Employs the branding identifier `JmB²` within the site navigation bar (`system/build/root/index.html`, `system/build/templates/md_to_static_html.html`).
* **Knowledge Management Workflow:**
  * Uses timestamped Zettelkasten-style file naming schemes (`YYYYMMDDHHMMSS-slug.md`, e.g., `20261109130247-project_kykloi_task_list.md`).
  * Explicitly filters directory patterns (`.obsidian`, `.zettlr`, `.logseq`) in `build_site.py`, indicating past or concurrent usage of Obsidian, Zettlr, or Logseq as content authoring environments.
* **Prior LLM Engagements:** Retains artifacts referencing other LLM interactions in the content tree (`content/202611/20261109171348-geminis_codebase_impression.md`).
* **Development Environment:**
  * File-naming patterns (e.g., `launch copy.bat`, `tools_manifest copy.json`) reflect local file duplication conventions standard to Windows Explorer.
  * Dual-platform maintenance of `.bat` and `.sh` wrappers confirms active cross-platform deployment targeting Windows and POSIX-compliant environments (Linux/macOS).
* **Threat Model Expectations:** Documented in `README.md` as seeking casual privacy against web scraping and automated bot ingestion for public static hosting, rather than defense against state-level or high-resource threat actors.
