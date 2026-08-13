# SPDX-License-Identifier: Apache-2.0
"""BoxExporter — writes per-box and per-spacer 3MF files (T068a/T068b/T070/T072).

Output layout (FR-025):

    {out_dir}/{game}/mmu/{label}_body.3mf
    {out_dir}/{game}/mmu/{label}_lid.3mf
    {out_dir}/{game}/single/{label}_body_single.3mf
    {out_dir}/{game}/single/{label}_lid_single.3mf

The `mmu` pass keeps positive inserts (labels, accents) as separate coloured
solids so the slicer can assign them their own material; the `single` pass fuses
everything into one body. Writes are gated on mesh equivalence, so re-exporting
an unchanged project rewrites nothing.

Geometry export runs through PythonSCAD, which is not importable from plain
CPython. When it is unavailable the exporter still creates the file tree and
records the piece's bounding box, so the layout, PDF and packing pipeline stay
testable off-app.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from pyboxbuilder.export.hausdorff import should_write

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid

MMU = "mmu"
SINGLE = "single"


@dataclass(frozen=True)
class PieceBounds:
    """Measured bounding box of one exported piece (T068b / FR-027)."""

    label: str
    """Piece name, e.g. "PlayerBoxBlack_body"."""
    size: tuple[float, float, float]
    """(width, length, height) in mm."""
    mode: str
    """"mmu" or "single"."""

    def fits_bed(self, bed: tuple[float, float, float]) -> bool:
        """True when the piece fits a printer bed of the given size."""
        return all(s <= b + 1e-6 for s, b in zip(self.size, bed))

    def __str__(self) -> str:
        w, l, h = self.size
        return f"{self.label} [{self.mode}]: {w:.1f} x {l:.1f} x {h:.1f} mm"


@dataclass
class ExporterState:
    """Files written / skipped so far, plus the bounding boxes measured."""

    written: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    bounds: list[PieceBounds] = field(default_factory=list)


class BoxExporter:
    """Writes the 3MF tree for one project.

    Args:
        out_dir: Root output directory.
        game: Project name; becomes the subdirectory under `out_dir`.
    """

    def __init__(self, out_dir: str | Path, game: str) -> None:
        self.root = Path(out_dir) / game
        self.game = game
        self.state = ExporterState()

    # ------------------------------------------------------------- filenames

    def path_for(self, label: str, part: str, mode: str) -> Path:
        """Path of one piece. `part` is "body" or "lid"."""
        suffix = "_single" if mode == SINGLE else ""
        return self.root / mode / f"{label}_{part}{suffix}.3mf"

    def relative(self, path: Path) -> str:
        """Path as recorded in `ExportResult`, relative to the output root."""
        return f"{self.game}/{path.relative_to(self.root).as_posix()}"

    # ----------------------------------------------------------------- write

    def write_piece(
        self,
        label: str,
        part: str,
        mode: str,
        solid: "Bosl2Solid | None" = None,
        inserts: "list[Bosl2Solid] | None" = None,
        size: tuple[float, float, float] | None = None,
    ) -> str | None:
        """Export one piece, skipping the write when the geometry is unchanged.

        Args:
            label: Box label.
            part: "body" or "lid".
            mode: "mmu" or "single".
            solid: The main geometry. None writes a placeholder (no app available).
            inserts: Positive coloured inserts. Kept as separate objects in mmu
                mode and unioned into `solid` in single mode (T068a).
            size: Bounding box to record when it cannot be measured from `solid`.

        Returns:
            The relative path if written, None if skipped.
        """
        path = self.path_for(label, part, mode)
        path.parent.mkdir(parents=True, exist_ok=True)

        payload = self._compose(solid, inserts, mode)
        measured = _measure(payload) or size
        if measured is not None:
            self.state.bounds.append(
                PieceBounds(label=f"{label}_{part}", size=measured, mode=mode)
            )

        # Keep the .3mf suffix on the temp file — the exporter picks its format
        # from the extension and silently falls back to STL without it.
        candidate = path.with_name(f".{path.stem}.tmp.3mf")
        wrote_candidate = _export_3mf(payload, candidate)

        if not wrote_candidate:
            # No geometry backend: create the file if it is missing, otherwise
            # leave the previous export in place rather than truncating it.
            if path.exists():
                self.state.skipped.append(self.relative(path))
                return None
            path.touch()
            self.state.written.append(self.relative(path))
            return self.relative(path)

        if path.exists() and not should_write(path, candidate):
            candidate.unlink(missing_ok=True)
            self.state.skipped.append(self.relative(path))
            return None

        candidate.replace(path)
        self.state.written.append(self.relative(path))
        return self.relative(path)

    def write_box(
        self,
        label: str,
        body: "Bosl2Solid | None" = None,
        lid: "Bosl2Solid | None" = None,
        body_inserts: "list[Bosl2Solid] | None" = None,
        lid_inserts: "list[Bosl2Solid] | None" = None,
        size: tuple[float, float, float] | None = None,
        has_lid: bool = True,
    ) -> list[str]:
        """Export a box's body and (optionally) lid in both colour modes."""
        out = []
        for mode in (MMU, SINGLE):
            written = self.write_piece(label, "body", mode, body, body_inserts, size)
            if written:
                out.append(written)
            if has_lid:
                written = self.write_piece(label, "lid", mode, lid, lid_inserts, size)
                if written:
                    out.append(written)
        return out

    def delete_stale(self, prefix: str, keep_labels: set[str]) -> list[str]:
        """Delete `{prefix}*` files whose label is no longer generated (T126)."""
        removed = []
        for mode in (MMU, SINGLE):
            mode_dir = self.root / mode
            if not mode_dir.exists():
                continue
            for f in mode_dir.glob(f"{prefix}*"):
                label = _label_from_filename(f.name, mode)
                if label not in keep_labels:
                    f.unlink(missing_ok=True)
                    removed.append(self.relative(f))
        return removed

    # -------------------------------------------------------------- internals

    @staticmethod
    def _compose(
        solid: "Bosl2Solid | None",
        inserts: "list[Bosl2Solid] | None",
        mode: str,
    ) -> "Bosl2Solid | list[Bosl2Solid] | None":
        """Combine a piece with its coloured inserts for the given mode."""
        if not inserts:
            return solid
        if mode == MMU:
            # Keep the inserts as distinct objects so each keeps its material.
            return ([solid] if solid is not None else []) + list(inserts)
        merged = solid
        for insert in inserts:
            merged = insert if merged is None else merged + insert
        return merged


def _label_from_filename(name: str, mode: str) -> str:
    """Recover a box label from an exported filename."""
    stem = name[:-4] if name.endswith(".3mf") else name
    for suffix in ("_body_single", "_lid_single", "_body", "_lid"):
        if stem.endswith(suffix):
            return stem[: -len(suffix)]
    return stem


def _measure(payload) -> tuple[float, float, float] | None:
    """Measure a solid's bounding box, or None if it cannot be measured.

    PythonSCAD computes `.size` by meshing, so this only works inside the app.
    """
    if payload is None:
        return None
    solids = payload if isinstance(payload, list) else [payload]

    boxes = []
    for solid in solids:
        box = _solid_bounds(solid)
        if box is not None:
            boxes.append(box)
    if not boxes:
        return None

    lo = [min(p[i] for p, _ in boxes) for i in range(3)]
    hi = [max(p[i] + s[i] for p, s in boxes) for i in range(3)]
    return (hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2])


def _solid_bounds(solid) -> tuple[tuple[float, ...], tuple[float, ...]] | None:
    """(origin, size) of one solid's AABB, or None if it exposes no usable one.

    `Bosl2Solid.bounds()` already answers in (position, size) form and is the
    reliable source; the raw `.position` / `.size` attributes are only meaningful
    on native objects — on a pybosl2 wrapper they are bound methods, not triples.
    """
    bounds = getattr(solid, "bounds", None)
    if callable(bounds):
        try:
            origin, size = bounds()
            return (tuple(float(v) for v in origin), tuple(float(v) for v in size))
        except Exception:
            return None

    position, size = getattr(solid, "position", None), getattr(solid, "size", None)
    try:
        return (tuple(float(v) for v in position), tuple(float(v) for v in size))
    except (TypeError, ValueError):
        return None


def _export_3mf(payload, path: Path) -> bool:
    """Write a 3MF, returning False when no geometry backend is available."""
    if payload is None:
        return False
    try:
        from openscad import export  # type: ignore[import-not-found]
    except ImportError:
        return False

    solids = payload if isinstance(payload, list) else [payload]
    if not solids:
        return False

    combined = solids[0]
    for solid in solids[1:]:
        combined = combined | solid
    try:
        # `export` only takes native PyOpenSCAD objects; `.shape` is how a
        # pybosl2 wrapper crosses that boundary.
        export(getattr(combined, "shape", combined), str(path))
    except Exception:
        return False
    return path.exists()
