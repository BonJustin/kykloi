---
title: Confidential Vault & Key Derivation Log
date_edtf: 2026-12-01T08:30:00
keywords:
  - encryption
  - confidential
  - webcrypto
  - pbkdf2
  - secure-notes
description: Encrypted document testing confidential formatting, mathematical proofs, and callouts.
---

# Confidential Vault & Key Derivation Log

This document is encrypted using pure-Python AES-256-GCM during compilation and decrypted in the browser via `decrypt.js`.

> [!WARNING] Classified Record
> The contents of this note should only be visible after supplying the correct archive passphrase to the prompt.

## 1. Cryptographic Key Derivation Proof

The archive key derivation process follows the PBKDF2 standard:

$$
K = \text{PBKDF2}(\text{HMAC-SHA256}, \text{Passphrase}, \text{Salt}, 100000, 32)
$$

The initialization vector $IV$ is 96 bits (12 bytes) drawn directly from system entropy (`os.urandom(12)`).

Authentication tag calculation:

$$
T = \text{GHASH}_H(A \mathbin{\Vert} C \mathbin{\Vert} [|A|]_{64} \mathbin{\Vert} [|C|]_{64}) \oplus \text{AES}_K(J_0)
$$

## 2. Cross-Boundary Navigation

* Link to public reference document: [Public Pandoc Markdown Notes](../pandoc_markdown.md)
* Link to sibling secure media gallery: [[20261201084500-secure_media_gallery|Encrypted Media Gallery]]
* Link back to Zettlr feature test: [[02_zettlr_features]]

## 3. Task Checklist for Security Verification

- [x] WebCrypto subtle crypto initialized
- [x] Memory decryption matches SHA-256 digest
- [ ] Verify passphrase prompt rejection on invalid entry
