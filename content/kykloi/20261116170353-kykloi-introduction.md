---
title: "Kykloi - Introduction"
date_edtf: "2026-11-16"
keywords: ["kykloi", "documentation", "overview", "architecture"]
---

# Introduction

**Kykloi** is a portable, archival personal knowledge management tool. Plain text archival Markdown is converted to portable static web pages with a durable and low-dependency lifespan.

The system is designed with a long-term preservation philosophy: content remains readable in open standard formats, and site generation requires no external cloud services, database servers, or mandatory software installations.

---

## 1. Key Capabilities

* **Archival Portability:** Kykloi carries its own self-extracting runtime environments for Python and Pandoc. It can build and run on modern Windows, Linux, and macOS systems without requiring you to install developer tooling or system dependencies.
* **Selective In-Browser Encryption:** Notes and media placed in any `/secure/` directory are automatically encrypted using authenticated **AES-256-GCM**. Plaintext content is decrypted exclusively inside the browser using your passphrase; unencrypted data never leaves your device.
* **Offline Full-Text Search:** The generated site includes a browser-based search engine powered by SQLite (compiled to WebAssembly). Readers can instantly query document titles, dates, and keywords without a backend server.
* **Academic Reference Support:** Centralized bibliography files (`.bib`) are automatically parsed and formatted into citations and reference lists during compilation.
* **Incremental Builds:** Kykloi tracks file modifications with cryptographic hashes. Only modified documents and assets are recompiled, keeping compilation times nearly instantaneous.

---

## 2. Core Workflow

1. **Write Notes:** Create standard Markdown files within the `content/` directory. Notes can use frontmatter headers for metadata:
   ```yaml
   ---
   title: "My Note Title"
   date_edtf: "2026-11-16"
   keywords: ["research", "notes"]
   ---
   ```
2. **Secure Confidential Notes:** Any Markdown file or image placed inside a `/secure/` folder (for example, `content/secure/private_note.md`) is automatically flagged for client-side encryption.
3. **Launch the Control Hub:** Run the platform launcher from the root folder:
   * **Windows:** Double-click or execute `launch.bat`
   * **Linux / macOS:** Execute `./launch.sh`
4. **Build and Preview:** Use the interactive terminal menu to compile the static site (`Option [1]`) and open the live vault in your default web browser (`Option [4]`).

---

## 3. Privacy & Threat Model

Kykloi's secure folder design provides **casual privacy** for publicly hosted static sites:

* **What is Protected:** The body content and embedded media of secure notes are fully encrypted. Automated web crawlers, search engine indexers, and unauthorized visitors cannot read this content without the passphrase.
* **What is Discoverable:** To keep the search interface functional, note metadata (titles, tags, and dates) is included in the client-side search index.
* **Intended Use:** This architecture is intended to guard against accidental exposure, casual browsing, and automated scraping. Documents requiring high-assurance defense against well-resourced adversaries should never be deployed to public static hosts.

---

## 4. Documentation Index

Consult the following technical guides for in-depth information on specific subsystems:

* **[Cryptographic Architecture & Acceleration](20261117053719-kykloi-cryptography.md):** Details on encryption standards, hardware acceleration engines (AES-NI and NEON), performance diagnostics, and fallback mechanisms.
