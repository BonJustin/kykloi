## `tree ~/dev/kykloi`

```
*add tree*
```

## `style.css`

```
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

/* Remove underlines from all links by default and on hover */
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

/* Level 1: Solid round bullets (disc) */
main ul li {
    list-style-type: disc;
}

/* Level 2: Hollow bullets (circle) */
main ul ul li {
    list-style-type: circle;
}

/* Level 3: Solid round bullets */
main ul ul ul li {
    list-style-type: disc;
}

/* Level 4: Hollow bullets */
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

## `decrypt.js`

```
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
```

## `pico_search.js`

```
/* pico_search.js - Kykloi SQLite3 FTS5 Search Hub Driver */
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
          // Immediately display the 50 most recent notes upon initialization
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

  // Handle nav search button click on index page
  if (navSearchBtn) {
    navSearchBtn.addEventListener("click", (e) => {
      e.preventDefault();
      bodyInput.focus();
      bodyInput.scrollIntoView({ behavior: "smooth", block: "center" });
    });
  }

  // Handle focus request if navigated from a note with ?focus=1
  if (window.location.search.includes("focus=1")) {
    bodyInput.focus();
  }

  // Desktop default focus on load
  if (window.innerWidth > 768) {
    bodyInput.focus();
  }

  // Keyboard shortcuts (/ or Ctrl+K / Cmd+K to focus search on index)
  window.addEventListener("keydown", (e) => {
    const isModifierK = (e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k";
    const isSlash = e.key === "/" && !["INPUT", "TEXTAREA"].includes(document.activeElement?.tagName);

    if (isModifierK || isSlash) {
      e.preventDefault();
      bodyInput.focus();
      bodyInput.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  });

  // Pre-initialize background worker
  initWorker();
});
```

## `search_worker.js`

```
/* search_worker.js - Kykloi SQLite3 WASM FTS5 Search Worker */
"use strict";

importScripts("sqlite3.js");

let sqlite3 = null;
let db = null;
let initPromise = null;

/**
 * Initializes the SQLite3 WASM runtime and deserializes search.db into memory.
 */
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

/**
 * Builds candidate FTS5 queries.
 * Supports advanced syntax (quotes, column filters, boolean operators) with a safe prefix fallback.
 */
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

/**
 * Returns the 50 most recent documents (default view for empty query).
 */
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

/**
 * Executes full-text search against the docs_fts virtual table.
 */
function executeSearch(query, searchId) {
  const trimmed = (query || "").trim();

  // If query is empty, return the 50 most recent documents
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
      // Loop falls back to the safe prefix query if advanced syntax threw a syntax error
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

self.onmessage = async (e) => {
  const { type, dbUrl, query, searchId } = e.data || {};

  switch (type) {
    case "init":
      if (!initPromise) {
        initPromise = initDatabase(dbUrl)
          .then(() => {
            self.postMessage({ type: "ready" });
          })
          .catch((err) => {
            initPromise = null;
            self.postMessage({ type: "error", error: err.message });
          });
      }
      break;

    case "search":
      if (initPromise) {
        try {
          await initPromise;
          executeSearch(query || "", searchId);
        } catch (err) {
          self.postMessage({
            type: "results",
            query,
            searchId,
            hits: [],
            hasMore: false,
            isDefault: false,
            error: err.message,
          });
        }
      }
      break;

    default:
      console.warn("[Kykloi Search Worker] Unhandled message type:", type);
  }
};
```

## `index.html`

```
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

## `md_to_static_html.html`

```
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
        <link rel="stylesheet" href="$relative_root$assets/katex/katex.min.css" />
        <script src="$relative_root$assets/katex/katex.min.js" defer></script>
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
                        <!-- Form with complete browser/extension password save suppression -->
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

## `metadata.json`

```
$meta-json$
```

## `build_site.py`

```
-- translate_links.lua
-- 1. Rewrites relative markdown links (.md) to HTML (.html)
-- 2. If KYKLOI_SECURE_BUILD is active, rewrites image sources to append .enc

local is_secure = os.getenv("KYKLOI_SECURE_BUILD") == "1"

function Link(el)
  -- Skip absolute URLs or protocols
  if el.target:match("^%a+://") or el.target:match("^//") or el.target:match("^mailto:") then
    return el
  end

  -- Decode URL to inspect extension if encoded
  local target = el.target

  -- Separate path from anchor or query
  local path, rest = target:match("^(.-)%.md([#?].*)$")
  if not path then
    path = target:match("^(.-)%.md$")
    rest = ""
  end

  if path then
    el.target = path .. ".html" .. rest
  end

  return el
end

function Image(el)
  if not is_secure then
    return el
  end

  -- Skip absolute URLs, protocols, or existing data URIs
  if el.src:match("^%a+://") or el.src:match("^//") or el.src:match("^data:") then
    return el
  end

  -- Extract clean base URL ignoring anchors or query parameters
  local base_src, suffix = el.src:match("^(.-)(%?.*)$")
  if not base_src then
    base_src = el.src
    suffix = ""
  end

  -- Append .enc if not already present
  if not base_src:match("%.enc$") then
    el.src = base_src .. ".enc" .. suffix
  end

  el.attributes["data-encrypted-media"] = "true"
  return el
end
```

## `migrate_wikilinks.py`

```
#!/usr/bin/env python3
"""
migrate_wikilinks.py - Robust, Zero-Dependency CommonMark Link Normalizer.
Converts Obsidian, Zettlr, Logseq, and Foam wikilinks into standards-compliant CommonMark.
Handles spaces, anchors, block IDs, frontmatter IDs, and Zettelkasten timestamp prefixes.
Protects KaTeX blocks, code fences, inline code, and YAML frontmatter.
Part of Project Kykloi.
"""

import argparse
import os
import re
import urllib.parse
from pathlib import Path

# Matches standard Zettelkasten timestamp formats (8 to 14 digits)
ID_PREFIX_PATTERN = re.compile(r"^(\d{14}|\d{12}|\d{8})(?:[-_\s].*)?$")

# Matches Zettlr frontmatter ID: "id: 20240101120000" or "id: '20240101120000'"
FRONTMATTER_ID_PATTERN = re.compile(r"^id:\s*['\"]?(\d{8,14})['\"]?", re.MULTILINE)

# Match ![[target#anchor|alt]] or ![[target]]
WIKI_IMAGE_PATTERN = re.compile(r"!\[\[\s*([^\]\|\n]+?)(?:\|([^\]\n]*))?\s*\]\]")

# Match [[target#anchor|label]] or [[target]]
WIKI_LINK_PATTERN = re.compile(r"\[\[\s*([^\]\|\n]+?)(?:\|([^\]\n]*))?\s*\]\]")

# Carve out protected syntactic blocks from Markdown content
PROTECTED_ZONES_PATTERN = re.compile(
    r"("
    r"^---[\s\S]*?^---|"  # YAML Frontmatter
    r"```[\s\S]*?```|"  # Fenced code blocks (backticks)
    r"~~~[\s\S]*?~~~|"  # Fenced code blocks (tildes)
    r"\$\$(?:\\.|[^\\])*?\$\$|"  # Display math $$ ... $$
    r"\\\[[\s\S]*?\\\]|"  # Display math \[ ... \]
    r"`[^`\n]+`|"  # Inline code
    r"\$(?:\\.|[^\$\\\n])+\$|"  # Inline math $ ... $
    r"\\\([\s\S]*?\\\)"  # Inline math \( ... \)
    r")",
    re.MULTILINE,
)

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

JUNK_FILE_EXTENSIONS = {
    ".ztr-directory",
    ".ds_store",
    "thumbs.db",
    "desktop.ini",
}


def is_junk_path(path: Path) -> bool:
    for part in path.parts:
        if part.lower() in JUNK_DIR_NAMES or part.startswith("."):
            return True
    if path.name.lower() in JUNK_FILE_EXTENSIONS:
        return True
    return False


def extract_frontmatter_id(path: Path) -> str | None:
    """Fast probe to extract Zettlr/Obsidian ID from YAML header."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            chunk = f.read(1024)
        if chunk.startswith("---"):
            end_idx = chunk.find("---", 3)
            if end_idx != -1:
                header = chunk[3:end_idx]
                match = FRONTMATTER_ID_PATTERN.search(header)
                if match:
                    return match.group(1)
    except OSError:
        pass
    return None


def build_inventory(src_root: Path) -> dict[str, Path]:
    """
    Constructs an exhaustive dictionary of target lookups:
    - Relative POSIX path without extension: 'folder/Note'
    - Exact filename: 'Note.md', 'Image.png'
    - File stem (case-sensitive and lowercase): 'Note'
    - Zettelkasten ID (from filename prefix or frontmatter)
    """
    inventory: dict[str, Path] = {}

    for p in src_root.rglob("*"):
        if not p.is_file() or is_junk_path(p):
            continue

        rel = p.relative_to(src_root)
        posix_rel = rel.as_posix()
        name = p.name
        stem = p.stem

        inventory[posix_rel] = rel
        inventory[name] = rel
        inventory[stem] = rel
        inventory[stem.lower()] = rel

        if p.suffix.lower() == ".md":
            no_ext_rel = rel.with_suffix("").as_posix()
            inventory[no_ext_rel] = rel
            inventory[no_ext_rel.lower()] = rel

            # Filename-based ZK ID (e.g., 20240101120000-topic.md)
            m = ID_PREFIX_PATTERN.match(stem)
            if m:
                inventory[m.group(1)] = rel

            # Frontmatter-based ID
            f_id = extract_frontmatter_id(p)
            if f_id:
                inventory[f_id] = rel

    return inventory


def format_commonmark_url(source_rel: Path, target_rel: Path, anchor: str = "") -> str:
    """
    Computes a relative path from source to target, percent-encoding spaces
    and illegal characters while preserving valid path separators and anchor hashes.
    """
    source_dir = source_rel.parent
    rel_path_str = os.path.relpath(target_rel, start=source_dir)
    posix_path = Path(rel_path_str).as_posix()

    # Percent-encode destination path (preserve forward slashes)
    encoded_path = urllib.parse.quote(posix_path, safe="/#%")

    if anchor:
        # Encode or slugify anchor
        clean_anchor = anchor.strip()
        if not clean_anchor.startswith("#"):
            clean_anchor = "#" + clean_anchor
        encoded_anchor = urllib.parse.quote(clean_anchor, safe="#-_")
        return f"{encoded_path}{encoded_anchor}"

    return encoded_path


def resolve_target(
    raw_target: str, inventory: dict[str, Path]
) -> tuple[Path | None, str]:
    """
    Resolves targets containing anchors, paths, or ZK IDs.
    Returns: (Matched Path or None, Extracted Anchor)
    """
    target = raw_target.strip()
    anchor = ""

    if "#" in target:
        target, anchor = target.split("#", 1)
        target = target.strip()
        anchor = "#" + anchor.strip()

    if not target:
        # Pure internal document anchor: [[#Heading]]
        return None, anchor

    # 1. Direct dictionary match (exact path, stem, or filename)
    if target in inventory:
        return inventory[target], anchor

    # 2. Case-insensitive lookup
    target_lower = target.lower()
    if target_lower in inventory:
        return inventory[target_lower], anchor

    # 3. Basename lookup (e.g. user wrote [[folder/sub/Note]] but note was moved)
    base_name = Path(target).name
    if base_name in inventory:
        return inventory[base_name], anchor

    base_lower = base_name.lower()
    if base_lower in inventory:
        return inventory[base_lower], anchor

    # 4. Leading Zettelkasten ID probe (e.g. Zettlr [[20240101120000 Note Title]])
    zk_match = ID_PREFIX_PATTERN.match(base_name)
    if zk_match:
        zk_id = zk_match.group(1)
        if zk_id in inventory:
            return inventory[zk_id], anchor

    return None, anchor


def convert_file_content(
    doc_rel: Path,
    content: str,
    inventory: dict[str, Path],
) -> tuple[str, int]:
    replacements = 0

    def replace_image(match: re.Match) -> str:
        nonlocal replacements
        raw_target = match.group(1).strip()
        alt_text = match.group(2).strip() if match.group(2) else ""

        target_file, _ = resolve_target(raw_target, inventory)
        if target_file:
            encoded_url = format_commonmark_url(doc_rel, target_file)
            replacements += 1
            display = alt_text or target_file.name
            return f"![{display}]({encoded_url})"

        return match.group(0)

    def replace_link(match: re.Match) -> str:
        nonlocal replacements
        raw_target = match.group(1).strip()
        explicit_label = match.group(2).strip() if match.group(2) else ""

        target_file, anchor = resolve_target(raw_target, inventory)

        if target_file:
            encoded_url = format_commonmark_url(doc_rel, target_file, anchor)
            replacements += 1

            if explicit_label:
                display = explicit_label
            else:
                display = target_file.stem.replace("-", " ").replace("_", " ").title()
                if anchor and not target_file.name:
                    display = anchor.lstrip("#")

            return f"[{display}]({encoded_url})"

        if not target_file and anchor:
            # Self-referencing heading link: [[#Introduction]]
            replacements += 1
            display = explicit_label or anchor.lstrip("#")
            clean_anchor = urllib.parse.quote(anchor, safe="#-_")
            return f"[{display}]({clean_anchor})"

        return match.group(0)

    tokens = PROTECTED_ZONES_PATTERN.split(content)
    output_segments: list[str] = []

    for idx, segment in enumerate(tokens):
        if idx % 2 == 1:
            output_segments.append(segment)
        else:
            subbed = WIKI_IMAGE_PATTERN.sub(replace_image, segment)
            subbed = WIKI_LINK_PATTERN.sub(replace_link, subbed)
            output_segments.append(subbed)

    return "".join(output_segments), replacements


def run_migration_pipeline(
    src_root: Path, dry_run: bool = False, verbose: bool = False
) -> tuple[int, int]:
    if not src_root.exists():
        return 0, 0

    md_candidates: list[Path] = []
    for p in src_root.rglob("*.md"):
        if is_junk_path(p):
            continue
        try:
            # Microsecond byte check before full parsing
            with open(p, "rb") as f:
                if b"[[" in f.read():
                    md_candidates.append(p)
        except OSError:
            continue

    if not md_candidates:
        return 0, 0

    inventory = build_inventory(src_root)
    files_modified = 0
    links_converted = 0

    for md in md_candidates:
        try:
            with open(md, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError:
            continue

        doc_rel = md.relative_to(src_root)
        new_content, count = convert_file_content(doc_rel, content, inventory)

        if count > 0:
            files_modified += 1
            links_converted += count
            if not dry_run:
                with open(md, "w", encoding="utf-8") as f:
                    f.write(new_content)
            if verbose:
                print(f"[Migrate] Converted {count} link(s) in {doc_rel}")

    return files_modified, links_converted


def main():
    parser = argparse.ArgumentParser(
        description="Migrate Obsidian/Zettlr wikilinks to standard CommonMark relative links."
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview migrations without disk writes."
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Print granular file conversions."
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    src_root = project_root / "content"

    modified, count = run_migration_pipeline(
        src_root=src_root, dry_run=args.dry_run, verbose=args.verbose
    )
    action = "Identified" if args.dry_run else "Converted"
    print(f"Wikilink Migration: {action} {count} link(s) across {modified} file(s).")


if __name__ == "__main__":
    main()
```

## `pandoc_md_to_static_html.yaml`

```
reader: markdown
writer: html
embed-resources: false
variables:
  document-css: false
  title: false
filters:
  - citeproc
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

## `translate_links.lua`

```
-- translate_links.lua
-- 1. Rewrites relative markdown links (.md) to HTML (.html)
-- 2. If KYKLOI_SECURE_BUILD is active, rewrites image sources to append .enc

local is_secure = os.getenv("KYKLOI_SECURE_BUILD") == "1"

function Link(el)
  -- Skip absolute URLs or protocols
  if el.target:match("^%a+://") or el.target:match("^//") or el.target:match("^mailto:") then
    return el
  end

  -- Decode URL to inspect extension if encoded
  local target = el.target

  -- Separate path from anchor or query
  local path, rest = target:match("^(.-)%.md([#?].*)$")
  if not path then
    path = target:match("^(.-)%.md$")
    rest = ""
  end

  if path then
    el.target = path .. ".html" .. rest
  end

  return el
end

function Image(el)
  if not is_secure then
    return el
  end

  -- Skip absolute URLs, protocols, or existing data URIs
  if el.src:match("^%a+://") or el.src:match("^//") or el.src:match("^data:") then
    return el
  end

  -- Extract clean base URL ignoring anchors or query parameters
  local base_src, suffix = el.src:match("^(.-)(%?.*)$")
  if not base_src then
    base_src = el.src
    suffix = ""
  end

  -- Append .enc if not already present
  if not base_src:match("%.enc$") then
    el.src = base_src .. ".enc" .. suffix
  end

  el.attributes["data-encrypted-media"] = "true"
  return el
end
```

## `pyproject.toml`

```
[project]
name = "kykloi"
version = "0.4.0"
description = "Deterministic Archival Markdown SSG with WebCrypto Encryption"
readme = "README.md"
requires-python = ">=3.12"
dependencies = []
```
