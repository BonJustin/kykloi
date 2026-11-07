document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("kykloi-decrypt-form");
  if (!form) return;

  const passwordInput = document.getElementById("kykloi-password");
  const errorMsg = document.getElementById("kykloi-decrypt-error");
  const lockContainer = document.getElementById("kykloi-lock-container");
  const contentContainer = document.getElementById("kykloi-decrypted-content");
  const payloadEl = document.getElementById("kykloi-encrypted-payload");

  if (!payloadEl) return;

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

  function base64ToUint8Array(b64) {
    const binaryString = atob(b64);
    const len = binaryString.length;
    // Single contiguous typed allocation
    const bytes = new Uint8Array(len);

    for (let i = 0; i < len; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes;
  }

  async function decryptEnvelope(password, rawText) {
    let base64Payload = rawText.trim();
    if (base64Payload.startsWith('"') && base64Payload.endsWith('"')) {
      try {
        base64Payload = JSON.parse(base64Payload);
      } catch (e) {
        console.warn("[Kykloi] JSON parse fallback used:", e);
      }
    }

    const bytes = base64ToUint8Array(base64Payload);

    console.debug(`[Kykloi] Envelope received: ${bytes.length} bytes.`);

    if (bytes.length < 28) {
      throw new Error("Payload too short to contain Salt + IV headers.");
    }

    const salt = bytes.subarray(0, 16);
    const iv = bytes.subarray(16, 28);
    const ciphertext = bytes.subarray(28);

    const encoder = new TextEncoder();
    const keyMaterial = await window.crypto.subtle.importKey(
      "raw",
      encoder.encode(password),
      { name: "PBKDF2" },
      false,
      ["deriveKey"]
    );

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

      payloadEl.textContent = "";
      lockContainer.remove();

      renderDecryptedMath(contentContainer);
    } catch (err) {
      console.error("[Kykloi Decryption Error]:", err);
      errorMsg.style.display = "block";
      passwordInput.value = "";
      passwordInput.focus();
    }
  });
});
