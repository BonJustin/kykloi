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
