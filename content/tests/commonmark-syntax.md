---
title: Comprehensive CommonMark Structural Syntax
date_edtf: 2026-12-01
keywords: commonmark, tables, codeblocks, protected-zones, escaping
description: Stress-tests code block shielding, nested lists, and Markdown tables.
---

# Comprehensive CommonMark Structural Syntax

This note stresses standard CommonMark block handling, table rendering, and regex protected-zone validation.

## 1. Protected Zone Verification (Crucial)

The link migration script (`migrate_wikilinks.py`) must **never** modify wikilink syntax when it is contained within code fences, inline code spans, or raw HTML blocks:

```markdown
# This block must remain untouched by migrate_wikilinks.py:
[[unmigrated_reference_inside_code_fence]]
![[unmigrated_image_inside_code_fence.png|300]]
$x = \text{math inside code}$
```

Inline code check: `[[unmigrated_inline_code_span]]` and `$\alpha + \beta$` must remain raw code.

Tilde-fenced code check:
~~~python
def example():
    # [[unmigrated_in_tilde_block]]
    return "kykloi"
~~~

## 2. Tables

### Simple Pipe Table

| Specification | Implementation | Archival Status |
| :--- | :--- | :--- |
| Markup Language | CommonMark | ISO/IEC Target |
| Cryptography | AES-256-GCM | NIST Standard |
| Search Engine | SQLite FTS5 | Public Domain |

### Complex Formatted Table

| ID | Module | Status | Notes / Links |
| :---: | :--- | :---: | :--- |
| 101 | Migration Engine | Verified | Handled by [[01_obsidian_features\|Obsidian Suite]] |
| 102 | Search Driver | Active | Queries `search.db` via WASM |
| 103 | Decryption Layer | Stable | Relies on W3C WebCrypto API |

## 3. Deeply Nested Lists

1. Level 1 (Ordered Item A)
   * Level 2 (Unordered sub-bullet)
     * Level 3 (Unordered sub-bullet)
       1. Level 4 (Ordered leaf node)
       2. Level 4 (Ordered leaf node)
2. Level 1 (Ordered Item B)
   * Level 2 (Unordered sub-bullet)
     * Level 3 (Nested block with paragraph)

       This paragraph belongs to the third nesting tier.
