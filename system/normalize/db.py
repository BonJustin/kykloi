"""
system/normalize/db.py - SQLite Ledger & Stat-Cache Acceleration Layer.
Stores the master file registry, link dependencies, and schema state.
"""

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

SCHEMA_VERSION = "1.0"

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;

CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stem TEXT UNIQUE NOT NULL,
    rel_path TEXT UNIQUE NOT NULL,
    sha256 TEXT NOT NULL,
    mtime REAL NOT NULL,
    size INTEGER NOT NULL,
    is_media INTEGER NOT NULL DEFAULT 0,
    is_secure INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_files_stem ON files(stem);
CREATE INDEX IF NOT EXISTS idx_files_sha256 ON files(sha256);
CREATE INDEX IF NOT EXISTS idx_files_rel_path ON files(rel_path);

CREATE TABLE IF NOT EXISTS links (
    source_stem TEXT NOT NULL,
    target_stem TEXT NOT NULL,
    raw_target TEXT NOT NULL,
    line_number INTEGER,
    FOREIGN KEY(source_stem) REFERENCES files(stem) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_links_target ON links(target_stem);
CREATE INDEX IF NOT EXISTS idx_links_source ON links(source_stem);
"""


@dataclass(frozen=True)
class FileRecord:
    id: Optional[int]
    stem: str
    rel_path: str
    sha256: str
    mtime: float
    size: int
    is_media: bool
    is_secure: bool


@dataclass(frozen=True)
class LinkRecord:
    source_stem: str
    target_stem: str
    raw_target: str
    line_number: Optional[int]


class VaultDB:
    """Manages transactional access to vault_index.db."""

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self._conn: Optional[sqlite3.Connection] = None

    def connect(self) -> sqlite3.Connection:
        if self._conn is None:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(
                str(self.db_path),
                timeout=30.0,
                isolation_level=None,  # Autocommit mode; transactions managed via BEGIN/COMMIT
            )
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("PRAGMA journal_mode = WAL;")
            conn.execute("PRAGMA synchronous = NORMAL;")
            self._conn = conn
        return self._conn

    def close(self):
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def init_schema(self):
        """Initializes tables, indices, and default metadata."""
        conn = self.connect()
        with conn:
            conn.executescript(SCHEMA_SQL)
            conn.execute(
                "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?);",
                ("schema_version", SCHEMA_VERSION),
            )

    # -----------------------------------------------------------------------
    # Metadata Queries
    # -----------------------------------------------------------------------

    def get_meta(self, key: str) -> Optional[str]:
        conn = self.connect()
        row = conn.execute("SELECT value FROM meta WHERE key = ?;", (key,)).fetchone()
        return row["value"] if row else None

    def set_meta(self, key: str, value: str):
        conn = self.connect()
        conn.execute(
            "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?);",
            (key, value),
        )

    # -----------------------------------------------------------------------
    # File Ledger Operations
    # -----------------------------------------------------------------------

    def upsert_file(self, record: FileRecord) -> int:
        """
        Inserts or updates a file record. If the stem already exists, updates path, hash, and stat cache.
        """
        conn = self.connect()
        cursor = conn.execute(
            """
            INSERT INTO files (stem, rel_path, sha256, mtime, size, is_media, is_secure)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(stem) DO UPDATE SET
                rel_path = excluded.rel_path,
                sha256 = excluded.sha256,
                mtime = excluded.mtime,
                size = excluded.size,
                is_media = excluded.is_media,
                is_secure = excluded.is_secure;
            """,
            (
                record.stem,
                record.rel_path,
                record.sha256,
                record.mtime,
                record.size,
                1 if record.is_media else 0,
                1 if record.is_secure else 0,
            ),
        )
        return cursor.lastrowid

    def get_file_by_stem(self, stem: str) -> Optional[FileRecord]:
        conn = self.connect()
        row = conn.execute("SELECT * FROM files WHERE stem = ?;", (stem,)).fetchone()
        if not row:
            return None
        return self._row_to_file_record(row)

    def get_file_by_path(self, rel_path: str) -> Optional[FileRecord]:
        conn = self.connect()
        row = conn.execute(
            "SELECT * FROM files WHERE rel_path = ?;", (rel_path,)
        ).fetchone()
        if not row:
            return None
        return self._row_to_file_record(row)

    def get_file_by_hash(self, sha256: str) -> List[FileRecord]:
        conn = self.connect()
        rows = conn.execute(
            "SELECT * FROM files WHERE sha256 = ?;", (sha256,)
        ).fetchall()
        return [self._row_to_file_record(r) for r in rows]

    def get_all_files(self) -> Dict[str, FileRecord]:
        """Returns a mapping of rel_path -> FileRecord."""
        conn = self.connect()
        rows = conn.execute("SELECT * FROM files;").fetchall()
        return {r["rel_path"]: self._row_to_file_record(r) for r in rows}

    def delete_file_by_stem(self, stem: str):
        conn = self.connect()
        conn.execute("DELETE FROM files WHERE stem = ?;", (stem,))

    def delete_file_by_path(self, rel_path: str):
        conn = self.connect()
        conn.execute("DELETE FROM files WHERE rel_path = ?;", (rel_path,))

    # -----------------------------------------------------------------------
    # Stat-Cache Fast-Path Queries
    # -----------------------------------------------------------------------

    def is_stat_cache_hit(self, rel_path: str, mtime: float, size: int) -> bool:
        """
        O(1) index check: returns True if rel_path exists and (mtime, size) match exactly.
        Eliminates redundant disk I/O and SHA-256 computation.
        """
        conn = self.connect()
        row = conn.execute(
            "SELECT mtime, size FROM files WHERE rel_path = ?;",
            (rel_path,),
        ).fetchone()
        if not row:
            return False
        # Account for precision variations in float mtime across OS filesystems
        return abs(row["mtime"] - mtime) < 0.0001 and row["size"] == size

    # -----------------------------------------------------------------------
    # Link Graph Operations
    # -----------------------------------------------------------------------

    def replace_document_links(self, source_stem: str, links: List[LinkRecord]):
        """
        Atomically replaces all outgoing link edges for a given source stem.
        """
        conn = self.connect()
        with conn:
            conn.execute("DELETE FROM links WHERE source_stem = ?;", (source_stem,))
            if links:
                conn.executemany(
                    """
                    INSERT INTO links (source_stem, target_stem, raw_target, line_number)
                    VALUES (?, ?, ?, ?);
                    """,
                    [
                        (l.source_stem, l.target_stem, l.raw_target, l.line_number)
                        for l in links
                    ],
                )

    def get_referencing_links(self, target_stem: str) -> List[LinkRecord]:
        """
        Retrieves all link records across the vault targeting this stem.
        """
        conn = self.connect()
        rows = conn.execute(
            "SELECT source_stem, target_stem, raw_target, line_number FROM links WHERE target_stem = ?;",
            (target_stem,),
        ).fetchall()
        return [
            LinkRecord(
                source_stem=r["source_stem"],
                target_stem=r["target_stem"],
                raw_target=r["raw_target"],
                line_number=r["line_number"],
            )
            for r in rows
        ]

    def get_outgoing_links(self, source_stem: str) -> List[LinkRecord]:
        """
        Retrieves all outgoing link records originating from this stem.
        """
        conn = self.connect()
        rows = conn.execute(
            "SELECT source_stem, target_stem, raw_target, line_number FROM links WHERE source_stem = ?;",
            (source_stem,),
        ).fetchall()
        return [
            LinkRecord(
                source_stem=r["source_stem"],
                target_stem=r["target_stem"],
                raw_target=r["raw_target"],
                line_number=r["line_number"],
            )
            for r in rows
        ]

    # -----------------------------------------------------------------------
    # Helper Conversion
    # -----------------------------------------------------------------------

    @staticmethod
    def _row_to_file_record(row: sqlite3.Row) -> FileRecord:
        return FileRecord(
            id=row["id"],
            stem=row["stem"],
            rel_path=row["rel_path"],
            sha256=row["sha256"],
            mtime=row["mtime"],
            size=row["size"],
            is_media=bool(row["is_media"]),
            is_secure=bool(row["is_secure"]),
        )
