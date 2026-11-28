"""
system/normalize - Content Normalization and Read-Only Diagnostic Engine.
Part of Project Kykloi.
"""

from .cli import (
    NormalizationPlan,
    build_normalization_plan,
    execute_normalization_plan,
    main,
    recover_uncommitted_journal,
    run_audit,
    run_normalization_pipeline,
    scaffold_new_document,
    sync_db_with_disk,
)
from .db import (
    BuildArtifactRecord,
    DocMetadataRecord,
    FileRecord,
    LinkRecord,
    VaultDB,
)
from .engine import (
    ActionType,
    BoundaryViolation,
    DiffPlan,
    FileAction,
    compute_diff,
    resolve_collision_stem,
)
from .graph import (
    BrokenLinkDiagnostic,
    ExtractedLink,
    compute_relative_link,
    extract_stem_from_path,
    is_external_or_anchor,
    mask_inline_code_spans,
    parse_markdown_links,
    split_target_url,
    to_link_records,
)
from .scanner import ScannedFile, VaultScanResult, is_junk_path, scan_vault
from .slugify import (
    is_valid_stem,
    sanitize_path_segments,
    slugify_stem,
)

__all__ = [
    # Database
    "VaultDB",
    "FileRecord",
    "LinkRecord",
    "DocMetadataRecord",
    "BuildArtifactRecord",
    # Slugify & Path Sanitization
    "slugify_stem",
    "is_valid_stem",
    "sanitize_path_segments",
    # Scanner
    "scan_vault",
    "is_junk_path",
    "ScannedFile",
    "VaultScanResult",
    # Identity Decision Engine
    "compute_diff",
    "DiffPlan",
    "FileAction",
    "ActionType",
    "BoundaryViolation",
    "resolve_collision_stem",
    # Graph & Read-Only Diagnostics
    "ExtractedLink",
    "BrokenLinkDiagnostic",
    "parse_markdown_links",
    "to_link_records",
    "compute_relative_link",
    "split_target_url",
    "extract_stem_from_path",
    "is_external_or_anchor",
    "mask_inline_code_spans",
    # Normalization & Orchestration
    "NormalizationPlan",
    "build_normalization_plan",
    "execute_normalization_plan",
    "recover_uncommitted_journal",
    "sync_db_with_disk",
    "run_audit",
    "run_normalization_pipeline",
    "scaffold_new_document",
    "main",
]
