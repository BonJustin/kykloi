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
