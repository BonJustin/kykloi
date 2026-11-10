---
title: Obsidian Feature & Callout Verification
date_edtf: 2026-12-01
keywords:
  - obsidian
  - callouts
  - wikilinks
  - admonitions
  - highlights
description: Test document for Obsidian-style Markdown conventions and link migration.
---

# Obsidian Feature & Callout Verification

This document tests features commonly used in Obsidian vaults.

## 1. Wikilink and Transclusion Syntax

Before running the migration pipeline, verify that the following wikilinks resolve properly:

* Direct wikilink to root document: [Pandoc Markdown](../pandoc_markdown.md)
* Wikilink with explicit alias: [Pandoc Markdown Specification Reference](../pandoc_markdown.md)
* Wikilink to dated file by stem: [20261109130247 Project Kykloi Task List](../202611/20261109130247-project_kykloi_task_list.md)
* Wikilink with section anchor: [Mathematics Section](../pandoc_markdown.md#math)
* Wikilink with section anchor and custom alias: [Tables Reference](../pandoc_markdown.md#tables)
* Isolated internal anchor link: [Jump to Callout Admonitions below](#callout-variants)

## 2. Image Embeds and Dimension Stripping

Obsidian allows virtual image sizing tags (`|300` or `|600x400`) that violate CommonMark. Kykloi should strip the virtual sizing parameters while preserving the link and descriptive alt text:

* Unadorned image embed:
  ![test_artemis_2.jpg](../secure/media/test_artemis_2.jpg)

* Image embed with width specification:
  ![test_artemis_2.jpg](../secure/media/test_artemis_2.jpg)

* Image embed with 2D dimensions:
  ![test_artemis_2.jpg](../secure/media/test_artemis_2.jpg)

* Image embed with descriptive caption and dimensions:
  ![Artemis Launch Vehicle on Pad](../secure/media/test_artemis_2.jpg)

## 3. Callout Variants

The Lua filter converts standard `> [!TYPE]` blockquotes into semantic `<aside>` tags without injecting class wrappers.

> [!NOTE] Default Note Admonition
> This is a default note callout. It provides contextual information that supplements the main body text.

> [!WARNING] Critical Integrity Alert
> Passphrases used for `/secure/` documents are never stored on the server. Loss of passphrase results in permanent data loss.

> [!TIP] Keyboard Efficiency
> Pressing `/` or `Ctrl+K` on the index page immediately activates and focuses the SQLite search input.

> [!IMPORTANT]
> A callout without an explicit title should automatically format its type into title case (e.g., **Important**).

## 4. Markdown Highlights and Typography

* Text highlighting extension: ==Critical passage requiring visual emphasis==.
* Combined formatting: ==**Bold and highlighted concept**==.
* Small caps via semantic classes: [Project Kykloi Archive]{.smallcaps}.
