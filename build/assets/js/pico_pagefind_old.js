document.addEventListener("DOMContentLoaded", () => {
  const searchModal = document.getElementById("search-modal");
  const openSearchBtn = document.getElementById("open-search");
  const closeSearchBtn = document.getElementById("close-search");
  const searchInput = document.getElementById("search-input");
  const searchResults = document.getElementById("search-results");

  // Inline search elements
  const bodySearchInput = document.getElementById("body-search-input");
  const bodySearchResults = document.getElementById("body-search-results");

  // 1. Calculate the site root once from this script's location
  // assets/js/pico_pagefind.js -> ../../ -> site root
  const siteRoot = new URL("../../", import.meta.url).href;

  let pagefind;

  async function initPagefind() {
    if (!pagefind) {
      try {
        const pagefindUrl = new URL("pagefind/pagefind.js", siteRoot).href;
        pagefind = await import(pagefindUrl);
        await pagefind.init();
      } catch (err) {
        console.error("Failed to load Pagefind index.", err);
      }
    }
  }

  // REUSABLE SEARCH LOGIC
  async function performSearch(query, resultsContainer) {
    if (!pagefind) return;

    if (!query) {
      resultsContainer.innerHTML = "";
      return;
    }

    const search = await pagefind.search(query);
    const results = await Promise.all(
      search.results.slice(0, 100).map((result) => result.data())
    );

    // 2. siteRoot is now safely accessible here
    resultsContainer.innerHTML = results
      .map((data) => {
        const resolvedUrl = new URL(data.url.replace(/^\//, ""), siteRoot).href;
        const title = data.meta?.title || data.url;

        return `
        <a href="${resolvedUrl}" style="text-decoration: none; display: block; border-bottom: 1px solid var(--pico-muted-border-color); padding: 0.5rem 0;">
          <small style="color: var(--pico-primary); font-weight: bold;">${title}</small>
        </a>
      `;
      })
      .join("");
  }

  // --- Modal Event Listeners ---
  if (openSearchBtn && searchModal) {
    openSearchBtn.addEventListener("click", async (e) => {
      e.preventDefault();
      searchModal.showModal();
      await initPagefind();
      if (searchInput) searchInput.focus();
    });

    closeSearchBtn?.addEventListener("click", () => searchModal.close());
    searchModal.addEventListener("click", (e) => {
      if (e.target === searchModal) searchModal.close();
    });

    searchInput?.addEventListener("input", async (e) => {
      await performSearch(e.target.value.trim(), searchResults);
    });
  }

  // --- Inline Search Event Listeners ---
  if (bodySearchInput && bodySearchResults) {
    bodySearchInput.addEventListener("input", async (e) => {
      await initPagefind();
      await performSearch(e.target.value.trim(), bodySearchResults);
    });
  }
});
