document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("kykloi-decrypt-form");
  if (!form) return;

  const passwordInput = document.getElementById("kykloi-password");
  const errorMsg = document.getElementById("kykloi-decrypt-error");
  const lockContainer = document.getElementById("kykloi-lock-container");
  const contentContainer = document.getElementById("kykloi-decrypted-content");
  const payloadEl = document.getElementById("kykloi-encrypted-payload");

  if (!payloadEl) return;

  async function decryptEnvelope(password, base64Payload) {
    // 1. Decode Base64 to ArrayBuffer
    const binaryString = atob(base64Payload);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }

    // Envelope layout: Salt (16 bytes) | IV (12 bytes) | Ciphertext + GCM Tag (rest)
    if (bytes.length < 28) {
      throw new Error("Invalid payload format.");
    }

    const salt = bytes.slice(0, 16);
    const iv = bytes.slice(16, 28);
    const ciphertext = bytes.slice(28);

    // 2. Import raw password string into WebCrypto key material
    const encoder = new TextEncoder();
    const keyMaterial = await window.crypto.subtle.importKey(
      "raw",
      encoder.encode(password),
      { name: "PBKDF2" },
      false,
      ["deriveKey"]
    );

    // 3. Derive 256-bit AES-GCM Key via PBKDF2-HMAC-SHA256 (600,000 iterations)
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

    // 4. Decrypt payload (WebCrypto validates the 16-byte authentication tag automatically)
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
    const rawPayload = payloadEl.textContent.trim();

    try {
      const html = await decryptEnvelope(password, rawPayload);

      // Inject decrypted HTML body safely
      contentContainer.innerHTML = html;
      contentContainer.style.display = "block";
      lockContainer.remove();

      // Trigger KaTeX dynamic auto-rendering if present on the page
      if (typeof renderMathInElement === "function") {
        renderMathInElement(contentContainer);
      }
    } catch (err) {
      errorMsg.style.display = "block";
      passwordInput.value = "";
      passwordInput.focus();
    }
  });
});
