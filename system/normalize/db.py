"""
system/normalize/db.py - SQLite Ledger & Stat-Cache Acceleration Layer.
Stores the master file registry, link dependencies, document metadata, and build artifacts.
"""

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set

SCHEMA_VERSION = "4.0"

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
    canonical_filename TEXT UNIQUE NOT NULL COLLATE NOCASE,
    stem TEXT NOT NULL COLLATE NOCASE,
    ext TEXT NOT NULL COLLATE NOCASE,
    rel_path TEXT UNIQUE NOT NULL COLLATE NOCASE,
    sha256 TEXT NOT NULL,
    mtime REAL NOT NULL,
    mtime_ns INTEGER NOT NULL,
    size INTEGER NOT NULL,
    is_media INTEGER NOT NULL DEFAULT 0,
    is_secure INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_files_canonical ON files(canonical_filename);
CREATE INDEX IF NOT EXISTS idx_files_stem ON files(stem);
CREATE INDEX IF NOT EXISTS idx_files_sha256 ON files(sha256);
CREATE INDEX IF NOT EXISTS idx_files_rel_path ON files(rel_path);

CREATE TABLE IF NOT EXISTS links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_canonical TEXT NOT NULL COLLATE NOCASE,
    target_canonical TEXT NOT NULL COLLATE NOCASE,
    target_rel_path TEXT NOT NULL DEFAULT '',
    raw_target TEXT NOT NULL,
    line_number INTEGER,
    start_char INTEGER NOT NULL DEFAULT 0,
    end_char INTEGER NOT NULL DEFAULT 0,
    is_image INTEGER NOT NULL DEFAULT 0,
    is_broken INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY(source_canonical) REFERENCES files(canonical_filename) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_links_target ON links(target_canonical);
CREATE INDEX IF NOT EXISTS idx_links_source ON links(source_canonical);
CREATE INDEX IF NOT EXISTS idx_links_broken ON links(is_broken);

CREATE TABLE IF NOT EXISTS doc_metadata (
    canonical_filename TEXT PRIMARY KEY COLLATE NOCASE,
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

CREATE TABLE IF NOT EXISTS mutation_journal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    stage TEXT NOT NULL CHECK(stage IN ('STAGED', 'RENAMED', 'PATCHED', 'COMMITTED')),
    file_renames_json TEXT NOT NULL,
    content_patches_json TEXT NOT NULL,
    created_at TEXT NOT NULL
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
    mtime_ns: int
    size: int
    is_media: bool
    is_secure: bool


@dataclass(frozen=True)
class LinkRecord:
    source_canonical: str
    target_canonical: str
    raw_target: str
    line_number: Optional[int]
    target_rel_path: str = ""
    start_char: int = 0
    end_char: int = 0
    is_image: bool = False
    is_broken: bool = False


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


@dataclass(frozen=True)
class JournalRecord:
    id: Optional[int]
    session_id: str
    stage: str
    file_renames_json: str
    content_patches_json: str
    created_at: str


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
            )
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("PRAGMA journal_mode = WAL;")
            conn.execute("PRAGMA synchronous = NORMAL;")
            self._conn = conn
        return self._conn

    def close(self):
        if self._conn is not None:
            try:
                self._conn.commit()
            except Exception:
                pass
            self._conn.close()
            self._conn = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def transaction(self):
        """Returns a transaction context manager via `with conn:`."""
        return self.connect()

    def init_schema(self):
        """
        Initializes tables, indices, and default metadata.
        Automatically drops and rebuilds tables if schema_version mismatches.
        """
        conn = self.connect()
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
        with conn:
            conn.execute(
                "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?);",
                (key, value),
            )

    # -----------------------------------------------------------------------
    # File Ledger Operations
    # -----------------------------------------------------------------------

    def upsert_file(self, record: FileRecord) -> int:
        conn = self.connect()
        with conn:
            cursor = conn.execute(
                """
                INSERT INTO files (canonical_filename, stem, ext, rel_path, sha256, mtime, mtime_ns, size, is_media, is_secure)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(canonical_filename) DO UPDATE SET
                    stem = excluded.stem,
                    ext = excluded.ext,
                    rel_path = excluded.rel_path,
                    sha256 = excluded.sha256,
                    mtime = excluded.mtime,
                    mtime_ns = excluded.mtime_ns,
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
                    record.mtime_ns,
                    record.size,
                    1 if record.is_media else 0,
                    1 if record.is_secure else 0,
                ),
            )
            return cursor.lastrowid or 0

    def upsert_files_batch(self, records: List[FileRecord]):
        if not records:
            return
        conn = self.connect()
        with conn:
            conn.executemany(
                """
                INSERT INTO files (canonical_filename, stem, ext, rel_path, sha256, mtime, mtime_ns, size, is_media, is_secure)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(canonical_filename) DO UPDATE SET
                    stem = excluded.stem,
                    ext = excluded.ext,
                    rel_path = excluded.rel_path,
                    sha256 = excluded.sha256,
                    mtime = excluded.mtime,
                    mtime_ns = excluded.mtime_ns,
                    size = excluded.size,
                    is_media = excluded.is_media,
                    is_secure = excluded.is_secure;
                """,
                [
                    (
                        r.canonical_filename,
                        r.stem,
                        r.ext,
                        r.rel_path,
                        r.sha256,
                        r.mtime,
                        r.mtime_ns,
                        r.size,
                        1 if r.is_media else 0,
                        1 if r.is_secure else 0,
                    )
                    for r in records
                ],
            )

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
        with conn:
            conn.execute(
                "DELETE FROM files WHERE canonical_filename = ?;", (canonical_filename,)
            )

    def delete_file_by_path(self, rel_path: str):
        conn = self.connect()
        with conn:
            conn.execute("DELETE FROM files WHERE rel_path = ?;", (rel_path,))

    def delete_files_by_paths_batch(self, rel_paths: List[str]):
        if not rel_paths:
            return
        conn = self.connect()
        with conn:
            conn.executemany(
                "DELETE FROM files WHERE rel_path = ?;", [(p,) for p in rel_paths]
            )

    # -----------------------------------------------------------------------
    # Stat-Cache Fast-Path Queries
    # -----------------------------------------------------------------------

    def is_stat_cache_hit(self, rel_path: str, mtime_ns: int, size: int) -> bool:
        conn = self.connect()
        row = conn.execute(
            "SELECT mtime_ns, size FROM files WHERE rel_path = ?;",
            (rel_path,),
        ).fetchone()
        if not row:
            return False
        return row["mtime_ns"] == mtime_ns and row["size"] == size

    # -----------------------------------------------------------------------
    # Link Graph Operations
    # -----------------------------------------------------------------------

    def replace_document_links(self, source_canonical: str, links: List[LinkRecord]):
        conn = self.connect()
        with conn:
            conn.execute(
                "DELETE FROM links WHERE source_canonical = ?;", (source_canonical,)
            )
            if links:
                conn.executemany(
                    """
                    INSERT INTO links (source_canonical, target_canonical, target_rel_path, raw_target, line_number, start_char, end_char, is_image, is_broken)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    [
                        (
                            l.source_canonical,
                            l.target_canonical,
                            l.target_rel_path,
                            l.raw_target,
                            l.line_number,
                            l.start_char,
                            l.end_char,
                            1 if l.is_image else 0,
                            1 if l.is_broken else 0,
                        )
                        for l in links
                    ],
                )

    def replace_all_links_batch(self, links_by_source: Dict[str, List[LinkRecord]]):
        if not links_by_source:
            return
        conn = self.connect()
        with conn:
            for source_canonical, links in links_by_source.items():
                conn.execute(
                    "DELETE FROM links WHERE source_canonical = ?;", (source_canonical,)
                )
                if links:
                    conn.executemany(
                        """
                        INSERT INTO links (source_canonical, target_canonical, target_rel_path, raw_target, line_number, start_char, end_char, is_image, is_broken)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                        """,
                        [
                            (
                                l.source_canonical,
                                l.target_canonical,
                                l.target_rel_path,
                                l.raw_target,
                                l.line_number,
                                l.start_char,
                                l.end_char,
                                1 if l.is_image else 0,
                                1 if l.is_broken else 0,
                            )
                            for l in links
                        ],
                    )

    def get_referencing_links(self, target_canonical: str) -> List[LinkRecord]:
        conn = self.connect()
        rows = conn.execute(
            "SELECT source_canonical, target_canonical, target_rel_path, raw_target, line_number, start_char, end_char, is_image, is_broken FROM links WHERE target_canonical = ?;",
            (target_canonical,),
        ).fetchall()
        return [
            LinkRecord(
                source_canonical=r["source_canonical"],
                target_canonical=r["target_canonical"],
                target_rel_path=r["target_rel_path"],
                raw_target=r["raw_target"],
                line_number=r["line_number"],
                start_char=r["start_char"],
                end_char=r["end_char"],
                is_image=bool(r["is_image"]),
                is_broken=bool(r["is_broken"]),
            )
            for r in rows
        ]

    def get_outgoing_links(self, source_canonical: str) -> List[LinkRecord]:
        conn = self.connect()
        rows = conn.execute(
            "SELECT source_canonical, target_canonical, target_rel_path, raw_target, line_number, start_char, end_char, is_image, is_broken FROM links WHERE source_canonical = ?;",
            (source_canonical,),
        ).fetchall()
        return [
            LinkRecord(
                source_canonical=r["source_canonical"],
                target_canonical=r["target_canonical"],
                target_rel_path=r["target_rel_path"],
                raw_target=r["raw_target"],
                line_number=r["line_number"],
                start_char=r["start_char"],
                end_char=r["end_char"],
                is_image=bool(r["is_image"]),
                is_broken=bool(r["is_broken"]),
            )
            for r in rows
        ]

    def get_all_links(self) -> List[LinkRecord]:
        conn = self.connect()
        rows = conn.execute(
            "SELECT source_canonical, target_canonical, target_rel_path, raw_target, line_number, start_char, end_char, is_image, is_broken FROM links;"
        ).fetchall()
        return [
            LinkRecord(
                source_canonical=r["source_canonical"],
                target_canonical=r["target_canonical"],
                target_rel_path=r["target_rel_path"],
                raw_target=r["raw_target"],
                line_number=r["line_number"],
                start_char=r["start_char"],
                end_char=r["end_char"],
                is_image=bool(r["is_image"]),
                is_broken=bool(r["is_broken"]),
            )
            for r in rows
        ]

    # -----------------------------------------------------------------------
    # Mutation Journal Operations
    # -----------------------------------------------------------------------

    def record_journal(
        self,
        session_id: str,
        stage: str,
        file_renames_json: str,
        content_patches_json: str,
        created_at: str,
    ) -> int:
        conn = self.connect()
        with conn:
            cursor = conn.execute(
                """
                INSERT INTO mutation_journal (session_id, stage, file_renames_json, content_patches_json, created_at)
                VALUES (?, ?, ?, ?, ?);
                """,
                (
                    session_id,
                    stage,
                    file_renames_json,
                    content_patches_json,
                    created_at,
                ),
            )
            return cursor.lastrowid or 0

    def update_journal_stage(self, journal_id: int, new_stage: str):
        conn = self.connect()
        with conn:
            conn.execute(
                "UPDATE mutation_journal SET stage = ? WHERE id = ?;",
                (new_stage, journal_id),
            )

    def get_uncommitted_journal(self) -> Optional[JournalRecord]:
        conn = self.connect()
        row = conn.execute(
            "SELECT * FROM mutation_journal WHERE stage != 'COMMITTED' ORDER BY id DESC LIMIT 1;"
        ).fetchone()
        if not row:
            return None
        return JournalRecord(
            id=row["id"],
            session_id=row["session_id"],
            stage=row["stage"],
            file_renames_json=row["file_renames_json"],
            content_patches_json=row["content_patches_json"],
            created_at=row["created_at"],
        )

    def clear_committed_journals(self):
        conn = self.connect()
        with conn:
            conn.execute("DELETE FROM mutation_journal WHERE stage = 'COMMITTED';")

    # -----------------------------------------------------------------------
    # Document Metadata Operations
    # -----------------------------------------------------------------------

    def upsert_doc_metadata(self, record: DocMetadataRecord):
        conn = self.connect()
        with conn:
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

    def upsert_doc_metadata_batch(self, records: List[DocMetadataRecord]):
        if not records:
            return
        conn = self.connect()
        with conn:
            conn.executemany(
                """
                INSERT INTO doc_metadata (canonical_filename, title, date_edtf, keywords, has_citations)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(canonical_filename) DO UPDATE SET
                    title = excluded.title,
                    date_edtf = excluded.date_edtf,
                    keywords = excluded.keywords,
                    has_citations = excluded.has_citations;
                """,
                [
                    (
                        r.canonical_filename,
                        r.title,
                        r.date_edtf,
                        r.keywords,
                        1 if r.has_citations else 0,
                    )
                    for r in records
                ],
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
            mtime_ns=row["mtime_ns"]
            if "mtime_ns" in row.keys()
            else int(row["mtime"] * 1e9),
            size=row["size"],
            is_media=bool(row["is_media"]),
            is_secure=bool(row["is_secure"]),
        )
