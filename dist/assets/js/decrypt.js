document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("kykloi-decrypt-form");
  if (!form) return;

  const passwordInput = document.getElementById("kykloi-password");
  const errorMsg = document.getElementById("kykloi-decrypt-error");
  const lockContainer = document.getElementById("kykloi-lock-container");
  const contentContainer = document.getElementById("kykloi-decrypted-content");
  const payloadEl = document.getElementById("kykloi-encrypted-payload");

  if (!payloadEl) return;

  async function decryptEnvelope(password, rawText) {
    // 1. Cleanly parse JSON to extract unquoted Base64 string
    let base64Payload = rawText.trim();
    if (base64Payload.startsWith('"') && base64Payload.endsWith('"')) {
      try {
        base64Payload = JSON.parse(base64Payload);
      } catch (e) {
        console.warn("JSON parse fallback used:", e);
      }
    }

    // 2. Decode Base64 to ArrayBuffer
    const binaryString = atob(base64Payload);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }

    console.debug(`[Kykloi] Decrypting payload: Total envelope size = ${bytes.length} bytes`);

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

    // 4. Derive AES-GCM Key (matches Python PBKDF2 parameters)
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

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorMsg.style.display = "none";
    const password = passwordInput.value;
    const rawPayload = payloadEl.textContent;

    try {
      console.debug("[Kykloi] Attempting decryption...");
      const html = await decryptEnvelope(password, rawPayload);
      console.debug("[Kykloi] Decryption successful! Mounting document.");

      contentContainer.innerHTML = html;
      contentContainer.style.display = "block";
      lockContainer.remove();

      if (typeof renderMathInElement === "function") {
        renderMathInElement(contentContainer);
      }
    } catch (err) {
      console.error("[Kykloi Decryption Error]:", err);
      errorMsg.style.display = "block";
      passwordInput.value = "";
      passwordInput.focus();
    }
  });
});
