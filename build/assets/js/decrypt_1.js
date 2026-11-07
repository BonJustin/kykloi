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
   * Pandoc outputs: <span class="math inline">...</span> or <span class="math display">...</span>
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

      // Normalize and defensively strip wrapper delimiters if present
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
   * Derives PBKDF2/AES-GCM key material and decrypts the Base64 envelope.
   * @param {string} password - User-provided passphrase.
   * @param {string} rawText - Base64 encoded payload string.
   * @returns {Promise<string>} - Decrypted UTF-8 HTML string.
   */
  async function decryptEnvelope(password, rawText) {
    // 1. Cleanly parse JSON to extract unquoted Base64 string
    let base64Payload = rawText.trim();
    if (base64Payload.startsWith('"') && base64Payload.endsWith('"')) {
      try {
        base64Payload = JSON.parse(base64Payload);
      } catch (e) {
        console.warn("[Kykloi] JSON parse fallback used:", e);
      }
    }

    // 2. Decode Base64 string to Uint8Array
    const binaryString = atob(base64Payload);
    const bytes = Uint8Array.from(binaryString, (char) => char.charCodeAt(0));

    console.debug(`[Kykloi] Envelope received: ${bytes.length} bytes.`);

    if (bytes.length < 28) {
      throw new Error("Payload too short to contain Salt + IV headers.");
    }

    // Envelope schema: Salt (16B) | IV (12B) | Ciphertext + Tag (remaining bytes)
    const salt = bytes.slice(0, 16);
    const iv = bytes.slice(16, 28);
    const ciphertext = bytes.slice(28);

    // 3. Derive Key Material from Passphrase
    const encoder = new TextEncoder();
    const keyMaterial = await window.crypto.subtle.importKey(
      "raw",
      encoder.encode(password),
      { name: "PBKDF2" },
      false,
      ["deriveKey"]
    );

    // 4. Derive AES-GCM Key (matches Python PBKDF2 parameters: 600,000 iterations)
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

    // 5. Perform Decryption & Authentication
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

      // Mount decrypted markup and purge lock interface
      contentContainer.innerHTML = html;
      contentContainer.style.display = "block";
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
