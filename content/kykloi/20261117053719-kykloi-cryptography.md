---
title: "Kykloi - Cryptographic Architecture & Acceleration"
date_edtf: "2026-11-17"
keywords: ["kykloi", "documentation", "cryptography", "encryption", "aes-gcm", "performance"]
---

# Cryptographic Architecture & Acceleration

Project Kykloi implements client-side authenticated symmetric encryption to secure confidential Markdown notes and embedded binary assets (images, PDFs, documents) located within any `/secure/` directory.

---

## 1. Cryptographic Primitives & Specifications

Kykloi adheres to modern cryptographic standards designed to execute in zero-trust static hosting environments:

* **Cipher:** **AES-256-GCM** (Galois/Counter Mode, 256-bit key length, 128-bit authentication tag, 96-bit unique IV).
* **Key Derivation Function:** **PBKDF2-HMAC-SHA256** using 100,000 iterations and a cryptographically random 128-bit salt generated per artifact.
* **Client-Side Decryption:** Executed in the browser via the W3C standard **WebCrypto API** (`SubtleCrypto`), ensuring plaintexts never traverse the network in decrypted form.
* **Payload Envelope Format:** Encrypted outputs are serialized as binary or Base64 envelopes comprising:
  $$\text{Payload} = [\text{Salt (16 bytes)}] \parallel [\text{IV (12 bytes)}] \parallel [\text{Ciphertext}] \parallel [\text{Auth Tag (16 bytes)}]$$

---

## 2. The Acceleration Problem

Encrypting small Markdown text files produces minimal execution overhead. However, encrypting multi-megabyte media attachments (e.g., high-resolution photography, diagrams) in interpreted, pure-Python code requires billions of Galois Field arithmetic operations ($\text{GF}(2^{128})$). 

A pure-Python AES-GCM engine processes data at approximately **$1\text{ MB/s}$ to $2\text{ MB/s}$ per core**. Under this baseline rate, a vault with $100\text{ MB}$ of secure media requires over a minute to compile.

In contrast, compiled native implementations leveraging dedicated CPU instruction sets (**Intel/AMD AES-NI** or **ARMv8 NEON Crypto**) process data at **$1,500\text{ MB/s}$ to $3,000\text{ MB/s}$**, completing identical builds in fractions of a second.

---

## 3. Tiered Engine Resolution Hierarchy

To resolve this bottleneck without violating Kykloi's zero-dependency archival guarantee, `build_site.py` dynamically resolves the fastest available engine using a prioritized three-tier fallback pipeline. Every candidate engine must validate against the official **NIST SP 800-38D Known Answer Test (KAT)** before activation.

### Tier 1: Native OS C-ABI (Automatic & Out-of-the-Box)
Kykloi binds directly to shared C libraries already present in the host operating system using Python's standard `ctypes` foreign function interface. This tier requires **no Python packages, no host Python installation, and no administrative configuration**:
* **Windows (All versions $\ge$ Vista):** Binds to Windows Cryptography Next Generation (`bcrypt.dll`). Executes hardware AES-NI instructions natively.
* **Linux (Debian, Ubuntu, Fedora, Arch, Alpine):** Binds to standard system OpenSSL (`libcrypto.so.3` or `libcrypto.so.1.1`).
* **macOS:** Binds to resident OpenSSL dynamic libraries or the runtime's internal `_ssl` object.

### Tier 2: Host Python Packages (Optional Auxiliary)
If running inside a stripped container or specialized chroot where native OS C-libraries are unmapped, Kykloi inspects the Python interpreter for pre-compiled cryptographic wheels:
* `cryptography`
* `pycryptodome`

### Tier 3: Pure-Python Engine (Archival Baseline)
If all external and OS-level acceleration primitives are unavailable, Kykloi falls back to its built-in pure-Python AES-256-GCM implementation. The build process remains operational and deterministic, with zero external dependencies.

---

## 4. Diagnostics & Environment Verification

### Inspecting Engine Status

To inspect which cryptographic accelerator is currently mapped to your Kykloi environment:

```bash
# Windows
launch.bat --crypto-info

# POSIX (Linux / macOS)
./launch.sh --crypto-info
```

Alternatively, launch the interactive Control Plane and select **Option [5] (Cryptographic Acceleration Diagnostics)**.

The diagnostic utility reports the active engine:
* `Windows CNG (bcrypt.dll / AES-NI)` $\rightarrow$ Fully optimized.
* `System OpenSSL EVP (libcrypto / AES-NI / NEON)` $\rightarrow$ Fully optimized.
* `Python cryptography (OpenSSL C-Extension)` $\rightarrow$ Fully optimized.
* `Pure-Python AES-GCM (Zero-Dependency Fallback)` $\rightarrow$ Baseline fallback mode active.

---

## 5. Activating Acceleration on Fallback Systems

If your system diagnostic indicates that the **Pure-Python Baseline** is active, you can achieve acceleration by providing a host Python environment with compiled cryptographic primitives:

1. **Verify Host Python:** Ensure Python 3.10 or newer is installed on your host system:
   ```bash
   python --version   # Windows
   python3 --version  # Linux / macOS
   ```
2. **Install Compiled Primitives:**
   ```bash
   pip install cryptography
   ```
3. **Execute Launcher:**
   Run `launch.bat` or `./launch.sh`. The launcher will prioritize your host Python environment, detect the compiled C-extension, and transition from Baseline Fallback to Hardware Accelerated mode.
```
