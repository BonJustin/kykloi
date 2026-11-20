"""
system/normalize/db.py - SQLite Ledger & Stat-Cache Acceleration Layer.
Stores the master file registry, link dependencies, and schema state.
"""

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set

SCHEMA_VERSION = "3.0"

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
    canonical_filename TEXT UNIQUE NOT NULL,
    stem TEXT NOT NULL,
    ext TEXT NOT NULL,
    rel_path TEXT UNIQUE NOT NULL,
    sha256 TEXT NOT NULL,
    mtime REAL NOT NULL,
    size INTEGER NOT NULL,
    is_media INTEGER NOT NULL DEFAULT 0,
    is_secure INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_files_canonical ON files(canonical_filename);
CREATE INDEX IF NOT EXISTS idx_files_stem ON files(stem);
CREATE INDEX IF NOT EXISTS idx_files_sha256 ON files(sha256);
CREATE INDEX IF NOT EXISTS idx_files_rel_path ON files(rel_path);

CREATE TABLE IF NOT EXISTS links (
    source_canonical TEXT NOT NULL,
    target_canonical TEXT NOT NULL,
    raw_target TEXT NOT NULL,
    line_number INTEGER,
    FOREIGN KEY(source_canonical) REFERENCES files(canonical_filename) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_links_target ON links(target_canonical);
CREATE INDEX IF NOT EXISTS idx_links_source ON links(source_canonical);

CREATE TABLE IF NOT EXISTS doc_metadata (
    canonical_filename TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    date_edtf TEXT NOT NULL,
    keywords TEXT NOT NULL,
    has_citations INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY(canonical_filename) REFERENCES files(canonical_filename) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS build_artifacts (
    target_rel_path TEXT PRIMARY KEY,
    source_sha256 TEXT NOT NULL,
    artifact_category TEXT NOT NULL
);
"""


@dataclass(frozen=True)
class FileRecord:
    id: Optional[int]
    canonical_filename: str
    stem: str
    ext: str
    rel_path: str
    sha256: str
    mtime: float
    size: int
    is_media: bool
    is_secure: bool


@dataclass(frozen=True)
class LinkRecord:
    source_canonical: str
    target_canonical: str
    raw_target: str
    line_number: Optional[int]


@dataclass(frozen=True)
class DocMetadataRecord:
    canonical_filename: str
    title: str
    date_edtf: str
    keywords: str
    has_citations: bool


@dataclass(frozen=True)
class BuildArtifactRecord:
    target_rel_path: str
    source_sha256: str
    artifact_category: str


class VaultDB:
    """Manages transactional access to vault-index.db."""

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
        """
        Initializes tables, indices, and default metadata.
        Automatically drops and rebuilds tables if schema_version mismatches.
        """
        conn = self.connect()
        # Verify existing schema version if meta table exists
        has_meta = (
            conn.execute(
                "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='meta';"
            ).fetchone()[0]
            > 0
        )

        current_version = self.get_meta("schema_version") if has_meta else None

        if current_version != SCHEMA_VERSION:
            with conn:
                conn.execute("PRAGMA foreign_keys = OFF;")
                conn.execute("DROP TABLE IF EXISTS build_artifacts;")
                conn.execute("DROP TABLE IF EXISTS doc_metadata;")
                conn.execute("DROP TABLE IF EXISTS links;")
                conn.execute("DROP TABLE IF EXISTS files;")
                conn.execute("DROP TABLE IF EXISTS meta;")
                conn.execute("PRAGMA foreign_keys = ON;")
                conn.executescript(SCHEMA_SQL)
                conn.execute(
                    "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?);",
                    ("schema_version", SCHEMA_VERSION),
                )
        else:
            with conn:
                conn.executescript(SCHEMA_SQL)

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
        Inserts or updates a file record keyed on canonical_filename.
        """
        conn = self.connect()
        cursor = conn.execute(
            """
            INSERT INTO files (canonical_filename, stem, ext, rel_path, sha256, mtime, size, is_media, is_secure)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(canonical_filename) DO UPDATE SET
                stem = excluded.stem,
                ext = excluded.ext,
                rel_path = excluded.rel_path,
                sha256 = excluded.sha256,
                mtime = excluded.mtime,
                size = excluded.size,
                is_media = excluded.is_media,
                is_secure = excluded.is_secure;
            """,
            (
                record.canonical_filename,
                record.stem,
                record.ext,
                record.rel_path,
                record.sha256,
                record.mtime,
                record.size,
                1 if record.is_media else 0,
                1 if record.is_secure else 0,
            ),
        )
        return cursor.lastrowid

    def get_file_by_canonical(self, canonical_filename: str) -> Optional[FileRecord]:
        conn = self.connect()
        row = conn.execute(
            "SELECT * FROM files WHERE canonical_filename = ?;", (canonical_filename,)
        ).fetchone()
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

    def delete_file_by_canonical(self, canonical_filename: str):
        conn = self.connect()
        conn.execute(
            "DELETE FROM files WHERE canonical_filename = ?;", (canonical_filename,)
        )

    def delete_file_by_path(self, rel_path: str):
        conn = self.connect()
        conn.execute("DELETE FROM files WHERE rel_path = ?;", (rel_path,))

    # -----------------------------------------------------------------------
    # Stat-Cache Fast-Path Queries
    # -----------------------------------------------------------------------

    def is_stat_cache_hit(self, rel_path: str, mtime: float, size: int) -> bool:
        conn = self.connect()
        row = conn.execute(
            "SELECT mtime, size FROM files WHERE rel_path = ?;",
            (rel_path,),
        ).fetchone()
        if not row:
            return False
        return abs(row["mtime"] - mtime) < 0.0001 and row["size"] == size

    # -----------------------------------------------------------------------
    # Link Graph Operations
    # -----------------------------------------------------------------------

    def replace_document_links(self, source_canonical: str, links: List[LinkRecord]):
        """
        Atomically replaces all outgoing link edges for a given source canonical filename.
        """
        conn = self.connect()
        with conn:
            conn.execute(
                "DELETE FROM links WHERE source_canonical = ?;", (source_canonical,)
            )
            if links:
                conn.executemany(
                    """
                    INSERT INTO links (source_canonical, target_canonical, raw_target, line_number)
                    VALUES (?, ?, ?, ?);
                    """,
                    [
                        (
                            l.source_canonical,
                            l.target_canonical,
                            l.raw_target,
                            l.line_number,
                        )
                        for l in links
                    ],
                )

    def get_referencing_links(self, target_canonical: str) -> List[LinkRecord]:
        conn = self.connect()
        rows = conn.execute(
            "SELECT source_canonical, target_canonical, raw_target, line_number FROM links WHERE target_canonical = ?;",
            (target_canonical,),
        ).fetchall()
        return [
            LinkRecord(
                source_canonical=r["source_canonical"],
                target_canonical=r["target_canonical"],
                raw_target=r["raw_target"],
                line_number=r["line_number"],
            )
            for r in rows
        ]

    def get_outgoing_links(self, source_canonical: str) -> List[LinkRecord]:
        conn = self.connect()
        rows = conn.execute(
            "SELECT source_canonical, target_canonical, raw_target, line_number FROM links WHERE source_canonical = ?;",
            (source_canonical,),
        ).fetchall()
        return [
            LinkRecord(
                source_canonical=r["source_canonical"],
                target_canonical=r["target_canonical"],
                raw_target=r["raw_target"],
                line_number=r["line_number"],
            )
            for r in rows
        ]

    # -----------------------------------------------------------------------
    # Document Metadata Operations
    # -----------------------------------------------------------------------

    def upsert_doc_metadata(self, record: DocMetadataRecord):
        conn = self.connect()
        conn.execute(
            """
            INSERT INTO doc_metadata (canonical_filename, title, date_edtf, keywords, has_citations)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(canonical_filename) DO UPDATE SET
                title = excluded.title,
                date_edtf = excluded.date_edtf,
                keywords = excluded.keywords,
                has_citations = excluded.has_citations;
            """,
            (
                record.canonical_filename,
                record.title,
                record.date_edtf,
                record.keywords,
                1 if record.has_citations else 0,
            ),
        )

    def get_doc_metadata(self, canonical_filename: str) -> Optional[DocMetadataRecord]:
        conn = self.connect()
        row = conn.execute(
            "SELECT * FROM doc_metadata WHERE canonical_filename = ?;",
            (canonical_filename,),
        ).fetchone()
        if not row:
            return None
        return DocMetadataRecord(
            canonical_filename=row["canonical_filename"],
            title=row["title"],
            date_edtf=row["date_edtf"],
            keywords=row["keywords"],
            has_citations=bool(row["has_citations"]),
        )

    def get_all_doc_metadata(self) -> Dict[str, DocMetadataRecord]:
        conn = self.connect()
        rows = conn.execute("SELECT * FROM doc_metadata;").fetchall()
        return {
            r["canonical_filename"]: DocMetadataRecord(
                canonical_filename=r["canonical_filename"],
                title=r["title"],
                date_edtf=r["date_edtf"],
                keywords=r["keywords"],
                has_citations=bool(r["has_citations"]),
            )
            for r in rows
        }

    # -----------------------------------------------------------------------
    # Build Artifact Operations
    # -----------------------------------------------------------------------

    def upsert_build_artifacts(self, records: List[BuildArtifactRecord]):
        if not records:
            return
        conn = self.connect()
        with conn:
            conn.executemany(
                """
                INSERT INTO build_artifacts (target_rel_path, source_sha256, artifact_category)
                VALUES (?, ?, ?)
                ON CONFLICT(target_rel_path) DO UPDATE SET
                    source_sha256 = excluded.source_sha256,
                    artifact_category = excluded.artifact_category;
                """,
                [
                    (r.target_rel_path, r.source_sha256, r.artifact_category)
                    for r in records
                ],
            )

    def get_all_build_artifacts(self) -> Dict[str, BuildArtifactRecord]:
        conn = self.connect()
        rows = conn.execute("SELECT * FROM build_artifacts;").fetchall()
        return {
            r["target_rel_path"]: BuildArtifactRecord(
                target_rel_path=r["target_rel_path"],
                source_sha256=r["source_sha256"],
                artifact_category=r["artifact_category"],
            )
            for r in rows
        }

    def prune_build_artifacts(self, valid_targets: Set[str]) -> int:
        conn = self.connect()
        rows = conn.execute("SELECT target_rel_path FROM build_artifacts;").fetchall()
        to_delete = [
            r["target_rel_path"]
            for r in rows
            if r["target_rel_path"] not in valid_targets
        ]
        if to_delete:
            with conn:
                conn.executemany(
                    "DELETE FROM build_artifacts WHERE target_rel_path = ?;",
                    [(t,) for t in to_delete],
                )
        return len(to_delete)

    def clear_build_state(self):
        conn = self.connect()
        with conn:
            conn.execute("DELETE FROM build_artifacts;")
            conn.execute("DELETE FROM meta WHERE key != 'schema_version';")

    # -----------------------------------------------------------------------
    # Helper Conversion
    # -----------------------------------------------------------------------

    @staticmethod
    def _row_to_file_record(row: sqlite3.Row) -> FileRecord:
        return FileRecord(
            id=row["id"],
            canonical_filename=row["canonical_filename"],
            stem=row["stem"],
            ext=row["ext"],
            rel_path=row["rel_path"],
            sha256=row["sha256"],
            mtime=row["mtime"],
            size=row["size"],
            is_media=bool(row["is_media"]),
            is_secure=bool(row["is_secure"]),
        )
