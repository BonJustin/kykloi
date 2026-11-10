---
id: 20261201091500
title: Zettlr Conventions & Academic Notation
date_edtf: 2026-12-01T09:15:00
date: 2026-12-01
keywords: zettlr, zettelkasten, footnotes, academic, cross-referencing
author:
  - J. M. B.
description: Validates Zettlr unique IDs, cross-linking, task lists, and academic footnoting.
---

# Zettlr Conventions & Academic Notation

This note verifies Zettlr-specific conventions, including root frontmatter ID cross-referencing and academic notations.

## 1. Zettelkasten Unique ID Cross-Referencing

Zettlr frequently uses 14-digit IDs in the frontmatter (`id: 20261201091500`) or within the filename:

* Link referencing another note by its 14-digit ID prefix: [20261109130247 Project Kykloi Task List](../202611/20261109130247-project_kykloi_task_list.md)
* Link referencing another note by ID with custom label: [Task List Index](../202611/20261109130247-project_kykloi_task_list.md)
* Link referencing a note located in a sibling subdirectory: [[01_obsidian_features]]

## 2. Academic Footnotes

Archival documents require reliable citation and footnote rendering.[^archival-standard]

Inline footnotes allow quick commentary without disrupting reading cadence.[^quick-note]

Multi-paragraph footnotes should also preserve block indentation.[^complex-footnote]

[^archival-standard]: Archival standards prioritize vendor neutrality, plain text, and standards-compliant CommonMark over proprietary databases.
[^quick-note]: A concise, single-line footnote reference.
[^complex-footnote]: This is the first paragraph of a multi-block footnote.

    Subsequent paragraphs must align properly beneath the initial definition to be captured by Pandoc's parser.

## 3. Task List Form Elements

Pandoc compiles task lists into semantic checkboxes:

- [x] Initial design specifications established
- [x] Pure-Python AES-256-GCM NIST KAT test passed
- [ ] Implement client-side tag filtering in SQLite FTS5 worker
- [ ] Audit WebCrypto streaming performance on multi-megabyte media

## 4. Definition Lists

Term 1: Archival Integrity
: The quality of digital assets remaining renderable and understandable over decades without software degradation.

Term 2: Permacomputing
: A design philosophy prioritizing frugality, repairability, longevity, and low-power hardware execution.
