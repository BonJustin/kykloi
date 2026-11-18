"""
system/normalize - Content Normalization and Link Reconciliation Engine.
Part of Project Kykloi.
"""

from .cli import (
    TransactionManifest,
    build_transaction_manifest,
    execute_transaction,
    main,
    sync_db_with_disk,
)
from .db import FileRecord, LinkRecord, VaultDB
from .engine import (
    ActionType,
    DiffPlan,
    FileAction,
    compute_diff,
    resolve_collision_stem,
)
from .graph import (
    ExtractedLink,
    compute_relative_link,
    extract_stem_from_path,
    heal_markdown_links,
    is_external_or_anchor,
    parse_markdown_links,
    split_target_url,
    to_link_records,
)
from .scanner import ScannedFile, VaultScanResult, is_junk_path, scan_vault
from .slugify import is_valid_stem, sanitize_path_segments, slugify_stem

__all__ = [
    "VaultDB",
    "FileRecord",
    "LinkRecord",
    "slugify_stem",
    "is_valid_stem",
    "sanitize_path_segments",
    "scan_vault",
    "is_junk_path",
    "ScannedFile",
    "VaultScanResult",
    "compute_diff",
    "DiffPlan",
    "FileAction",
    "ActionType",
    "resolve_collision_stem",
    "ExtractedLink",
    "parse_markdown_links",
    "to_link_records",
    "compute_relative_link",
    "heal_markdown_links",
    "split_target_url",
    "extract_stem_from_path",
    "is_external_or_anchor",
    "TransactionManifest",
    "build_transaction_manifest",
    "execute_transaction",
    "sync_db_with_disk",
    "main",
]
