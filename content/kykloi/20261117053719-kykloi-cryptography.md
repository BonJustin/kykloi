---
title: "Kykloi - Cryptographic Architecture & Acceleration"
date_edtf: "2026-11-17"
keywords: ["kykloi", "documentation", "cryptography", "encryption", "aes-gcm", "performance"]
---

# Cryptographic Architecture & Acceleration

Project Kykloi uses client-side encryption to protect private Markdown notes and attachments (such as images and PDFs) stored in any `/secure/` folder.

Files are encrypted before they leave your computer. When viewed on the web, decryption happens entirely inside your browser, meaning unencrypted content is never sent across the network.

---

## 1. Security Specifications

Kykloi relies on industry-standard encryption practices:

* **Encryption Standard:** **AES-256-GCM**. This provides both confidentiality (keeping data secret) and integrity verification (detecting any tampering).
* **Password Protection:** **PBKDF2-HMAC-SHA256** with 100,000 iterations and a unique, random salt for each file. This slows down brute-force password guessing attacks.
* **In-Browser Decryption:** Handled by the browser's built-in **WebCrypto API**. Decryption occurs locally on your device using your passphrase.
* **Encrypted File Structure:** Each encrypted item bundles four components together:
  * **Salt:** Used to derive the key from your passphrase.
  * **Initialization Vector (IV):** Ensures identical files encrypt differently every time.
  * **Ciphertext:** The encrypted content.
  * **Authentication Tag:** Verifies the content has not been modified.

---

## 2. Why Hardware Acceleration Matters

Encrypting text notes takes milliseconds. However, encrypting large media files (such as high-resolution images or documents) requires substantial processing power:

* **Pure-Python (No Acceleration):** Processes data at roughly **1 to 2 MB per second**. Encrypting a site with 100 MB of attachments can take over a minute.
* **Hardware Acceleration:** Uses dedicated instructions built into modern processors (Intel/AMD AES-NI or Apple/ARM NEON) to process data at **1,500 to 3,000 MB per second**. The same 100 MB of data compiles in a fraction of a second.

---

## 3. How Kykloi Selects an Encryption Engine

When you build your site, Kykloi checks your system and automatically selects the fastest available encryption engine using a three-tier system:

### Tier 1: System-Level Hardware Acceleration (Default & Recommended)
Kykloi accesses the secure libraries already installed on your operating system. This provides hardware-accelerated speed with **zero extra installation required**:
* **Windows:** Uses the built-in Windows Cryptography API (`bcrypt.dll`).
* **Linux:** Uses the system OpenSSL library (`libcrypto.so`).
* **macOS:** Uses resident system cryptographic libraries.

### Tier 2: Python Cryptography Packages (Optional)
If your operating system libraries cannot be reached (for example, inside certain restricted containers), Kykloi looks for installed Python packages such as:
* `cryptography`
* `pycryptodome`

### Tier 3: Pure-Python Engine (Built-in Fallback)
If no hardware acceleration or external libraries are available, Kykloi falls back to its internal Python engine. The build will still succeed and produce valid encrypted files, but compiling large attachments will take longer.

---

## 4. Checking Your Acceleration Status

You can check which engine your system is using via the command line:

```bash
# Windows
launch.bat --crypto-info

# Linux / macOS
./launch.sh --crypto-info
```

Alternatively, open the interactive launcher menu and select **Option [5] (Cryptographic Acceleration Diagnostics)**.

### Interpreting the Results
* **`Windows CNG` or `System OpenSSL`:** Hardware acceleration is active. No action needed.
* **`Python cryptography`:** Accelerated via an installed Python package. No action needed.
* **`Pure-Python AES-GCM`:** Running in fallback mode. Site builds will be slower if you have large files in `/secure/`.

---

## 5. Enabling Acceleration on Fallback Systems

If diagnostics report that your system is using the **Pure-Python Fallback**, you can enable hardware speeds by installing the standard Python cryptography library:

1. **Verify Python Installation:** Ensure Python 3.10 or newer is installed:
   ```bash
   python --version   # Windows
   python3 --version  # Linux / macOS
   ```
2. **Install the Acceleration Library:**
   ```bash
   pip install cryptography
   ```
3. **Re-run the Launcher:**
   Execute `launch.bat` or `./launch.sh`. Kykloi will automatically detect the package and switch to accelerated mode.
