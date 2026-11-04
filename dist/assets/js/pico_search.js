document.addEventListener("DOMContentLoaded", () => {
  const searchModal = document.getElementById("search-modal");
  const openSearchBtn = document.getElementById("open-search");
  const closeSearchBtn = document.getElementById("close-search");
  const searchInput = document.getElementById("search-input");
  const searchResults = document.getElementById("search-results");

  // Inline search elements (e.g., on index_template.html)
  const bodySearchInput = document.getElementById("body-search-input");
  const bodySearchResults = document.getElementById("body-search-results");

  // Retrieve base relative offset for nested files (e.g., "../../")
  const relativeRoot = document.body.dataset.relativeRoot || "./";

  let miniSearch = null;

  function initMiniSearch() {
    if (miniSearch) return;

    if (typeof MiniSearch === "undefined" || !window.__SEARCH_DOCS__) {
      console.warn("Search index or MiniSearch library not loaded.");
      return;
    }

    miniSearch = new MiniSearch({
      fields: ["title", "keywords"], // fields to index for full-text search
      storeFields: ["title", "url"],  // fields to return directly in search hits
      searchOptions: {
        boost: { title: 2 },
        fuzzy: 0.2,
        prefix: true,
      },
    });

    miniSearch.addAll(window.__SEARCH_DOCS__);
  }

  function performSearch(query, resultsContainer) {
    if (!resultsContainer) return;
    initMiniSearch();

    if (!miniSearch || !query) {
      resultsContainer.innerHTML = "";
      return;
    }

    const hits = miniSearch.search(query).slice(0, 50);

    resultsContainer.innerHTML = hits
      .map((item) => {
        // Resolve URL relative to the active document's directory depth
        const targetUrl = `${relativeRoot}${item.url}`;
        const title = item.title || item.url;

        return `
          <li style="list-style: none; border-bottom: 1px solid var(--pico-muted-border-color); padding: 0.5rem 0;">
            <a href="${targetUrl}" style="text-decoration: none; display: block;">
              <span style="color: var(--pico-primary); font-weight: bold;">${title}</span>
            </a>
          </li>
        `;
      })
      .join("");
  }

  // --- Modal Search Event Listeners ---
  if (openSearchBtn && searchModal) {
    openSearchBtn.addEventListener("click", (e) => {
      e.preventDefault();
      searchModal.showModal();
      initMiniSearch();
      if (searchInput) {
        searchInput.focus();
      }
    });

    closeSearchBtn?.addEventListener("click", () => searchModal.close());

    searchModal.addEventListener("click", (e) => {
      if (e.target === searchModal) {
        searchModal.close();
      }
    });

    searchInput?.addEventListener("input", (e) => {
      performSearch(e.target.value.trim(), searchResults);
    });
  }

  // --- Inline Search Event Listeners ---
  if (bodySearchInput && bodySearchResults) {
    bodySearchInput.addEventListener("input", (e) => {
      performSearch(e.target.value.trim(), bodySearchResults);
    });
  }
});
