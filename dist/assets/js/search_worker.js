/* search_worker.js - Kykloi SQLite3 WASM FTS5 Search Worker */
"use strict";

importScripts("sqlite3.js");

let sqlite3 = null;
let db = null;
let initPromise = null;

/**
 * Initializes the SQLite3 WASM runtime and deserializes search.db into memory.
 * @param {string} dbUrl - Fully-qualified or absolute URL to search.db
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

  // Allocate contiguous heap space in WASM memory for the database buffer
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
 * Sanitizes user input into safe FTS5 prefix match tokens.
 * Quoting individual tokens prevents injection or syntax collisions with FTS5 operators (AND, OR, NOT).
 * @param {string} rawQuery
 * @returns {string|null}
 */
function sanitizeFtsQuery(rawQuery) {
  const tokens = rawQuery
    .replace(/[^\p{L}\p{N}_]+/gu, " ")
    .trim()
    .split(/\s+/)
    .filter(Boolean);

  if (tokens.length === 0) return null;

  return tokens.map((t) => `"${t.replace(/"/g, '""')}"*`).join(" ");
}

/**
 * Executes full-text search against the docs_fts virtual table.
 * Fetches up to 101 rows to detect if more than 100 hits exist in a single query.
 */
function executeSearch(query, searchId) {
  const ftsQuery = sanitizeFtsQuery(query);
  if (!ftsQuery || !db) {
    self.postMessage({
      type: "results",
      query,
      searchId,
      hits: [],
      hasMore: false,
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

  const rows = [];
  try {
    db.exec({
      sql,
      bind: [ftsQuery],
      rowMode: "object",
      callback: (row) => rows.push(row),
    });

    const hasMore = rows.length > 100;
    const hits = hasMore ? rows.slice(0, 100) : rows;

    self.postMessage({
      type: "results",
      query,
      searchId,
      hits,
      hasMore,
    });
  } catch (err) {
    console.warn("[Kykloi Search Worker] FTS query execution warning:", err);
    self.postMessage({
      type: "results",
      query,
      searchId,
      hits: [],
      hasMore: false,
      error: err.message,
    });
  }
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
            error: err.message,
          });
        }
      } else {
        self.postMessage({
          type: "results",
          query,
          searchId,
          hits: [],
          hasMore: false,
          error: "Worker received search before initialization.",
        });
      }
      break;

    default:
      console.warn("[Kykloi Search Worker] Unhandled message type:", type);
  }
};
