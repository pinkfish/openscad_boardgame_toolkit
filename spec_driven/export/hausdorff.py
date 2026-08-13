# SPDX-License-Identifier: Apache-2.0
"""Conditional write gated on mesh equivalence (T071 / FR-026).

Re-exporting an unchanged box should not rewrite its 3MF — a rewritten file
looks modified to the slicer and to git even when the geometry is identical.
`should_write` decides by comparing the candidate against what is already on
disk, preferring a Hausdorff distance from pymeshlab and falling back to a
byte hash when pymeshlab is not installed.
"""

from __future__ import annotations

import hashlib
import re
import zipfile
from pathlib import Path

HAUSDORFF_TOLERANCE_MM = 0.001
"""Meshes closer than this are treated as the same geometry."""

_MESH_RE = re.compile(rb"<mesh>.*?</mesh>", re.S)


def file_digest(path: Path) -> str | None:
    """SHA-256 of a file's bytes, or None when the file does not exist."""
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def mesh_digest(path: Path) -> str | None:
    """SHA-256 of a file's *geometry*, ignoring metadata.

    A 3MF carries a title, a creation timestamp and fresh random UUIDs on every
    write, so two exports of identical geometry never match byte for byte. This
    hashes only the `<mesh>` elements, which is what actually has to change
    before a rewrite is worth doing. Non-3MF files fall back to a byte hash.
    """
    if not path.exists():
        return None
    if path.suffix.lower() != ".3mf":
        return file_digest(path)

    try:
        with zipfile.ZipFile(path) as zf:
            models = sorted(n for n in zf.namelist() if n.endswith(".model"))
            h = hashlib.sha256()
            for name in models:
                for mesh in _MESH_RE.findall(zf.read(name)):
                    h.update(mesh)
            return h.hexdigest()
    except (zipfile.BadZipFile, OSError):
        return file_digest(path)


def hausdorff_distance(mesh_a: Path, mesh_b: Path) -> float | None:
    """Max Hausdorff distance between two mesh files, in mm.

    Returns None when pymeshlab is unavailable or either mesh cannot be read,
    which tells the caller to fall back to a byte comparison.
    """
    try:
        import pymeshlab  # type: ignore[import-not-found]
    except ImportError:
        return None

    try:
        ms = pymeshlab.MeshSet()
        ms.load_new_mesh(str(mesh_a))
        ms.load_new_mesh(str(mesh_b))
        res = ms.get_hausdorff_distance(sampledmesh=0, targetmesh=1)
        return float(res["max"])
    except Exception:
        return None


def meshes_equivalent(
    existing: Path, candidate: Path, tolerance: float = HAUSDORFF_TOLERANCE_MM
) -> bool:
    """True when `candidate` is the same geometry as `existing`."""
    if not existing.exists() or not candidate.exists():
        return False

    distance = hausdorff_distance(existing, candidate)
    if distance is not None:
        return distance < tolerance

    return mesh_digest(existing) == mesh_digest(candidate)


def should_write(existing: Path, candidate: Path, tolerance: float = HAUSDORFF_TOLERANCE_MM) -> bool:
    """True when `candidate` differs enough from `existing` to be worth writing."""
    return not meshes_equivalent(existing, candidate, tolerance)
