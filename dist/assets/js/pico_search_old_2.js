document.addEventListener("DOMContentLoaded", () => {
  const searchModal = document.getElementById("search-modal");
  const openSearchBtn = document.getElementById("open-search");
  const closeSearchBtn = document.getElementById("close-search");
  const searchInput = document.getElementById("search-input");
  const searchResults = document.getElementById("search-results");

  // Inline search elements (e.g., on index.html)
  const bodySearchInput = document.getElementById("body-search-input");
  const bodySearchResults = document.getElementById("body-search-results");

  // Base relative offset for nested files (e.g., "", "../", or "../../")
  const relativeRoot = document.body.dataset.relativeRoot || "";

  let miniSearch = null;

  function initMiniSearch() {
    if (miniSearch) return;

    if (typeof MiniSearch === "undefined" || !window.__SEARCH_DOCS__) {
      console.warn("Search index or MiniSearch library not loaded.");
      return;
    }

    miniSearch = new MiniSearch({
      // All indexed search dimensions
      fields: ["title", "keywords", "date_edtf", "abstract"],

      // Stored data returned in search results
      storeFields: ["title", "url", "date_edtf", "abstract"],

      // Custom tokenizer: preserves EDTF date syntax (- / ? ~ %) while splitting standard punctuation
      tokenize: (text) =>
        text
          .toLowerCase()
          .split(/[\s,;:!()[\]{}"]+/)
          .filter(Boolean),

      searchOptions: {
        boost: {
          title: 4.0,     // Primary hit target
          keywords: 2.5,  // Explicit semantic tags
          date_edtf: 1.5, // Structured dates/eras
          abstract: 1.0,  // Contextual body summary
        },
        prefix: true, // Typeahead prefix completion
        fuzzy: (term) => (term.length > 3 ? 0.2 : false), // Fuzz words, protect short date tokens
        combineWith: "AND",
      },
    });

    miniSearch.addAll(window.__SEARCH_DOCS__);
  }

  function performSearch(query, resultsContainer) {
    if (!resultsContainer) return;
    initMiniSearch();

    const trimmed = query.trim();
    if (!miniSearch || !trimmed) {
      resultsContainer.innerHTML = "";
      return;
    }

    const hits = miniSearch.search(trimmed).slice(0, 50);

    resultsContainer.innerHTML = hits
      .map((item) => {
        const targetUrl = `${relativeRoot}${item.url}`;
        const title = item.title || item.url;

        // Inline EDTF date tag (if document contains date_edtf)
        const dateHtml = item.date_edtf
          ? `<time style="opacity: 0.65; font-size: 0.85em; margin-left: 0.5rem; font-family: monospace;">(${item.date_edtf})</time>`
          : "";

        // Truncated abstract preview snippet (if present)
        let snippetHtml = "";
        if (item.abstract) {
          const maxLen = 140;
          const cleanAbstract =
            item.abstract.length > maxLen
              ? `${item.abstract.slice(0, maxLen).trim()}…`
              : item.abstract;
          snippetHtml = `<p style="margin: 0.25rem 0 0 0; font-size: 0.85rem; color: var(--pico-muted-color); line-height: 1.35;">${cleanAbstract}</p>`;
        }

        return `
          <li style="list-style: none; border-bottom: 1px solid var(--pico-muted-border-color); padding: 0.6rem 0;">
            <a href="${targetUrl}" style="text-decoration: none; display: block;">
              <span style="color: var(--pico-primary); font-weight: bold;">${title}</span>
              ${dateHtml}
              ${snippetHtml}
            </a>
          </li>
        `;
      })
      .join("");
  }

  // --- Modal Search Handlers ---
  if (openSearchBtn && searchModal) {
    openSearchBtn.addEventListener("click", (e) => {
      e.preventDefault();
      searchModal.showModal();
      initMiniSearch();
      searchInput?.focus();
    });

    closeSearchBtn?.addEventListener("click", () => searchModal.close());

    searchModal.addEventListener("click", (e) => {
      if (e.target === searchModal) searchModal.close();
    });

    searchInput?.addEventListener("input", (e) => {
      performSearch(e.target.value, searchResults);
    });
  }

  // --- Inline Search Handlers ---
  if (bodySearchInput && bodySearchResults) {
    bodySearchInput.addEventListener("input", (e) => {
      performSearch(e.target.value, bodySearchResults);
    });
  }
});
