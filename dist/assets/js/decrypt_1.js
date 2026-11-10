document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("kykloi-decrypt-form");
  if (!form) return;

  const passwordInput = document.getElementById("kykloi-password");
  const submitButton = form.querySelector('button[type="submit"]');
  const errorMsg = document.getElementById("kykloi-decrypt-error");
  const lockContainer = document.getElementById("kykloi-lock-container");
  const contentContainer = document.getElementById("kykloi-decrypted-content");
  const payloadEl = document.getElementById("kykloi-encrypted-payload");

  if (!payloadEl) return;

  if (
    typeof window.crypto === "undefined" ||
    typeof window.crypto.subtle === "undefined"
  ) {
    console.error(
      "[Kykloi] WebCrypto API is unavailable in this browsing context."
    );
    if (errorMsg) {
      errorMsg.textContent =
        "Decryption unavailable: WebCrypto is disabled by your browser in this context.";
      errorMsg.style.display = "block";
    }
    if (passwordInput) passwordInput.disabled = true;
    if (submitButton) submitButton.disabled = true;
    return;
  }

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
    const bytes = new Uint8Array(len);

    for (let i = 0; i < len; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes;
  }

  async function deriveAesKey(password, salt) {
    const encoder = new TextEncoder();
    const keyMaterial = await window.crypto.subtle.importKey(
      "raw",
      encoder.encode(password),
      { name: "PBKDF2" },
      false,
      ["deriveKey"]
    );

    return await window.crypto.subtle.deriveKey(
      {
        name: "PBKDF2",
        salt: salt,
        iterations: 100000,
        hash: "SHA-256",
      },
      keyMaterial,
      { name: "AES-GCM", length: 256 },
      false,
      ["decrypt"]
    );
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
    if (bytes.length < 28) {
      throw new Error("Payload too short to contain Salt + IV headers.");
    }

    const salt = bytes.subarray(0, 16);
    const iv = bytes.subarray(16, 28);
    const ciphertext = bytes.subarray(28);

    const key = await deriveAesKey(password, salt);

    const decryptedBuffer = await window.crypto.subtle.decrypt(
      { name: "AES-GCM", iv: iv },
      key,
      ciphertext
    );

    return new TextDecoder().decode(decryptedBuffer);
  }

  function getMimeTypeFromUrl(url) {
    const cleanUrl = url.split(/[?#]/)[0].replace(/\.enc$/i, "");
    const ext = cleanUrl.split(".").pop().toLowerCase();
    const mimeMap = {
      jpg: "image/jpeg",
      jpeg: "image/jpeg",
      png: "image/png",
      gif: "image/gif",
      webp: "image/webp",
      svg: "image/svg+xml",
      bmp: "image/bmp",
      ico: "image/x-icon",
    };
    return mimeMap[ext] || "application/octet-stream";
  }

  async function decryptBinaryBlob(password, arrayBuffer) {
    const bytes = new Uint8Array(arrayBuffer);
    if (bytes.length < 28) {
      throw new Error("Encrypted blob too short.");
    }

    const salt = bytes.subarray(0, 16);
    const iv = bytes.subarray(16, 28);
    const ciphertext = bytes.subarray(28);

    const key = await deriveAesKey(password, salt);

    return await window.crypto.subtle.decrypt(
      { name: "AES-GCM", iv: iv },
      key,
      ciphertext
    );
  }

  async function hydrateEncryptedImages(container, password) {
    const encryptedImgs = container.querySelectorAll(
      'img[data-encrypted-media="true"], img[src$=".enc"]'
    );

    if (encryptedImgs.length === 0) return;

    for (const img of encryptedImgs) {
      const srcUrl = img.getAttribute("src");
      if (!srcUrl) continue;

      try {
        const response = await fetch(srcUrl);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status} fetching ${srcUrl}`);
        }

        const buffer = await response.arrayBuffer();
        const decryptedBuffer = await decryptBinaryBlob(password, buffer);

        const mimeType = getMimeTypeFromUrl(srcUrl);
        const blob = new Blob([decryptedBuffer], { type: mimeType });
        const blobUrl = URL.createObjectURL(blob);

        img.src = blobUrl;
        img.removeAttribute("data-encrypted-media");
      } catch (mediaErr) {
        console.error(`[Kykloi] Failed to decrypt blob (${srcUrl}):`, mediaErr);
        img.alt = `[Decryption error: ${img.alt || "image"}]`;
      }
    }
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    if (errorMsg) {
      errorMsg.style.display = "none";
      errorMsg.textContent =
        "Decryption failed: Incorrect passphrase or corrupted payload.";
    }

    const password = passwordInput.value;
    const rawPayload = payloadEl.textContent;

    const originalButtonText = submitButton ? submitButton.textContent : "";
    if (submitButton) {
      submitButton.disabled = true;
      submitButton.textContent = "Decrypting...";
    }
    if (passwordInput) {
      passwordInput.disabled = true;
    }

    try {
      const html = await decryptEnvelope(password, rawPayload);

      contentContainer.innerHTML = html;
      contentContainer.style.display = "block";

      payloadEl.textContent = "";
      if (lockContainer) {
        lockContainer.remove();
      }

      renderDecryptedMath(contentContainer);

      // Decrypt and hydrate media blobs
      hydrateEncryptedImages(contentContainer, password);
    } catch (err) {
      console.error("[Kykloi Decryption Error]:", err);

      if (errorMsg) {
        errorMsg.style.display = "block";
      }
      if (passwordInput) {
        passwordInput.disabled = false;
        passwordInput.value = "";
        passwordInput.focus();
      }
      if (submitButton) {
        submitButton.disabled = false;
        submitButton.textContent = originalButtonText;
      }
    }
  });
});
