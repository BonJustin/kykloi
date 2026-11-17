---
title: "Kykloi - Introduction"
date_edtf: "2026-11-16"
keywords: ["kykloi", "documentation"]
---

# Introduction

***Kykloi** is a simple, portable, archival personal knowlege base and website generator.*

**Tasks**

* Test from USB on Windows.
* Default to user `cache` on POSIX systems, fallback to `tmp`.
* Opportunistic use system level AES-256-GCM, host Python `cryptography` package, with fallback to built-in pure Python.
* Installation routines for various use-cases.
    - USB flash drive
    - Github Actions/Pages dual repository.
    - Local developer environment.
* Test citation engine!
* Automate trimming of the log file at a reasonable size.
