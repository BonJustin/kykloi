/* pico_search.js - Kykloi SQLite3 FTS5 Search UI Driver */
"use strict";

document.addEventListener("DOMContentLoaded", () => {
  const searchModal = document.getElementById("search-modal");
  const openSearchBtn = document.getElementById("open-search");
  const closeSearchBtn = document.getElementById("close-search");
  const modalInput = document.getElementById("search-input");
  const modalResults = document.getElementById("search-results");

  const bodyInput = document.getElementById("body-search-input");
  const bodyResults = document.getElementById("body-search-results");

  const rawRoot = document.body.dataset.relativeRoot || "";
  const relativeRoot = rawRoot && !rawRoot.endsWith("/") ? `${rawRoot}/` : rawRoot;

  // Resolve absolute URLs to ensure robust loading regardless of page nesting
  const workerUrl = new URL(`${relativeRoot}assets/js/search_worker.js`, window.location.href).href;
  const dbUrl = new URL(`${relativeRoot}search.db`, window.location.href).href;

  let worker = null;
  let isWorkerReady = false;
  let activeSearchId = 0;
  let targetResultsContainer = null;

  function initWorker() {
    if (worker) return;

    try {
      worker = new Worker(workerUrl);

      worker.onmessage = (e) => {
        const { type, query, searchId, hits, hasMore, error } = e.data || {};

        if (type === "ready") {
          isWorkerReady = true;
          return;
        }

        if (type === "error") {
          console.error("[Kykloi Search] Worker initialization failed:", error);
          if (targetResultsContainer) {
            targetResultsContainer.innerHTML = `
              <li style="list-style: none; padding: 1rem 0; color: var(--pico-color-red-500); text-align: center;">
                Search index unavailable: ${escapeHtml(error)}
              </li>`;
          }
          return;
        }

        if (type === "results") {
          // Discard results from superseded keystrokes
          if (searchId !== activeSearchId) return;
          renderResults(hits, hasMore, query, targetResultsContainer);
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

  function renderResults(hits, hasMore, query, container) {
    if (!container) return;

    const trimmed = query.trim();
    if (!trimmed) {
      container.innerHTML = "";
      return;
    }

    if (!hits || hits.length === 0) {
      container.innerHTML = `
        <li style="list-style: none; padding: 1rem 0; text-align: center; color: var(--pico-muted-color);">
          No documents matching "<strong>${escapeHtml(trimmed)}</strong>"
        </li>`;
      return;
    }

    let html = hits
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
      html += `
        <li style="list-style: none; padding: 0.75rem 0; text-align: center; color: var(--pico-muted-color); font-size: 0.85rem;">
          Showing top 100 results. Refine your query for more specific matches.
        </li>`;
    }

    container.innerHTML = html;
    container.scrollTop = 0;
  }

  function dispatchSearch(query, container) {
    targetResultsContainer = container;
    initWorker();

    const trimmed = query.trim();
    if (!trimmed) {
      if (container) container.innerHTML = "";
      return;
    }

    activeSearchId += 1;
    worker.postMessage({
      type: "search",
      query: trimmed,
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

  // Modal UI Interactions
  if (openSearchBtn && searchModal) {
    openSearchBtn.addEventListener("click", (e) => {
      e.preventDefault();
      searchModal.showModal();
      initWorker();
      modalInput?.focus();
    });

    closeSearchBtn?.addEventListener("click", () => searchModal.close());

    searchModal.addEventListener("click", (e) => {
      if (e.target === searchModal) searchModal.close();
    });

    modalInput?.addEventListener("input", (e) => {
      debouncedSearch(e.target.value, modalResults);
    });
  }

  // Global Keyboard Shortcuts (Ctrl+K, Cmd+K, or "/" outside of inputs)
  window.addEventListener("keydown", (e) => {
    const isModifierK = (e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k";
    const isSlash = e.key === "/" && !["INPUT", "TEXTAREA"].includes(document.activeElement?.tagName);

    if ((isModifierK || isSlash) && searchModal && !searchModal.open) {
      e.preventDefault();
      searchModal.showModal();
      initWorker();
      modalInput?.focus();
    }
  });

  // Embedded Page Search (e.g., Homepage Input)
  if (bodyInput && bodyResults) {
    bodyInput.addEventListener("input", (e) => {
      debouncedSearch(e.target.value, bodyResults);
    });
  }

  // Preemptively initialize worker in background
  initWorker();
});
