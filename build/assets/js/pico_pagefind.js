document.addEventListener("DOMContentLoaded", () => {
  const searchModal = document.getElementById("search-modal");
  const openSearchBtn = document.getElementById("open-search");
  const closeSearchBtn = document.getElementById("close-search");
  const searchInput = document.getElementById("search-input");
  const searchResults = document.getElementById("search-results");

  // New elements for inline search
  const bodySearchInput = document.getElementById("body-search-input");
  const bodySearchResults = document.getElementById("body-search-results");

  let pagefind;

  async function initPagefind() {
    if (!pagefind) {
      try {
        const pagefindUrl = new URL('../../pagefind/pagefind.js', import.meta.url).href;
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
      search.results.slice(0, 100).map(result => result.data())
    );

    resultsContainer.innerHTML = results
      .map((data) => {
        // data.url from Pagefind typically starts with a leading slash: "/note.html"
        // Strip the leading slash so URL() resolves it relative to siteRoot
        const relativeUrlPath = data.url.replace(/^\//, "");
        const resolvedUrl = new URL(relativeUrlPath, siteRoot).href;
        const displayTitle = data.meta.title || "Untitled";

        return `
        <a href="${resolvedUrl}" style="text-decoration: none; display: block; border-bottom: 1px solid var(--pico-muted-border-color); padding: 0.5rem 0;">
          ${displayTitle}
        </a>
      `;
      })
      .join("");
    }

  // --- Modal Event Listeners ---
  openSearchBtn.addEventListener("click", async (e) => {
    e.preventDefault();
    searchModal.showModal();
    await initPagefind();
    searchInput.focus();
  });

  closeSearchBtn.addEventListener("click", () => searchModal.close());
  searchModal.addEventListener("click", (e) => {
    if (e.target === searchModal) searchModal.close();
  });

  searchInput.addEventListener("input", async (e) => {
    await performSearch(e.target.value.trim(), searchResults);
  });

  // --- Inline Search Event Listeners ---
  if (bodySearchInput) {
    bodySearchInput.addEventListener("input", async (e) => {
      // Initialize Pagefind on first interaction with the inline box
      await initPagefind();
      await performSearch(e.target.value.trim(), bodySearchResults);
    });
  }
});
