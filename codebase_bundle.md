# Project Directory Tree

```text
kykloi/
├── .git/ (contents excluded)
├── .github/ (contents excluded)
├── .venv/ (contents excluded)
├── content/
│   └── kykloi/
│       ├── media/
│       │   └── test_artemis_2.jpg
│       ├── secure/
│       │   └── media/
│       │       └── test_artemis_2-1.jpg
│       ├── 20261116170353-kykloi-introduction.md
│       ├── 20261117053719-kykloi-cryptography.md
│       ├── 20261117062543-kykloi-to-do-list.md
│       └── 20261117181402-kykloi-highlights.md
├── dist/ (contents excluded)
├── system/
│   ├── __pycache__/ (contents excluded)
│   ├── build/
│   │   ├── __pycache__/ (contents excluded)
│   │   ├── assets/
│   │   │   ├── css/
│   │   │   │   ├── pico.css
│   │   │   │   └── style.css
│   │   │   ├── fonts/ (contents excluded)
│   │   │   ├── js/
│   │   │   │   ├── decrypt.js
│   │   │   │   ├── search_worker.js
│   │   │   │   ├── sqlite3.js
│   │   │   │   ├── sqlite3.wasm
│   │   │   │   └── wasm-search.js
│   │   │   └── katex/ (contents excluded)
│   │   ├── root/
│   │   │   ├── apple-touch-icon.png
│   │   │   ├── favicon-96x96.png
│   │   │   ├── favicon.ico
│   │   │   ├── favicon.svg
│   │   │   ├── index.html
│   │   │   ├── site.webmanifest
│   │   │   ├── web-app-manifest-192x192.png
│   │   │   └── web-app-manifest-512x512.png
│   │   ├── templates/
│   │   │   └── pandoc-template.html
│   │   ├── .build_manifest.json
│   │   ├── build.py
│   │   ├── html-config.yaml
│   │   └── translate-links.lua
│   ├── normalize/
│   │   ├── __pycache__/ (contents excluded)
│   │   ├── __init__.py
│   │   ├── cli.py
│   │   ├── db.py
│   │   ├── engine.py
│   │   ├── graph.py
│   │   ├── scanner.py
│   │   ├── slugify.py
│   │   └── vault-index.db
│   ├── tools/
│   │   ├── archives/
│   │   │   ├── cpython-3.12.16+20261110-aarch64-apple-darwin-install_only.tar.gz
│   │   │   ├── cpython-3.12.16+20261110-aarch64-pc-windows-msvc-install_only.tar.gz
│   │   │   ├── cpython-3.12.16+20261110-aarch64-unknown-linux-gnu-install_only.tar.gz
│   │   │   ├── cpython-3.12.16+20261110-aarch64-unknown-linux-musl-install_only.tar.gz
│   │   │   ├── cpython-3.12.16+20261110-x86_64-apple-darwin-install_only.tar.gz
│   │   │   ├── cpython-3.12.16+20261110-x86_64-pc-windows-msvc-install_only.tar.gz
│   │   │   ├── cpython-3.12.16+20261110-x86_64-unknown-linux-gnu-install_only.tar.gz
│   │   │   ├── cpython-3.12.16+20261110-x86_64-unknown-linux-musl-install_only.tar.gz
│   │   │   ├── pandoc-3.14-arm64-macOS.zip
│   │   │   ├── pandoc-3.14-linux-amd64.tar.gz
│   │   │   ├── pandoc-3.14-linux-arm64.tar.gz
│   │   │   ├── pandoc-3.14-windows-x86_64.zip
│   │   │   └── pandoc-3.14-x86_64-macOS.zip
│   │   ├── tools-manifest.json
│   │   └── verify-manifest.py
│   ├── kykloi.log
│   ├── launch.py
│   └── logger.py
├── .gitignore
├── .python-version
├── assemble_code_to_md.py
├── launch.bat
├── launch.sh
├── pyproject.toml
├── README.md
├── system_instructions.md
└── uv.lock
```

# Source Files

## system/build/assets/css/style.css

```css
/* --- Libertinus Serif --- */
@font-face {
    font-family: 'Libertinus Serif';
    src: url('../fonts/libertinusserif-regular-webfont.woff2') format('woff2');
    font-weight: 400;
    font-style: normal;
}

@font-face {
    font-family: 'Libertinus Serif';
    src: url('../fonts/libertinusserif-italic-webfont.woff2') format('woff2');
    font-weight: 400;
    font-style: italic;
}

@font-face {
    font-family: 'Libertinus Serif';
    src: url('../fonts/libertinusserif-bold-webfont.woff2') format('woff2');
    font-weight: 700;
    font-style: normal;
}

@font-face {
    font-family: 'Libertinus Serif';
    src: url('../fonts/libertinusserif-bolditalic-webfont.woff2') format('woff2');
    font-weight: 700;
    font-style: italic;
}

/* --- JetBrains Mono --- */
@font-face {
    font-family: 'JetBrains Mono';
    src: url('../fonts/jetbrainsmono-variablefont_wght-webfont.woff2') format('woff2');
    font-weight: 100 900;
    font-style: normal;
}

:root {
    --pico-font-family-sans-serif: system-ui, sans-serif;
    --pico-font-family-serif: "Libertinus Serif", Georgia, serif;
    --pico-font-family-monospace: "JetBrains Mono", ui-monospace, monospace;
    --pico-font-family: var(--pico-font-family-serif);
}

h1 {
    text-align: center;
    color: var(--pico-primary);
}

span.smallcaps {
    font-variant: small-caps;
}

main figure {
    text-align: center;
    display: block;
}

figcaption {
    text-align: center;
    color: var(--pico-muted-color);
}

a:not([role="button"]) {
    --pico-text-decoration: none;
    --text-decoration: none;
    text-decoration: none;
}

main ul,
main ol {
    padding-inline-start: 1rem;
}

li > ul,
li > ol {
    margin-top: calc(var(--pico-typography-spacing-vertical) * 0.25);
    margin-bottom: 0;
}

li {
    margin-bottom: calc(var(--pico-typography-spacing-vertical) * 0.25);
}

main ul li {
    list-style-type: disc;
}

main ul ul li {
    list-style-type: circle;
}

main ul ul ul li {
    list-style-type: disc;
}

main ul ul ul ul li {
    list-style-type: circle;
}

dl dd {
    margin-bottom: calc(var(--pico-typography-spacing-vertical) * 0.5);
}

li > p {
    margin-bottom: calc(var(--pico-typography-spacing-vertical) * 0.25);
}
li > p:last-child {
    margin-bottom: 0;
}

header.site_header {
    padding-inline: var(--pico-spacing);
}

main {
    max-width: 78ch;
    margin-inline: auto;
}

main figure img,
main p > img {
    display: block;
    margin: 0 auto;
    border: var(--pico-border-width) solid var(--pico-primary);
    border-radius: var(--pico-border-radius);
    box-sizing: border-box;
}

.katex-display {
    margin-top: var(--pico-typography-spacing-vertical);
    margin-bottom: var(--pico-typography-spacing-vertical);
    overflow-x: auto;
    overflow-y: hidden;
    padding-top: 0.5em;
    padding-bottom: 0.5em;
}

.brand_text {
    color: var(--pico-primary);
    font-size: 2rem;
    font-weight: bold;
    display: flex;
    align-items: baseline;
}

footer {
    color: var(--pico-muted-color);
}
```

## system/build/assets/js/decrypt.js

```javascript
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
    if (typeof window.katex === "undefined") {
      return;
    }

    const mathElements = container.querySelectorAll(".math");
    for (let i = 0; i < mathElements.length; i++) {
      const el = mathElements[i];
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
        window.katex.render(tex, el, {
          displayMode: isDisplay,
          throwOnError: false,
          fleqn: false,
        });
      } catch (kErr) {
        console.error("[Kykloi KaTeX Error]:", kErr);
      }
    }
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

        img.onload = () => {
          URL.revokeObjectURL(blobUrl);
        };

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

    function sanitizeDecryptedHtml(untrustedHtml) {
      const parser = new DOMParser();
      const doc = parser.parseFromString(untrustedHtml, "text/html");

      const ALLOWED_TAGS = new Set([
        "P", "DIV", "SPAN", "H1", "H2", "H3", "H4", "H5", "H6",
        "UL", "OL", "LI", "BLOCKQUOTE", "PRE", "CODE", "EM", "STRONG",
        "DEL", "INS", "MARK", "HR", "SUP", "SUB", "TABLE", "THEAD",
        "TBODY", "TR", "TH", "TD", "A", "IMG", "FIGURE", "FIGCAPTION",
        "DL", "DT", "DD", "DETAILS", "SUMMARY", "SECTION", "HEADER", "FOOTER"
      ]);

      const ALLOWED_ATTRS = new Set([
        "class", "id", "href", "src", "alt", "title",
        "data-encrypted-media", "data-relative-root"
      ]);

      doc.body.querySelectorAll("*").forEach((el) => {
        if (!ALLOWED_TAGS.has(el.tagName)) {
          el.remove();
          return;
        }
        for (let i = el.attributes.length - 1; i >= 0; i--) {
          const attr = el.attributes[i];
          const name = attr.name.toLowerCase();
          const val = attr.value.trim().toLowerCase();

          if (!ALLOWED_ATTRS.has(name) ||
              ((name === "href" || name === "src") && val.startsWith("javascript:"))) {
            el.removeAttribute(attr.name);
          }
        }
      });
      return doc.body.innerHTML;
    }

      try {
        const html = await decryptEnvelope(password, rawPayload);

        contentContainer.innerHTML = sanitizeDecryptedHtml(html);
        contentContainer.style.display = "block";

      payloadEl.textContent = "";
      if (lockContainer) {
        lockContainer.remove();
      }

      renderDecryptedMath(contentContainer);
      await hydrateEncryptedImages(contentContainer, password);
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
```

## system/build/assets/js/search_worker.js

```javascript
"use strict";

importScripts("sqlite3.js");

let sqlite3 = null;
let db = null;
let initPromise = null;
const messageQueue = [];

async function initDatabase(dbUrl) {
  if (db) return;

  if (!sqlite3) {
    sqlite3 = await self.sqlite3InitModule({
      print: (msg) => console.log("[Kykloi SQLite]", msg),
      printErr: (msg) => console.error("[Kykloi SQLite Error]", msg),
    });
  }

  const response = await fetch(dbUrl);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status} fetching search index from ${dbUrl}`);
  }

  const arrayBuffer = await response.arrayBuffer();
  const bytes = new Uint8Array(arrayBuffer);

  const pData = sqlite3.wasm.allocFromTypedArray(bytes);
  db = new sqlite3.oo1.DB();

  const SQLITE_DESERIALIZE_FREEONCLOSE = sqlite3.capi.SQLITE_DESERIALIZE_FREEONCLOSE || 1;
  const SQLITE_DESERIALIZE_RESIZEABLE = sqlite3.capi.SQLITE_DESERIALIZE_RESIZEABLE || 2;

  const rc = sqlite3.capi.sqlite3_deserialize(
    db.pointer,
    "main",
    pData,
    bytes.byteLength,
    bytes.byteLength,
    SQLITE_DESERIALIZE_FREEONCLOSE | SQLITE_DESERIALIZE_RESIZEABLE
  );

  if (rc !== 0) {
    throw new Error(`sqlite3_deserialize failed with return code: ${rc}`);
  }
}

function buildFtsQueries(rawQuery) {
  const trimmed = rawQuery.trim();
  if (!trimmed) return [];

  const hasAdvancedSyntax = /["':]|\b(AND|OR|NOT)\b|^-/i.test(trimmed);

  const tokens = trimmed
    .replace(/[^\p{L}\p{N}_]+/gu, " ")
    .trim()
    .split(/\s+/)
    .filter(Boolean);

  const fallbackQuery = tokens.length > 0
    ? tokens.map((t) => `"${t.replace(/"/g, '""')}"*`).join(" ")
    : null;

  if (hasAdvancedSyntax) {
    return [trimmed, fallbackQuery].filter(Boolean);
  }

  return [fallbackQuery].filter(Boolean);
}

function getRecentDocuments(searchId) {
  if (!db) return;

  const sql = `
    SELECT title, url, date_edtf
    FROM docs_fts
    ORDER BY (date_edtf != '') DESC, date_edtf DESC, rowid DESC
    LIMIT 50;
  `;

  const rows = [];
  try {
    db.exec({
      sql,
      rowMode: "object",
      callback: (row) => rows.push(row),
    });

    self.postMessage({
      type: "results",
      query: "",
      searchId,
      hits: rows,
      hasMore: false,
      isDefault: true,
    });
  } catch (err) {
    console.warn("[Kykloi Search Worker] Failed to fetch recent documents:", err);
    self.postMessage({
      type: "results",
      query: "",
      searchId,
      hits: [],
      hasMore: false,
      isDefault: true,
      error: err.message,
    });
  }
}

function executeSearch(query, searchId) {
  const trimmed = (query || "").trim();

  if (!trimmed) {
    getRecentDocuments(searchId);
    return;
  }

  const candidateQueries = buildFtsQueries(trimmed);
  if (candidateQueries.length === 0 || !db) {
    self.postMessage({
      type: "results",
      query,
      searchId,
      hits: [],
      hasMore: false,
      isDefault: false,
    });
    return;
  }

  const sql = `
    SELECT title, url, date_edtf
    FROM docs_fts
    WHERE docs_fts MATCH ?
    ORDER BY rank
    LIMIT 101;
  `;

  let rows = [];
  let executionSuccess = false;

  for (const ftsQuery of candidateQueries) {
    try {
      rows = [];
      db.exec({
        sql,
        bind: [ftsQuery],
        rowMode: "object",
        callback: (row) => rows.push(row),
      });
      executionSuccess = true;
      break;
    } catch (err) {
    }
  }

  if (!executionSuccess) {
    self.postMessage({
      type: "results",
      query,
      searchId,
      hits: [],
      hasMore: false,
      isDefault: false,
    });
    return;
  }

  const hasMore = rows.length > 100;
  const hits = hasMore ? rows.slice(0, 100) : rows;

  self.postMessage({
    type: "results",
    query,
    searchId,
    hits,
    hasMore,
    isDefault: false,
  });
}

async function processMessage(data) {
  const { type, dbUrl, query, searchId } = data || {};

  switch (type) {
    case "init":
      if (!initPromise) {
        initPromise = initDatabase(dbUrl)
          .then(() => {
            self.postMessage({ type: "ready" });
            while (messageQueue.length > 0) {
              const pending = messageQueue.shift();
              processMessage(pending);
            }
          })
          .catch((err) => {
            initPromise = null;
            self.postMessage({ type: "error", error: err.message });
          });
      }
      break;

    case "search":
      if (!db && initPromise) {
        messageQueue.push(data);
        return;
      }
      if (!db && !initPromise) {
        self.postMessage({
          type: "results",
          query,
          searchId,
          hits: [],
          hasMore: false,
          isDefault: false,
          error: "Search database is not initialized.",
        });
        return;
      }
      executeSearch(query || "", searchId);
      break;

    default:
      console.warn("[Kykloi Search Worker] Unhandled message type:", type);
  }
}

self.onmessage = (e) => {
  processMessage(e.data);
};
```

## system/build/assets/js/wasm-search.js

```javascript
"use strict";

document.addEventListener("DOMContentLoaded", () => {
  const bodyInput = document.getElementById("body-search-input");
  const bodyResults = document.getElementById("body-search-results");
  const navSearchBtn = document.getElementById("nav-search-btn");

  // Exit immediately if this page does not contain the Search Hub input
  if (!bodyInput || !bodyResults) return;

  const rawRoot = document.body.dataset.relativeRoot || "";
  const relativeRoot = rawRoot && !rawRoot.endsWith("/") ? `${rawRoot}/` : rawRoot;

  const workerUrl = new URL(`${relativeRoot}assets/js/search_worker.js`, window.location.href).href;
  const dbUrl = new URL(`${relativeRoot}search.db`, window.location.href).href;

  let worker = null;
  let activeSearchId = 0;

  function initWorker() {
    if (worker) return;

    try {
      worker = new Worker(workerUrl);

      worker.onmessage = (e) => {
        const { type, query, searchId, hits, hasMore, isDefault, error } = e.data || {};

        if (type === "ready") {
          if (bodyInput.value.trim() === "") {
            dispatchSearch("", bodyResults);
          }
          return;
        }

        if (type === "error") {
          console.error("[Kykloi Search] Worker initialization failed:", error);
          bodyResults.innerHTML = `
            <li style="list-style: none; padding: 1rem 0; color: var(--pico-color-red-500); text-align: center;">
              Search index unavailable: ${escapeHtml(error)}
            </li>`;
          return;
        }

        if (type === "results") {
          if (searchId !== activeSearchId) return;
          renderResults(hits, hasMore, query, isDefault, bodyResults);
        }
      };

      worker.postMessage({ type: "init", dbUrl });
    } catch (err) {
      console.error("[Kykloi Search] Failed to create search worker:", err);
    }
  }

  function escapeHtml(str) {
    if (!str) return "";
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function renderResults(hits, hasMore, query, isDefault, container) {
    if (!hits || hits.length === 0) {
      container.innerHTML = `
        <li style="list-style: none; padding: 1.5rem 0; text-align: center; color: var(--pico-muted-color);">
          No documents matching "<strong>${escapeHtml(query.trim())}</strong>"
        </li>`;
      return;
    }

    let headerHtml = "";
    if (isDefault) {
      headerHtml = `
        <li style="list-style: none; padding: 0.25rem 0 0.5rem 0; margin-bottom: 0.5rem; color: var(--pico-muted-color); font-size: 0.8rem; font-weight: bold; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 2px solid var(--pico-muted-border-color);">
          Recent Notes (${hits.length})
        </li>`;
    }

    let itemsHtml = hits
      .map((item) => {
        const cleanUrl = item.url.startsWith("/") ? item.url.slice(1) : item.url;
        const targetUrl = `${relativeRoot}${cleanUrl}`;
        const title = item.title || item.url;

        const dateHtml = item.date_edtf
          ? `<time style="opacity: 0.65; font-size: 0.85em; margin-left: 0.5rem; font-family: monospace;">(${escapeHtml(item.date_edtf)})</time>`
          : "";

        return `
          <li style="list-style: none; border-bottom: 1px solid var(--pico-muted-border-color); padding: 0.6rem 0;">
            <a href="${targetUrl}" style="text-decoration: none; display: block;">
              <span style="color: var(--pico-primary); font-weight: bold;">${escapeHtml(title)}</span>
              ${dateHtml}
            </a>
          </li>`;
      })
      .join("");

    if (hasMore) {
      itemsHtml += `
        <li style="list-style: none; padding: 0.75rem 0; text-align: center; color: var(--pico-muted-color); font-size: 0.85rem;">
          Showing top 100 results. Refine your query for more specific matches.
        </li>`;
    }

    container.innerHTML = headerHtml + itemsHtml;
  }

  function dispatchSearch(query, container) {
    initWorker();
    activeSearchId += 1;
    worker.postMessage({
      type: "search",
      query: (query || "").trim(),
      searchId: activeSearchId,
    });
  }

  function debounce(fn, delayMs) {
    let timer = null;
    return (...args) => {
      clearTimeout(timer);
      timer = setTimeout(() => fn(...args), delayMs);
    };
  }

  const debouncedSearch = debounce(dispatchSearch, 120);

  bodyInput.addEventListener("input", (e) => {
    debouncedSearch(e.target.value, bodyResults);
  });

  if (navSearchBtn) {
    navSearchBtn.addEventListener("click", (e) => {
      e.preventDefault();
      bodyInput.focus();
      bodyInput.scrollIntoView({ behavior: "smooth", block: "center" });
    });
  }

  if (window.location.search.includes("focus=1")) {
    bodyInput.focus();
  }

  if (window.innerWidth > 768) {
    bodyInput.focus();
  }

  window.addEventListener("keydown", (e) => {
    const isModifierK = (e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k";
    const isSlash = e.key === "/" && !["INPUT", "TEXTAREA"].includes(document.activeElement?.tagName);

    if (isModifierK || isSlash) {
      e.preventDefault();
      bodyInput.focus();
      bodyInput.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  });

  initWorker();
});
```

## system/build/root/index.html

```html
<!doctype html>
<html data-theme="light" xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <meta charset="utf-8" />
        <meta name="generator" content="pandoc" />
        <meta
            name="viewport"
            content="width=device-width, initial-scale=1.0, user-scalable=yes"
        />

        <title>Κύκλοι</title>

        <link rel="icon" type="image/x-icon" href="favicon.ico" />
        <link rel="icon" type="image/svg+xml" href="favicon.svg" />
        <link
            rel="icon"
            type="image/png"
            sizes="96x96"
            href="favicon-96x96.png"
        />
        <link rel="apple-touch-icon" href="apple-touch-icon.png" />
        <link rel="manifest" href="site.webmanifest" />

        <link rel="stylesheet" href="assets/css/pico.css" />
        <link rel="stylesheet" href="assets/css/style.css" />

        <!-- Search Hub Driver (SQLite3 WASM FTS5) -->
        <script src="assets/js/wasm-search.js" defer></script>
    </head>

    <body data-relative-root="">
        <header class="container site_header">
            <nav>
                <ul>
                    <li>
                        <span class="brand_text">
                            <a href="index.html" style="text-decoration: none">JmB²</a>
                        </span>
                    </li>
                </ul>
                <ul>
                    <li>
                        <a href="index.html" data-tooltip="Home">
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                width="24"
                                height="24"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                stroke-width="2"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                class="lucide lucide-house-icon lucide-house"
                            >
                                <path
                                    d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"
                                />
                                <path
                                    d="M3 10a2 2 0 0 1 .709-1.528l7-6a2 2 0 0 1 2.582 0l7 6A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"
                                />
                            </svg>
                        </a>
                    </li>
                    <li>
                        <a href="#body-search-input" id="nav-search-btn" data-tooltip="Search Notes">
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                width="24"
                                height="24"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                stroke-width="2"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                class="lucide lucide-search-icon lucide-search"
                            >
                                <path d="m21 21-4.34-4.34" />
                                <circle cx="11" cy="11" r="8" />
                            </svg>
                        </a>
                    </li>
                </ul>
            </nav>
            <hr />
        </header>

        <main>
            <div class="container">
                <header id="title-block-header">
                    <h1 class="title">Κύκλοι</h1>
                </header>

                <!-- Search Hub Input with autofocus -->
                <input
                    type="search"
                    id="body-search-input"
                    placeholder="Search titles, keywords, dates (or browse recent below)..."
                    autocomplete="off"
                    autocorrect="off"
                    autocapitalize="off"
                    spellcheck="false"
                    autofocus
                />

                <!-- Search Results & Recent Notes Container -->
                <ul
                    id="body-search-results"
                    style="list-style: none; padding-left: 0; margin-top: 1rem"
                ></ul>
            </div>
        </main>

        <footer class="container">
            <hr />
            <div class="grid">
                <div></div>
                <div style="text-align: right"></div>
            </div>
        </footer>
    </body>
</html>
```

## system/build/templates/pandoc-template.html

```html
<!doctype html>
<html
    data-theme="light"
    xmlns="http://www.w3.org/1999/xhtml"
    $if(lang)$
    lang="$lang$"
    xml:lang="$lang$"
    $endif$$if(dir)$
    dir="$dir$"
    $endif$
>
    <head>
        <meta charset="utf-8" />
        <meta name="generator" content="pandoc" />
        <meta
            name="viewport"
            content="width=device-width, initial-scale=1.0, user-scalable=yes"
        />

        $for(author-meta)$
        <meta name="author" content="$author-meta$" />
        $endfor$ $if(date-meta)$
        <meta name="dcterms.date" content="$date-meta$" />
        $endif$ $if(keywords)$
        <meta
            name="keywords"
            content="$for(keywords)$$keywords$$sep$, $endfor$"
        />
        $endif$ $if(description-meta)$
        <meta name="description" content="$description-meta$" />
        $endif$

        <title>$if(title-prefix)$$title-prefix$ – $endif$$pagetitle$</title>

        <link
            rel="icon"
            type="image/x-icon"
            href="$relative_root$favicon.ico"
        />
        <link
            rel="icon"
            type="image/svg+xml"
            href="$relative_root$favicon.svg"
        />
        <link
            rel="icon"
            type="image/png"
            sizes="96x96"
            href="$relative_root$favicon-96x96.png"
        />
        <link
            rel="apple-touch-icon"
            href="$relative_root$apple-touch-icon.png"
        />
        <link rel="manifest" href="$relative_root$site.webmanifest" />

        $for(css)$
        <link rel="stylesheet" href="$css$" />
        $endfor$

        $if(encrypted)$
        <script src="$relative_root$assets/js/decrypt.js" defer></script>
        $endif$

        $for(header-includes)$ $header-includes$ $endfor$ $if(math)$ $math$
        $endif$
    </head>

    <body data-relative-root="$relative_root$">
        <header class="container site_header">
            <nav>
                <ul>
                    <li>
                        <span class="brand_text">
                            <a
                                href="$relative_root$index.html"
                                style="text-decoration: none"
                                >JmB²</a
                            >
                        </span>
                    </li>
                </ul>
                <ul>
                    <li>
                        <a href="$relative_root$index.html" data-tooltip="Home">
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                width="24"
                                height="24"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                stroke-width="2"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                class="lucide lucide-house-icon lucide-house"
                            >
                                <path
                                    d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"
                                />
                                <path
                                    d="M3 10a2 2 0 0 1 .709-1.528l7-6a2 2 0 0 1 2.582 0l7 6A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"
                                />
                            </svg>
                        </a>
                    </li>
                    <li>
                        <a
                            href="$relative_root$index.html?focus=1"
                            data-tooltip="Search Notes"
                        >
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                width="24"
                                height="24"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                stroke-width="2"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                class="lucide lucide-search-icon lucide-search"
                            >
                                <path d="m21 21-4.34-4.34" />
                                <circle cx="11" cy="11" r="8" />
                            </svg>
                        </a>
                    </li>
                </ul>
            </nav>
            <hr />

            $for(include-before)$ $include-before$ $endfor$
        </header>

        <main>
            <div class="container">
                $if(encrypted)$
                <div id="kykloi-decrypted-content" style="display: none;"></div>

                <div id="kykloi-lock-container">
                    <article>
                        <header><strong>Protected Payload</strong></header>
                        <p style="color: var(--pico-muted-color); font-size: 0.9rem;">
                            The contents of this document are encrypted. Enter the passphrase to decrypt.
                        </p>
                        <form id="kykloi-decrypt-form" autocomplete="off" onsubmit="return false;">
                            <fieldset role="group">
                                <input
                                    type="password"
                                    id="kykloi-password"
                                    name="kykloi_passphrase"
                                    placeholder="Enter passphrase..."
                                    autocomplete="one-time-code"
                                    autocorrect="off"
                                    autocapitalize="off"
                                    spellcheck="false"
                                    data-1p-ignore="true"
                                    data-bwignore="true"
                                    data-lpignore="true"
                                    required
                                    autofocus
                                />
                                <button type="submit">Unlock</button>
                            </fieldset>
                        </form>
                        <small
                            id="kykloi-decrypt-error"
                            style="display: none; color: var(--pico-color-red-500); font-weight: bold;"
                        >
                            Decryption failed: Incorrect passphrase or corrupted payload.
                        </small>
                    </article>
                </div>

                <script id="kykloi-encrypted-payload" type="text/plain">
__KYKLOI_ENCRYPTED_PAYLOAD__
                </script>
                $else$
                $if(toc)$
                <nav id="$idprefix$TOC" role="doc-toc">
                    $if(toc-title)$
                    <h2 id="$idprefix$toc-title">$toc-title$</h2>
                    $endif$ $table-of-contents$
                </nav>
                $endif$
                $body$
                $endif$
            </div>
        </main>

        <footer class="container">
            <hr />
            <div class="grid">
                <div></div>
                <div style="text-align: right"></div>
            </div>

            $for(include-after)$ $include-after$ $endfor$
        </footer>
    </body>
</html>
```

## system/build/build.py

```python
#!/usr/bin/env python3
"""
system/build/build.py - Zero-Dependency Deterministic SSG Compiler.
Part of Project Kykloi (v0.7.0).
Leverages vault_index.db SQLite ledger for O(1) stat-cached incremental builds.
Features Tiered Multi-Engine AES-256-GCM Acceleration with Deterministic Fallback.
Priority Order:
  1. Native OS C-ABI Shared Libraries (CommonCrypto / CNG / OpenSSL EVP)
  2. Host Python Compiled Packages (cryptography / pycryptodome)
  3. Pure-Python Baseline Engine (Zero-Dependency Fallback)
"""

import argparse
import base64
import concurrent.futures
import ctypes
import ctypes.util
import getpass
import hashlib
import json
import logging
import multiprocessing
import os
import platform
import re
import shutil
import sqlite3
import subprocess
import sys
import urllib.parse
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional, Tuple

APP_DIR = Path(__file__).resolve().parent
SYSTEM_DIR = APP_DIR.parent
PROJECT_ROOT = SYSTEM_DIR.parent

# Register project root and system subsystems on sys.path
for path_entry in (PROJECT_ROOT, SYSTEM_DIR, APP_DIR):
    if str(path_entry) not in sys.path:
        sys.path.insert(0, str(path_entry))

from logger import get_logger, setup_logging, timed_step

from system.normalize.cli import sync_db_with_disk
from system.normalize.db import VaultDB
from system.normalize.scanner import is_junk_path

# ===========================================================================
# 1. PURE-PYTHON AES-256-GCM ENGINE & TABLE-DRIVEN GHASH (TIER 3 BASELINE)
# ===========================================================================

S_BOX = [
    0x63,
    0x7C,
    0x77,
    0x7B,
    0xF2,
    0x6B,
    0x6F,
    0xC5,
    0x30,
    0x01,
    0x67,
    0x2B,
    0xFE,
    0xD7,
    0xAB,
    0x76,
    0xCA,
    0x82,
    0xC9,
    0x7D,
    0xFA,
    0x59,
    0x47,
    0xF0,
    0xAD,
    0xD4,
    0xA2,
    0xAF,
    0x9C,
    0xA4,
    0x72,
    0xC0,
    0xB7,
    0xFD,
    0x93,
    0x26,
    0x36,
    0x3F,
    0xF7,
    0xCC,
    0x34,
    0xA5,
    0xE5,
    0xF1,
    0x71,
    0xD8,
    0x31,
    0x15,
    0x04,
    0xC7,
    0x23,
    0xC3,
    0x18,
    0x96,
    0x05,
    0x9A,
    0x07,
    0x12,
    0x80,
    0xE2,
    0xEB,
    0x27,
    0xB2,
    0x75,
    0x09,
    0x83,
    0x2C,
    0x1A,
    0x1B,
    0x6E,
    0x5A,
    0xA0,
    0x52,
    0x3B,
    0xD6,
    0xB3,
    0x29,
    0xE3,
    0x2F,
    0x84,
    0x53,
    0xD1,
    0x00,
    0xED,
    0x20,
    0xFC,
    0xB1,
    0x5B,
    0x6A,
    0xCB,
    0xBE,
    0x39,
    0x4A,
    0x4C,
    0x58,
    0xCF,
    0xD0,
    0xEF,
    0xAA,
    0xFB,
    0x43,
    0x4D,
    0x33,
    0x85,
    0x45,
    0xF9,
    0x02,
    0x7F,
    0x50,
    0x3C,
    0x9F,
    0xA8,
    0x51,
    0xA3,
    0x40,
    0x8F,
    0x92,
    0x9D,
    0x38,
    0xF5,
    0xBC,
    0xB6,
    0xDA,
    0x21,
    0x10,
    0xFF,
    0xF3,
    0xD2,
    0xCD,
    0x0C,
    0x13,
    0xEC,
    0x5F,
    0x97,
    0x44,
    0x17,
    0xC4,
    0xA7,
    0x7E,
    0x3D,
    0x64,
    0x5D,
    0x19,
    0x73,
    0x60,
    0x81,
    0x4F,
    0xDC,
    0x22,
    0x2A,
    0x90,
    0x88,
    0x46,
    0xEE,
    0xB8,
    0x14,
    0xDE,
    0x5E,
    0x0B,
    0xDB,
    0xE0,
    0x32,
    0x3A,
    0x0A,
    0x49,
    0x06,
    0x24,
    0x5C,
    0xC2,
    0xD3,
    0xAC,
    0x62,
    0x91,
    0x95,
    0xE4,
    0x79,
    0xE7,
    0xC8,
    0x37,
    0x6D,
    0x8D,
    0xD5,
    0x4E,
    0xA9,
    0x6C,
    0x56,
    0xF4,
    0xEA,
    0x65,
    0x7A,
    0xAE,
    0x08,
    0xBA,
    0x78,
    0x25,
    0x2E,
    0x1C,
    0xA6,
    0xB4,
    0xC6,
    0xE8,
    0xDD,
    0x74,
    0x1F,
    0x4B,
    0xBD,
    0x8B,
    0x8A,
    0x70,
    0x3E,
    0xB5,
    0x66,
    0x48,
    0x03,
    0xF6,
    0x0E,
    0x61,
    0x35,
    0x57,
    0xB9,
    0x86,
    0xC1,
    0x1D,
    0x9E,
    0xE1,
    0xF8,
    0x98,
    0x11,
    0x69,
    0xD9,
    0x8E,
    0x94,
    0x9B,
    0x1E,
    0x87,
    0xE9,
    0xCE,
    0x55,
    0x28,
    0xDF,
    0x8C,
    0xA1,
    0x89,
    0x0D,
    0xBF,
    0xE6,
    0x42,
    0x68,
    0x41,
    0x99,
    0x2D,
    0x0F,
    0xB0,
    0x54,
    0xBB,
    0x16,
]

RCON = [0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36]


def _xtime(a: int) -> int:
    return ((a << 1) ^ 0x1B) & 0xFF if (a & 0x80) else (a << 1)


def _key_expansion_256(key: bytes) -> list[int]:
    w = list(key)
    for i in range(8, 60):
        temp = w[(i - 1) * 4 : i * 4]
        if i % 8 == 0:
            temp = [S_BOX[temp[1]], S_BOX[temp[2]], S_BOX[temp[3]], S_BOX[temp[0]]]
            temp[0] ^= RCON[i // 8]
        elif i % 8 == 4:
            temp = [S_BOX[x] for x in temp]
        for j in range(4):
            w.append(w[(i - 8) * 4 + j] ^ temp[j])
    return w


def _cipher_block(state_in: bytes | list[int], round_keys: list[int]) -> bytes:
    state = list(state_in)
    for i in range(16):
        state[i] ^= round_keys[i]

    for r in range(1, 14):
        rk = r * 16
        s0, s1, s2, s3 = (
            S_BOX[state[0]],
            S_BOX[state[5]],
            S_BOX[state[10]],
            S_BOX[state[15]],
        )
        s4, s5, s6, s7 = (
            S_BOX[state[4]],
            S_BOX[state[9]],
            S_BOX[state[14]],
            S_BOX[state[3]],
        )
        s8, s9, s10, s11 = (
            S_BOX[state[8]],
            S_BOX[state[13]],
            S_BOX[state[2]],
            S_BOX[state[7]],
        )
        s12, s13, s14, s15 = (
            S_BOX[state[12]],
            S_BOX[state[1]],
            S_BOX[state[6]],
            S_BOX[state[11]],
        )

        state[0] = _xtime(s0 ^ s1) ^ s1 ^ s2 ^ s3 ^ round_keys[rk]
        state[1] = _xtime(s1 ^ s2) ^ s2 ^ s3 ^ s0 ^ round_keys[rk + 1]
        state[2] = _xtime(s2 ^ s3) ^ s3 ^ s0 ^ s1 ^ round_keys[rk + 2]
        state[3] = _xtime(s3 ^ s0) ^ s0 ^ s1 ^ s2 ^ round_keys[rk + 3]

        state[4] = _xtime(s4 ^ s5) ^ s5 ^ s6 ^ s7 ^ round_keys[rk + 4]
        state[5] = _xtime(s5 ^ s6) ^ s6 ^ s7 ^ s4 ^ round_keys[rk + 5]
        state[6] = _xtime(s6 ^ s7) ^ s7 ^ s4 ^ s5 ^ round_keys[rk + 6]
        state[7] = _xtime(s7 ^ s4) ^ s4 ^ s5 ^ s6 ^ round_keys[rk + 7]

        state[8] = _xtime(s8 ^ s9) ^ s9 ^ s10 ^ s11 ^ round_keys[rk + 8]
        state[9] = _xtime(s9 ^ s10) ^ s10 ^ s11 ^ s8 ^ round_keys[rk + 9]
        state[10] = _xtime(s10 ^ s11) ^ s11 ^ s8 ^ s9 ^ round_keys[rk + 10]
        state[11] = _xtime(s11 ^ s8) ^ s8 ^ s9 ^ s10 ^ round_keys[rk + 11]

        state[12] = _xtime(s12 ^ s13) ^ s13 ^ s14 ^ s15 ^ round_keys[rk + 12]
        state[13] = _xtime(s13 ^ s14) ^ s14 ^ s15 ^ s12 ^ round_keys[rk + 13]
        state[14] = _xtime(s14 ^ s15) ^ s15 ^ s12 ^ s13 ^ round_keys[rk + 14]
        state[15] = _xtime(s15 ^ s12) ^ s12 ^ s13 ^ s14 ^ round_keys[rk + 15]

    rk = 224
    out = bytearray(16)
    out[0] = S_BOX[state[0]] ^ round_keys[rk]
    out[1] = S_BOX[state[5]] ^ round_keys[rk + 1]
    out[2] = S_BOX[state[10]] ^ round_keys[rk + 2]
    out[3] = S_BOX[state[15]] ^ round_keys[rk + 3]
    out[4] = S_BOX[state[4]] ^ round_keys[rk + 4]
    out[5] = S_BOX[state[9]] ^ round_keys[rk + 5]
    out[6] = S_BOX[state[14]] ^ round_keys[rk + 6]
    out[7] = S_BOX[state[3]] ^ round_keys[rk + 7]
    out[8] = S_BOX[state[8]] ^ round_keys[rk + 8]
    out[9] = S_BOX[state[13]] ^ round_keys[rk + 9]
    out[10] = S_BOX[state[2]] ^ round_keys[rk + 10]
    out[11] = S_BOX[state[7]] ^ round_keys[rk + 11]
    out[12] = S_BOX[state[12]] ^ round_keys[rk + 12]
    out[13] = S_BOX[state[1]] ^ round_keys[rk + 13]
    out[14] = S_BOX[state[6]] ^ round_keys[rk + 14]
    out[15] = S_BOX[state[11]] ^ round_keys[rk + 15]

    return bytes(out)


def _ghash_mult(x: int, y: int) -> int:
    r = 0xE1000000000000000000000000000000
    z = 0
    v = x
    for i in range(128):
        if (y >> (127 - i)) & 1:
            z ^= v
        if v & 1:
            v = (v >> 1) ^ r
        else:
            v >>= 1
    return z


_GHASH_TABLES_CACHE: dict[int, list[list[int]]] = {}


def _init_ghash_tables(h: int) -> list[list[int]]:
    if h in _GHASH_TABLES_CACHE:
        return _GHASH_TABLES_CACHE[h]
    tables: list[list[int]] = []
    for j in range(16):
        shift = 8 * (15 - j)
        basis = [_ghash_mult((1 << bit) << shift, h) for bit in range(8)]
        table = [0] * 256
        for b in range(1, 256):
            low_bit = (b & -b).bit_length() - 1
            table[b] = table[b & (b - 1)] ^ basis[low_bit]
        tables.append(table)
    _GHASH_TABLES_CACHE[h] = tables
    return tables


def _ghash_block(t: list[list[int]], x: int) -> int:
    return (
        t[0][(x >> 120) & 0xFF]
        ^ t[1][(x >> 112) & 0xFF]
        ^ t[2][(x >> 104) & 0xFF]
        ^ t[3][(x >> 96) & 0xFF]
        ^ t[4][(x >> 88) & 0xFF]
        ^ t[5][(x >> 80) & 0xFF]
        ^ t[6][(x >> 72) & 0xFF]
        ^ t[7][(x >> 64) & 0xFF]
        ^ t[8][(x >> 56) & 0xFF]
        ^ t[9][(x >> 48) & 0xFF]
        ^ t[10][(x >> 40) & 0xFF]
        ^ t[11][(x >> 32) & 0xFF]
        ^ t[12][(x >> 24) & 0xFF]
        ^ t[13][(x >> 16) & 0xFF]
        ^ t[14][(x >> 8) & 0xFF]
        ^ t[15][x & 0xFF]
    )


def pure_aes_gcm_encrypt(
    key: bytes, iv: bytes, plaintext: bytes
) -> Tuple[bytes, bytes]:
    if len(key) != 32 or len(iv) != 12:
        raise ValueError("Key must be 32 bytes and IV must be 12 bytes.")

    round_keys = _key_expansion_256(key)
    h_bytes = _cipher_block(bytes(16), round_keys)
    h = int.from_bytes(h_bytes, byteorder="big")
    ghash_tables = _init_ghash_tables(h)

    j0 = iv + b"\x00\x00\x00\x01"
    ciphertext = bytearray()
    num_blocks = (len(plaintext) + 15) // 16

    for i in range(num_blocks):
        ctr_val = (2 + i) & 0xFFFFFFFF
        ctr_block = iv + ctr_val.to_bytes(4, byteorder="big")
        keystream = _cipher_block(ctr_block, round_keys)
        chunk = plaintext[i * 16 : (i + 1) * 16]
        for p_b, k_b in zip(chunk, keystream):
            ciphertext.append(p_b ^ k_b)

    ciphertext_bytes = bytes(ciphertext)
    pad_len = (16 - (len(ciphertext_bytes) % 16)) % 16
    padded_ct = ciphertext_bytes + (b"\x00" * pad_len)

    s = 0
    for i in range(0, len(padded_ct), 16):
        block_int = int.from_bytes(padded_ct[i : i + 16], byteorder="big")
        s = _ghash_block(ghash_tables, s ^ block_int)

    len_block_int = len(ciphertext_bytes) * 8
    s = _ghash_block(ghash_tables, s ^ len_block_int)

    tag_mask = _cipher_block(j0, round_keys)
    tag = bytes(a ^ b for a, b in zip(s.to_bytes(16, "big"), tag_mask))

    return ciphertext_bytes, tag


# ===========================================================================
# 2. ACCELERATED CRYPTO ENGINES
# ===========================================================================


def _init_darwin_commoncrypto() -> Optional[
    Callable[[bytes, bytes, bytes], Tuple[bytes, bytes]]
]:
    if sys.platform != "darwin":
        return None

    try:
        lib = ctypes.CDLL("/usr/lib/libSystem.B.dylib")
        if not hasattr(lib, "CCCryptorGCMOneshotEncrypt"):
            return None

        fn = lib.CCCryptorGCMOneshotEncrypt
        fn.restype = ctypes.c_int32
        fn.argtypes = [
            ctypes.c_uint32,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_size_t,
        ]

        def _encrypt_commoncrypto(
            key: bytes, iv: bytes, plaintext: bytes
        ) -> Tuple[bytes, bytes]:
            pt_len = len(plaintext)
            ct = ctypes.create_string_buffer(max(1, pt_len))
            tag = ctypes.create_string_buffer(16)

            st = fn(
                0,
                key,
                len(key),
                iv,
                len(iv),
                None,
                0,
                plaintext if pt_len > 0 else None,
                pt_len,
                ct,
                tag,
                16,
            )
            if st != 0:
                raise RuntimeError(f"CommonCrypto error code: {st}")

            return bytes(ct.raw[:pt_len]), bytes(tag.raw)

        return _encrypt_commoncrypto
    except Exception:
        return None


class _BCRYPT_AUTHENTICATED_CIPHER_MODE_INFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_ulong),
        ("dwInfoVersion", ctypes.c_ulong),
        ("pbNonce", ctypes.c_void_p),
        ("cbNonce", ctypes.c_ulong),
        ("pbAuthData", ctypes.c_void_p),
        ("cbAuthData", ctypes.c_ulong),
        ("pbTag", ctypes.c_void_p),
        ("cbTag", ctypes.c_ulong),
        ("pbMacContext", ctypes.c_void_p),
        ("cbMacContext", ctypes.c_ulong),
        ("cbAAD", ctypes.c_ulong),
        ("cbData", ctypes.c_ulonglong),
        ("dwFlags", ctypes.c_ulong),
    ]


_CNG_ALG_HANDLE: Optional[ctypes.c_void_p] = None


def _init_windows_cng() -> Optional[
    Callable[[bytes, bytes, bytes], Tuple[bytes, bytes]]
]:
    global _CNG_ALG_HANDLE
    if sys.platform != "win32":
        return None

    try:
        bcrypt = ctypes.windll.bcrypt  # type: ignore[attr-defined]

        alg_handle = ctypes.c_void_p()
        status = bcrypt.BCryptOpenAlgorithmProvider(
            ctypes.byref(alg_handle),
            ctypes.c_wchar_p("AES"),
            None,
            ctypes.c_ulong(0),
        )
        if status != 0:
            return None

        chain_mode = "ChainingModeGCM\0".encode("utf-16le")
        status = bcrypt.BCryptSetProperty(
            alg_handle,
            ctypes.c_wchar_p("ChainingMode"),
            chain_mode,
            ctypes.c_ulong(len(chain_mode)),
            ctypes.c_ulong(0),
        )
        if status != 0:
            bcrypt.BCryptCloseAlgorithmProvider(alg_handle, ctypes.c_ulong(0))
            return None

        _CNG_ALG_HANDLE = alg_handle

        def _encrypt_cng(
            key: bytes, iv: bytes, plaintext: bytes
        ) -> Tuple[bytes, bytes]:
            key_handle = ctypes.c_void_p()
            st = bcrypt.BCryptGenerateSymmetricKey(
                _CNG_ALG_HANDLE,
                ctypes.byref(key_handle),
                None,
                ctypes.c_ulong(0),
                ctypes.c_char_p(key),
                ctypes.c_ulong(len(key)),
                ctypes.c_ulong(0),
            )
            if st != 0:
                raise RuntimeError(f"BCryptGenerateSymmetricKey error: {hex(st)}")

            try:
                c_iv = ctypes.create_string_buffer(iv, len(iv))
                c_tag = ctypes.create_string_buffer(16)

                auth_info = _BCRYPT_AUTHENTICATED_CIPHER_MODE_INFO()
                auth_info.cbSize = ctypes.sizeof(_BCRYPT_AUTHENTICATED_CIPHER_MODE_INFO)
                auth_info.dwInfoVersion = 1
                auth_info.pbNonce = ctypes.cast(c_iv, ctypes.c_void_p)
                auth_info.cbNonce = len(iv)
                auth_info.pbTag = ctypes.cast(c_tag, ctypes.c_void_p)
                auth_info.cbTag = 16

                pt_len = len(plaintext)
                out_buf = ctypes.create_string_buffer(max(1, pt_len))
                bytes_done = ctypes.c_ulong(0)

                st = bcrypt.BCryptEncrypt(
                    key_handle,
                    ctypes.c_char_p(plaintext) if pt_len > 0 else None,
                    ctypes.c_ulong(pt_len),
                    ctypes.byref(auth_info),
                    None,
                    ctypes.c_ulong(0),
                    out_buf,
                    ctypes.c_ulong(pt_len),
                    ctypes.byref(bytes_done),
                    ctypes.c_ulong(0),
                )
                if st != 0:
                    raise RuntimeError(f"BCryptEncrypt error: {hex(st)}")

                return bytes(out_buf.raw[: bytes_done.value]), bytes(c_tag.raw)
            finally:
                bcrypt.BCryptDestroyKey(key_handle)

        return _encrypt_cng
    except Exception:
        return None


def _is_safe_posix_libcrypto_path(path: str) -> bool:
    if sys.platform == "darwin":
        clean = path.strip()
        if clean in ("crypto", "libcrypto", "libcrypto.dylib", "libcrypto.35.dylib"):
            return False
        try:
            resolved = str(Path(clean).resolve())
        except Exception:
            resolved = clean
        if resolved.startswith(("/usr/lib/", "/System/", "/Library/Apple/")):
            return False
    return True


def _find_posix_libcrypto() -> Optional[ctypes.CDLL]:
    candidates: list[str] = []

    py_lib_dir = Path(sys.prefix) / "lib"
    if py_lib_dir.is_dir():
        for pattern in ("libcrypto*.dylib", "libcrypto*.so*"):
            for found in sorted(py_lib_dir.glob(pattern)):
                candidates.append(str(found))

    if sys.platform == "darwin":
        candidates.extend(
            [
                "/opt/homebrew/opt/openssl@3/lib/libcrypto.dylib",
                "/opt/homebrew/opt/openssl@1.1/lib/libcrypto.dylib",
                "/opt/homebrew/lib/libcrypto.dylib",
                "/usr/local/opt/openssl@3/lib/libcrypto.dylib",
                "/usr/local/opt/openssl@1.1/lib/libcrypto.dylib",
                "/usr/local/lib/libcrypto.dylib",
                "/opt/local/lib/libcrypto.dylib",
                "/opt/local/lib/openssl-3/libcrypto.dylib",
                "/opt/local/lib/openssl-1.1/libcrypto.dylib",
            ]
        )
    else:
        for name in ("crypto", "libcrypto"):
            path = ctypes.util.find_library(name)
            if path:
                candidates.append(path)

        candidates.extend(
            [
                "libcrypto.so.3",
                "libcrypto.so.1.1",
                "libcrypto.so",
                "/lib/libcrypto.so.3",
                "/lib/libcrypto.so.1.1",
                "/lib64/libcrypto.so.3",
                "/lib64/libcrypto.so.1.1",
                "/usr/lib/x86_64-linux-gnu/libcrypto.so.3",
                "/usr/lib/aarch64-linux-gnu/libcrypto.so.3",
                "/usr/lib/x86_64-linux-gnu/libcrypto.so.1.1",
                "/usr/lib/aarch64-linux-gnu/libcrypto.so.1.1",
                "/usr/lib64/libcrypto.so.3",
                "/usr/lib64/libcrypto.so.1.1",
                "/usr/lib/libcrypto.so.3",
                "/usr/lib/libcrypto.so.1.1",
                "/usr/lib/libcrypto.so",
                "/usr/local/lib/libcrypto.so.3",
                "/usr/local/lib/libcrypto.so.1.1",
                "/usr/local/lib/libcrypto.so",
                "/usr/local/lib64/libcrypto.so",
            ]
        )

    required_symbols = (
        "EVP_CIPHER_CTX_new",
        "EVP_CIPHER_CTX_free",
        "EVP_aes_256_gcm",
        "EVP_EncryptInit_ex",
        "EVP_CIPHER_CTX_ctrl",
        "EVP_EncryptUpdate",
        "EVP_EncryptFinal_ex",
    )

    for p in candidates:
        if not _is_safe_posix_libcrypto_path(p):
            continue
        if "/" in p and not os.path.isfile(p):
            continue
        try:
            lib = ctypes.CDLL(p)
            if all(hasattr(lib, sym) for sym in required_symbols):
                return lib
        except OSError:
            continue

    return None


def _init_posix_openssl() -> Optional[
    Callable[[bytes, bytes, bytes], Tuple[bytes, bytes]]
]:
    lib = _find_posix_libcrypto()
    if not lib:
        return None

    try:
        lib.EVP_CIPHER_CTX_new.restype = ctypes.c_void_p
        lib.EVP_CIPHER_CTX_new.argtypes = []

        lib.EVP_CIPHER_CTX_free.restype = None
        lib.EVP_CIPHER_CTX_free.argtypes = [ctypes.c_void_p]

        lib.EVP_aes_256_gcm.restype = ctypes.c_void_p
        lib.EVP_aes_256_gcm.argtypes = []

        lib.EVP_EncryptInit_ex.restype = ctypes.c_int
        lib.EVP_EncryptInit_ex.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
        ]

        lib.EVP_CIPHER_CTX_ctrl.restype = ctypes.c_int
        lib.EVP_CIPHER_CTX_ctrl.argtypes = [
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_void_p,
        ]

        lib.EVP_EncryptUpdate.restype = ctypes.c_int
        lib.EVP_EncryptUpdate.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_int),
            ctypes.c_char_p,
            ctypes.c_int,
        ]

        lib.EVP_EncryptFinal_ex.restype = ctypes.c_int
        lib.EVP_EncryptFinal_ex.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_int),
        ]

        EVP_CTRL_GCM_SET_IVLEN = 0x9
        EVP_CTRL_GCM_GET_TAG = 0x10

        def _encrypt_openssl(
            key: bytes, iv: bytes, plaintext: bytes
        ) -> Tuple[bytes, bytes]:
            ctx = lib.EVP_CIPHER_CTX_new()
            if not ctx:
                raise RuntimeError("EVP_CIPHER_CTX_new allocation failure.")

            try:
                cipher = lib.EVP_aes_256_gcm()
                if lib.EVP_EncryptInit_ex(ctx, cipher, None, None, None) != 1:
                    raise RuntimeError("EVP_EncryptInit_ex cipher bind failed.")

                if (
                    lib.EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, len(iv), None)
                    != 1
                ):
                    raise RuntimeError(
                        "EVP_CIPHER_CTX_ctrl IV length assignment failed."
                    )

                if lib.EVP_EncryptInit_ex(ctx, None, None, key, iv) != 1:
                    raise RuntimeError(
                        "EVP_EncryptInit_ex key/iv initialization failed."
                    )

                pt_len = len(plaintext)
                c_ct = ctypes.create_string_buffer(max(1, pt_len + 16))
                out_len = ctypes.c_int(0)

                if pt_len > 0:
                    if (
                        lib.EVP_EncryptUpdate(
                            ctx, c_ct, ctypes.byref(out_len), plaintext, pt_len
                        )
                        != 1
                    ):
                        raise RuntimeError("EVP_EncryptUpdate failed.")

                total_len = out_len.value
                final_buf = ctypes.create_string_buffer(16)
                final_len = ctypes.c_int(0)
                if (
                    lib.EVP_EncryptFinal_ex(ctx, final_buf, ctypes.byref(final_len))
                    != 1
                ):
                    raise RuntimeError("EVP_EncryptFinal_ex failed.")

                tag = ctypes.create_string_buffer(16)
                if lib.EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_GET_TAG, 16, tag) != 1:
                    raise RuntimeError("EVP_CIPHER_CTX_ctrl tag extraction failed.")

                return bytes(c_ct.raw[:total_len]), bytes(tag.raw)
            finally:
                lib.EVP_CIPHER_CTX_free(ctx)

        return _encrypt_openssl
    except Exception:
        return None


def _init_py_cryptography() -> Optional[
    Callable[[bytes, bytes, bytes], Tuple[bytes, bytes]]
]:
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM

        def _encrypt(key: bytes, iv: bytes, plaintext: bytes) -> Tuple[bytes, bytes]:
            ct_tag = AESGCM(key).encrypt(iv, plaintext, None)
            return ct_tag[:-16], ct_tag[-16:]

        return _encrypt
    except ImportError:
        return None


def _init_py_cryptodome() -> Optional[
    Callable[[bytes, bytes, bytes], Tuple[bytes, bytes]]
]:
    try:
        from Cryptodome.Cipher import AES  # type: ignore[import-not-found]

        def _encrypt(key: bytes, iv: bytes, plaintext: bytes) -> Tuple[bytes, bytes]:
            cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
            ct, tag = cipher.encrypt_and_digest(plaintext)
            return ct, tag

        return _encrypt
    except ImportError:
        return None


# ===========================================================================
# 3. ENGINE DISPATCHER & NIST KAT VERIFICATION
# ===========================================================================

KAT_KEY = bytes.fromhex("00" * 32)
KAT_IV = bytes.fromhex("00" * 12)
KAT_PT = bytes.fromhex("00" * 16)
KAT_EXPECTED_CT = bytes.fromhex("cea7403d4d606b6e074ec5d3baf39d18")
KAT_EXPECTED_TAG = bytes.fromhex("d0d1c8a799996bf0265b98b5d48ab919")


def _test_engine_kat(fn: Callable[[bytes, bytes, bytes], Tuple[bytes, bytes]]) -> bool:
    try:
        ct, tag = fn(KAT_KEY, KAT_IV, KAT_PT)
        return ct == KAT_EXPECTED_CT and tag == KAT_EXPECTED_TAG
    except Exception:
        return False


def _resolve_active_crypto_engine() -> Tuple[
    str, Callable[[bytes, bytes, bytes], Tuple[bytes, bytes]]
]:
    if os.environ.get("KYKLOI_CRYPTO_ENGINE") == "pure":
        if _test_engine_kat(pure_aes_gcm_encrypt):
            return "Pure-Python AES-GCM (Forced Fallback)", pure_aes_gcm_encrypt

    # Priority Tier 1: Native OS C-ABI via ctypes
    if sys.platform == "darwin":
        darwin_fn = _init_darwin_commoncrypto()
        if darwin_fn and _test_engine_kat(darwin_fn):
            return "Apple CommonCrypto (libSystem / NEON / AES-NI)", darwin_fn

        openssl_fn = _init_posix_openssl()
        if openssl_fn and _test_engine_kat(openssl_fn):
            return "Safe OpenSSL EVP (MacPorts / Homebrew / sys.prefix)", openssl_fn

    elif sys.platform == "win32":
        cng_fn = _init_windows_cng()
        if cng_fn and _test_engine_kat(cng_fn):
            return "Windows CNG (bcrypt.dll / AES-NI)", cng_fn
    else:
        openssl_fn = _init_posix_openssl()
        if openssl_fn and _test_engine_kat(openssl_fn):
            return "System OpenSSL EVP (libcrypto / AES-NI / NEON)", openssl_fn

    # Priority Tier 2: Compiled Site Packages
    crypto_fn = _init_py_cryptography()
    if crypto_fn and _test_engine_kat(crypto_fn):
        return "Python cryptography (OpenSSL C-Extension)", crypto_fn

    cryptodome_fn = _init_py_cryptodome()
    if cryptodome_fn and _test_engine_kat(cryptodome_fn):
        return "Python pycryptodome (Hardware Accelerated)", cryptodome_fn

    # Priority Tier 3: Pure-Python Fallback Baseline
    if _test_engine_kat(pure_aes_gcm_encrypt):
        return "Pure-Python AES-GCM (Zero-Dependency Fallback)", pure_aes_gcm_encrypt

    raise RuntimeError("CRITICAL: All cryptographic engines failed NIST KAT self-test.")


ACTIVE_ENGINE_NAME, ACTIVE_ENCRYPT_FN = _resolve_active_crypto_engine()


def aes_gcm_encrypt(key: bytes, iv: bytes, plaintext: bytes) -> Tuple[bytes, bytes]:
    return ACTIVE_ENCRYPT_FN(key, iv, plaintext)


def verify_cryptographic_engine():
    if not _test_engine_kat(ACTIVE_ENCRYPT_FN):
        raise RuntimeError(
            f"CRITICAL: NIST KAT verification failed for active engine: {ACTIVE_ENGINE_NAME}"
        )


# ===========================================================================
# 4. PATHS & PIPELINE DEFINITIONS
# ===========================================================================

SRC = PROJECT_ROOT / "content"
DST = PROJECT_ROOT / "dist"
NORM_DB_PATH = SYSTEM_DIR / "normalize" / "vault-index.db"

DEFAULTS_YAML = APP_DIR / "html-config.yaml"
DEFAULT_TEMPLATE = APP_DIR / "templates" / "pandoc-template.html"
LUA_FILTER = APP_DIR / "translate-links.lua"
MANIFEST_FILE = APP_DIR / ".build_manifest.json"
SEARCH_DB_FILE = DST / "search.db"

CITATION_PATTERN = re.compile(
    r"(?:\[@[a-zA-Z0-9_:.#$%&-]+|(?<!\w)@[a-zA-Z0-9_:.#$%&-]+)"
)


@dataclass(frozen=True)
class CompileTask:
    md_path: Path
    out_path: Path
    template_path: Path
    relative_root: str
    doc_title: str
    defaults_yaml: Path
    lua_filter: Path
    bibliography_path: Optional[Path]
    is_secure: bool
    passphrase: Optional[str]
    dry_run: bool
    pandoc_bin: str


@dataclass(frozen=True)
class EncryptBlobTask:
    src_path: Path
    dst_path: Path
    passphrase: str
    dry_run: bool


def parse_args():
    p = argparse.ArgumentParser(
        description="Deterministic Archival Static Site Generator (Zero-Dependency Cryptography & SQLite FTS5)."
    )
    p.add_argument(
        "--clean", action="store_true", help="Purge destination directory and manifest."
    )
    p.add_argument("--dry-run", action="store_true", help="Simulate build pipeline.")
    p.add_argument(
        "--verbose", action="store_true", help="Output granular diagnostic logs."
    )
    p.add_argument(
        "--workers",
        type=int,
        default=os.cpu_count() or 4,
        help="Worker concurrency pool.",
    )
    p.add_argument(
        "--password",
        type=str,
        default=os.environ.get("KYKLOI_ENCRYPT_KEY"),
        help="Secure passphrase.",
    )
    p.add_argument(
        "--log-file",
        type=str,
        default=None,
        help="Destination path for persistent diagnostic logs.",
    )
    return p.parse_args()


# ===========================================================================
# 5. BINARY RESOLUTION & CRYPTOGRAPHIC UTILITIES
# ===========================================================================


def resolve_pandoc_binary(root_dir: Path) -> str:
    system = platform.system().lower()
    machine = platform.machine().lower()
    arch = (
        "x86_64"
        if machine in ("x86_64", "amd64")
        else ("arm64" if machine in ("arm64", "aarch64") else machine)
    )
    target = f"{'macos' if system == 'darwin' else system}-{arch}"
    pandoc_target = "windows-x86_64" if target == "windows-arm64" else target

    archives_dir = root_dir / "system" / "tools" / "archives"
    manifest_path = root_dir / "system" / "tools" / "tools-manifest.json"

    if system == "windows":
        runtime_dir = (
            Path(os.environ.get("TEMP", "/tmp")) / f"kykloi_pandoc_{pandoc_target}"
        )
        pandoc_bin = runtime_dir / "pandoc.exe"
    else:
        xdg_cache = os.environ.get("XDG_CACHE_HOME")
        if xdg_cache and Path(xdg_cache).is_dir():
            base_runtime = Path(xdg_cache)
        elif (Path.home() / ".cache").exists():
            base_runtime = Path.home() / ".cache"
        else:
            base_runtime = Path("/tmp")
        runtime_dir = base_runtime / f"kykloi_pandoc_{pandoc_target}"
        pandoc_bin = runtime_dir / "bin" / "pandoc"

    stamp_file = runtime_dir / ".verified_sha256"

    if (
        pandoc_bin.is_file()
        and stamp_file.is_file()
        and (system == "windows" or os.access(pandoc_bin, os.X_OK))
    ):
        return str(pandoc_bin.resolve())

    if not manifest_path.is_file():
        raise FileNotFoundError(f"Tools manifest missing at {manifest_path}")

    try:
        with open(manifest_path, "r", encoding="utf-8") as mf:
            tools_manifest = json.load(mf)
        target_info = tools_manifest["tools"]["pandoc"]["targets"][pandoc_target]
        archive_name = target_info["archive"]
        expected_hash = target_info["sha256"]
    except (KeyError, json.JSONDecodeError) as err:
        raise ValueError(
            f"Failed to read Pandoc manifest definition for {pandoc_target}: {err}"
        )

    archive_path = archives_dir / archive_name
    ext = "zip" if archive_name.endswith(".zip") else "tar.gz"
    log = get_logger("pandoc")

    if archive_path.is_file():
        log.info("Verifying integrity checksum for %s...", archive_path.name)
        actual_hash = compute_file_hash(archive_path)
        if actual_hash != expected_hash:
            raise ValueError(
                f"SHA-256 mismatch for {archive_path.name}:\n"
                f"  Expected: {expected_hash}\n"
                f"  Actual:   {actual_hash}"
            )

        log.info(
            "Extracting isolated Pandoc runtime: %s -> %s",
            archive_path.name,
            runtime_dir,
        )
        runtime_dir.mkdir(parents=True, exist_ok=True)

        if ext == "zip":
            import zipfile

            with zipfile.ZipFile(archive_path, "r") as zf:
                for member in zf.namelist():
                    filename = Path(member).name
                    if filename in ("pandoc", "pandoc.exe"):
                        target_file = (
                            (runtime_dir / "bin" / filename)
                            if system != "windows"
                            else (runtime_dir / filename)
                        )
                        target_file.parent.mkdir(parents=True, exist_ok=True)
                        with zf.open(member) as src, open(target_file, "wb") as dst:
                            shutil.copyfileobj(src, dst)
                        target_file.chmod(0o755)
                        if system == "darwin":
                            subprocess.run(
                                [
                                    "xattr",
                                    "-dr",
                                    "com.apple.quarantine",
                                    str(runtime_dir),
                                ],
                                capture_output=True,
                            )
                        stamp_file.write_text(actual_hash, encoding="utf-8")
                        return str(target_file.resolve())
        else:
            import tarfile

            with tarfile.open(archive_path, "r:gz") as tf:
                for member in tf.getmembers():
                    filename = Path(member.name).name
                    if filename == "pandoc":
                        target_file = runtime_dir / "bin" / "pandoc"
                        target_file.parent.mkdir(parents=True, exist_ok=True)
                        src = tf.extractfile(member)
                        if src:
                            with open(target_file, "wb") as dst:
                                shutil.copyfileobj(src, dst)
                            target_file.chmod(0o755)
                            if system == "darwin":
                                subprocess.run(
                                    [
                                        "xattr",
                                        "-dr",
                                        "com.apple.quarantine",
                                        str(runtime_dir),
                                    ],
                                    capture_output=True,
                                )
                            stamp_file.write_text(actual_hash, encoding="utf-8")
                            return str(target_file.resolve())

    sys_pandoc = shutil.which("pandoc")
    if sys_pandoc:
        return sys_pandoc

    raise FileNotFoundError(
        f"Pandoc executable not found on host and archive missing at {archive_path}"
    )


def compute_file_hash(path: Path) -> str:
    hasher = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()
    except OSError:
        return ""


def compute_global_dependencies_hash(bibliography_file: Optional[Path] = None) -> str:
    hasher = hashlib.sha256()
    tracked = [DEFAULTS_YAML, LUA_FILTER, DEFAULT_TEMPLATE, Path(__file__).resolve()]
    if bibliography_file and bibliography_file.is_file():
        tracked.append(bibliography_file)

    for f in tracked:
        if f.is_file():
            hasher.update(f.name.encode("utf-8"))
            hasher.update(compute_file_hash(f).encode("utf-8"))
    return hasher.hexdigest()


def compute_passphrase_fingerprint(passphrase: str) -> str:
    salt = b"kykloi:key_rotation_fingerprint:v1"
    return hashlib.sha256(salt + passphrase.encode("utf-8")).hexdigest()


def derive_key(passphrase: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac(
        "sha256", passphrase.encode("utf-8"), salt, 100_000, dklen=32
    )


def encrypt_payload(html_content: str, passphrase: str) -> str:
    salt = os.urandom(16)
    iv = os.urandom(12)
    key = derive_key(passphrase, salt)
    pt_bytes = html_content.encode("utf-8")
    ciphertext, tag = aes_gcm_encrypt(key, iv, pt_bytes)
    envelope = salt + iv + ciphertext + tag
    return base64.b64encode(envelope).decode("ascii")


def encrypt_binary_file(src_path: Path, dst_path: Path, passphrase: str) -> None:
    with open(src_path, "rb") as f:
        plaintext = f.read()

    salt = os.urandom(16)
    iv = os.urandom(12)
    key = derive_key(passphrase, salt)
    ciphertext, tag = aes_gcm_encrypt(key, iv, plaintext)
    envelope = salt + iv + ciphertext + tag

    dst_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = dst_path.with_suffix(dst_path.suffix + ".tmp")
    with open(tmp_path, "wb") as f:
        f.write(envelope)
    tmp_path.replace(dst_path)


def load_manifest(manifest_path: Path) -> dict:
    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def save_manifest(manifest_path: Path, manifest: dict, dry_run: bool):
    if dry_run:
        return
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = manifest_path.with_suffix(".json.tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
    tmp_path.replace(manifest_path)


# ===========================================================================
# 6. FRONTMATTER & METADATA-ONLY SQLITE FTS5
# ===========================================================================


def parse_frontmatter_robust(text: str) -> dict:
    if not text.startswith("---"):
        return {}

    lines = text.splitlines()
    yaml_lines = []
    for line in lines[1:]:
        if line.strip() in ("---", "..."):
            break
        yaml_lines.append(line)

    result = {}
    current_key = None
    multiline_mode = None
    multiline_accumulator = []

    def commit_multiline():
        nonlocal current_key, multiline_mode, multiline_accumulator
        if current_key and multiline_mode:
            val = (
                "\n".join(multiline_accumulator)
                if multiline_mode == "|"
                else " ".join(" ".join(multiline_accumulator).split())
            )
            result[current_key] = val
        multiline_mode = None
        multiline_accumulator = []

    for line in yaml_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip())

        if multiline_mode and indent > 0:
            multiline_accumulator.append(stripped)
            continue
        elif multiline_mode and indent == 0:
            commit_multiline()

        if stripped.startswith("- ") and current_key:
            item = stripped[2:].strip().strip("'\"")
            if not isinstance(result.get(current_key), list):
                result[current_key] = []
            result[current_key].append(item)
            continue

        if ":" in stripped:
            key, raw_val = stripped.split(":", 1)
            key = key.strip()
            raw_val = raw_val.strip()
            current_key = key

            if raw_val in ("|", ">"):
                multiline_mode = raw_val
                multiline_accumulator = []
                continue

            if raw_val.startswith("[") and raw_val.endswith("]"):
                inner = raw_val[1:-1].strip()
                result[key] = (
                    [x.strip().strip("'\"") for x in inner.split(",") if x.strip()]
                    if inner
                    else []
                )
                continue

            if (raw_val.startswith('"') and raw_val.endswith('"')) or (
                raw_val.startswith("'") and raw_val.endswith("'")
            ):
                raw_val = raw_val[1:-1]

            result[key] = raw_val

    commit_multiline()
    return result


def extract_metadata_fast(md_path: Path) -> tuple[Path, dict[str, str], bool]:
    meta = {"title": "", "keywords": "", "date_edtf": ""}
    has_citations = False
    try:
        with open(md_path, "r", encoding="utf-8") as f:
            full_content = f.read()

        parsed = parse_frontmatter_robust(full_content)
        meta["title"] = str(parsed.get("title", "")).strip()
        meta["date_edtf"] = str(
            parsed.get("date_edtf") or parsed.get("date", "")
        ).strip()

        keywords_val = parsed.get("keywords", "")
        if isinstance(keywords_val, list):
            meta["keywords"] = " ".join(str(k).strip() for k in keywords_val)
        elif isinstance(keywords_val, str):
            meta["keywords"] = keywords_val.strip()

        has_citations = bool(CITATION_PATTERN.search(full_content))

    except OSError as err:
        get_logger("frontmatter").warning("Error reading %s: %s", md_path.name, err)

    if not meta["title"]:
        clean_stem = md_path.stem
        ts_match = re.match(r"^(\d{8}|\d{12}|\d{14})[-_\s]+(.+)$", clean_stem)
        if ts_match:
            clean_stem = ts_match.group(2)
        meta["title"] = clean_stem.replace("-", " ").replace("_", " ").title()

    return md_path, meta, has_citations


def build_sqlite_search_index(
    records: list[dict], out_path: Path, dry_run: bool
) -> None:
    if dry_run:
        return

    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = out_path.with_suffix(".tmp.db")
    if tmp_path.exists():
        tmp_path.unlink()

    try:
        conn = sqlite3.connect(tmp_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA page_size = 4096;")
        cursor.execute("PRAGMA journal_mode = OFF;")
        cursor.execute("PRAGMA synchronous = OFF;")

        cursor.execute(
            """
            CREATE VIRTUAL TABLE docs_fts USING fts5(
                title,
                keywords,
                date_edtf,
                url UNINDEXED,
                tokenize='porter unicode61'
            );
            """
        )

        cursor.executemany(
            """
            INSERT INTO docs_fts (title, keywords, date_edtf, url)
            VALUES (?, ?, ?, ?);
            """,
            [
                (
                    r.get("title", ""),
                    r.get("keywords", ""),
                    r.get("date_edtf", ""),
                    r.get("url", ""),
                )
                for r in records
            ],
        )

        conn.commit()
        cursor.execute("INSERT INTO docs_fts(docs_fts) VALUES('optimize');")
        conn.commit()
        cursor.execute("VACUUM;")
        conn.close()

        tmp_path.replace(out_path)
        get_logger("search").info(
            "Generated search index: %d record(s) indexed (%d bytes) at %s",
            len(records),
            out_path.stat().st_size,
            out_path.name,
        )

    except Exception:
        if tmp_path.exists():
            tmp_path.unlink()
        raise


# ===========================================================================
# 7. COMPILATION WORKERS
# ===========================================================================


def compile_markdown_worker(task: CompileTask) -> tuple[Path, bool, Optional[str]]:
    if task.dry_run:
        return task.md_path, True, None

    css_files = ["assets/css/pico.css", "assets/css/style.css"]

    if not task.is_secure:
        cmd = [
            task.pandoc_bin,
            str(task.md_path),
            "--defaults",
            str(task.defaults_yaml),
            "--template",
            str(task.template_path),
            "--lua-filter",
            str(task.lua_filter),
            "-V",
            f"relative_root={task.relative_root}",
            "-V",
            f"pagetitle={task.doc_title}",
            f"--math-method=katex:{task.relative_root}assets/katex/",
            "-o",
            str(task.out_path),
        ]
        if task.bibliography_path:
            cmd.extend(
                [
                    "--citeproc",
                    f"--bibliography={str(task.bibliography_path.resolve())}",
                ]
            )

        for css in css_files:
            cmd.extend(["--css", f"{task.relative_root}{css}"])

        task.out_path.parent.mkdir(parents=True, exist_ok=True)
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            return task.md_path, False, res.stderr.strip()
        return task.md_path, True, None

    if not task.passphrase:
        return (
            task.md_path,
            False,
            "Cannot compile secure file: No passphrase provided.",
        )

    env = os.environ.copy()
    env["KYKLOI_SECURE_BUILD"] = "1"

    body_cmd = [
        task.pandoc_bin,
        str(task.md_path),
        "--defaults",
        str(task.defaults_yaml),
        "--lua-filter",
        str(task.lua_filter),
        f"--math-method=katex:{task.relative_root}assets/katex/",
    ]
    if task.bibliography_path:
        body_cmd.extend(
            ["--citeproc", f"--bibliography={str(task.bibliography_path.resolve())}"]
        )

    body_res = subprocess.run(body_cmd, capture_output=True, text=True, env=env)
    if body_res.returncode != 0:
        return task.md_path, False, f"Body compilation error: {body_res.stderr.strip()}"

    try:
        ciphertext_b64 = encrypt_payload(body_res.stdout, task.passphrase)
    except Exception as e:
        return task.md_path, False, f"Encryption failed: {e}"

    envelope_cmd = [
        task.pandoc_bin,
        str(task.md_path),
        "--defaults",
        str(task.defaults_yaml),
        "--template",
        str(task.template_path),
        f"--math-method=katex:{task.relative_root}assets/katex/",
        "-V",
        f"relative_root={task.relative_root}",
        "-V",
        f"pagetitle={task.doc_title}",
        "-V",
        "encrypted=true",
    ]
    for css in css_files:
        envelope_cmd.extend(["--css", f"{task.relative_root}{css}"])

    envelope_res = subprocess.run(envelope_cmd, capture_output=True, text=True)
    if envelope_res.returncode != 0:
        return (
            task.md_path,
            False,
            f"Envelope generation error: {envelope_res.stderr.strip()}",
        )

    try:
        final_html = envelope_res.stdout.replace(
            "__KYKLOI_ENCRYPTED_PAYLOAD__", ciphertext_b64
        )
        task.out_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_out = task.out_path.with_suffix(task.out_path.suffix + ".tmp")
        with open(tmp_out, "w", encoding="utf-8") as f:
            f.write(final_html)
        tmp_out.replace(task.out_path)
    except OSError as e:
        return task.md_path, False, f"Disk write error: {e}"

    return task.md_path, True, None


def encrypt_blob_worker(task: EncryptBlobTask) -> tuple[Path, bool, Optional[str]]:
    if task.dry_run:
        return task.src_path, True, None

    try:
        encrypt_binary_file(task.src_path, task.dst_path, task.passphrase)
        return task.src_path, True, None
    except Exception as exc:
        return task.src_path, False, str(exc)


def prune_orphans(dst_dir: Path, expected_files: set[Path], dry_run: bool) -> int:
    if not dst_dir.exists():
        return 0

    orphans_removed = 0
    for item in list(dst_dir.rglob("*")):
        if item.is_file() and item.resolve() not in expected_files:
            if not dry_run:
                item.unlink()
            orphans_removed += 1

    for dirpath in sorted(dst_dir.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if dirpath.is_dir() and not any(dirpath.iterdir()):
            if not dry_run:
                dirpath.rmdir()

    return orphans_removed


def find_vault_bibliography(src_root: Path) -> Optional[Path]:
    for candidate in ["references.bib", "library.bib", "bibliography.bib"]:
        p = src_root / candidate
        if p.is_file():
            return p
    return None


# ===========================================================================
# 8. PIPELINE ORCHESTRATION (LEDGER INTEGRATED)
# ===========================================================================


def main():
    args = parse_args()
    log_file_path = Path(args.log_file).resolve() if args.log_file else None
    log = setup_logging(
        subsystem="compiler",
        verbose=args.verbose,
        log_file=log_file_path,
        enable_console=True,
    )

    with timed_step(
        log, "Cryptographic Self-Test (NIST AES-256-GCM KAT)", logging.DEBUG
    ):
        try:
            verify_cryptographic_engine()
            log.info("Cryptographic accelerator active: [%s]", ACTIVE_ENGINE_NAME)
        except RuntimeError as err:
            log.critical("Cryptographic verification failure: %s", err)
            sys.exit(1)

    with timed_step(log, "Pandoc Binary Resolution", logging.DEBUG):
        try:
            pandoc_bin = resolve_pandoc_binary(PROJECT_ROOT)
            log.info("Resolved Pandoc executable: %s", pandoc_bin)
        except FileNotFoundError as err:
            log.critical("Toolchain dependency error: %s", err)
            sys.exit(1)

    for path, desc in [
        (SRC, "Source directory"),
        (DEFAULTS_YAML, "Pandoc defaults configuration"),
        (DEFAULT_TEMPLATE, "Content template"),
        (LUA_FILTER, "Lua link translation filter"),
    ]:
        if not path.exists():
            log.error("Missing required pipeline dependency: %s at %s", desc, path)
            sys.exit(1)

    if args.clean:
        if DST.exists() and not args.dry_run:
            shutil.rmtree(DST)
        if MANIFEST_FILE.exists() and not args.dry_run:
            MANIFEST_FILE.unlink()

    DST.mkdir(parents=True, exist_ok=True)

    old_manifest = load_manifest(MANIFEST_FILE)
    new_manifest: dict = {}

    central_bib = find_vault_bibliography(SRC)
    current_global_hash = compute_global_dependencies_hash(central_bib)
    new_manifest["__GLOBAL_DEPENDENCIES__"] = current_global_hash
    global_deps_changed = (
        old_manifest.get("__GLOBAL_DEPENDENCIES__") != current_global_hash
    )

    if global_deps_changed:
        log.info("Core templates/toolchain modified. Triggering full re-compilation.")

    # -----------------------------------------------------------------------
    # Synchronize Vault Ledger with O(1) Stat-Cache
    # -----------------------------------------------------------------------
    with timed_step(log, "Ledger Synchronization & Fast Stat Check"):
        with VaultDB(NORM_DB_PATH) as db:
            db.init_schema()
            sync_db_with_disk(SRC, db)
            vault_records = list(db.get_all_files().values())

    md_records = [r for r in vault_records if not r.is_media]
    media_records = [r for r in vault_records if r.is_media]
    has_secure_files = any(r.is_secure for r in vault_records)

    passphrase = args.password
    if has_secure_files and not passphrase and not args.dry_run:
        if not sys.stdin.isatty():
            log.error(
                "Passphrase required for /secure/ notes in non-interactive environment. "
                "Provide --password or set KYKLOI_ENCRYPT_KEY."
            )
            sys.exit(1)

        try:
            passphrase = getpass.getpass("Enter passphrase for /secure/ notes: ")
        except (OSError, EOFError):
            log.error("Terminal disconnected: Unable to prompt for passphrase.")
            sys.exit(1)

        if not passphrase:
            log.error("Passphrase required for secure notes.")
            sys.exit(1)

    passphrase_changed = False
    if has_secure_files and passphrase:
        current_key_fingerprint = compute_passphrase_fingerprint(passphrase)
        new_manifest["__PASSPHRASE_FINGERPRINT__"] = current_key_fingerprint
        old_key_fingerprint = old_manifest.get("__PASSPHRASE_FINGERPRINT__")
        if old_manifest and old_key_fingerprint != current_key_fingerprint:
            passphrase_changed = True
            log.info(
                "Passphrase rotation detected. Invalidating encrypted document cache."
            )

    expected_outputs: set[Path] = set()
    compile_tasks: list[CompileTask] = []
    encrypt_blob_tasks: list[EncryptBlobTask] = []
    asset_sync_jobs: list[tuple[Path, Path]] = []

    # -----------------------------------------------------------------------
    # Media & Binary Assets Dispatch (Zero Redundant Hashing)
    # -----------------------------------------------------------------------
    for rec in media_records:
        src_path = SRC / rec.rel_path
        rel_posix = Path(rec.rel_path)

        if rec.is_secure:
            target = DST / rel_posix.with_name(rel_posix.name + ".enc")
            expected_outputs.add(target.resolve())
            manifest_key = f"secure_blob:{rec.rel_path}"
            new_manifest[manifest_key] = rec.sha256

            if (
                not target.exists()
                or passphrase_changed
                or old_manifest.get(manifest_key) != rec.sha256
            ):
                encrypt_blob_tasks.append(
                    EncryptBlobTask(
                        src_path=src_path,
                        dst_path=target,
                        passphrase=passphrase or "",
                        dry_run=args.dry_run,
                    )
                )
        else:
            target = DST / rel_posix
            expected_outputs.add(target.resolve())
            manifest_key = f"media:{rec.rel_path}"
            new_manifest[manifest_key] = rec.sha256

            if not target.exists() or old_manifest.get(manifest_key) != rec.sha256:
                asset_sync_jobs.append((src_path, target))

    # -----------------------------------------------------------------------
    # Markdown Documents Dispatch (Zero Redundant Hashing)
    # -----------------------------------------------------------------------
    metadata_extraction_jobs: list[Path] = []
    file_metadata_map: dict[Path, dict[str, str]] = {}
    doc_has_citations_map: dict[Path, bool] = {}

    for rec in md_records:
        src_path = SRC / rec.rel_path
        rel = Path(rec.rel_path)
        manifest_key = f"content:{rec.rel_path}"
        meta_cache_key = f"meta:{rec.rel_path}"
        out = DST / rel.with_suffix(".html")
        expected_outputs.add(out.resolve())

        new_manifest[manifest_key] = rec.sha256

        depth = len(rel.parent.parts) if rel.parent != Path(".") else 0
        relative_root = ("../" * depth) if depth > 0 else ""

        md_content_changed = old_manifest.get(manifest_key) != rec.sha256

        is_dirty = (
            not out.exists()
            or global_deps_changed
            or md_content_changed
            or (rec.is_secure and passphrase_changed)
        )

        cached_meta = old_manifest.get(meta_cache_key)
        meta_is_dirty = (
            global_deps_changed
            or md_content_changed
            or not isinstance(cached_meta, dict)
        )

        if not meta_is_dirty and isinstance(cached_meta, dict):
            file_metadata_map[src_path] = cached_meta
            doc_has_citations_map[src_path] = cached_meta.get(
                "__has_citations__", False
            )
            new_manifest[meta_cache_key] = cached_meta
        else:
            metadata_extraction_jobs.append(src_path)

        if is_dirty:
            compile_tasks.append(
                CompileTask(
                    md_path=src_path,
                    out_path=out,
                    template_path=DEFAULT_TEMPLATE,
                    relative_root=relative_root,
                    doc_title="",
                    defaults_yaml=DEFAULTS_YAML,
                    lua_filter=LUA_FILTER,
                    bibliography_path=None,
                    is_secure=rec.is_secure,
                    passphrase=passphrase,
                    dry_run=args.dry_run,
                    pandoc_bin=pandoc_bin,
                )
            )

    if metadata_extraction_jobs:
        for md_path in metadata_extraction_jobs:
            _, extracted_meta, has_cites = extract_metadata_fast(md_path)
            extracted_meta["__has_citations__"] = has_cites
            file_metadata_map[md_path] = extracted_meta
            doc_has_citations_map[md_path] = has_cites
            rel_str = md_path.relative_to(SRC).as_posix()
            new_manifest[f"meta:{rel_str}"] = extracted_meta

    final_compile_tasks: list[CompileTask] = []
    for t in compile_tasks:
        needs_bib = (
            central_bib
            if (central_bib and doc_has_citations_map.get(t.md_path, False))
            else None
        )
        meta = file_metadata_map[t.md_path]
        final_compile_tasks.append(
            CompileTask(
                md_path=t.md_path,
                out_path=t.out_path,
                template_path=t.template_path,
                relative_root=t.relative_root,
                doc_title=meta["title"],
                defaults_yaml=t.defaults_yaml,
                lua_filter=t.lua_filter,
                bibliography_path=needs_bib,
                is_secure=t.is_secure,
                passphrase=t.passphrase,
                dry_run=t.dry_run,
                pandoc_bin=pandoc_bin,
            )
        )
    compile_tasks = final_compile_tasks

    # -----------------------------------------------------------------------
    # Search Records Generation
    # -----------------------------------------------------------------------
    search_records: list[dict] = []
    for idx, rec in enumerate(md_records):
        src_path = SRC / rec.rel_path
        raw_url = Path(rec.rel_path).with_suffix(".html").as_posix().lstrip("/")
        clean_url = urllib.parse.quote(raw_url, safe="/")
        meta = file_metadata_map[src_path]
        search_records.append(
            {
                "id": idx + 1,
                "title": meta["title"],
                "keywords": meta["keywords"],
                "date_edtf": meta["date_edtf"],
                "url": clean_url,
            }
        )

    expected_outputs.add(SEARCH_DB_FILE.resolve())

    # -----------------------------------------------------------------------
    # Static Assets Sync (UI Functional & Root Icons)
    # -----------------------------------------------------------------------
    for folder_name, manifest_prefix in [
        ("assets", "functional_asset"),
        ("root", "root_asset"),
    ]:
        src_dir = APP_DIR / folder_name
        if not src_dir.exists():
            continue
        for p in src_dir.rglob("*"):
            if p.is_file() and not is_junk_path(p, src_dir):
                rel_p = p.relative_to(src_dir)
                target = DST / ("assets" / rel_p if folder_name == "assets" else rel_p)
                expected_outputs.add(target.resolve())
                manifest_key = f"{manifest_prefix}:{rel_p.as_posix()}"
                h = compute_file_hash(p)
                new_manifest[manifest_key] = h
                if not target.exists() or old_manifest.get(manifest_key) != h:
                    asset_sync_jobs.append((p, target))

    with timed_step(log, "Artifact Pruning", logging.DEBUG):
        orphans_pruned = prune_orphans(
            dst_dir=DST, expected_files=expected_outputs, dry_run=args.dry_run
        )
        if orphans_pruned:
            log.info("Pruned %d orphaned artifact(s) from target.", orphans_pruned)

    if asset_sync_jobs:
        log.info("Synchronizing %d static/media asset(s)...", len(asset_sync_jobs))
        for src_file, target_file in asset_sync_jobs:
            if not args.dry_run:
                target_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, target_file)
            log.debug("Synchronized asset: %s -> %s", src_file.name, target_file.name)

    failed = 0
    mp_context = multiprocessing.get_context("spawn")

    if encrypt_blob_tasks:
        log.info("Encrypting %d binary blob(s)...", len(encrypt_blob_tasks))
        with timed_step(
            log, f"Binary Blob Encryption ({len(encrypt_blob_tasks)} items)"
        ):
            with concurrent.futures.ProcessPoolExecutor(
                max_workers=args.workers, mp_context=mp_context
            ) as executor:
                futures = [
                    executor.submit(encrypt_blob_worker, t) for t in encrypt_blob_tasks
                ]
                for future in concurrent.futures.as_completed(futures):
                    path, ok, err = future.result()
                    if not ok:
                        failed += 1
                        log.error("Failed to encrypt blob %s: %s", path.name, err)
                    else:
                        log.debug("Encrypted binary asset: %s", path.name)

    if compile_tasks:
        log.info("Compiling %d Markdown document(s)...", len(compile_tasks))
        with timed_step(log, f"Markdown Compilation ({len(compile_tasks)} documents)"):
            with concurrent.futures.ProcessPoolExecutor(
                max_workers=args.workers, mp_context=mp_context
            ) as executor:
                futures = [
                    executor.submit(compile_markdown_worker, t) for t in compile_tasks
                ]
                for future in concurrent.futures.as_completed(futures):
                    path, ok, err = future.result()
                    if not ok:
                        failed += 1
                        log.error("Compilation error in %s: %s", path.name, err)
                    else:
                        log.debug("Compiled: %s", path.name)
    else:
        log.info(
            "Document compilation cache hit. All %d documents are up-to-date.",
            len(md_records),
        )

    if failed == 0:
        search_index_needed = (
            not SEARCH_DB_FILE.exists()
            or bool(metadata_extraction_jobs)
            or orphans_pruned > 0
        )
        if search_index_needed:
            build_sqlite_search_index(
                search_records, SEARCH_DB_FILE, dry_run=args.dry_run
            )
            if SEARCH_DB_FILE.exists() and not args.dry_run:
                new_manifest["__SEARCH_DB_HASH__"] = compute_file_hash(SEARCH_DB_FILE)
        else:
            new_manifest["__SEARCH_DB_HASH__"] = old_manifest.get(
                "__SEARCH_DB_HASH__", ""
            )

        save_manifest(MANIFEST_FILE, new_manifest, args.dry_run)
        log.info("Build pipeline completed successfully.")
    else:
        log.error(
            "Build failed with %d error(s). Build manifest retained in prior state.",
            failed,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
```

## system/build/html-config.yaml

```yaml
from: markdown+mark+task_lists
to: html
wrap: none
section-divs: true
eol: lf
default-image-extension: .jpg
variables:
  document-css: false
  title: false
```

## system/build/translate-links.lua

```lua
local is_secure = os.getenv("KYKLOI_SECURE_BUILD") == "1"

local function is_external(url)
  return url:match("^%a+://") ~= nil or url:match("^//") ~= nil or url:match("^mailto:") ~= nil
end

function Link(el)
  -- Bypass external protocols and pure in-page anchors immediately
  if is_external(el.target) or el.target:sub(1, 1) == "#" or el.target:sub(1, 1) == "?" then
    return el
  end

  local path, separator, suffix = el.target:match("^([^#?]+)([#?])(.*)$")
  if not path then
    path = el.target
    separator = ""
    suffix = ""
  end

  -- If path component is empty, it is an in-page query or fragment
  if path == "" then
    return el
  end

  local ext = path:match("%.([a-zA-Z0-9]+)$")
  if ext then
    local lower_ext = ext:lower()
    if lower_ext == "md" or lower_ext == "markdown" then
      path = path:sub(1, -#ext - 2) .. ".html"
      el.target = path .. separator .. suffix
    end
  end

  return el
end

function Image(el)
  if not is_secure or is_external(el.src) or el.src:match("^data:") then
    return el
  end

  local path, separator, suffix = el.src:match("^([^#?]+)([#?])(.*)$")
  if not path then
    path = el.src
    separator = ""
    suffix = ""
  end

  if not path:match("%.enc$") then
    path = path .. ".enc"
    el.src = path .. separator .. suffix
  end

  el.attributes["data-encrypted-media"] = "true"
  return el
end
```

## system/normalize/__init__.py

```python
"""
system/normalize - Content Normalization and Link Reconciliation Engine.
Part of Project Kykloi.
"""

from .cli import (
    TransactionManifest,
    build_transaction_manifest,
    execute_transaction,
    main,
    sync_db_with_disk,
)
from .db import FileRecord, LinkRecord, VaultDB
from .engine import (
    ActionType,
    DiffPlan,
    FileAction,
    compute_diff,
    resolve_collision_stem,
)
from .graph import (
    ExtractedLink,
    compute_relative_link,
    extract_stem_from_path,
    heal_markdown_links,
    is_external_or_anchor,
    parse_markdown_links,
    split_target_url,
    to_link_records,
)
from .scanner import ScannedFile, VaultScanResult, is_junk_path, scan_vault
from .slugify import is_valid_stem, sanitize_path_segments, slugify_stem

__all__ = [
    "VaultDB",
    "FileRecord",
    "LinkRecord",
    "slugify_stem",
    "is_valid_stem",
    "sanitize_path_segments",
    "scan_vault",
    "is_junk_path",
    "ScannedFile",
    "VaultScanResult",
    "compute_diff",
    "DiffPlan",
    "FileAction",
    "ActionType",
    "resolve_collision_stem",
    "ExtractedLink",
    "parse_markdown_links",
    "to_link_records",
    "compute_relative_link",
    "heal_markdown_links",
    "split_target_url",
    "extract_stem_from_path",
    "is_external_or_anchor",
    "TransactionManifest",
    "build_transaction_manifest",
    "execute_transaction",
    "sync_db_with_disk",
    "main",
]
```

## system/normalize/cli.py

```python
# system/normalize/cli.py
"""
system/normalize/cli.py
"""

import argparse
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from system.normalize.db import FileRecord, VaultDB
from system.normalize.engine import ActionType, DiffPlan, compute_diff
from system.normalize.graph import (
    heal_markdown_links,
    parse_markdown_links,
    to_link_records,
)
from system.normalize.scanner import MARKDOWN_EXTENSIONS, scan_vault
from system.normalize.slugify import slugify_stem

# Terminal ANSI Color Constants
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"


class ContentBoundaryError(RuntimeError):
    """Raised when an operation attempts to target files outside content_root."""

    pass


def assert_within_content_root(target_path: Path, content_root: Path):
    """Enforces the strict boundary invariant: operations must stay inside content_root."""
    try:
        target_path.resolve().relative_to(content_root.resolve())
    except ValueError:
        raise ContentBoundaryError(
            f"Security Violation: Target path '{target_path}' lies outside vault root '{content_root}'."
        )


@dataclass
class TransactionManifest:
    """Discrete list of disk and ledger mutations staged for atomic execution."""

    disk_renames: List[Tuple[Path, Path]] = field(
        default_factory=list
    )  # (src_abs, dst_abs)
    text_rewrites: List[Tuple[Path, str]] = field(
        default_factory=list
    )  # (file_abs, new_content)
    files_to_upsert: List[FileRecord] = field(default_factory=list)
    files_to_delete: List[str] = field(default_factory=list)
    links_to_replace: Dict[str, list] = field(default_factory=dict)

    @property
    def has_changes(self) -> bool:
        return bool(
            self.disk_renames
            or self.text_rewrites
            or self.files_to_upsert
            or self.files_to_delete
            or self.links_to_replace
        )


def build_transaction_manifest(
    content_root: Path,
    diff_plan: DiffPlan,
    db: VaultDB,
) -> Tuple[TransactionManifest, List[str]]:
    """
    Translates a DiffPlan into an executable TransactionManifest.
    Plans all disk renames, path sanitizations, content link healing, and SQLite updates.
    """
    content_root = content_root.resolve()
    manifest = TransactionManifest()
    diagnostics: List[str] = []

    stem_to_new_rel_path: Dict[str, str] = {}

    for action in diff_plan.actions:
        if action.action_type in (
            ActionType.MOVE,
            ActionType.RENAME,
            ActionType.MOVE_AND_RENAME,
            ActionType.SANITIZE_STEM,
            ActionType.SANITIZE_PATH,
            ActionType.RESOLVE_COLLISION,
        ):
            if action.src_rel_path and action.dst_rel_path and action.old_stem:
                src_abs = (content_root / action.src_rel_path).resolve()
                dst_abs = (content_root / action.dst_rel_path).resolve()

                # Boundary invariant verification
                assert_within_content_root(src_abs, content_root)
                assert_within_content_root(dst_abs, content_root)

                manifest.disk_renames.append((src_abs, dst_abs))

                stem_to_new_rel_path[action.old_stem] = action.dst_rel_path
                stem_to_new_rel_path[slugify_stem(action.old_stem)] = (
                    action.dst_rel_path
                )
                if action.new_stem:
                    stem_to_new_rel_path[action.new_stem] = action.dst_rel_path
                    stem_to_new_rel_path[slugify_stem(action.new_stem)] = (
                        action.dst_rel_path
                    )

    # Evaluate all Markdown files on disk for link healing
    for item in content_root.rglob("*"):
        if (
            item.is_symlink()
            or not item.is_file()
            or item.suffix.lower() not in MARKDOWN_EXTENSIONS
        ):
            continue

        try:
            rel_path = item.relative_to(content_root).as_posix()
        except ValueError:
            continue

        try:
            content = item.read_text(encoding="utf-8")
        except OSError:
            continue

        healed_content, rewrites = heal_markdown_links(
            content=content,
            source_rel_path=rel_path,
            stem_to_new_rel_path=stem_to_new_rel_path,
        )

        if rewrites > 0 and healed_content != content:
            item_resolved = item.resolve()
            assert_within_content_root(item_resolved, content_root)
            manifest.text_rewrites.append((item_resolved, healed_content))

    return manifest, diagnostics


def prune_empty_directories(content_root: Path):
    """Recursively removes empty directory branches left behind after file renames, strictly within content_root."""
    content_root = content_root.resolve()
    for root, dirs, _ in os.walk(content_root, topdown=False):
        for d in dirs:
            dir_path = (Path(root) / d).resolve()
            if dir_path == content_root:
                continue
            try:
                assert_within_content_root(dir_path, content_root)
                if not any(dir_path.iterdir()):
                    dir_path.rmdir()
            except (OSError, ContentBoundaryError):
                pass


def execute_transaction(manifest: TransactionManifest, db: VaultDB) -> bool:
    """
    Applies the manifest atomically with rollback journaling.
    Phase 1: Stage text rewrites to .norm_tmp files.
    Phase 2: Apply renames in order, journaling executed steps.
    Phase 3: Atomically commit text rewrites via rename.
    """
    executed_renames: List[Tuple[Path, Path]] = []
    created_tmp_files: List[Path] = []

    try:
        # Phase 1: Stage text rewrites
        for abs_path, new_content in manifest.text_rewrites:
            tmp_path = abs_path.with_suffix(abs_path.suffix + ".norm_tmp")
            tmp_path.write_text(new_content, encoding="utf-8")
            created_tmp_files.append(tmp_path)

            # Phase 2: Execute disk renames
            for src, dst in manifest.disk_renames:
                if src == dst:
                    continue
                dst.parent.mkdir(parents=True, exist_ok=True)
                if src.parent == dst.parent and src.name.lower() == dst.name.lower():
                    case_tmp = (
                        dst.parent / f".norm_case_tmp_{os.urandom(4).hex()}_{dst.name}"
                    )
                    try:
                        src.rename(case_tmp)
                        case_tmp.rename(dst)
                    except Exception:
                        if case_tmp.exists() and not src.exists():
                            case_tmp.rename(src)
                        raise
                else:
                    src.rename(dst)
                executed_renames.append((dst, src))

        # Phase 3: Atomically swap text rewrites
        for abs_path, _ in manifest.text_rewrites:
            tmp_path = abs_path.with_suffix(abs_path.suffix + ".norm_tmp")
            tmp_path.replace(abs_path)
            if tmp_path in created_tmp_files:
                created_tmp_files.remove(tmp_path)

        return True

    except Exception as err:
        print(
            f"\n{RED}[FATAL] Error during execution: {err}. Initiating rollback...{RESET}",
            file=sys.stderr,
        )

        for tmp_file in created_tmp_files:
            try:
                if tmp_file.exists():
                    tmp_file.unlink()
            except OSError:
                pass

        for applied_dst, original_src in reversed(executed_renames):
            try:
                if applied_dst.exists():
                    original_src.parent.mkdir(parents=True, exist_ok=True)
                    if (
                        applied_dst.parent == original_src.parent
                        and applied_dst.name.lower() == original_src.name.lower()
                    ):
                        case_tmp = (
                            original_src.parent
                            / f".norm_rb_tmp_{os.urandom(4).hex()}_{original_src.name}"
                        )
                        applied_dst.rename(case_tmp)
                        case_tmp.rename(original_src)
                    else:
                        applied_dst.rename(original_src)
            except OSError as rb_err:
                print(
                    f"{RED}[CRITICAL] Failed to rollback {applied_dst} -> {original_src}: {rb_err}{RESET}",
                    file=sys.stderr,
                )

        print(
            f"{YELLOW}[ROLLBACK COMPLETE] Vault state restored.{RESET}", file=sys.stderr
        )
        raise


def sync_db_with_disk(content_root: Path, db: VaultDB):
    """Refreshes the SQLite ledger to match physical disk state after execution."""
    scan_res = scan_vault(content_root, db)
    current_paths = {f.rel_path for f in scan_res.files}
    current_canonicals = {f.canonical_filename for f in scan_res.files}

    for rel_path, rec in db.get_all_files().items():
        if rel_path not in current_paths:
            db.delete_file_by_path(rel_path)

    for f in scan_res.files:
        db.upsert_file(
            FileRecord(
                id=None,
                canonical_filename=f.canonical_filename,
                stem=f.stem,
                ext=f.ext,
                rel_path=f.rel_path,
                sha256=f.sha256,
                mtime=f.mtime,
                size=f.size,
                is_media=f.is_media,
                is_secure=f.is_secure,
            )
        )
        if not f.is_media and f.ext in MARKDOWN_EXTENSIONS:
            try:
                content = f.abs_path.read_text(encoding="utf-8")
                extracted = parse_markdown_links(content, f.canonical_filename)
                valid_links = [
                    l for l in extracted if l.target_canonical in current_canonicals
                ]
                db.replace_document_links(
                    f.canonical_filename, to_link_records(valid_links)
                )
            except OSError:
                pass


def audit_security_boundaries(
    scan_result: VaultScanResult,
) -> List[Tuple[str, str, int, str]]:
    """
    Validates media isolation boundaries between secure and public contexts.
    Cross-context document hyperlinks (Markdown -> Markdown) are permitted.
    Cross-context media embeds (e.g. secure note embedding public image or vice-versa)
    are flagged as fatal violations due to encryption runtime constraints.
    """
    violations = []
    canonical_map = {f.canonical_filename: f for f in scan_result.files}
    stem_map = {f.stem: f for f in scan_result.files if not f.is_media}

    for f in scan_result.files:
        if f.is_media or f.ext not in MARKDOWN_EXTENSIONS:
            continue
        try:
            content = f.abs_path.read_text(encoding="utf-8")
            links = parse_markdown_links(content, f.canonical_filename)
            for link in links:
                target_file = canonical_map.get(link.target_canonical)
                if not target_file:
                    target_file = stem_map.get(link.target_stem)

                if not target_file:
                    continue

                # Document-to-document navigation across boundaries is permitted.
                # Only enforce boundary separation on media asset embeds.
                if (
                    link.is_image or target_file.is_media
                ) and target_file.is_secure != f.is_secure:
                    s_ctx = "SECURE" if f.is_secure else "PUBLIC"
                    t_ctx = "SECURE" if target_file.is_secure else "PUBLIC"
                    violations.append(
                        (
                            f.rel_path,
                            target_file.rel_path,
                            link.line_number,
                            f"{s_ctx} document embeds {t_ctx} media asset",
                        )
                    )
        except OSError:
            pass

    return violations


def print_diff_report(
    diff_plan: DiffPlan,
    manifest: TransactionManifest,
    scan_time_ms: float,
    boundary_violations: List[Tuple[str, str, int, str]],
):
    """Outputs an ANSI-colorized summary table of planned mutations."""
    print(f"\n{BOLD}{CYAN}=== Kykloi Content Normalization Plan ==={RESET}")
    print(f"{DIM}Scan duration: {scan_time_ms:.2f} ms{RESET}\n")

    if boundary_violations:
        print(f"{BOLD}{RED}CRITICAL SECURITY BOUNDARY VIOLATIONS:{RESET}")
        for src, tgt, line, reason in boundary_violations:
            print(f"  {RED}[!] {src}:{line} -> {tgt} ({reason}){RESET}")
        print(
            f"\n  {YELLOW}Resolve security context mismatches by moving/duplicating assets.{RESET}\n"
        )

    if diff_plan.collisions:
        print(f"{BOLD}{RED}CRITICAL ANOMALIES (Filename Collisions Detected):{RESET}")
        for fname, paths in diff_plan.collisions.items():
            print(f"  {RED}Filename collision on '{fname}':{RESET}")
            for p in paths:
                print(f"    - {p}")
        print()

    mutations = [a for a in diff_plan.actions if a.action_type != ActionType.NOOP]

    if not mutations and not manifest.text_rewrites:
        print(f"{GREEN}[+] Vault is fully canonical. Zero mutations required.{RESET}\n")
        return

    print(f"{BOLD}{'Action':<18} {'Details':<60}{RESET}")
    print(f"{DIM}{'-' * 78}{RESET}")

    for a in mutations:
        color = YELLOW
        if a.action_type in (ActionType.SANITIZE_STEM, ActionType.SANITIZE_PATH):
            color = MAGENTA
        elif a.action_type == ActionType.CREATE:
            color = GREEN
        elif a.action_type == ActionType.DELETE:
            color = RED

        label = f"{color}{a.action_type.name:<18}{RESET}"
        if a.src_rel_path and a.dst_rel_path:
            details = f"{a.src_rel_path} -> {a.dst_rel_path}"
        elif a.dst_rel_path:
            details = a.dst_rel_path
        else:
            details = a.src_rel_path or ""
        print(f"{label} {details}")

    if manifest.text_rewrites:
        for p, _ in manifest.text_rewrites:
            label = f"{CYAN}{'HEAL_LINKS':<18}{RESET}"
            print(f"{label} Rewriting relative link targets in {p.name}")

    print(f"{DIM}{'-' * 78}{RESET}")
    print(
        f"Summary: {BOLD}{len(manifest.disk_renames)}{RESET} file rename(s), "
        f"{BOLD}{len(manifest.text_rewrites)}{RESET} document(s) with healed links.\n"
    )


def run_normalization_pipeline(
    content_root: Path,
    db_path: Path,
    dry_run: bool = False,
    auto_apply: bool = False,
    check_only: bool = False,
) -> int:
    """
    Programmatic entry point for running normalization.
    Returns:
      0 on success (or clean in check mode),
      1 on pending mutations (in check mode) or collision / error.
    """
    content_root = content_root.resolve()
    db_path = db_path.resolve()

    if not content_root.exists() or not content_root.is_dir():
        print(
            f"{RED}[FATAL] Content directory not found: {content_root}{RESET}",
            file=sys.stderr,
        )
        return 1

    t0 = time.perf_counter()
    with VaultDB(db_path) as db:
        db.init_schema()

        scan_result = scan_vault(content_root, db)
        boundary_violations = audit_security_boundaries(scan_result)
        diff_plan = compute_diff(scan_result, db)
        manifest, _ = build_transaction_manifest(content_root, diff_plan, db)
        scan_time_ms = (time.perf_counter() - t0) * 1000.0

        print_diff_report(diff_plan, manifest, scan_time_ms, boundary_violations)

        if boundary_violations:
            print(
                f"{RED}[FATAL] Execution halted: {len(boundary_violations)} security boundary violation(s) must be manually resolved.{RESET}\n",
                file=sys.stderr,
            )
            return 1

        has_work = manifest.has_changes or diff_plan.has_mutations

        if check_only:
            return 1 if (has_work or diff_plan.collisions) else 0

        if dry_run or not has_work:
            return 0

        if not auto_apply:
            if not sys.stdin.isatty():
                print(
                    f"{RED}[ERROR] Non-interactive environment. Re-run with --check or --auto-apply.{RESET}",
                    file=sys.stderr,
                )
                return 1

            try:
                answer = (
                    input(
                        f"{BOLD}Apply these transformations to disk and database? [y/N]: {RESET}"
                    )
                    .strip()
                    .lower()
                )
            except (KeyboardInterrupt, EOFError):
                print(f"\n{YELLOW}Aborted by user.{RESET}")
                return 1

            if answer not in ("y", "yes"):
                print(
                    f"{YELLOW}Operation cancelled. Zero modifications written.{RESET}"
                )
                return 0

        execute_transaction(manifest, db)
        prune_empty_directories(content_root)
        sync_db_with_disk(content_root, db)
        print(
            f"{GREEN}[SUCCESS] Transformations applied and ledger synchronized successfully.{RESET}"
        )
        return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deterministic Content Normalizer & Link Reconciler for Project Kykloi."
    )
    parser.add_argument(
        "--vault-dir",
        type=Path,
        default=PROJECT_ROOT / "content",
        help="Path to content vault directory (default: content/)",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=SCRIPT_DIR / "vault-index.db",
        help="Path to SQLite acceleration ledger (default: system/normalize/vault-index.db)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Lint mode: Exits with code 0 if vault is clean, 1 if mutations are planned.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate scan and report planned transformations without writing to disk.",
    )
    parser.add_argument(
        "--auto-apply",
        action="store_true",
        help="Apply planned transformations automatically without prompting.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    code = run_normalization_pipeline(
        content_root=args.vault_dir,
        db_path=args.db_path,
        dry_run=args.dry_run,
        auto_apply=args.auto_apply,
        check_only=args.check,
    )
    sys.exit(code)


if __name__ == "__main__":
    main()
```

## system/normalize/db.py

```python
"""
system/normalize/db.py - SQLite Ledger & Stat-Cache Acceleration Layer.
Stores the master file registry, link dependencies, and schema state.
"""

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

SCHEMA_VERSION = "2.0"

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;

CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    canonical_filename TEXT UNIQUE NOT NULL,
    stem TEXT NOT NULL,
    ext TEXT NOT NULL,
    rel_path TEXT UNIQUE NOT NULL,
    sha256 TEXT NOT NULL,
    mtime REAL NOT NULL,
    size INTEGER NOT NULL,
    is_media INTEGER NOT NULL DEFAULT 0,
    is_secure INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_files_canonical ON files(canonical_filename);
CREATE INDEX IF NOT EXISTS idx_files_stem ON files(stem);
CREATE INDEX IF NOT EXISTS idx_files_sha256 ON files(sha256);
CREATE INDEX IF NOT EXISTS idx_files_rel_path ON files(rel_path);

CREATE TABLE IF NOT EXISTS links (
    source_canonical TEXT NOT NULL,
    target_canonical TEXT NOT NULL,
    raw_target TEXT NOT NULL,
    line_number INTEGER,
    FOREIGN KEY(source_canonical) REFERENCES files(canonical_filename) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_links_target ON links(target_canonical);
CREATE INDEX IF NOT EXISTS idx_links_source ON links(source_canonical);
"""


@dataclass(frozen=True)
class FileRecord:
    id: Optional[int]
    canonical_filename: str
    stem: str
    ext: str
    rel_path: str
    sha256: str
    mtime: float
    size: int
    is_media: bool
    is_secure: bool


@dataclass(frozen=True)
class LinkRecord:
    source_canonical: str
    target_canonical: str
    raw_target: str
    line_number: Optional[int]


class VaultDB:
    """Manages transactional access to vault-index.db."""

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self._conn: Optional[sqlite3.Connection] = None

    def connect(self) -> sqlite3.Connection:
        if self._conn is None:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(
                str(self.db_path),
                timeout=30.0,
                isolation_level=None,  # Autocommit mode; transactions managed via BEGIN/COMMIT
            )
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("PRAGMA journal_mode = WAL;")
            conn.execute("PRAGMA synchronous = NORMAL;")
            self._conn = conn
        return self._conn

    def close(self):
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def init_schema(self):
        """
        Initializes tables, indices, and default metadata.
        Automatically drops and rebuilds tables if schema_version mismatches.
        """
        conn = self.connect()
        # Verify existing schema version if meta table exists
        has_meta = (
            conn.execute(
                "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='meta';"
            ).fetchone()[0]
            > 0
        )

        current_version = self.get_meta("schema_version") if has_meta else None

        if current_version != SCHEMA_VERSION:
            with conn:
                conn.execute("PRAGMA foreign_keys = OFF;")
                conn.execute("DROP TABLE IF EXISTS links;")
                conn.execute("DROP TABLE IF EXISTS files;")
                conn.execute("DROP TABLE IF EXISTS meta;")
                conn.execute("PRAGMA foreign_keys = ON;")
                conn.executescript(SCHEMA_SQL)
                conn.execute(
                    "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?);",
                    ("schema_version", SCHEMA_VERSION),
                )
        else:
            with conn:
                conn.executescript(SCHEMA_SQL)

    # -----------------------------------------------------------------------
    # Metadata Queries
    # -----------------------------------------------------------------------

    def get_meta(self, key: str) -> Optional[str]:
        conn = self.connect()
        row = conn.execute("SELECT value FROM meta WHERE key = ?;", (key,)).fetchone()
        return row["value"] if row else None

    def set_meta(self, key: str, value: str):
        conn = self.connect()
        conn.execute(
            "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?);",
            (key, value),
        )

    # -----------------------------------------------------------------------
    # File Ledger Operations
    # -----------------------------------------------------------------------

    def upsert_file(self, record: FileRecord) -> int:
        """
        Inserts or updates a file record keyed on canonical_filename.
        """
        conn = self.connect()
        cursor = conn.execute(
            """
            INSERT INTO files (canonical_filename, stem, ext, rel_path, sha256, mtime, size, is_media, is_secure)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(canonical_filename) DO UPDATE SET
                stem = excluded.stem,
                ext = excluded.ext,
                rel_path = excluded.rel_path,
                sha256 = excluded.sha256,
                mtime = excluded.mtime,
                size = excluded.size,
                is_media = excluded.is_media,
                is_secure = excluded.is_secure;
            """,
            (
                record.canonical_filename,
                record.stem,
                record.ext,
                record.rel_path,
                record.sha256,
                record.mtime,
                record.size,
                1 if record.is_media else 0,
                1 if record.is_secure else 0,
            ),
        )
        return cursor.lastrowid

    def get_file_by_canonical(self, canonical_filename: str) -> Optional[FileRecord]:
        conn = self.connect()
        row = conn.execute(
            "SELECT * FROM files WHERE canonical_filename = ?;", (canonical_filename,)
        ).fetchone()
        if not row:
            return None
        return self._row_to_file_record(row)

    def get_file_by_path(self, rel_path: str) -> Optional[FileRecord]:
        conn = self.connect()
        row = conn.execute(
            "SELECT * FROM files WHERE rel_path = ?;", (rel_path,)
        ).fetchone()
        if not row:
            return None
        return self._row_to_file_record(row)

    def get_file_by_hash(self, sha256: str) -> List[FileRecord]:
        conn = self.connect()
        rows = conn.execute(
            "SELECT * FROM files WHERE sha256 = ?;", (sha256,)
        ).fetchall()
        return [self._row_to_file_record(r) for r in rows]

    def get_all_files(self) -> Dict[str, FileRecord]:
        """Returns a mapping of rel_path -> FileRecord."""
        conn = self.connect()
        rows = conn.execute("SELECT * FROM files;").fetchall()
        return {r["rel_path"]: self._row_to_file_record(r) for r in rows}

    def delete_file_by_canonical(self, canonical_filename: str):
        conn = self.connect()
        conn.execute(
            "DELETE FROM files WHERE canonical_filename = ?;", (canonical_filename,)
        )

    def delete_file_by_path(self, rel_path: str):
        conn = self.connect()
        conn.execute("DELETE FROM files WHERE rel_path = ?;", (rel_path,))

    # -----------------------------------------------------------------------
    # Stat-Cache Fast-Path Queries
    # -----------------------------------------------------------------------

    def is_stat_cache_hit(self, rel_path: str, mtime: float, size: int) -> bool:
        conn = self.connect()
        row = conn.execute(
            "SELECT mtime, size FROM files WHERE rel_path = ?;",
            (rel_path,),
        ).fetchone()
        if not row:
            return False
        return abs(row["mtime"] - mtime) < 0.0001 and row["size"] == size

    # -----------------------------------------------------------------------
    # Link Graph Operations
    # -----------------------------------------------------------------------

    def replace_document_links(self, source_canonical: str, links: List[LinkRecord]):
        """
        Atomically replaces all outgoing link edges for a given source canonical filename.
        """
        conn = self.connect()
        with conn:
            conn.execute(
                "DELETE FROM links WHERE source_canonical = ?;", (source_canonical,)
            )
            if links:
                conn.executemany(
                    """
                    INSERT INTO links (source_canonical, target_canonical, raw_target, line_number)
                    VALUES (?, ?, ?, ?);
                    """,
                    [
                        (
                            l.source_canonical,
                            l.target_canonical,
                            l.raw_target,
                            l.line_number,
                        )
                        for l in links
                    ],
                )

    def get_referencing_links(self, target_canonical: str) -> List[LinkRecord]:
        conn = self.connect()
        rows = conn.execute(
            "SELECT source_canonical, target_canonical, raw_target, line_number FROM links WHERE target_canonical = ?;",
            (target_canonical,),
        ).fetchall()
        return [
            LinkRecord(
                source_canonical=r["source_canonical"],
                target_canonical=r["target_canonical"],
                raw_target=r["raw_target"],
                line_number=r["line_number"],
            )
            for r in rows
        ]

    def get_outgoing_links(self, source_canonical: str) -> List[LinkRecord]:
        conn = self.connect()
        rows = conn.execute(
            "SELECT source_canonical, target_canonical, raw_target, line_number FROM links WHERE source_canonical = ?;",
            (source_canonical,),
        ).fetchall()
        return [
            LinkRecord(
                source_canonical=r["source_canonical"],
                target_canonical=r["target_canonical"],
                raw_target=r["raw_target"],
                line_number=r["line_number"],
            )
            for r in rows
        ]

    # -----------------------------------------------------------------------
    # Helper Conversion
    # -----------------------------------------------------------------------

    @staticmethod
    def _row_to_file_record(row: sqlite3.Row) -> FileRecord:
        return FileRecord(
            id=row["id"],
            canonical_filename=row["canonical_filename"],
            stem=row["stem"],
            ext=row["ext"],
            rel_path=row["rel_path"],
            sha256=row["sha256"],
            mtime=row["mtime"],
            size=row["size"],
            is_media=bool(row["is_media"]),
            is_secure=bool(row["is_secure"]),
        )
```

## system/normalize/engine.py

```python
"""
system/normalize/engine.py - Identity Decision Matrix & Reconciliation Engine.
Correlates physical disk state against the SQLite ledger (P, S, H) to plan mutations.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import PurePosixPath
from typing import Dict, List, Optional, Set, Tuple

from .db import FileRecord, VaultDB
from .scanner import ScannedFile, VaultScanResult
from .slugify import is_valid_stem, sanitize_path_segments, slugify_stem


class ActionType(Enum):
    NOOP = auto()
    CREATE = auto()
    DELETE = auto()
    MODIFY_CONTENT = auto()
    MOVE = auto()
    RENAME = auto()
    MOVE_AND_RENAME = auto()
    SANITIZE_STEM = auto()
    SANITIZE_PATH = auto()
    RESOLVE_COLLISION = auto()


@dataclass(frozen=True)
class FileAction:
    action_type: ActionType
    src_rel_path: Optional[str]
    dst_rel_path: Optional[str]
    old_stem: Optional[str]
    new_stem: Optional[str]
    sha256: str
    is_media: bool
    is_secure: bool
    reason: str


@dataclass(frozen=True)
class BoundaryViolation:
    source_rel_path: str
    target_rel_path: str
    source_is_secure: bool
    target_is_secure: bool
    line_number: int


@dataclass
class DiffPlan:
    actions: List[FileAction] = field(default_factory=list)
    collisions: Dict[str, List[str]] = field(default_factory=lambda: defaultdict(list))
    broken_references: Dict[str, List[str]] = field(
        default_factory=lambda: defaultdict(list)
    )
    boundary_violations: List[BoundaryViolation] = field(default_factory=list)

    @property
    def has_mutations(self) -> bool:
        return any(a.action_type != ActionType.NOOP for a in self.actions)


def resolve_collision_stem(
    base_stem: str, ext: str, existing_filenames: Set[str]
) -> str:
    """Appends the lowest available positive integer suffix (e.g. 'energy-1.md')."""
    counter = 1
    while True:
        candidate_stem = f"{base_stem}-{counter}"
        candidate_filename = f"{candidate_stem}{ext}"
        if candidate_filename not in existing_filenames:
            return candidate_stem
        counter += 1


def compute_diff(scan_result: VaultScanResult, db: VaultDB) -> DiffPlan:
    """
    Computes differences between physical disk scan and SQLite ledger.
    Implements the Identity Decision Matrix: (P, S, H) -> (P', S', H')
    """
    plan = DiffPlan()

    db_files = db.get_all_files()
    db_by_stem: Dict[str, FileRecord] = {r.stem: r for r in db_files.values()}
    db_by_hash: Dict[str, List[FileRecord]] = defaultdict(list)
    for r in db_files.values():
        db_by_hash[r.sha256].append(r)

    disk_files = scan_result.files
    disk_by_path: Dict[str, ScannedFile] = {f.rel_path: f for f in disk_files}

    # Step 1: Detect canonical filename collisions across scanned disk files
    disk_filenames: Dict[str, List[ScannedFile]] = defaultdict(list)
    for f in disk_files:
        disk_filenames[f.canonical_filename].append(f)

    for c_filename, occurrences in disk_filenames.items():
        if len(occurrences) > 1:
            plan.collisions[c_filename] = [o.rel_path for o in occurrences]

    unmatched_db_paths: Set[str] = set(db_files.keys())
    unmatched_disk_paths: Set[str] = set(disk_by_path.keys())
    matched_pairs: List[Tuple[FileRecord, ScannedFile]] = []

    # Step 2: Correlate exact path matches (P == P')
    for rel_path in list(unmatched_disk_paths):
        if rel_path in unmatched_db_paths:
            db_rec = db_files[rel_path]
            disk_rec = disk_by_path[rel_path]
            matched_pairs.append((db_rec, disk_rec))
            unmatched_db_paths.remove(rel_path)
            unmatched_disk_paths.remove(rel_path)

    # Step 3: Correlate moved files with identical content hash (H == H')
    for rel_path in list(unmatched_disk_paths):
        disk_rec = disk_by_path[rel_path]
        candidates = [
            db_rec
            for db_rec in db_by_hash.get(disk_rec.sha256, [])
            if db_rec.rel_path in unmatched_db_paths
        ]
        if candidates:
            chosen = next(
                (c for c in candidates if c.stem == disk_rec.stem), candidates[0]
            )
            matched_pairs.append((chosen, disk_rec))
            unmatched_db_paths.remove(chosen.rel_path)
            unmatched_disk_paths.remove(rel_path)

    # Step 4: Correlate moved files with modified content via Stem UID (S == S', H != H')
    for rel_path in list(unmatched_disk_paths):
        disk_rec = disk_by_path[rel_path]
        if disk_rec.stem in db_by_stem:
            db_rec = db_by_stem[disk_rec.stem]
            if db_rec.rel_path in unmatched_db_paths:
                matched_pairs.append((db_rec, disk_rec))
                unmatched_db_paths.remove(db_rec.rel_path)
                unmatched_disk_paths.remove(rel_path)

    # Track allocated canonical filenames to ensure global uniqueness across content/
    allocated_filenames: Set[str] = set()

    # Sort matched pairs deterministically by (mtime, rel_path)
    matched_pairs.sort(key=lambda pair: (pair[1].mtime, pair[1].rel_path))

    # Evaluate correlated pairs
    for db_rec, disk_rec in matched_pairs:
        p_match = db_rec.rel_path == disk_rec.rel_path
        s_match = db_rec.stem == disk_rec.stem
        h_match = db_rec.sha256 == disk_rec.sha256

        canonical_stem = slugify_stem(disk_rec.stem)
        canonical_filename = f"{canonical_stem}{disk_rec.ext}"
        canonical_path = sanitize_path_segments(disk_rec.rel_path)

        needs_stem_sanitize = (
            not is_valid_stem(disk_rec.stem) or disk_rec.stem != canonical_stem
        )
        needs_path_sanitize = disk_rec.rel_path != canonical_path
        is_colliding = canonical_filename in allocated_filenames

        if p_match and s_match and h_match:
            if is_colliding or needs_stem_sanitize:
                target_stem = canonical_stem
                if is_colliding:
                    target_stem = resolve_collision_stem(
                        canonical_stem, disk_rec.ext, allocated_filenames
                    )
                target_filename = f"{target_stem}{disk_rec.ext}"
                allocated_filenames.add(target_filename)
                action_type = (
                    ActionType.RESOLVE_COLLISION
                    if is_colliding
                    else ActionType.SANITIZE_STEM
                )
                plan.actions.append(
                    FileAction(
                        action_type=action_type,
                        src_rel_path=disk_rec.rel_path,
                        dst_rel_path=str(
                            PurePosixPath(disk_rec.rel_path).with_name(target_filename)
                        ),
                        old_stem=disk_rec.stem,
                        new_stem=target_stem,
                        sha256=disk_rec.sha256,
                        is_media=disk_rec.is_media,
                        is_secure=disk_rec.is_secure,
                        reason="Collision resolved or stem violates archival specification.",
                    )
                )
            elif needs_path_sanitize:
                allocated_filenames.add(canonical_filename)
                plan.actions.append(
                    FileAction(
                        action_type=ActionType.SANITIZE_PATH,
                        src_rel_path=disk_rec.rel_path,
                        dst_rel_path=canonical_path,
                        old_stem=disk_rec.stem,
                        new_stem=disk_rec.stem,
                        sha256=disk_rec.sha256,
                        is_media=disk_rec.is_media,
                        is_secure=disk_rec.is_secure,
                        reason="Directory path segments contain un-normalized characters.",
                    )
                )
            else:
                allocated_filenames.add(canonical_filename)
                plan.actions.append(
                    FileAction(
                        action_type=ActionType.NOOP,
                        src_rel_path=disk_rec.rel_path,
                        dst_rel_path=disk_rec.rel_path,
                        old_stem=disk_rec.stem,
                        new_stem=disk_rec.stem,
                        sha256=disk_rec.sha256,
                        is_media=disk_rec.is_media,
                        is_secure=disk_rec.is_secure,
                        reason="Identical to ledger state.",
                    )
                )

        elif p_match and s_match and not h_match:
            allocated_filenames.add(canonical_filename)
            plan.actions.append(
                FileAction(
                    action_type=ActionType.MODIFY_CONTENT,
                    src_rel_path=disk_rec.rel_path,
                    dst_rel_path=disk_rec.rel_path,
                    old_stem=disk_rec.stem,
                    new_stem=disk_rec.stem,
                    sha256=disk_rec.sha256,
                    is_media=disk_rec.is_media,
                    is_secure=disk_rec.is_secure,
                    reason="File content modified in place.",
                )
            )

        elif not p_match and s_match and h_match:
            allocated_filenames.add(canonical_filename)
            plan.actions.append(
                FileAction(
                    action_type=ActionType.MOVE,
                    src_rel_path=db_rec.rel_path,
                    dst_rel_path=disk_rec.rel_path,
                    old_stem=db_rec.stem,
                    new_stem=disk_rec.stem,
                    sha256=disk_rec.sha256,
                    is_media=disk_rec.is_media,
                    is_secure=disk_rec.is_secure,
                    reason=f"Moved from '{db_rec.rel_path}' to '{disk_rec.rel_path}'.",
                )
            )

        elif (
            PurePosixPath(db_rec.rel_path).parent
            == PurePosixPath(disk_rec.rel_path).parent
            and not s_match
            and h_match
        ):
            allocated_filenames.add(canonical_filename)
            plan.actions.append(
                FileAction(
                    action_type=ActionType.RENAME,
                    src_rel_path=db_rec.rel_path,
                    dst_rel_path=disk_rec.rel_path,
                    old_stem=db_rec.stem,
                    new_stem=disk_rec.stem,
                    sha256=disk_rec.sha256,
                    is_media=disk_rec.is_media,
                    is_secure=disk_rec.is_secure,
                    reason=f"Renamed from '{db_rec.stem}' to '{disk_rec.stem}'.",
                )
            )

        elif (
            PurePosixPath(db_rec.rel_path).parent
            != PurePosixPath(disk_rec.rel_path).parent
            and not s_match
            and h_match
        ):
            allocated_filenames.add(canonical_filename)
            plan.actions.append(
                FileAction(
                    action_type=ActionType.MOVE_AND_RENAME,
                    src_rel_path=db_rec.rel_path,
                    dst_rel_path=disk_rec.rel_path,
                    old_stem=db_rec.stem,
                    new_stem=disk_rec.stem,
                    sha256=disk_rec.sha256,
                    is_media=disk_rec.is_media,
                    is_secure=disk_rec.is_secure,
                    reason=f"Moved and renamed from '{db_rec.rel_path}'.",
                )
            )

        elif not p_match and s_match and not h_match:
            allocated_filenames.add(canonical_filename)
            plan.actions.append(
                FileAction(
                    action_type=ActionType.MOVE,
                    src_rel_path=db_rec.rel_path,
                    dst_rel_path=disk_rec.rel_path,
                    old_stem=db_rec.stem,
                    new_stem=disk_rec.stem,
                    sha256=disk_rec.sha256,
                    is_media=disk_rec.is_media,
                    is_secure=disk_rec.is_secure,
                    reason=f"Moved from '{db_rec.rel_path}' and modified.",
                )
            )

    # Step 5: Remaining unmatched disk files -> CREATE, SANITIZE, or RESOLVE_COLLISION
    for db_rec in db_files.values():
        if db_rec.rel_path in unmatched_db_paths:
            allocated_filenames.add(db_rec.canonical_filename)

    sorted_unmatched_disk = sorted(
        unmatched_disk_paths,
        key=lambda p: (disk_by_path[p].mtime, p),
    )

    for rel_path in sorted_unmatched_disk:
        disk_rec = disk_by_path[rel_path]
        canonical_stem = slugify_stem(disk_rec.stem)
        canonical_filename = f"{canonical_stem}{disk_rec.ext}"
        target_stem = canonical_stem
        is_collision = False

        if canonical_filename in allocated_filenames:
            target_stem = resolve_collision_stem(
                canonical_stem, disk_rec.ext, allocated_filenames
            )
            is_collision = True

        target_filename = f"{target_stem}{disk_rec.ext}"
        allocated_filenames.add(target_filename)

        canonical_path = sanitize_path_segments(rel_path)
        if target_stem != disk_rec.stem:
            canonical_path = str(
                PurePosixPath(canonical_path).with_name(target_filename)
            )

        needs_stem_sanitize = (
            not is_valid_stem(disk_rec.stem) or disk_rec.stem != target_stem
        )
        needs_path_sanitize = disk_rec.rel_path != canonical_path

        if is_collision:
            plan.actions.append(
                FileAction(
                    action_type=ActionType.RESOLVE_COLLISION,
                    src_rel_path=disk_rec.rel_path,
                    dst_rel_path=canonical_path,
                    old_stem=disk_rec.stem,
                    new_stem=target_stem,
                    sha256=disk_rec.sha256,
                    is_media=disk_rec.is_media,
                    is_secure=disk_rec.is_secure,
                    reason=f"Stem collision on '{canonical_stem}' resolved to '{target_stem}'.",
                )
            )
        elif needs_stem_sanitize or needs_path_sanitize:
            action_type = (
                ActionType.SANITIZE_STEM
                if needs_stem_sanitize
                else ActionType.SANITIZE_PATH
            )
            plan.actions.append(
                FileAction(
                    action_type=action_type,
                    src_rel_path=disk_rec.rel_path,
                    dst_rel_path=canonical_path,
                    old_stem=disk_rec.stem,
                    new_stem=target_stem,
                    sha256=disk_rec.sha256,
                    is_media=disk_rec.is_media,
                    is_secure=disk_rec.is_secure,
                    reason="New file on disk requires name/path sanitization.",
                )
            )
        else:
            plan.actions.append(
                FileAction(
                    action_type=ActionType.CREATE,
                    src_rel_path=None,
                    dst_rel_path=disk_rec.rel_path,
                    old_stem=None,
                    new_stem=disk_rec.stem,
                    sha256=disk_rec.sha256,
                    is_media=disk_rec.is_media,
                    is_secure=disk_rec.is_secure,
                    reason="New file detected on disk.",
                )
            )

        # Step 6: Remaining unmatched DB files -> DELETE
        for rel_path in sorted(unmatched_db_paths):
            db_rec = db_files[rel_path]
            inbound_links = db.get_referencing_links(db_rec.canonical_filename)

            if inbound_links:
                plan.broken_references[db_rec.stem] = [
                    l.source_canonical for l in inbound_links
                ]

            plan.actions.append(
                FileAction(
                    action_type=ActionType.DELETE,
                    src_rel_path=db_rec.rel_path,
                    dst_rel_path=None,
                    old_stem=db_rec.stem,
                    new_stem=None,
                    sha256=db_rec.sha256,
                    is_media=db_rec.is_media,
                    is_secure=db_rec.is_secure,
                    reason=f"File removed from disk (had {len(inbound_links)} inbound references).",
                )
            )

    return plan
```

## system/normalize/graph.py

````python
"""
system/normalize/graph.py - CommonMark Link Extraction, Validation & Path Healing.
Provides POSIX relative path calculation and AST-safe link rewriting.
"""

import posixpath
import re
import urllib.parse
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Dict, List, Tuple

from .db import LinkRecord
from .slugify import slugify_stem

# Detect external protocols or anchor-only references
EXTERNAL_OR_ANCHOR_PATTERN = re.compile(
    r"^(?:[a-zA-Z][a-zA-Z0-9+.-]*://|//|mailto:|tel:|#)"
)

# Match: [label](<destination with spaces>) OR [label](bare_destination)
LINK_OR_IMAGE_PATTERN = re.compile(
    r"(!?\[((?:[^\[\]]|\\.)*)\])\(\s*(?:<([^>]+)>|([^\s\)\"\']+))(?:\s+([\"'])(.*?)\5)?\s*\)"
)


@dataclass(frozen=True)
class ExtractedLink:
    source_canonical: str
    target_canonical: str
    target_stem: str
    raw_target: str
    line_number: int
    is_image: bool
    label: str
    target_path: str
    suffix: str  # #fragment or ?query


def mask_inline_code_spans(text: str) -> str:
    """
    Scans a single line and replaces contents of inline code spans with whitespace.
    Strictly adheres to CommonMark delimiter matching without regex backtracking.
    """
    out = []
    i = 0
    n = len(text)
    while i < n:
        if text[i] == "`":
            start = i
            while i < n and text[i] == "`":
                i += 1
            delim_len = i - start
            delim = "`" * delim_len
            end = text.find(delim, i)
            if end != -1:
                total_len = (end + delim_len) - start
                out.append(" " * total_len)
                i = end + delim_len
            else:
                out.append(text[start:i])
        else:
            out.append(text[i])
            i += 1
    return "".join(out)


def split_target_url(raw_target: str) -> Tuple[str, str]:
    """
    Splits a raw link target into (path_portion, suffix_portion).
    Example: '../notes/energy.md#first-law' -> ('../notes/energy.md', '#first-law')
    """
    match = re.search(r"[#?]", raw_target)
    if match:
        idx = match.start()
        return raw_target[:idx], raw_target[idx:]
    return raw_target, ""


def is_external_or_anchor(url: str) -> bool:
    """Checks whether the link is external or purely a local in-page anchor."""
    clean = url.strip()
    return bool(EXTERNAL_OR_ANCHOR_PATTERN.match(clean))


def extract_stem_from_path(path_str: str) -> str:
    """
    Extracts and canonicalizes the filename stem from a relative path string.
    Decodes percent-encoding (e.g. 'Math%20Notes/Matrix.md' -> 'matrix').
    """
    unquoted = urllib.parse.unquote(path_str)
    pure = PurePosixPath(unquoted)
    return slugify_stem(pure.stem)


def parse_markdown_links(content: str, source_canonical: str) -> List[ExtractedLink]:
    """
    Parses Markdown text and extracts relative links and images.
    Accurately ignores links enclosed inside fenced or inline code spans.
    """
    extracted: List[ExtractedLink] = []
    lines = content.splitlines()

    in_fenced_block = False
    fenced_fence_char = ""
    fenced_fence_len = 0

    for line_idx, line in enumerate(lines, start=1):
        stripped = line.strip()

        # Fenced code block detection: ``` or ~~~
        if not in_fenced_block:
            if stripped.startswith("```") or stripped.startswith("~~~"):
                fence_char = stripped[0]
                match = re.match(r"^[`~]+", stripped)
                if match and len(match.group(0)) >= 3:
                    in_fenced_block = True
                    fenced_fence_char = fence_char
                    fenced_fence_len = len(match.group(0))
                    continue
        else:
            if stripped.startswith(fenced_fence_char * fenced_fence_len):
                in_fenced_block = False
            continue

        if in_fenced_block:
            continue

        sanitized_line = mask_inline_code_spans(line)

        for match in LINK_OR_IMAGE_PATTERN.finditer(sanitized_line):
            is_image = match.group(1).startswith("!")
            label = match.group(2)
            raw_url = (match.group(3) or match.group(4) or "").strip()

            if is_external_or_anchor(raw_url):
                continue

            path_part, suffix_part = split_target_url(raw_url)
            target_stem = extract_stem_from_path(path_part)

            if not target_stem:
                continue

            unquoted_path = urllib.parse.unquote(path_part)
            ext = PurePosixPath(unquoted_path).suffix.lower()
            if not ext:
                ext = ".md"
            target_canonical = f"{target_stem}{ext}"

            extracted.append(
                ExtractedLink(
                    source_canonical=source_canonical,
                    target_canonical=target_canonical,
                    target_stem=target_stem,
                    raw_target=raw_url,
                    line_number=line_idx,
                    is_image=is_image,
                    label=label,
                    target_path=path_part,
                    suffix=suffix_part,
                )
            )

    return extracted


def to_link_records(extracted_links: List[ExtractedLink]) -> List[LinkRecord]:
    """Converts ExtractedLink items into SQLite LinkRecord objects."""
    return [
        LinkRecord(
            source_canonical=link.source_canonical,
            target_canonical=link.target_canonical,
            raw_target=link.raw_target,
            line_number=link.line_number,
        )
        for link in extracted_links
    ]


def compute_relative_link(source_rel_path: str, target_rel_path: str) -> str:
    """
    Calculates the explicit relative POSIX path from source_rel_path to target_rel_path.
    Guaranteed deterministic forward-slash output across all host operating systems.
    """
    src_parent = PurePosixPath(source_rel_path).parent
    src_dir_str = "." if str(src_parent) == "." else str(src_parent)
    return posixpath.relpath(target_rel_path, start=src_dir_str)


def heal_markdown_links(
    content: str,
    source_rel_path: str,
    stem_to_new_rel_path: Dict[str, str],
) -> Tuple[str, int]:
    """
    Rewrites relative links targeting files that have changed paths or stems.
    Preserves link labels, images, optional titles, and anchors/query strings.
    Ignores links inside fenced code blocks and inline code spans.
    """
    lines = content.splitlines(keepends=True)
    new_lines: List[str] = []
    total_rewrites = 0

    in_fenced_block = False
    fenced_fence_char = ""
    fenced_fence_len = 0

    for line in lines:
        stripped = line.strip()

        if not in_fenced_block:
            if stripped.startswith("```") or stripped.startswith("~~~"):
                fence_char = stripped[0]
                match = re.match(r"^[`~]+", stripped)
                if match and len(match.group(0)) >= 3:
                    in_fenced_block = True
                    fenced_fence_char = fence_char
                    fenced_fence_len = len(match.group(0))
                    new_lines.append(line)
                    continue
        else:
            if stripped.startswith(fenced_fence_char * fenced_fence_len):
                in_fenced_block = False
            new_lines.append(line)
            continue

        if in_fenced_block:
            new_lines.append(line)
            continue

        # Compute code spans via linear scan to avoid false matches
        inline_spans = []
        i = 0
        n = len(line)
        while i < n:
            if line[i] == "`":
                s = i
                while i < n and line[i] == "`":
                    i += 1
                d_len = i - s
                d = "`" * d_len
                e = line.find(d, i)
                if e != -1:
                    inline_spans.append((s, e + d_len))
                    i = e + d_len
                else:
                    break
            else:
                i += 1

        line_rewrites = 0

        def replace_link(m: re.Match) -> str:
            nonlocal line_rewrites

            if any(start <= m.start() < end for start, end in inline_spans):
                return m.group(0)

            prefix = m.group(1)
            # Group 3 is <destination>, Group 4 is bare destination
            raw_url = (m.group(3) or m.group(4) or "").strip()
            # Quote character and title shifted from groups 4 & 5 to 5 & 6
            quote_char = m.group(5) or ""
            title_text = m.group(6) or ""

            if is_external_or_anchor(raw_url):
                return m.group(0)

            path_part, suffix_part = split_target_url(raw_url)
            target_stem = extract_stem_from_path(path_part)

            if target_stem not in stem_to_new_rel_path:
                return m.group(0)

            new_target_rel_path = stem_to_new_rel_path[target_stem]
            healed_rel_path = compute_relative_link(
                source_rel_path, new_target_rel_path
            )
            new_url = f"{healed_rel_path}{suffix_part}"

            if new_url == raw_url:
                return m.group(0)

            line_rewrites += 1
            if quote_char and title_text:
                return f"{prefix}({new_url} {quote_char}{title_text}{quote_char})"
            return f"{prefix}({new_url})"

        new_line = LINK_OR_IMAGE_PATTERN.sub(replace_link, line)
        new_lines.append(new_line)
        total_rewrites += line_rewrites

    return "".join(new_lines), total_rewrites
````

## system/normalize/scanner.py

```python
# system/normalize/scanner.py
"""
system/normalize/scanner.py - Fast-Path Traversal & Stat-Cache Aware File Scanner.
Traverses content/ and avoids redundant I/O for unchanged files.
"""

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from .db import VaultDB

JUNK_DIR_NAMES = {
    ".obsidian",
    ".trash",
    ".zettlr",
    ".logseq",
    "logseq",
    ".git",
    ".vscode",
    ".idea",
}

JUNK_FILE_EXTENSIONS = {".ztr-directory", ".ds_store", "thumbs.db", "desktop.ini"}

MARKDOWN_EXTENSIONS = {".md", ".markdown"}


def is_junk_path(path: Path, root: Path) -> bool:
    """
    Checks if a given path belongs to junk/hidden editor folders or artifact files.
    """
    try:
        rel_parts = path.relative_to(root).parts
    except ValueError:
        rel_parts = path.parts

    for part in rel_parts:
        if part.lower() in JUNK_DIR_NAMES or (part.startswith(".") and part != "."):
            return True

    name_lower = path.name.lower()
    if name_lower in JUNK_FILE_EXTENSIONS:
        return True
    if any(name_lower.endswith(ext) for ext in JUNK_FILE_EXTENSIONS):
        return True
    return False


def is_secure_rel_path(rel_posix_path: str) -> bool:
    """Returns True if the path resides inside a /secure/ subfolder."""
    parts = rel_posix_path.split("/")
    return "secure" in parts


def compute_file_sha256(file_path: Path) -> str:
    """Computes SHA-256 hash using 64 KiB buffer chunks."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


@dataclass(frozen=True)
class ScannedFile:
    abs_path: Path
    rel_path: str  # POSIX format (e.g. 'notes/math.md')
    canonical_filename: str
    stem: str
    ext: str
    mtime: float
    size: int
    sha256: str
    is_media: bool
    is_secure: bool
    is_cache_hit: bool


@dataclass(frozen=True)
class VaultScanResult:
    files: List[ScannedFile]
    files_by_path: Dict[str, ScannedFile]
    cache_hits: int
    cache_misses: int


def scan_vault(content_root: Path, db: Optional[VaultDB] = None) -> VaultScanResult:
    """
    Scans content_root applying junk filtering, symlink suppression, and SQLite stat-cache verification.
    If db is provided and a file matches (mtime, size), disk hash computation is bypassed.
    """
    content_root = content_root.resolve()
    scanned_files: List[ScannedFile] = []
    files_by_path: Dict[str, ScannedFile] = {}
    cache_hits = 0
    cache_misses = 0

    if not content_root.exists() or not content_root.is_dir():
        return VaultScanResult([], {}, 0, 0)

    for root, dirs, filenames in os.walk(content_root, followlinks=False):
        # Boundary guard: ignore directory symlinks and prune junk directories in-place
        dirs[:] = [
            d
            for d in dirs
            if not (Path(root) / d).is_symlink()
            and not is_junk_path(Path(root) / d, content_root)
        ]

        for filename in filenames:
            abs_path = Path(root) / filename

            # Boundary guard: never follow or catalog symlinks
            if abs_path.is_symlink():
                continue

            if is_junk_path(abs_path, content_root):
                continue

            try:
                rel_path = abs_path.relative_to(content_root).as_posix()
            except ValueError:
                # Path escapes content_root; strictly ignore
                continue

            stat = abs_path.stat()
            mtime = stat.st_mtime
            size = stat.st_size

            from .slugify import slugify_stem

            ext = abs_path.suffix.lower()
            is_media = ext not in MARKDOWN_EXTENSIONS
            is_secure = is_secure_rel_path(rel_path)
            stem = abs_path.stem
            canonical_filename = f"{slugify_stem(stem)}{ext}"

            sha256: Optional[str] = None
            is_cache_hit = False

            if db is not None and db.is_stat_cache_hit(rel_path, mtime, size):
                cached_rec = db.get_file_by_path(rel_path)
                if cached_rec is not None:
                    sha256 = cached_rec.sha256
                    is_cache_hit = True
                    cache_hits += 1

            if sha256 is None:
                sha256 = compute_file_sha256(abs_path)
                cache_misses += 1

            record = ScannedFile(
                abs_path=abs_path,
                rel_path=rel_path,
                canonical_filename=canonical_filename,
                stem=stem,
                ext=ext,
                mtime=mtime,
                size=size,
                sha256=sha256,
                is_media=is_media,
                is_secure=is_secure,
                is_cache_hit=is_cache_hit,
            )

            scanned_files.append(record)
            files_by_path[rel_path] = record

    return VaultScanResult(
        files=scanned_files,
        files_by_path=files_by_path,
        cache_hits=cache_hits,
        cache_misses=cache_misses,
    )
```

## system/normalize/slugify.py

```python
"""
system/normalize/slugify.py - Deterministic Cross-Platform Slugifier & Path Sanitizer.
Strictly adheres to POSIX and Windows-safe constraints.
"""

import re
import unicodedata
from pathlib import PurePosixPath

# Matches valid stems: starts with [a-z0-9], followed by [a-z0-9], '-', or '_'
STEM_PATTERN = re.compile(r"^[a-z0-9][a-z0-9\-_]*$")

# Characters explicitly forbidden across POSIX and Windows filesystems
FORBIDDEN_CHARS_PATTERN = re.compile(r'[<>:"/\\|?*\x00-\x1f]')

# Non-alphanumeric separators (excluding hyphen and underscore)
PUNCTUATION_SEPARATOR_PATTERN = re.compile(r"[\s\.,;!#$@%^&()\[\]{}+=~`'\"]+")

# Runs of hyphens or underscores
COLLAPSE_HYPHENS = re.compile(r"-{2,}")
COLLAPSE_UNDERSCORES = re.compile(r"_{2,}")


def is_valid_stem(stem: str) -> bool:
    """
    Validates whether a filename stem meets the strict archival UID specification:
      Regex: ^[a-z0-9][a-z0-9\\-_]*$
    """
    if not stem or len(stem) > 255:
        return False
    return bool(STEM_PATTERN.match(stem))


def slugify_stem(raw_stem: str, default_fallback: str = "untitled") -> str:
    """
    Transforms an arbitrary filename stem into a canonical, normalized UID:
      1. Normalizes Unicode to NFC.
      2. Converts ASCII/Unicode characters to lowercase.
      3. Replaces spaces, dots, and common punctuation with hyphens.
      4. Strips forbidden filesystem characters.
      5. Collapses redundant consecutive hyphens/underscores.
      6. Trims leading/trailing hyphens, underscores, and dots.
      7. Ensures leading character is alphanumeric; prepends 'n-' if it starts with a hyphen/digit boundary.
    """
    if not raw_stem or not raw_stem.strip():
        return default_fallback

    # Step 1: Unicode NFC Normalization
    text = unicodedata.normalize("NFC", raw_stem.strip())

    # Step 2: Lowercase conversion
    text = text.lower()

    # Step 3: Strip absolute forbidden chars
    text = FORBIDDEN_CHARS_PATTERN.sub("", text)

    # Step 4: Convert whitespace and punctuation clusters to hyphens
    text = PUNCTUATION_SEPARATOR_PATTERN.sub("-", text)

    # Step 5: Retain only ASCII [a-z0-9], hyphens, and underscores
    # Strips non-ASCII unicode diacritics / symbols to ensure pure cross-platform portability
    text = re.sub(r"[^a-z0-9\-_]", "", text)

    # Step 6: Collapse consecutive hyphens and underscores
    text = COLLAPSE_HYPHENS.sub("-", text)
    text = COLLAPSE_UNDERSCORES.sub("_", text)

    # Step 7: Trim leading/trailing hyphens and underscores
    text = text.strip("-_")

    if not text:
        return default_fallback

    # Step 8: Ensure leading character is in [a-z0-9]
    if not text[0].isalnum():
        text = f"doc-{text.lstrip('-_')}"

    return text[:255]


def sanitize_path_segments(rel_path: str) -> str:
    """
    Sanitizes all directory segments and the filename in a relative POSIX path.
    Preserves file extension in lowercase.

    Example:
      'My Notes/2026 Math/Matrix Calculation.MD' -> 'my-notes/2026-math/matrix-calculation.md'
    """
    pure_path = PurePosixPath(rel_path)
    sanitized_parts = []

    for part in pure_path.parent.parts:
        if part in (".", ""):
            continue
        sanitized_parts.append(slugify_stem(part))

    stem = slugify_stem(pure_path.stem)
    ext = pure_path.suffix.lower()

    filename = f"{stem}{ext}"
    if sanitized_parts:
        return "/".join(sanitized_parts) + "/" + filename
    return filename
```

## system/tools/tools-manifest.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "description": "Kykloi Offline Appliance Toolchain Manifest",
  "version": "1.0",
  "tools": {
    "pandoc": {
      "version": "3.14",
      "upstream": "https://github.com/jgm/pandoc/releases/tag/3.14",
      "targets": {
        "linux-x86_64": {
          "archive": "pandoc-3.14-linux-amd64.tar.gz",
          "url": "https://github.com/jgm/pandoc/releases/download/3.14/pandoc-3.14-linux-amd64.tar.gz",
          "sha256": "c5f4720cdefb3f7bdc5d07202ef579feef0d1370773c873804dd8fdaa8c4f1b8"
        },
        "linux-arm64": {
          "archive": "pandoc-3.14-linux-arm64.tar.gz",
          "url": "https://github.com/jgm/pandoc/releases/download/3.14/pandoc-3.14-linux-arm64.tar.gz",
          "sha256": "c692f3d78a415741bbbac4cdbbbe26fa7edca1f43d2301b982fbf4009cc8cf7f"
        },
        "macos-arm64": {
          "archive": "pandoc-3.14-arm64-macOS.zip",
          "url": "https://github.com/jgm/pandoc/releases/download/3.14/pandoc-3.14-arm64-macOS.zip",
          "sha256": "58d6593884fec9d4424b641b92503c316d9c36decb2891ff8d73ae74dd3b6304"
        },
        "macos-x86_64": {
          "archive": "pandoc-3.14-x86_64-macOS.zip",
          "url": "https://github.com/jgm/pandoc/releases/download/3.14/pandoc-3.14-x86_64-macOS.zip",
          "sha256": "891708579061e7b1c1a6ce0df30ebb3cb2b6d0ca045ed3c8554ab830c1e0c270"
        },
        "windows-x86_64": {
          "archive": "pandoc-3.14-windows-x86_64.zip",
          "url": "https://github.com/jgm/pandoc/releases/download/3.14/pandoc-3.14-windows-x86_64.zip",
          "sha256": "0144b96e8c7b023fd382ec5ef5bdc475e873f1019d6fa72502492df2c9a94a3b"
        }
      }
    },
    "python": {
      "version": "3.12.16+20261110",
      "upstream": "https://github.com/astral-sh/python-build-standalone/releases/tag/20261110",
      "targets": {
        "linux-x86_64": {
          "archive": "cpython-3.12.16+20261110-x86_64-unknown-linux-gnu-install_only.tar.gz",
          "url": "https://github.com/astral-sh/python-build-standalone/releases/download/20261110/cpython-3.12.16+20261110-x86_64-unknown-linux-gnu-install_only.tar.gz",
          "sha256": "c2f87d4b4e8db3abddb0f116c6ccfc503d0cbdbb9ee8faacddad1b679ec12e99"
        },
        "linux-arm64": {
          "archive": "cpython-3.12.16+20261110-aarch64-unknown-linux-gnu-install_only.tar.gz",
          "url": "https://github.com/astral-sh/python-build-standalone/releases/download/20261110/cpython-3.12.16+20261110-aarch64-unknown-linux-gnu-install_only.tar.gz",
          "sha256": "4792f81750282597fb2a3389fe18b945ed2ba6aad5e45ad406d122c58cb33081"
        },
        "macos-arm64": {
          "archive": "cpython-3.12.16+20261110-aarch64-apple-darwin-install_only.tar.gz",
          "url": "https://github.com/astral-sh/python-build-standalone/releases/download/20261110/cpython-3.12.16+20261110-aarch64-apple-darwin-install_only.tar.gz",
          "sha256": "e956e60bc9465d577ef8062059aa05cd3a2665b4b8678a2ed24e432368330b8f"
        },
        "macos-x86_64": {
          "archive": "cpython-3.12.16+20261110-x86_64-apple-darwin-install_only.tar.gz",
          "url": "https://github.com/astral-sh/python-build-standalone/releases/download/20261110/cpython-3.12.16+20261110-x86_64-apple-darwin-install_only.tar.gz",
          "sha256": "83f2922437e6d546d0fcdb8c11f150a8e52787e8d9ea8651b1974e20908eb1bc"
        },
        "windows-x86_64": {
          "archive": "cpython-3.12.16+20261110-x86_64-pc-windows-msvc-install_only.tar.gz",
          "url": "https://github.com/astral-sh/python-build-standalone/releases/download/20261110/cpython-3.12.16+20261110-x86_64-pc-windows-msvc-install_only.tar.gz",
          "sha256": "e23fe5b16926de1d81661b1a97352e89fb167549c55a6825796ccd0f32ec7f1b"
        },
        "linux-arm64-musl": {
          "archive": "cpython-3.12.16+20261110-aarch64-unknown-linux-musl-install_only.tar.gz",
          "url": "https://github.com/astral-sh/python-build-standalone/releases/download/20261110/cpython-3.12.16+20261110-aarch64-unknown-linux-musl-install_only.tar.gz",
          "sha256": "d92d39867d6f16d81876b683c088373e2a965407c2011ad9979ffb4859a8bdcb"
        },
        "linux-x86_64-musl": {
          "archive": "cpython-3.12.16+20261110-x86_64-unknown-linux-musl-install_only.tar.gz",
          "url": "https://github.com/astral-sh/python-build-standalone/releases/download/20261110/cpython-3.12.16+20261110-x86_64-unknown-linux-musl-install_only.tar.gz",
          "sha256": "4f38d67f42dd29535e49b0ccdd6bc25ac7748b2c4550de78d8879ea4076ee9b3"
        },
        "windows-arm64": {
          "archive": "cpython-3.12.16+20261110-aarch64-pc-windows-msvc-install_only.tar.gz",
          "url": "https://github.com/astral-sh/python-build-standalone/releases/download/20261110/cpython-3.12.16+20261110-aarch64-pc-windows-msvc-install_only.tar.gz",
          "sha256": "7122bf62a0cf601527ba62e19ca715d64db86b269765da23937e9ac7f968f39c"
        }
      }
    }
  }
}
```

## system/launch.py

```python
#!/usr/bin/env python3
"""
system/launch.py - Autonomous Control Hub Daemon for Project Kykloi.
Features CLI argument parsing, defensive MIME registration, centralized telemetry,
cryptographic engine inspection, interactive vault normalization, and IPC server orchestration.
"""

import argparse
import http.server
import mimetypes
import os
import re
import socketserver
import subprocess
import sys
import threading
import urllib.parse
import webbrowser
from pathlib import Path

# ===========================================================================
# 1. PATH RESOLUTION, MODULE SETUP & DEFENSIVE MIME REGISTRATION
# ===========================================================================
SYSTEM_DIR = Path(__file__).resolve().parent
ROOT_DIR = SYSTEM_DIR.parent
CONTENT_DIR = ROOT_DIR / "content"
DIST_DIR = ROOT_DIR / "dist"
BUILD_SCRIPT = SYSTEM_DIR / "build" / "build.py"
NORM_DB_PATH = SYSTEM_DIR / "normalize" / "vault-index.db"

# Ensure the root project repository and internal subsystems are on sys.path
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(SYSTEM_DIR) not in sys.path:
    sys.path.insert(0, str(SYSTEM_DIR))
if str(SYSTEM_DIR / "build") not in sys.path:
    sys.path.insert(0, str(SYSTEM_DIR / "build"))

from build import ACTIVE_ENGINE_NAME, _resolve_active_crypto_engine
from logger import get_logger, setup_logging

from system.normalize.cli import run_normalization_pipeline
from system.normalize.db import VaultDB

mimetypes.init()
mimetypes.add_type("application/wasm", ".wasm")
mimetypes.add_type("font/woff2", ".woff2")
mimetypes.add_type("application/manifest+json", ".webmanifest")
mimetypes.add_type("application/octet-stream", ".enc")
mimetypes.add_type("image/svg+xml", ".svg")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("application/javascript", ".js")

RANGE_REGEX = re.compile(r"^bytes=(\d*)-(\d*)$")

# ===========================================================================
# 2. VAULT STATIC SERVER HANDLER
# ===========================================================================


class KykloiVaultHandler(http.server.BaseHTTPRequestHandler):
    server_version = "KykloiServer/0.7.0"
    protocol_version = "HTTP/1.1"

    def guess_mime(self, filepath: str) -> str:
        mime, _ = mimetypes.guess_type(filepath)
        return mime or "application/octet-stream"

    def log_message(self, format: str, *args):
        logger = get_logger("server")
        msg = format % args
        code_match = re.search(r'"\s+(\d{3})\s+', msg)
        status_code = int(code_match.group(1)) if code_match else 200

        if status_code >= 500:
            logger.error("%s - %s", self.address_string(), msg)
        elif status_code >= 400:
            logger.warning("%s - %s", self.address_string(), msg)
        else:
            logger.debug("%s - %s", self.address_string(), msg)

    def do_HEAD(self):
        self._dispatch_get(send_body=False)

    def do_GET(self):
        self._dispatch_get(send_body=True)

    def _dispatch_get(self, send_body: bool):
        parsed = urllib.parse.urlsplit(self.path)
        clean_path = urllib.parse.unquote(parsed.path)

        if not DIST_DIR.exists() or not any(DIST_DIR.iterdir()):
            body = b"Vault unbuilt. Run compilation in CLI.\n"
            self.send_response(503)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Connection", "close")
            self.end_headers()
            if send_body:
                self.wfile.write(body)
            return

        target_file = self._translate_dist_path(clean_path)
        if target_file is None or not os.path.isfile(target_file):
            self.send_error(404, "File Not Found")
            return

        self._serve_static_file(target_file, send_body)

    def _translate_dist_path(self, clean_path: str) -> str | None:
        stripped = clean_path.lstrip("/")
        target = (DIST_DIR / stripped).resolve()

        try:
            target.relative_to(DIST_DIR.resolve())
        except ValueError:
            return None

        if target.is_dir():
            index_candidate = target / "index.html"
            if index_candidate.is_file():
                return str(index_candidate)

        return str(target) if target.exists() else None

    def _serve_static_file(self, filepath: str, send_body: bool):
        try:
            file_size = os.path.getsize(filepath)
        except OSError:
            self.send_error(404, "File Inaccessible")
            return

        mime_type = self.guess_mime(filepath)
        range_header = self.headers.get("Range")

        # Full Request (200 OK)
        if not range_header:
            self.send_response(200)
            self.send_header("Content-Type", mime_type)
            self.send_header("Content-Length", str(file_size))
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()

            if send_body:
                self._stream_slice(filepath, start=0, length=file_size)
            return

        # RFC 7233 Range Request (206 Partial Content)
        match = RANGE_REGEX.match(range_header.strip())
        if not match:
            self._send_416(file_size)
            return

        raw_start, raw_end = match.groups()
        if raw_start and raw_end:
            start = int(raw_start)
            end = int(raw_end)
        elif raw_start:
            start = int(raw_start)
            end = file_size - 1
        elif raw_end:
            suffix_len = int(raw_end)
            start = max(0, file_size - suffix_len)
            end = file_size - 1
        else:
            self._send_416(file_size)
            return

        if start > end or start >= file_size or start < 0:
            self._send_416(file_size)
            return

        end = min(end, file_size - 1)
        content_length = (end - start) + 1

        self.send_response(206)
        self.send_header("Content-Type", mime_type)
        self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
        self.send_header("Content-Length", str(content_length))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()

        if send_body:
            self._stream_slice(filepath, start=start, length=content_length)

    def _send_416(self, file_size: int):
        self.send_response(416)
        self.send_header("Content-Range", f"bytes */{file_size}")
        self.send_header("Content-Length", "0")
        self.send_header("Connection", "close")
        self.end_headers()

    def _stream_slice(self, filepath: str, start: int, length: int):
        chunk_size = 65536
        remaining = length
        try:
            with open(filepath, "rb") as f:
                f.seek(start)
                while remaining > 0:
                    read_len = min(chunk_size, remaining)
                    data = f.read(read_len)
                    if not data:
                        break
                    self.wfile.write(data)
                    remaining -= len(data)
        except (BrokenPipeError, ConnectionResetError):
            pass


# ===========================================================================
# 3. BACKGROUND SERVER ORCHESTRATION
# ===========================================================================


class ThreadedServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


def start_background_server(
    host: str, start_port: int
) -> tuple[ThreadedServer, int, str]:
    max_attempts = 15
    for offset in range(max_attempts):
        candidate_port = start_port + offset
        try:
            server = ThreadedServer((host, candidate_port), KykloiVaultHandler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            url = f"http://{host}:{candidate_port}/"
            return server, candidate_port, url
        except OSError as e:
            if e.errno in (98, 48, 10048):
                continue
            raise
    raise RuntimeError(
        f"Unable to bind to an open port between {start_port} and {start_port + max_attempts - 1}"
    )


# ===========================================================================
# 4. COMPILER & NORMALIZER INVOCATION
# ===========================================================================


def execute_build(
    clean: bool = False,
    passphrase: str | None = None,
    log_file: str | None = None,
) -> int:
    logger = get_logger("launcher")
    cmd = [sys.executable, str(BUILD_SCRIPT)]
    if clean:
        cmd.append("--clean")
    if log_file:
        cmd.extend(["--log-file", log_file])

    env = os.environ.copy()
    if passphrase:
        env["KYKLOI_ENCRYPT_KEY"] = passphrase

    logger.info("Executing build: %s", " ".join(cmd))

    res = subprocess.run(cmd, cwd=str(ROOT_DIR), env=env)
    if res.returncode == 0:
        logger.info("Compilation process exited normally (code 0).")
    else:
        logger.error("Compilation process failed with exit code %d.", res.returncode)
    return res.returncode


def get_ledger_status_tag() -> str:
    """Returns a short formatted string detailing the state of vault-index.db."""
    if not NORM_DB_PATH.exists():
        return "Uninitialized"
    try:
        with VaultDB(NORM_DB_PATH) as db:
            files = db.get_all_files().values()
            docs = sum(1 for f in files if not f.is_media)
            media = sum(1 for f in files if f.is_media)
            return f"Indexed ({docs} notes, {media} assets)"
    except Exception:
        return "Degraded"


def print_crypto_diagnostics():
    engine_name, _ = _resolve_active_crypto_engine()
    is_pure_python = "Pure-Python" in engine_name

    print("\n================== KYKLOI CRYPTOGRAPHIC STATUS ==================")
    print(f"  Current Engine:     {engine_name}")
    print(
        f"  Execution Mode:     {'BASELINE FALLBACK (Unaccelerated)' if is_pure_python else 'HARDWARE ACCELERATED'}"
    )
    print(f"  Active Interpreter: {sys.executable}")
    print("=================================================================")

    if is_pure_python:
        print("\n[!] Pure-Python fallback is active. Build operations on large secure")
        print("    media files will experience reduced throughput (~1 MB/s).\n")
        print("    To enable hardware acceleration:")
        print(
            "    1. Ensure a standard host Python (>=3.10) is installed on your path."
        )
        print(
            "    2. Install the optional compiled primitive package in that environment:"
        )
        print("         pip install cryptography")
        print("       or:")
        print("         pip install pycryptodome\n")
    else:
        print("\n[+] System is fully optimized. Cryptographic operations will use")
        print("    native C-ABI / hardware intrinsics (AES-NI / NEON).\n")


def parse_args():
    p = argparse.ArgumentParser(description="Kykloi Vault Engine & Local Appliance.")
    p.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Bind interface (default: 127.0.0.1)",
    )
    p.add_argument("--port", type=int, default=8000, help="Base port (default: 8000)")
    p.add_argument("--build", action="store_true", help="Compile and exit immediately.")
    p.add_argument(
        "--clean",
        action="store_true",
        help="Perform clean rebuild when combined with --build.",
    )
    p.add_argument(
        "--password",
        type=str,
        default=os.environ.get("KYKLOI_ENCRYPT_KEY"),
        help="Passphrase for /secure/ notes.",
    )
    p.add_argument(
        "--normalize",
        action="store_true",
        help="Run interactive content normalization and exit.",
    )
    p.add_argument(
        "--auto-normalize",
        action="store_true",
        help="Run normalization automatically without confirmation prompts.",
    )
    p.add_argument(
        "--check-normalize",
        action="store_true",
        help="Audit vault: returns 0 if clean, 1 if anomalies/mutations are detected.",
    )
    p.add_argument(
        "--log-file",
        type=str,
        default=None,
        help="Path to persistent log file on disk.",
    )
    p.add_argument(
        "--verbose",
        action="store_true",
        help="Enable granular debug telemetry in console output.",
    )
    p.add_argument(
        "--crypto-info",
        action="store_true",
        help="Inspect active cryptographic acceleration engine and exit.",
    )
    return p.parse_args()


def pause_for_user(prompt: str = "\nPress Enter to return to the menu..."):
    """Pauses terminal output until the user presses Enter, handling SIGINT gracefully."""
    try:
        input(prompt)
    except (KeyboardInterrupt, EOFError):
        print()


def interactive_menu(
    vault_url: str,
    initial_password: str | None,
    log_file: str | None = None,
):
    session_password = initial_password
    logger = get_logger("menu")

    while True:
        vault_ready = DIST_DIR.exists() and any(DIST_DIR.iterdir())
        status_line = (
            f"Vault: Ready ({vault_url})" if vault_ready else "Vault: Not Compiled"
        )
        pw_status = "Set" if session_password else "Not Set"

        is_fallback = "Pure-Python" in ACTIVE_ENGINE_NAME
        crypto_tag = (
            f"{ACTIVE_ENGINE_NAME} [SLOW]" if is_fallback else ACTIVE_ENGINE_NAME
        )
        ledger_tag = get_ledger_status_tag()

        print("\n==================== KYKLOI CONTROL PLANE ====================")
        print(f"  Status:     {status_line}")
        print(f"  Passphrase: [{pw_status}]")
        print(f"  Ledger:     [{ledger_tag}]")
        print(f"  Crypto:     [{crypto_tag}]")
        print("==============================================================")
        print("  [1] Compile Site (Incremental)")
        print("  [2] Rebuild Site (Clean Purge)")
        print("  [3] Normalize Vault (Reconcile Links & Filenames)")
        print("  [4] Audit Vault Health (Check & Collision Audit)")
        print("  [5] Set / Update Secure Passphrase")
        print("  [6] Open Vault in Default Browser")
        print("  [7] Cryptographic Acceleration Diagnostics")
        print("  [0] Exit")
        print("==============================================================")

        try:
            choice = input("Select an option [0-7]: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n")
            break

        if choice == "1":
            execute_build(clean=False, passphrase=session_password, log_file=log_file)
            pause_for_user()
        elif choice == "2":
            execute_build(clean=True, passphrase=session_password, log_file=log_file)
            pause_for_user()
        elif choice == "3":
            logger.info("Initiating vault normalization pipeline...")
            run_normalization_pipeline(
                content_root=CONTENT_DIR,
                db_path=NORM_DB_PATH,
                dry_run=False,
                auto_apply=False,
                check_only=False,
            )
            pause_for_user()
        elif choice == "4":
            logger.info("Auditing vault structure and links...")
            run_normalization_pipeline(
                content_root=CONTENT_DIR,
                db_path=NORM_DB_PATH,
                dry_run=True,
                auto_apply=False,
                check_only=True,
            )
            pause_for_user()
        elif choice == "5":
            import getpass

            try:
                pw = getpass.getpass(
                    "Enter passphrase for /secure/ notes (leave empty to clear): "
                )
                session_password = pw.strip() or None
                if session_password:
                    logger.info("Passphrase stored in active session memory.")
                else:
                    logger.info("Passphrase cleared.")
            except (KeyboardInterrupt, EOFError):
                print()
                logger.warning("Passphrase input aborted by user.")
            pause_for_user()
        elif choice == "6":
            if not vault_ready:
                logger.warning("Vault must be compiled before opening in browser.")
            else:
                logger.info("Opening browser target: %s", vault_url)
                webbrowser.open(vault_url)
            pause_for_user()
        elif choice == "7":
            print_crypto_diagnostics()
            pause_for_user()
        elif choice == "0":
            break
        else:
            logger.warning("Unrecognized menu option: %s", choice)
            pause_for_user()


def main():
    args = parse_args()

    if args.crypto_info:
        print_crypto_diagnostics()
        sys.exit(0)

    log_file_path = Path(args.log_file).resolve() if args.log_file else None
    logger = setup_logging(
        subsystem="launcher",
        verbose=args.verbose,
        log_file=log_file_path,
        enable_console=True,
    )

    # CLI direct execution routes
    if args.normalize or args.auto_normalize or args.check_normalize:
        code = run_normalization_pipeline(
            content_root=CONTENT_DIR,
            db_path=NORM_DB_PATH,
            dry_run=False,
            auto_apply=args.auto_normalize,
            check_only=args.check_normalize,
        )
        sys.exit(code)

    if args.build:
        code = execute_build(
            clean=args.clean,
            passphrase=args.password,
            log_file=args.log_file,
        )
        sys.exit(code)

    try:
        server, port, vault_url = start_background_server(args.host, args.port)
        logger.info("Vault daemon online at %s (bound to port %d)", vault_url, port)
    except Exception as err:
        logger.critical("Local static server failed to bind: %s", err)
        sys.exit(1)

    try:
        interactive_menu(vault_url, args.password, log_file=args.log_file)
    finally:
        logger.info("Shutting down vault server daemon...")
        server.shutdown()
        server.server_close()
        logger.info("Daemon cleanly terminated.")


if __name__ == "__main__":
    main()
```

## system/logger.py

```python
"""
system/logger.py - Centralized Telemetry and Logging Engine for Project Kykloi.
Provides ANSI colorized terminal streams, persistent file sinks, routine tracing,
and threshold-triggered FIFO log truncation (in-place halving).
"""

import contextlib
import logging
import os
import sys
import time
from pathlib import Path
from typing import Optional

# Enable Virtual Terminal Processing on Windows 10+ for ANSI escape codes
if sys.platform == "win32":
    os.system("")

DEFAULT_LOG_FILE = Path(__file__).resolve().parent / "kykloi.log"
DEFAULT_MAX_BYTES = 5 * 1024 * 1024  # 5 MiB threshold
DEFAULT_PRUNE_RATIO = 0.5  # Retain newest 50% when threshold is breached


class AnsiColorFormatter(logging.Formatter):
    """Formats log records with ANSI colors for interactive terminal displays."""

    RESET = "\033[0m"
    DIM = "\033[2m"
    BOLD = "\033[1m"

    COLORS = {
        logging.DEBUG: "\033[36m",  # Cyan
        logging.INFO: "\033[32m",  # Green
        logging.WARNING: "\033[33m",  # Yellow
        logging.ERROR: "\033[31m",  # Red
        logging.CRITICAL: "\033[1;31m",  # Bold Red
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelno, self.RESET)
        time_str = self.formatTime(record, "%H:%M:%S")
        name = record.name
        if name.startswith("kykloi."):
            name = name[7:]

        lvl_name = f"{record.levelname:<5}"
        prefix = f"{self.DIM}[{time_str}]{self.RESET} {color}{lvl_name}{self.RESET} {self.DIM}[{name}]{self.RESET}"
        message = record.getMessage()

        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            message = f"{message}\n{record.exc_text}"
        if record.stack_info:
            message = f"{message}\n{self.formatStack(record.stack_info)}"

        return f"{prefix} {message}"


class PlainFileFormatter(logging.Formatter):
    """Deterministic plain-text formatter for file logging with ISO-8601 timestamps."""

    def format(self, record: logging.LogRecord) -> str:
        time_str = self.formatTime(record, "%Y-%m-%d %H:%M:%S")
        lvl_name = f"{record.levelname:<8}"
        name = record.name
        message = record.getMessage()

        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            message = f"{message}\n{record.exc_text}"
        if record.stack_info:
            message = f"{message}\n{self.formatStack(record.stack_info)}"

        return f"{time_str} | {lvl_name} | {name:<24} | {message}"


class HalfPruningFileHandler(logging.FileHandler):
    """
    Append-only file handler that monitors file size and atomically purges the oldest
    records when a defined capacity threshold is reached, retaining approximately half
    of the newest log output aligned to line boundaries.
    """

    def __init__(
        self,
        filename: Path | str,
        mode: str = "a",
        encoding: str = "utf-8",
        delay: bool = False,
        max_bytes: int = DEFAULT_MAX_BYTES,
        prune_ratio: float = DEFAULT_PRUNE_RATIO,
    ):
        super().__init__(filename, mode=mode, encoding=encoding, delay=delay)
        self.max_bytes = max_bytes
        self.prune_ratio = min(max(prune_ratio, 0.1), 0.9)

    def should_prune(self) -> bool:
        """Determines whether the physical log file size exceeds the threshold."""
        if self.max_bytes <= 0:
            return False
        try:
            return os.path.getsize(self.baseFilename) >= self.max_bytes
        except OSError:
            return False

    def do_prune(self) -> None:
        """
        Closes current stream, seeks past the oldest entries to the next clean newline,
        writes the preserved segment to a temporary file, and performs an atomic replace.
        """
        if self.stream is not None:
            self.stream.flush()
            self.stream.close()
            self.stream = None

        try:
            current_size = os.path.getsize(self.baseFilename)
            if current_size < self.max_bytes:
                return

            cutoff = int(current_size * (1.0 - self.prune_ratio))
            with open(self.baseFilename, "rb") as src:
                src.seek(cutoff)
                # Discard the partial line fragment at the cut boundary
                src.readline()
                retained_bytes = src.read()

            tmp_target = Path(self.baseFilename).with_suffix(".prune.tmp")
            with open(tmp_target, "wb") as dst:
                prune_notice = (
                    f"--- [KYKLOI LOG PRUNED: {current_size} bytes -> {len(retained_bytes)} bytes] ---\n"
                ).encode(self.encoding or "utf-8")
                dst.write(prune_notice)
                dst.write(retained_bytes)

            tmp_target.replace(self.baseFilename)
        except OSError:
            pass
        finally:
            self.stream = self._open()

    def emit(self, record: logging.LogRecord) -> None:
        """Emits a record, executing size verification and conditional truncation first."""
        try:
            if self.should_prune():
                self.do_prune()
            super().emit(record)
        except Exception:
            self.handleError(record)


def setup_logging(
    subsystem: str = "core",
    verbose: bool = False,
    log_file: Optional[Path] = None,
    enable_console: bool = True,
    max_bytes: Optional[int] = None,
    prune_ratio: float = DEFAULT_PRUNE_RATIO,
) -> logging.Logger:
    """Configures the root Kykloi logger with console and pruning file handlers."""
    root_logger = logging.getLogger("kykloi")
    root_logger.setLevel(logging.DEBUG)

    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
        console_handler.setFormatter(AnsiColorFormatter())
        root_logger.addHandler(console_handler)

    target_log_file = log_file if log_file is not None else DEFAULT_LOG_FILE
    if target_log_file:
        target_log_file.parent.mkdir(parents=True, exist_ok=True)

        # Allow environment configuration override if parameter not explicitly set
        effective_max_bytes = max_bytes
        if effective_max_bytes is None:
            env_val = os.environ.get("KYKLOI_LOG_MAX_BYTES")
            effective_max_bytes = (
                int(env_val) if env_val and env_val.isdigit() else DEFAULT_MAX_BYTES
            )

        file_handler = HalfPruningFileHandler(
            target_log_file,
            mode="a",
            encoding="utf-8",
            max_bytes=effective_max_bytes,
            prune_ratio=prune_ratio,
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(PlainFileFormatter())
        root_logger.addHandler(file_handler)

    return logging.getLogger(f"kykloi.{subsystem}")


def get_logger(subsystem: str) -> logging.Logger:
    """Retrieves a scoped child logger."""
    return logging.getLogger(f"kykloi.{subsystem}")


@contextlib.contextmanager
def timed_step(logger: logging.Logger, operation_name: str, level: int = logging.INFO):
    """Context manager for tracing operational subroutines with duration telemetry."""
    start_time = time.perf_counter()
    logger.log(level, "STARTED: %s", operation_name)
    try:
        yield
        elapsed = (time.perf_counter() - start_time) * 1000.0
        logger.log(level, "FINISHED: %s (%.2f ms)", operation_name, elapsed)
    except Exception as err:
        elapsed = (time.perf_counter() - start_time) * 1000.0
        logger.error("FAILED: %s after %.2f ms: %s", operation_name, elapsed, err)
        raise
```

## .gitignore

```
# Python-generated files
__pycache__/
*.py[oc]
wheels/
*.egg-info

# Virtual environments
.venv

# Project binaries
system/tools/archives/*.tar.gz
system/tools/archives/*.zip
!system/tools/archives/.gitkeep
```

## launch.bat

```bat
@echo off
setlocal enabledelayedexpansion

:: ---------------------------------------------------------------------------
:: 0. PARSE CLI FLAGS (e.g. --force-fallback)
:: ---------------------------------------------------------------------------
set "PASSTHROUGH_ARGS="

:parse_args
if "%~1"=="" goto :done_parse_args
if /i "%~1"=="--force-fallback" (
    set "KYKLOI_FORCE_FALLBACK=1"
) else (
    set "PASSTHROUGH_ARGS=!PASSTHROUGH_ARGS! %1"
)
shift
goto :parse_args
:done_parse_args

:: ---------------------------------------------------------------------------
:: 1. CONFIGURATION & VERSION CONSTRAINTS
:: ---------------------------------------------------------------------------
if "%REQ_MAJ%"=="" set "REQ_MAJ=3"
if "%REQ_MIN%"=="" set "REQ_MIN=10"

set "USE_HOST=0"

:: ---------------------------------------------------------------------------
:: 2. EVALUATE HOST PYTHON (Bypassed if KYKLOI_FORCE_FALLBACK=1)
:: ---------------------------------------------------------------------------
if not "%KYKLOI_FORCE_FALLBACK%"=="1" (
    where python >nul 2>&1
    if !ERRORLEVEL! equ 0 (
        set "HOST_MAJOR="
        set "HOST_MINOR="
        for /f "tokens=1,2 delims=." %%a in ('python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2^>nul') do (
            set "HOST_MAJOR=%%a"
            set "HOST_MINOR=%%b"
        )
        if defined HOST_MAJOR if defined HOST_MINOR (
            if "!HOST_MAJOR!"=="%REQ_MAJ%" (
                if !HOST_MINOR! geq %REQ_MIN% (
                    set "USE_HOST=1"
                )
            )
        )
    )
)

if "%USE_HOST%"=="1" goto :run_host_python
goto :skip_host_python

:run_host_python
for /f "delims=" %%i in ('where python') do (
    set "HOST_PATH=%%i"
    goto :host_resolved
)
:host_resolved
echo [Kykloi] Using host Python runtime: !HOST_PATH! (!HOST_MAJOR!.!HOST_MINOR!)
python system\launch.py %PASSTHROUGH_ARGS%
exit /b %ERRORLEVEL%

:skip_host_python

:: ---------------------------------------------------------------------------
:: 3. HYDRATE RUNTIME FROM LOCAL ARCHIVE (WITH SHA-256 VERIFICATION)
:: ---------------------------------------------------------------------------
set "SCRIPT_DIR=%~dp0"

:: Architecture Detection (x86_64 vs ARM64)
set "TARGET=windows-x86_64"
if /i "%PROCESSOR_ARCHITECTURE%"=="ARM64" set "TARGET=windows-arm64"
if /i "%PROCESSOR_ARCHITEW6432%"=="ARM64" set "TARGET=windows-arm64"

set "MANIFEST_PATH=%SCRIPT_DIR%system\tools\tools-manifest.json"
set "RUNTIME_ROOT=%TEMP%\kykloi_runtime_%TARGET%"
set "LOCAL_PY=%RUNTIME_ROOT%\python.exe"
set "STAMP_FILE=%RUNTIME_ROOT%\.verified_sha256"

if not exist "%LOCAL_PY%" goto :hydrate_runtime
if not exist "%STAMP_FILE%" goto :hydrate_runtime
goto :execute_runtime

:hydrate_runtime
if not exist "%MANIFEST_PATH%" (
    echo [FATAL] Tool manifest missing: %MANIFEST_PATH%
    pause
    exit /b 1
)

echo [Kykloi] Querying manifest definitions for %TARGET%...
:: Atomic single-process extraction to avoid multi-invocation latency
for /f "usebackq tokens=1,2 delims=|" %%A in (`powershell -NoProfile -Command "$m=(Get-Content -Raw '%MANIFEST_PATH%' | ConvertFrom-Json).tools.python.targets.'%TARGET%'; if($m){Write-Output ($m.archive + '|' + $m.sha256)}" 2^>nul`) do (
    set "ARCHIVE_NAME=%%A"
    set "EXPECTED_SHA=%%B"
)

if "%ARCHIVE_NAME%"=="" (
    echo [FATAL] Failed to extract manifest parameters for target %TARGET%
    pause
    exit /b 1
)

set "ARCHIVE_PY=%SCRIPT_DIR%system\tools\archives\%ARCHIVE_NAME%"

if not exist "%ARCHIVE_PY%" (
    echo [FATAL] Pre-packaged archive not found: %ARCHIVE_NAME%
    echo         Expected at: %ARCHIVE_PY%
    pause
    exit /b 1
)

echo [Kykloi] Verifying SHA-256 checksum for %ARCHIVE_NAME%...
for /f "skip=1 tokens=*" %%H in ('certutil -hashfile "%ARCHIVE_PY%" SHA256 2^>nul') do (
    set "RAW_HASH=%%H"
    goto :hash_extracted
)
:hash_extracted
set "ACTUAL_SHA=!RAW_HASH: =!"

if /i not "!ACTUAL_SHA!"=="!EXPECTED_SHA!" (
    echo [FATAL] Checksum verification failed for %ARCHIVE_NAME%
    echo         Expected: !EXPECTED_SHA!
    echo         Actual:   !ACTUAL_SHA!
    pause
    exit /b 1
)

echo [Kykloi] Checksum verified. Extracting portable Python runtime to %RUNTIME_ROOT%...
if exist "%RUNTIME_ROOT%" rmdir /s /q "%RUNTIME_ROOT%" >nul 2>&1
mkdir "%RUNTIME_ROOT%" >nul 2>&1
tar -xzf "%ARCHIVE_PY%" -C "%RUNTIME_ROOT%" --strip-components=1
<nul set /p="!ACTUAL_SHA!" > "%STAMP_FILE%"

:execute_runtime

:: ---------------------------------------------------------------------------
:: 4. EXECUTE APPLICATION LAUNCHER
:: ---------------------------------------------------------------------------
echo [Kykloi] Using fallback Python runtime: %LOCAL_PY%
"%LOCAL_PY%" "%SCRIPT_DIR%system\launch.py" %PASSTHROUGH_ARGS%
exit /b %ERRORLEVEL%
```

## launch.sh

```bash
#!/usr/bin/env sh
set -e

REQ_MAJ="${REQ_MAJ:-3}"
REQ_MIN="${REQ_MIN:-10}"

# ---------------------------------------------------------------------------
# 0. PARSE CLI FLAGS (e.g. --force-fallback)
# ---------------------------------------------------------------------------
for arg; do
  if [ "$arg" = "--force-fallback" ]; then
    KYKLOI_FORCE_FALLBACK=1
  else
    set -- "$@" "$arg"
  fi
  shift
done

# ---------------------------------------------------------------------------
# 1. EVALUATE HOST PYTHON
# ---------------------------------------------------------------------------
USE_HOST_PY=0

if [ "${KYKLOI_FORCE_FALLBACK}" != "1" ] && command -v python3 >/dev/null 2>&1; then
  PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "0.0")
  MAJ=$(echo "$PY_VER" | cut -d. -f1)
  MIN=$(echo "$PY_VER" | cut -d. -f2)
  if [ "$MAJ" -eq "$REQ_MAJ" ] && [ "$MIN" -ge "$REQ_MIN" ]; then
    USE_HOST_PY=1
  fi
fi

if [ "$USE_HOST_PY" -eq 1 ]; then
  echo "[Kykloi] Using host Python runtime: $(which python3) (${PY_VER})"
  exec python3 system/launch.py "$@"
fi

# ---------------------------------------------------------------------------
# 2. RESOLVE PLATFORM TARGET IDENTIFIER (GNU vs MUSL DETECTION)
# ---------------------------------------------------------------------------
OS="$(uname -s)"
ARCH="$(uname -m)"

detect_linux_libc() {
  # 1. Allow explicit user override
  if [ -n "$KYKLOI_LIBC" ]; then
    echo "$KYKLOI_LIBC"
    return
  fi

  # 2. Check for glibc via getconf (standard on Fedora, Debian, Ubuntu, etc.)
  if getconf GNU_LIBC_VERSION >/dev/null 2>&1; then
    echo "gnu"
    return
  fi

  # 3. Check ldd signature
  if ldd --version 2>&1 | grep -iq "glibc\|gnu"; then
    echo "gnu"
    return
  fi

  if ldd --version 2>&1 | grep -iq "musl"; then
    echo "musl"
    return
  fi

  # 4. Check for dynamic linkers in /lib or /lib64
  if ls /lib/ld-musl-*.so* >/dev/null 2>&1 || ls /lib64/ld-musl-*.so* >/dev/null 2>&1; then
    echo "musl"
    return
  fi

  # 5. Default to GNU
  echo "gnu"
}

case "$OS" in
Linux)
  LIBC="$(detect_linux_libc)"
  case "$ARCH" in
  x86_64)
    if [ "$LIBC" = "musl" ]; then
      TARGET="linux-x86_64-musl"
    else
      TARGET="linux-x86_64"
    fi
    ;;
  aarch64 | arm64)
    if [ "$LIBC" = "musl" ]; then
      TARGET="linux-arm64-musl"
    else
      TARGET="linux-arm64"
    fi
    ;;
  *)
    echo "[FATAL] Unsupported Linux architecture: $ARCH" >&2
    exit 1
    ;;
  esac
  ;;
Darwin)
  case "$ARCH" in
  x86_64) TARGET="macos-x86_64" ;;
  arm64) TARGET="macos-arm64" ;;
  *)
    echo "[FATAL] Unsupported macOS architecture: $ARCH" >&2
    exit 1
    ;;
  esac
  ;;
*)
  echo "[FATAL] Unsupported operating system: $OS" >&2
  exit 1
  ;;
esac

# ---------------------------------------------------------------------------
# 3. HYDRATE RUNTIME TO LOCAL STORAGE (WITH SHA-256 VERIFICATION)
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MANIFEST_PATH="$SCRIPT_DIR/system/tools/tools-manifest.json"

# Prioritize persistent user cache over /tmp to prevent noexec mount execution traps
if [ -n "$XDG_CACHE_HOME" ] && [ -w "$XDG_CACHE_HOME" ]; then
  BASE_RUNTIME="$XDG_CACHE_HOME"
elif [ -n "$HOME" ] && [ -w "$HOME" ]; then
  mkdir -p "$HOME/.cache" 2>/dev/null || true
  if [ -d "$HOME/.cache" ] && [ -w "$HOME/.cache" ]; then
    BASE_RUNTIME="$HOME/.cache"
  else
    BASE_RUNTIME="/tmp"
  fi
else
  BASE_RUNTIME="/tmp"
fi

RUNTIME_ROOT="${BASE_RUNTIME}/kykloi_runtime_${TARGET}"
LOCAL_PY="$RUNTIME_ROOT/bin/python3"
STAMP_FILE="$RUNTIME_ROOT/.verified_sha256"

compute_sha256() {
  target_file="$1"
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$target_file" | cut -d' ' -f1
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$target_file" | cut -d' ' -f1
  elif command -v openssl >/dev/null 2>&1; then
    openssl dgst -sha256 "$target_file" | awk '{print $NF}'
  else
    echo "[FATAL] No SHA-256 verification utility (sha256sum, shasum, openssl) available." >&2
    exit 1
  fi
}

extract_python_field() {
  target="$1"
  field="$2"
  manifest="$3"
  awk -v tgt="$target" -v fld="$field" '
        BEGIN { in_py=0; in_tgt=0 }
        /"python"[[:space:]]*:/ { in_py=1; next }
        in_py && $0 ~ "\"" tgt "\"[[:space:]]*:" { in_tgt=1; next }
        in_tgt && $0 ~ "\"" fld "\"[[:space:]]*:" {
            sub(/.*"[^"]+"[[:space:]]*:[[:space:]]*"/, "")
            sub(/".*/, "")
            print $0
            exit
        }
        in_tgt && /}[[:space:]]*,?[[:space:]]*$/ { in_tgt=0 }
    ' "$manifest"
}

if [ ! -f "$LOCAL_PY" ] || [ ! -f "$STAMP_FILE" ]; then
  if [ ! -f "$MANIFEST_PATH" ]; then
    echo "[FATAL] Verification manifest missing at: $MANIFEST_PATH" >&2
    exit 1
  fi

  ARCHIVE_NAME=$(extract_python_field "$TARGET" "archive" "$MANIFEST_PATH")
  EXPECTED_SHA=$(extract_python_field "$TARGET" "sha256" "$MANIFEST_PATH")

  if [ -z "$ARCHIVE_NAME" ] || [ -z "$EXPECTED_SHA" ]; then
    echo "[FATAL] Target ${TARGET} not found in manifest python definitions." >&2
    exit 1
  fi

  ARCHIVE_PY="$SCRIPT_DIR/system/tools/archives/$ARCHIVE_NAME"

  if [ ! -f "$ARCHIVE_PY" ]; then
    echo "[FATAL] Pre-packaged archive not found: $ARCHIVE_NAME" >&2
    echo "        Expected at: $ARCHIVE_PY" >&2
    exit 1
  fi

  echo "[Kykloi] Verifying SHA-256 for $ARCHIVE_NAME..."
  ACTUAL_SHA=$(compute_sha256 "$ARCHIVE_PY")

  if [ "$ACTUAL_SHA" != "$EXPECTED_SHA" ]; then
    echo "[FATAL] Checksum verification failed for $ARCHIVE_NAME" >&2
    echo "        Expected: $EXPECTED_SHA" >&2
    echo "        Actual:   $ACTUAL_SHA" >&2
    exit 1
  fi

  echo "[Kykloi] Checksum verified. Extracting portable Python runtime to $RUNTIME_ROOT..."
  rm -rf "$RUNTIME_ROOT"
  mkdir -p "$RUNTIME_ROOT"
  tar -xzf "$ARCHIVE_PY" -C "$RUNTIME_ROOT" --strip-components=1
  printf "%s" "$ACTUAL_SHA" >"$STAMP_FILE"

  if [ "$OS" = "Darwin" ]; then
    xattr -dr com.apple.quarantine "$RUNTIME_ROOT" 2>/dev/null || true
  fi
fi

# ---------------------------------------------------------------------------
# 4. EXECUTE APPLICATION LAUNCHER
# ---------------------------------------------------------------------------
echo "[Kykloi] Using fallback Python runtime: $LOCAL_PY"
exec "$LOCAL_PY" "$SCRIPT_DIR/system/launch.py" "$@"
```

## pyproject.toml

```toml
[project]
name = "Kykloi"
version = "0.7.0"
description = "Deterministic Archival Knowlege Management and SSG"
readme = "README.md"
requires-python = ">=3.10"
dependencies = []
```

## README.md

```md
# Kykloi

*This README is yet to be developed but in the meantime will contain bits of context as reminders and key points for inclusion in documentation later.*

## Contextual Tidbits

* Metadata inclusion from secure notes are included to maintain search functionality, but the note bodies are intended to be relatively secure.
* The primary threat model intended to be mitigated on secure pages is to prevent casual browsing and bot ingestion, and minor security threats. This is not intended to prevent motivated, high resource security threats, and if such a level of security is desired, such information should **not** be posted to the public internet or under highly secure access control only.
```
