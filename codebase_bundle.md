# Project Directory Tree

```text
kykloi/
├── .git/ (contents excluded)
├── .github/ (contents excluded)
├── .venv/ (contents excluded)
├── content/
│   ├── 202611/
│   │   ├── 20261109130247-project_kykloi_task_list.md
│   │   └── 20261109171348-geminis_codebase_impression.md
│   ├── media/
│   │   └── test_artemis_2.jpg
│   ├── secure/
│   │   ├── media/
│   │   │   └── test_artemis_2.jpg
│   │   └── 20261031165927-nested-directory-test.md
│   └── pandoc_markdown.md
├── dist/ (contents excluded)
├── system/
│   ├── build/
│   │   ├── __pycache__/ (contents excluded)
│   │   ├── assets/
│   │   │   ├── css/
│   │   │   │   ├── pico.css
│   │   │   │   └── style.css
│   │   │   ├── fonts/ (contents excluded)
│   │   │   ├── js/
│   │   │   │   ├── decrypt.js
│   │   │   │   ├── pico_search.js
│   │   │   │   ├── search_worker.js
│   │   │   │   ├── sqlite3.js
│   │   │   │   └── sqlite3.wasm
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
│   │   │   └── md_to_static_html.html
│   │   ├── .build_manifest.json
│   │   ├── build_site.py
│   │   ├── pandoc_md_to_static_html.yaml
│   │   └── translate_links.lua
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
│   │   ├── tools_manifest.json
│   │   └── verify_manifest.py
│   └── launch.py
├── .gitignore
├── .python-version
├── assemble_code_to_md.py
├── author_context.md
├── hash_generator.py
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
    max-width: 65ch;
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
      const blockedTags = ["SCRIPT", "IFRAME", "OBJECT", "EMBED"];

      doc.querySelectorAll("*").forEach((el) => {
        if (blockedTags.includes(el.tagName)) {
          el.remove();
          return;
        }
        for (let i = el.attributes.length - 1; i >= 0; i--) {
          const attr = el.attributes[i];
          const name = attr.name.toLowerCase();
          const val = attr.value.trim().toLowerCase();
          if (
            name.startsWith("on") ||
            (name === "href" && val.startsWith("javascript:")) ||
            (name === "src" && val.startsWith("javascript:"))
          ) {
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

## system/build/assets/js/pico_search.js

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
        <script src="assets/js/pico_search.js" defer></script>
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

## system/build/templates/md_to_static_html.html

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

## system/build/build_site.py

```python
#!/usr/bin/env python3
"""
system/build/build_site.py - Zero-Dependency Deterministic SSG Compiler.
Part of Project Kykloi (v0.5.0).
"""

import argparse
import base64
import concurrent.futures
import getpass
import hashlib
import json
import logging
import os
import platform
import re
import shutil
import sqlite3
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# ===========================================================================
# 1. PURE-PYTHON AES-256-GCM ENGINE & TABLE-DRIVEN GHASH
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
) -> tuple[bytes, bytes]:
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


def verify_cryptographic_engine():
    kat_key = bytes.fromhex("00" * 32)
    kat_iv = bytes.fromhex("00" * 12)
    kat_pt = bytes.fromhex("00" * 16)
    expected_ct = bytes.fromhex("cea7403d4d606b6e074ec5d3baf39d18")
    expected_tag = bytes.fromhex("d0d1c8a799996bf0265b98b5d48ab919")

    ct, tag = pure_aes_gcm_encrypt(kat_key, kat_iv, kat_pt)
    if ct != expected_ct or tag != expected_tag:
        raise RuntimeError("CRITICAL: NIST KAT verification failed for AES-GCM engine.")


# ===========================================================================
# 2. PATHS & HYGIENE
# ===========================================================================

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


def is_junk_path(path: Path, root: Optional[Path] = None) -> bool:
    base = root if root is not None else PROJECT_ROOT
    try:
        rel_parts = path.relative_to(base).parts
    except ValueError:
        rel_parts = path.parts
    for part in rel_parts:
        if part.lower() in JUNK_DIR_NAMES or part.startswith("."):
            return True
    return path.name.lower() in JUNK_FILE_EXTENSIONS


APP_DIR = Path(__file__).resolve().parent
SYSTEM_DIR = APP_DIR.parent
PROJECT_ROOT = SYSTEM_DIR.parent
SRC = PROJECT_ROOT / "content"
DST = PROJECT_ROOT / "dist"

DEFAULTS_YAML = APP_DIR / "pandoc_md_to_static_html.yaml"
DEFAULT_TEMPLATE = APP_DIR / "templates" / "md_to_static_html.html"
LUA_FILTER = APP_DIR / "translate_links.lua"
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
    return p.parse_args()


# ===========================================================================
# 3. BINARY RESOLUTION & CRYPTOGRAPHIC UTILITIES
# ===========================================================================


def resolve_pandoc_binary(root_dir: Path) -> str:
    """Resolves the Pandoc executable.
    1. Checks hydrated temporary runtime directory (hermetic determinism).
    2. Hydrates on demand from system/tools/archives/ if present.
    3. Falls back to host system PATH only if no local archive exists.
    """
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
    manifest_path = root_dir / "system" / "tools" / "tools_manifest.json"

    if system == "windows":
        runtime_dir = Path(os.environ.get("TEMP", "/tmp")) / f"kykloi_runtime_{target}"
        pandoc_bin = runtime_dir / "pandoc.exe"
    else:
        runtime_dir = Path(f"/tmp/kykloi_runtime_{target}")
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

    if archive_path.is_file():
        logging.info("Verifying SHA-256 for %s...", archive_path.name)
        actual_hash = compute_file_hash(archive_path)
        if actual_hash != expected_hash:
            raise ValueError(
                f"SHA-256 mismatch for {archive_path.name}:\n"
                f"  Expected: {expected_hash}\n"
                f"  Actual:   {actual_hash}"
            )

        logging.info(
            "Hydrating Pandoc from %s to %s...", archive_path.name, runtime_dir
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


def is_secure_path(path: Path, src_root: Path) -> bool:
    try:
        rel = path.relative_to(src_root)
        return "secure" in rel.parts
    except ValueError:
        return False


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
    ciphertext, tag = pure_aes_gcm_encrypt(key, iv, pt_bytes)
    envelope = salt + iv + ciphertext + tag
    return base64.b64encode(envelope).decode("ascii")


def encrypt_binary_file(src_path: Path, dst_path: Path, passphrase: str) -> None:
    with open(src_path, "rb") as f:
        plaintext = f.read()

    salt = os.urandom(16)
    iv = os.urandom(12)
    key = derive_key(passphrase, salt)
    ciphertext, tag = pure_aes_gcm_encrypt(key, iv, plaintext)
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
# 4. FRONTMATTER & METADATA-ONLY SQLITE FTS5
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
        logging.warning("Error reading %s: %s", md_path.name, err)

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
        logging.info(
            "Compiled SQLite FTS5 index (%d records, %d bytes).",
            len(records),
            out_path.stat().st_size,
        )

    except Exception:
        if tmp_path.exists():
            tmp_path.unlink()
        raise


# ===========================================================================
# 5. COMPILATION WORKERS
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


# ===========================================================================
# 6. PIPELINE ORCHESTRATION
# ===========================================================================


def find_vault_bibliography(src_root: Path) -> Optional[Path]:
    for candidate in ["references.bib", "library.bib", "bibliography.bib"]:
        p = src_root / candidate
        if p.is_file():
            return p
    return None


def main():
    args = parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    try:
        verify_cryptographic_engine()
    except RuntimeError as err:
        logging.critical(str(err))
        sys.exit(1)

    try:
        pandoc_bin = resolve_pandoc_binary(PROJECT_ROOT)
        logging.info("Resolved Pandoc executable: %s", pandoc_bin)
    except FileNotFoundError as err:
        logging.critical(str(err))
        sys.exit(1)

    for path, desc in [
        (SRC, "Source directory"),
        (DEFAULTS_YAML, "Pandoc defaults configuration"),
        (DEFAULT_TEMPLATE, "Content template"),
        (LUA_FILTER, "Lua link translation filter"),
    ]:
        if not path.exists():
            logging.error("Configuration error: %s missing at %s", desc, path)
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
        logging.info("Core templates/configurations modified. Recompiling site.")

    expected_outputs: set[Path] = set()
    compile_tasks: list[CompileTask] = []
    encrypt_blob_tasks: list[EncryptBlobTask] = []

    all_content_files = [
        p for p in SRC.rglob("*") if p.is_file() and not is_junk_path(p)
    ]
    md_files = sorted([p for p in all_content_files if p.suffix.lower() == ".md"])

    has_secure_files = any(is_secure_path(p, SRC) for p in all_content_files)

    passphrase = args.password
    if has_secure_files and not passphrase and not args.dry_run:
        if not sys.stdin.isatty():
            logging.error(
                "Passphrase required for /secure/ notes in non-interactive environment. "
                "Provide --password or set KYKLOI_ENCRYPT_KEY."
            )
            sys.exit(1)

        try:
            passphrase = getpass.getpass("Enter passphrase for /secure/ notes: ")
        except (OSError, EOFError):
            logging.error("Terminal disconnected: Unable to prompt for passphrase.")
            sys.exit(1)

        if not passphrase:
            logging.error("Passphrase required for secure notes.")
            sys.exit(1)

    passphrase_changed = False
    if has_secure_files and passphrase:
        current_key_fingerprint = compute_passphrase_fingerprint(passphrase)
        new_manifest["__PASSPHRASE_FINGERPRINT__"] = current_key_fingerprint
        old_key_fingerprint = old_manifest.get("__PASSPHRASE_FINGERPRINT__")
        if old_manifest and old_key_fingerprint != current_key_fingerprint:
            passphrase_changed = True
            logging.info("Passphrase rotation detected. Re-encrypting payloads.")

    asset_sync_jobs: list[tuple[Path, Path]] = []

    for p in all_content_files:
        if p.suffix.lower() == ".md":
            continue

        rel_src = p.relative_to(SRC)
        h = compute_file_hash(p)

        if is_secure_path(p, SRC):
            target = DST / rel_src.with_name(rel_src.name + ".enc")
            expected_outputs.add(target.resolve())
            manifest_key = f"secure_blob:{rel_src.as_posix()}"
            new_manifest[manifest_key] = h

            if (
                not target.exists()
                or passphrase_changed
                or old_manifest.get(manifest_key) != h
            ):
                encrypt_blob_tasks.append(
                    EncryptBlobTask(
                        src_path=p,
                        dst_path=target,
                        passphrase=passphrase or "",
                        dry_run=args.dry_run,
                    )
                )
        else:
            target = DST / rel_src
            expected_outputs.add(target.resolve())
            manifest_key = f"media:{rel_src.as_posix()}"
            new_manifest[manifest_key] = h
            if not target.exists() or old_manifest.get(manifest_key) != h:
                asset_sync_jobs.append((p, target))

    metadata_extraction_jobs: list[Path] = []
    file_metadata_map: dict[Path, dict[str, str]] = {}
    doc_has_citations_map: dict[Path, bool] = {}

    for md in md_files:
        rel = md.relative_to(SRC)
        manifest_key = f"content:{rel.as_posix()}"
        meta_cache_key = f"meta:{rel.as_posix()}"
        out = DST / rel.with_suffix(".html")
        expected_outputs.add(out.resolve())

        current_md_hash = compute_file_hash(md)
        new_manifest[manifest_key] = current_md_hash

        depth = len(rel.parent.parts) if rel.parent != Path(".") else 0
        relative_root = ("../" * depth) if depth > 0 else ""

        is_secure = is_secure_path(md, SRC)
        md_content_changed = old_manifest.get(manifest_key) != current_md_hash

        is_dirty = (
            not out.exists()
            or global_deps_changed
            or md_content_changed
            or (is_secure and passphrase_changed)
        )

        cached_meta = old_manifest.get(meta_cache_key)
        meta_is_dirty = (
            global_deps_changed
            or md_content_changed
            or not isinstance(cached_meta, dict)
        )

        if not meta_is_dirty and isinstance(cached_meta, dict):
            file_metadata_map[md] = cached_meta
            doc_has_citations_map[md] = cached_meta.get("__has_citations__", False)
            new_manifest[meta_cache_key] = cached_meta
        else:
            metadata_extraction_jobs.append(md)

        if is_dirty:
            compile_tasks.append(
                CompileTask(
                    md_path=md,
                    out_path=out,
                    template_path=DEFAULT_TEMPLATE,
                    relative_root=relative_root,
                    doc_title="",
                    defaults_yaml=DEFAULTS_YAML,
                    lua_filter=LUA_FILTER,
                    bibliography_path=None,
                    is_secure=is_secure,
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
            rel = md_path.relative_to(SRC)
            new_manifest[f"meta:{rel.as_posix()}"] = extracted_meta

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

    search_records: list[dict] = []
    for idx, md in enumerate(md_files):
        rel = md.relative_to(SRC)
        clean_url = rel.with_suffix(".html").as_posix().lstrip("/")
        meta = file_metadata_map[md]
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

    # Static Assets
    for folder_name, manifest_prefix in [
        ("assets", "functional_asset"),
        ("root", "root_asset"),
    ]:
        src_dir = APP_DIR / folder_name
        if not src_dir.exists():
            continue
        for p in src_dir.rglob("*"):
            if p.is_file() and not is_junk_path(p):
                rel_p = p.relative_to(src_dir)
                target = DST / ("assets" / rel_p if folder_name == "assets" else rel_p)
                expected_outputs.add(target.resolve())
                manifest_key = f"{manifest_prefix}:{rel_p.as_posix()}"
                h = compute_file_hash(p)
                new_manifest[manifest_key] = h
                if not target.exists() or old_manifest.get(manifest_key) != h:
                    asset_sync_jobs.append((p, target))

    orphans_pruned = prune_orphans(
        dst_dir=DST, expected_files=expected_outputs, dry_run=args.dry_run
    )
    if orphans_pruned:
        logging.info("Pruned %d orphaned artifact(s).", orphans_pruned)

    for src_file, target_file in asset_sync_jobs:
        if not args.dry_run:
            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, target_file)

    failed = 0

    if encrypt_blob_tasks:
        logging.info("Encrypting %d media blob(s)...", len(encrypt_blob_tasks))
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=args.workers
        ) as executor:
            futures = [
                executor.submit(encrypt_blob_worker, t) for t in encrypt_blob_tasks
            ]
            for future in concurrent.futures.as_completed(futures):
                path, ok, err = future.result()
                if not ok:
                    failed += 1
                    logging.error("Failed to encrypt blob %s: %s", path.name, err)

    if compile_tasks:
        logging.info("Compiling %d documents...", len(compile_tasks))
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=args.workers
        ) as executor:
            futures = [
                executor.submit(compile_markdown_worker, t) for t in compile_tasks
            ]
            for future in concurrent.futures.as_completed(futures):
                path, ok, err = future.result()
                if not ok:
                    failed += 1
                    logging.error("Error compiling %s: %s", path.name, err)
    else:
        logging.info("All documents are up-to-date.")

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
        logging.info("Pipeline completed successfully.")
    else:
        logging.error("Build failed with %d error(s). Manifest retained.", failed)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

## system/build/pandoc_md_to_static_html.yaml

```yaml
reader: markdown
writer: html5
embed-resources: false
variables:
  document-css: false
  title: false
top-level-division: chapter
wrap: none
columns: 78
dpi: 72
toc: false
toc-depth: 2
number-sections: false
section-divs: true
identifier-prefix: ""
title-prefix: ""
eol: lf
strip-comments: false
ascii: false
default-image-extension: .jpg
tab-stop: 4
preserve-tabs: false
html-q-tags: false
fail-if-warnings: false
```

## system/build/translate_links.lua

```lua
local is_secure = os.getenv("KYKLOI_SECURE_BUILD") == "1"

local function is_external(url)
  return url:match("^%a+://") ~= nil or url:match("^//") ~= nil or url:match("^mailto:") ~= nil
end

function Link(el)
  if is_external(el.target) or el.target:sub(1, 1) == "#" then
    return el
  end

  local path, separator, suffix = el.target:match("^([^#?]+)([#?])(.*)$")
  if not path then
    path = el.target
    separator = ""
    suffix = ""
  end

  if path:match("%.md$") then
    path = path:gsub("%.md$", ".html")
    el.target = path .. separator .. suffix
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

## system/tools/tools_manifest.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "description": "Kykloi Offline Appliance Toolchain Manifest",
  "version": "1.1",
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
Features CLI argument parsing, defensive MIME registration, and IPC vault orchestration.
"""

import argparse
import http.server
import mimetypes

# ===========================================================================
# 1. PATH RESOLUTION & DEFENSIVE MIME REGISTRATION
# ===========================================================================
import os
import re
import socketserver
import subprocess
import sys
import threading
import urllib.parse
import webbrowser
from pathlib import Path

SYSTEM_DIR = Path(__file__).resolve().parent
ROOT_DIR = SYSTEM_DIR.parent
DIST_DIR = ROOT_DIR / "dist"
BUILD_SCRIPT = SYSTEM_DIR / "build" / "build_site.py"

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
    server_version = "KykloiServer/0.6"
    protocol_version = "HTTP/1.1"

    def guess_mime(self, filepath: str) -> str:
        mime, _ = mimetypes.guess_type(filepath)
        return mime or "application/octet-stream"

    def log_message(self, format: str, *args):
        # Silence access logs to keep the interactive CLI uncluttered
        pass

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
# 4. COMPILER INVOCATION & INTERACTIVE CLI
# ===========================================================================


def execute_build(clean: bool = False, passphrase: str | None = None) -> int:
    cmd = [sys.executable, str(BUILD_SCRIPT)]
    if clean:
        cmd.append("--clean")
    if passphrase:
        cmd.extend(["--password", passphrase])

    masked_cmd = [
        "********" if i > 0 and cmd[i - 1] == "--password" else arg
        for i, arg in enumerate(cmd)
    ]
    print("\n" + "-" * 60)
    print(f"[Compiler] Executing: {' '.join(masked_cmd)}")
    print("-" * 60)

    res = subprocess.run(cmd, cwd=str(ROOT_DIR))
    print("-" * 60)
    return res.returncode


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
    return p.parse_args()


def interactive_menu(vault_url: str, initial_password: str | None):
    session_password = initial_password

    while True:
        vault_ready = DIST_DIR.exists() and any(DIST_DIR.iterdir())
        status_line = (
            f"Vault: Ready ({vault_url})" if vault_ready else "Vault: Not Compiled"
        )
        pw_status = "Set" if session_password else "Not Set"

        print("\n==================== KYKLOI CONTROL PLANE ====================")
        print(f"  Status:     {status_line}")
        print(f"  Passphrase: [{pw_status}]")
        print("==============================================================")
        print("  [1] Compile Site (Incremental)")
        print("  [2] Rebuild Site (Clean Purge)")
        print("  [3] Set / Update Secure Passphrase")
        print("  [4] Open Vault in Default Browser")
        print("  [0] Exit")
        print("==============================================================")

        try:
            choice = input("Select an option [0-4]: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n")
            break

        if choice == "1":
            execute_build(clean=False, passphrase=session_password)
        elif choice == "2":
            execute_build(clean=True, passphrase=session_password)
        elif choice == "3":
            import getpass

            try:
                pw = getpass.getpass(
                    "Enter passphrase for /secure/ notes (leave empty to clear): "
                )
                session_password = pw.strip() or None
                if session_password:
                    print("[Config] Passphrase stored in active session memory.")
                else:
                    print("[Config] Passphrase cleared.")
            except (KeyboardInterrupt, EOFError):
                print("\n[Config] Passphrase entry cancelled.")
        elif choice == "4":
            if not vault_ready:
                print("\n[!] Vault must be compiled before opening in browser.")
            else:
                print(f"\n[Browser] Opening {vault_url} ...")
                webbrowser.open(vault_url)
        elif choice == "0":
            break
        else:
            print("\n[!] Invalid selection.")


def main():
    args = parse_args()

    if args.build:
        code = execute_build(clean=args.clean, passphrase=args.password)
        sys.exit(code)

    try:
        server, port, vault_url = start_background_server(args.host, args.port)
    except Exception as err:
        sys.stderr.write(f"[FATAL] Server initialization failed: {err}\n")
        sys.exit(1)

    try:
        interactive_menu(vault_url, args.password)
    finally:
        print("\n[Kykloi] Shutting down local server and closing ports...")
        server.shutdown()
        server.server_close()
        print("[Kykloi] Shutdown complete.")


if __name__ == "__main__":
    main()
```

## author_context.md

```md
#### 1. User Disclosures (Directly Reported)
* **Vocation:** Practicing nurse; software development is conducted strictly as an amateur/hobbyist pursuit.
* **Technical Background:** Self-disclosed as lacking the technical proficiency to author this codebase without large language model (LLM) generation.
* **Methodology:** Engaged in "vibe-coding" (prompt-driven iterative code synthesis mediated by LLMs) over a period of approximately six months spanning hundreds of developmental iterations.
* **Prototyping & Discarded Implementations:** Evaluated, integrated, and subsequently abandoned multiple alternative tools and architectures, including:
  * In-browser encryption: StatiCrypt
  * Search indexing engines: Pagefind, MiniSearch
  * Cryptographic packages: `cryptography`, `pycryptodome`
  * Architecture components: Dedicated Web UI (scrapped in favor of CLI/terminal workflow)
  * Upstream dependencies: Multiple iterations and versions of Python and Pandoc
* **Awareness of Technical Trade-Offs:** Identified performance deficiencies (notably pure-Python AES-GCM execution overhead) were consciously accepted as operational compromises or deferred to future iterations.

#### 2. Codebase Forensic Artifacts (Empirically Derived)
* **Digital Identity / Moniker:** Employs the branding identifier `JmB²` within the site navigation bar (`system/build/root/index.html`, `system/build/templates/md_to_static_html.html`).
* **Knowledge Management Workflow:**
  * Uses timestamped Zettelkasten-style file naming schemes (`YYYYMMDDHHMMSS-slug.md`, e.g., `20261109130247-project_kykloi_task_list.md`).
  * Explicitly filters directory patterns (`.obsidian`, `.zettlr`, `.logseq`) in `build_site.py`, indicating past or concurrent usage of Obsidian, Zettlr, or Logseq as content authoring environments.
* **Prior LLM Engagements:** Retains artifacts referencing other LLM interactions in the content tree (`content/202611/20261109171348-geminis_codebase_impression.md`).
* **Development Environment:**
  * File-naming patterns (e.g., `launch copy.bat`, `tools_manifest copy.json`) reflect local file duplication conventions standard to Windows Explorer.
  * Dual-platform maintenance of `.bat` and `.sh` wrappers confirms active cross-platform deployment targeting Windows and POSIX-compliant environments (Linux/macOS).
* **Threat Model Expectations:** Documented in `README.md` as seeking casual privacy against web scraping and automated bot ingestion for public static hosting, rather than defense against state-level or high-resource threat actors.
```

## launch.bat

```bat
@echo off
setlocal enabledelayedexpansion

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
python system\launch.py %*
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

set "MANIFEST_PATH=%SCRIPT_DIR%system\tools\tools_manifest.json"
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
for /f "usebackq tokens=1,2* delims=|" %%A in (`powershell -NoProfile -Command "$m=(Get-Content -Raw '%MANIFEST_PATH%' | ConvertFrom-Json).tools.python.targets.'%TARGET%'; if($m){Write-Output ($m.archive + '|' + $m.sha256 + '|' + $m.url)}" 2^>nul`) do (
    set "ARCHIVE_NAME=%%A"
    set "EXPECTED_SHA=%%B"
    set "DOWNLOAD_URL=%%C"
)

if "%ARCHIVE_NAME%"=="" (
    echo [FATAL] Failed to extract manifest parameters for target %TARGET%
    pause
    exit /b 1
)

set "ARCHIVE_PY=%SCRIPT_DIR%system\tools\archives\%ARCHIVE_NAME%"

if not exist "%ARCHIVE_PY%" (
    echo [Kykloi] Pre-packaged archive not found locally: %ARCHIVE_NAME%
    echo [Kykloi] Attempting automatic download...
    if not exist "%SCRIPT_DIR%system\tools\archives" mkdir "%SCRIPT_DIR%system\tools\archives"
    powershell -NoProfile -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('%DOWNLOAD_URL%', '%ARCHIVE_PY%')"
    if not exist "%ARCHIVE_PY%" (
        echo [FATAL] Download failed from: %DOWNLOAD_URL%
        pause
        exit /b 1
    )
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
"%LOCAL_PY%" "%SCRIPT_DIR%system\launch.py" %*
exit /b %ERRORLEVEL%
```

## launch.sh

```bash
#!/usr/bin/env sh
set -e

REQ_MAJ="${REQ_MAJ:-3}"
REQ_MIN="${REQ_MIN:-10}"

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
            aarch64|arm64)
                if [ "$LIBC" = "musl" ]; then
                    TARGET="linux-arm64-musl"
                else
                    TARGET="linux-arm64"
                fi
                ;;
            *) echo "[FATAL] Unsupported Linux architecture: $ARCH" >&2; exit 1 ;;
        esac
        ;;
    Darwin)
        case "$ARCH" in
            x86_64) TARGET="macos-x86_64" ;;
            arm64)  TARGET="macos-arm64" ;;
            *) echo "[FATAL] Unsupported macOS architecture: $ARCH" >&2; exit 1 ;;
        esac
        ;;
    *)
        echo "[FATAL] Unsupported operating system: $OS" >&2; exit 1
        ;;
esac

# ---------------------------------------------------------------------------
# 3. HYDRATE RUNTIME TO LOCAL STORAGE (WITH SHA-256 VERIFICATION)
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MANIFEST_PATH="$SCRIPT_DIR/system/tools/tools_manifest.json"

# Support hardened systems where /tmp is mounted noexec
BASE_RUNTIME="/tmp"
if [ -n "$XDG_RUNTIME_DIR" ] && [ -w "$XDG_RUNTIME_DIR" ]; then
    BASE_RUNTIME="$XDG_RUNTIME_DIR"
elif [ -d "$HOME/.cache" ] && [ -w "$HOME/.cache" ]; then
    BASE_RUNTIME="$HOME/.cache"
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
    DOWNLOAD_URL=$(extract_python_field "$TARGET" "url" "$MANIFEST_PATH")

    if [ -z "$ARCHIVE_NAME" ] || [ -z "$EXPECTED_SHA" ]; then
        echo "[FATAL] Target ${TARGET} not found in manifest python definitions." >&2
        exit 1
    fi

    ARCHIVE_PY="$SCRIPT_DIR/system/tools/archives/$ARCHIVE_NAME"

    if [ ! -f "$ARCHIVE_PY" ]; then
        echo "[Kykloi] Pre-packaged archive not found locally: $ARCHIVE_NAME"
        echo "[Kykloi] Attempting automatic download..."
        mkdir -p "$SCRIPT_DIR/system/tools/archives"
        if command -v curl >/dev/null 2>&1; then
            curl -fSL "$DOWNLOAD_URL" -o "$ARCHIVE_PY"
        elif command -v wget >/dev/null 2>&1; then
            wget "$DOWNLOAD_URL" -O "$ARCHIVE_PY"
        else
            echo "[FATAL] No network downloader (curl, wget) available and local archive missing." >&2
            exit 1
        fi
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
    printf "%s" "$ACTUAL_SHA" > "$STAMP_FILE"

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
name = "kykloi"
version = "0.5.0"
description = "Deterministic Archival Markdown SSG with WebCrypto Encryption"
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
