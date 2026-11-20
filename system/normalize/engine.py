"""
system/normalize/engine.py - Identity Decision Matrix & Reconciliation Engine.
Correlates physical disk state against the SQLite ledger (P, S, H) to plan mutations.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import PurePosixPath
from typing import Dict, List, Optional, Set, Tuple

from .db import FileRecord, VaultDB
from .scanner import ScannedFile, VaultScanResult
from .slugify import is_valid_stem, sanitize_path_segments, slugify_stem


class ActionType(Enum):
    NOOP = auto()
    CREATE = auto()
    DELETE = auto()
    MODIFY_CONTENT = auto()
    MOVE = auto()
    RENAME = auto()
    MOVE_AND_RENAME = auto()
    SANITIZE_STEM = auto()
    SANITIZE_PATH = auto()
    RESOLVE_COLLISION = auto()


@dataclass(frozen=True)
class FileAction:
    action_type: ActionType
    src_rel_path: Optional[str]
    dst_rel_path: Optional[str]
    old_stem: Optional[str]
    new_stem: Optional[str]
    sha256: str
    is_media: bool
    is_secure: bool
    reason: str


@dataclass(frozen=True)
class BoundaryViolation:
    source_rel_path: str
    target_rel_path: str
    source_is_secure: bool
    target_is_secure: bool
    line_number: int


@dataclass
class DiffPlan:
    actions: List[FileAction] = field(default_factory=list)
    collisions: Dict[str, List[str]] = field(default_factory=lambda: defaultdict(list))
    broken_references: Dict[str, List[str]] = field(
        default_factory=lambda: defaultdict(list)
    )
    boundary_violations: List[BoundaryViolation] = field(default_factory=list)

    @property
    def has_mutations(self) -> bool:
        return any(a.action_type != ActionType.NOOP for a in self.actions)


def resolve_collision_stem(
    base_stem: str, ext: str, existing_filenames: Set[str]
) -> str:
    """Appends the lowest available positive integer suffix (e.g. 'energy-1.md')."""
    counter = 1
    while True:
        candidate_stem = f"{base_stem}-{counter}"
        candidate_filename = f"{candidate_stem}{ext}"
        if candidate_filename not in existing_filenames:
            return candidate_stem
        counter += 1


def compute_diff(scan_result: VaultScanResult, db: VaultDB) -> DiffPlan:
    """
    Computes differences between physical disk scan and SQLite ledger.
    Implements the Identity Decision Matrix: (P, S, H) -> (P', S', H')
    """
    plan = DiffPlan()

    db_files = db.get_all_files()
    db_by_stem: Dict[str, FileRecord] = {r.stem: r for r in db_files.values()}
    db_by_hash: Dict[str, List[FileRecord]] = defaultdict(list)
    for r in db_files.values():
        db_by_hash[r.sha256].append(r)

    disk_files = scan_result.files
    disk_by_path: Dict[str, ScannedFile] = {f.rel_path: f for f in disk_files}

    # Step 1: Detect canonical filename collisions across scanned disk files
    disk_filenames: Dict[str, List[ScannedFile]] = defaultdict(list)
    for f in disk_files:
        disk_filenames[f.canonical_filename].append(f)

    for c_filename, occurrences in disk_filenames.items():
        if len(occurrences) > 1:
            plan.collisions[c_filename] = [o.rel_path for o in occurrences]

    unmatched_db_paths: Set[str] = set(db_files.keys())
    unmatched_disk_paths: Set[str] = set(disk_by_path.keys())
    matched_pairs: List[Tuple[FileRecord, ScannedFile]] = []

    # Step 2: Correlate exact path matches (P == P')
    for rel_path in list(unmatched_disk_paths):
        if rel_path in unmatched_db_paths:
            db_rec = db_files[rel_path]
            disk_rec = disk_by_path[rel_path]
            matched_pairs.append((db_rec, disk_rec))
            unmatched_db_paths.remove(rel_path)
            unmatched_disk_paths.remove(rel_path)

    # Step 3: Correlate moved files with identical content hash (H == H')
    for rel_path in list(unmatched_disk_paths):
        disk_rec = disk_by_path[rel_path]
        candidates = [
            db_rec
            for db_rec in db_by_hash.get(disk_rec.sha256, [])
            if db_rec.rel_path in unmatched_db_paths
        ]
        if candidates:
            chosen = next(
                (c for c in candidates if c.stem == disk_rec.stem), candidates[0]
            )
            matched_pairs.append((chosen, disk_rec))
            unmatched_db_paths.remove(chosen.rel_path)
            unmatched_disk_paths.remove(rel_path)

    # Step 4: Correlate moved files with modified content via Stem UID (S == S', H != H')
    for rel_path in list(unmatched_disk_paths):
        disk_rec = disk_by_path[rel_path]
        if disk_rec.stem in db_by_stem:
            db_rec = db_by_stem[disk_rec.stem]
            if db_rec.rel_path in unmatched_db_paths:
                matched_pairs.append((db_rec, disk_rec))
                unmatched_db_paths.remove(db_rec.rel_path)
                unmatched_disk_paths.remove(rel_path)

    # Track allocated canonical filenames to ensure global uniqueness across content/
    allocated_filenames: Set[str] = set()

    # Sort matched pairs deterministically by (mtime, rel_path)
    matched_pairs.sort(key=lambda pair: (pair[1].mtime, pair[1].rel_path))

    # Evaluate correlated pairs
    for db_rec, disk_rec in matched_pairs:
        p_match = db_rec.rel_path == disk_rec.rel_path
        s_match = db_rec.stem == disk_rec.stem
        h_match = db_rec.sha256 == disk_rec.sha256

        canonical_stem = slugify_stem(disk_rec.stem)
        canonical_filename = f"{canonical_stem}{disk_rec.ext}"
        canonical_path = sanitize_path_segments(disk_rec.rel_path)

        needs_stem_sanitize = (
            not is_valid_stem(disk_rec.stem) or disk_rec.stem != canonical_stem
        )
        needs_path_sanitize = disk_rec.rel_path != canonical_path
        is_colliding = canonical_filename in allocated_filenames

        if p_match and s_match and h_match:
            if is_colliding or needs_stem_sanitize:
                target_stem = canonical_stem
                if is_colliding:
                    target_stem = resolve_collision_stem(
                        canonical_stem, disk_rec.ext, allocated_filenames
                    )
                target_filename = f"{target_stem}{disk_rec.ext}"
                allocated_filenames.add(target_filename)
                action_type = (
                    ActionType.RESOLVE_COLLISION
                    if is_colliding
                    else ActionType.SANITIZE_STEM
                )
                plan.actions.append(
                    FileAction(
                        action_type=action_type,
                        src_rel_path=disk_rec.rel_path,
                        dst_rel_path=str(
                            PurePosixPath(disk_rec.rel_path).with_name(target_filename)
                        ),
                        old_stem=disk_rec.stem,
                        new_stem=target_stem,
                        sha256=disk_rec.sha256,
                        is_media=disk_rec.is_media,
                        is_secure=disk_rec.is_secure,
                        reason="Collision resolved or stem violates archival specification.",
                    )
                )
            elif needs_path_sanitize:
                allocated_filenames.add(canonical_filename)
                plan.actions.append(
                    FileAction(
                        action_type=ActionType.SANITIZE_PATH,
                        src_rel_path=disk_rec.rel_path,
                        dst_rel_path=canonical_path,
                        old_stem=disk_rec.stem,
                        new_stem=disk_rec.stem,
                        sha256=disk_rec.sha256,
                        is_media=disk_rec.is_media,
                        is_secure=disk_rec.is_secure,
                        reason="Directory path segments contain un-normalized characters.",
                    )
                )
            else:
                allocated_filenames.add(canonical_filename)
                plan.actions.append(
                    FileAction(
                        action_type=ActionType.NOOP,
                        src_rel_path=disk_rec.rel_path,
                        dst_rel_path=disk_rec.rel_path,
                        old_stem=disk_rec.stem,
                        new_stem=disk_rec.stem,
                        sha256=disk_rec.sha256,
                        is_media=disk_rec.is_media,
                        is_secure=disk_rec.is_secure,
                        reason="Identical to ledger state.",
                    )
                )

        elif p_match and s_match and not h_match:
            allocated_filenames.add(canonical_filename)
            plan.actions.append(
                FileAction(
                    action_type=ActionType.MODIFY_CONTENT,
                    src_rel_path=disk_rec.rel_path,
                    dst_rel_path=disk_rec.rel_path,
                    old_stem=disk_rec.stem,
                    new_stem=disk_rec.stem,
                    sha256=disk_rec.sha256,
                    is_media=disk_rec.is_media,
                    is_secure=disk_rec.is_secure,
                    reason="File content modified in place.",
                )
            )

        elif not p_match and s_match and h_match:
            allocated_filenames.add(canonical_filename)
            plan.actions.append(
                FileAction(
                    action_type=ActionType.MOVE,
                    src_rel_path=db_rec.rel_path,
                    dst_rel_path=disk_rec.rel_path,
                    old_stem=db_rec.stem,
                    new_stem=disk_rec.stem,
                    sha256=disk_rec.sha256,
                    is_media=disk_rec.is_media,
                    is_secure=disk_rec.is_secure,
                    reason=f"Moved from '{db_rec.rel_path}' to '{disk_rec.rel_path}'.",
                )
            )

        elif (
            PurePosixPath(db_rec.rel_path).parent
            == PurePosixPath(disk_rec.rel_path).parent
            and not s_match
            and h_match
        ):
            allocated_filenames.add(canonical_filename)
            plan.actions.append(
                FileAction(
                    action_type=ActionType.RENAME,
                    src_rel_path=db_rec.rel_path,
                    dst_rel_path=disk_rec.rel_path,
                    old_stem=db_rec.stem,
                    new_stem=disk_rec.stem,
                    sha256=disk_rec.sha256,
                    is_media=disk_rec.is_media,
                    is_secure=disk_rec.is_secure,
                    reason=f"Renamed from '{db_rec.stem}' to '{disk_rec.stem}'.",
                )
            )

        elif (
            PurePosixPath(db_rec.rel_path).parent
            != PurePosixPath(disk_rec.rel_path).parent
            and not s_match
            and h_match
        ):
            allocated_filenames.add(canonical_filename)
            plan.actions.append(
                FileAction(
                    action_type=ActionType.MOVE_AND_RENAME,
                    src_rel_path=db_rec.rel_path,
                    dst_rel_path=disk_rec.rel_path,
                    old_stem=db_rec.stem,
                    new_stem=disk_rec.stem,
                    sha256=disk_rec.sha256,
                    is_media=disk_rec.is_media,
                    is_secure=disk_rec.is_secure,
                    reason=f"Moved and renamed from '{db_rec.rel_path}'.",
                )
            )

        elif not p_match and s_match and not h_match:
            allocated_filenames.add(canonical_filename)
            plan.actions.append(
                FileAction(
                    action_type=ActionType.MOVE,
                    src_rel_path=db_rec.rel_path,
                    dst_rel_path=disk_rec.rel_path,
                    old_stem=db_rec.stem,
                    new_stem=disk_rec.stem,
                    sha256=disk_rec.sha256,
                    is_media=disk_rec.is_media,
                    is_secure=disk_rec.is_secure,
                    reason=f"Moved from '{db_rec.rel_path}' and modified.",
                )
            )

    # Step 5: Remaining unmatched disk files -> CREATE, SANITIZE, or RESOLVE_COLLISION
    for db_rec in db_files.values():
        if db_rec.rel_path in unmatched_db_paths:
            allocated_filenames.add(db_rec.canonical_filename)

    sorted_unmatched_disk = sorted(
        unmatched_disk_paths,
        key=lambda p: (disk_by_path[p].mtime, p),
    )

    for rel_path in sorted_unmatched_disk:
        disk_rec = disk_by_path[rel_path]
        canonical_stem = slugify_stem(disk_rec.stem)
        canonical_filename = f"{canonical_stem}{disk_rec.ext}"
        target_stem = canonical_stem
        is_collision = False

        if canonical_filename in allocated_filenames:
            target_stem = resolve_collision_stem(
                canonical_stem, disk_rec.ext, allocated_filenames
            )
            is_collision = True

        target_filename = f"{target_stem}{disk_rec.ext}"
        allocated_filenames.add(target_filename)

        canonical_path = sanitize_path_segments(rel_path)
        if target_stem != disk_rec.stem:
            canonical_path = str(
                PurePosixPath(canonical_path).with_name(target_filename)
            )

        needs_stem_sanitize = (
            not is_valid_stem(disk_rec.stem) or disk_rec.stem != target_stem
        )
        needs_path_sanitize = disk_rec.rel_path != canonical_path

        if is_collision:
            plan.actions.append(
                FileAction(
                    action_type=ActionType.RESOLVE_COLLISION,
                    src_rel_path=disk_rec.rel_path,
                    dst_rel_path=canonical_path,
                    old_stem=disk_rec.stem,
                    new_stem=target_stem,
                    sha256=disk_rec.sha256,
                    is_media=disk_rec.is_media,
                    is_secure=disk_rec.is_secure,
                    reason=f"Stem collision on '{canonical_stem}' resolved to '{target_stem}'.",
                )
            )
        elif needs_stem_sanitize or needs_path_sanitize:
            action_type = (
                ActionType.SANITIZE_STEM
                if needs_stem_sanitize
                else ActionType.SANITIZE_PATH
            )
            plan.actions.append(
                FileAction(
                    action_type=action_type,
                    src_rel_path=disk_rec.rel_path,
                    dst_rel_path=canonical_path,
                    old_stem=disk_rec.stem,
                    new_stem=target_stem,
                    sha256=disk_rec.sha256,
                    is_media=disk_rec.is_media,
                    is_secure=disk_rec.is_secure,
                    reason="New file on disk requires name/path sanitization.",
                )
            )
        else:
            plan.actions.append(
                FileAction(
                    action_type=ActionType.CREATE,
                    src_rel_path=None,
                    dst_rel_path=disk_rec.rel_path,
                    old_stem=None,
                    new_stem=disk_rec.stem,
                    sha256=disk_rec.sha256,
                    is_media=disk_rec.is_media,
                    is_secure=disk_rec.is_secure,
                    reason="New file detected on disk.",
                )
            )

        # Step 6: Remaining unmatched DB files -> DELETE
        for deleted_rel_path in sorted(unmatched_db_paths):
            db_rec = db_files[deleted_rel_path]
            inbound_links = db.get_referencing_links(db_rec.canonical_filename)

            if inbound_links:
                plan.broken_references[db_rec.stem] = [
                    l.source_canonical for l in inbound_links
                ]

            plan.actions.append(
                FileAction(
                    action_type=ActionType.DELETE,
                    src_rel_path=db_rec.rel_path,
                    dst_rel_path=None,
                    old_stem=db_rec.stem,
                    new_stem=None,
                    sha256=db_rec.sha256,
                    is_media=db_rec.is_media,
                    is_secure=db_rec.is_secure,
                    reason=f"File removed from disk (had {len(inbound_links)} inbound references).",
                )
            )

        return plan
