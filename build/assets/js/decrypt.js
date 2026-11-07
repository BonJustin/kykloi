document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("kykloi-decrypt-form");
  if (!form) return;

  const passwordInput = document.getElementById("kykloi-password");
  const errorMsg = document.getElementById("kykloi-decrypt-error");
  const lockContainer = document.getElementById("kykloi-lock-container");
  const contentContainer = document.getElementById("kykloi-decrypted-content");
  const payloadEl = document.getElementById("kykloi-encrypted-payload");

  if (!payloadEl) return;

  /**
   * Renders Pandoc-generated mathematical elements via KaTeX core.
   * @param {HTMLElement} container - The decrypted content container.
   */
  function renderDecryptedMath(container) {
    if (typeof katex === "undefined") {
      console.warn("[Kykloi] KaTeX engine not available in global scope.");
      return;
    }

    const mathElements = container.querySelectorAll(".math");
    mathElements.forEach((el) => {
      let tex = el.textContent.trim();

      if (tex.startsWith("\\(") && tex.endsWith("\\)")) {
        tex = tex.slice(2, -2).trim();
      } else if (tex.startsWith("\\[") && tex.endsWith("\\]")) {
        tex = tex.slice(2, -2).trim();
      } else if (tex.startsWith("$$") && tex.endsWith("$$")) {
        tex = tex.slice(2, -2).trim();
      } else if (tex.startsWith("$") && tex.endsWith("$")) {
        tex = tex.slice(1, -1).trim();
      }

      const isDisplay =
        el.classList.contains("display") ||
        el.classList.contains("math-display") ||
        el.tagName === "DIV";

      try {
        katex.render(tex, el, {
          displayMode: isDisplay,
          throwOnError: false,
        });
      } catch (kErr) {
        console.error("[Kykloi KaTeX Error]:", kErr);
      }
    });
  }

  /**
   * High-efficiency Base64 decoding into an ArrayBuffer.
   * Avoids iterator closure allocations that trigger GC pauses.
   * @param {string} b64 - Base64 encoded payload.
   * @returns {Uint8Array}
   */
  function base64ToUint8Array(b64) {
    const binaryString = atob(b64);
    const len = binaryString.length;
    // Single contiguous typed allocation
    const bytes = new Uint8Array(len);

    // Optimized sequential iteration without closure overhead
    for (let i = 0; i < len; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes;
  }

  /**
   * Derives PBKDF2/AES-GCM key material and decrypts the binary envelope.
   * @param {string} password - User-provided passphrase.
   * @param {string} rawText - Base64 encoded payload string.
   * @returns {Promise<string>} - Decrypted UTF-8 HTML string.
   */
  async function decryptEnvelope(password, rawText) {
    let base64Payload = rawText.trim();
    if (base64Payload.startsWith('"') && base64Payload.endsWith('"')) {
      try {
        base64Payload = JSON.parse(base64Payload);
      } catch (e) {
        console.warn("[Kykloi] JSON parse fallback used:", e);
      }
    }

    // MEMORY OPTIMIZATION: Decode using standard typed loop
    const bytes = base64ToUint8Array(base64Payload);

    console.debug(`[Kykloi] Envelope received: ${bytes.length} bytes.`);

    if (bytes.length < 28) {
      throw new Error("Payload too short to contain Salt + IV headers.");
    }

    // MEMORY OPTIMIZATION: Zero-copy slicing via .subarray()
    // .subarray() returns a window view into the existing memory buffer
    // rather than copying data into a newly allocated buffer via .slice()
    const salt = bytes.subarray(0, 16);
    const iv = bytes.subarray(16, 28);
    const ciphertext = bytes.subarray(28);

    // Derive PBKDF2 intermediate key
    const encoder = new TextEncoder();
    const keyMaterial = await window.crypto.subtle.importKey(
      "raw",
      encoder.encode(password),
      { name: "PBKDF2" },
      false,
      ["deriveKey"]
    );

    // Derive symmetric AES-GCM decryption key
    const key = await window.crypto.subtle.deriveKey(
      {
        name: "PBKDF2",
        salt: salt,
        iterations: 600000,
        hash: "SHA-256",
      },
      keyMaterial,
      { name: "AES-GCM", length: 256 },
      false,
      ["decrypt"]
    );

    // Hardware-accelerated AEAD decryption
    const decryptedBuffer = await window.crypto.subtle.decrypt(
      { name: "AES-GCM", iv: iv },
      key,
      ciphertext
    );

    return new TextDecoder().decode(decryptedBuffer);
  }

  // --- Form Submission Handler ---
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorMsg.style.display = "none";
    const password = passwordInput.value;
    const rawPayload = payloadEl.textContent;

    try {
      console.debug("[Kykloi] Attempting decryption...");
      const html = await decryptEnvelope(password, rawPayload);
      console.debug("[Kykloi] Decryption successful! Mounting document.");

      // Mount decrypted markup
      contentContainer.innerHTML = html;
      contentContainer.style.display = "block";

      // MEMORY OPTIMIZATION: Immediate memory reclamation
      // Clear large Base64 payload string from DOM and script memory
      payloadEl.textContent = "";
      lockContainer.remove();

      // Render math formulas
      renderDecryptedMath(contentContainer);
    } catch (err) {
      console.error("[Kykloi Decryption Error]:", err);
      errorMsg.style.display = "block";
      passwordInput.value = "";
      passwordInput.focus();
    }
  });
});
