# SPDX-License-Identifier: Apache-2.0
"""Compartment elements — individual game components nested inside a compartment.

A `CompartmentElement` is one physical piece (a worker meeple, a hero standee, a
hex tile, a wooden marker) with its own silhouette, its own local (x, y) offset
inside the owning compartment, its own rotation and its own depth. A compartment
that carries elements is an *element pack*: the elements are positioned in a local
frame and the pack's bounding box is what the box-level layout engine sees, so the
pack behaves exactly like one ordinary rectangular compartment (FR-004b).

Geometry generation delegates to pybosl2 and is only imported when a cutout is
actually built, so the layout maths stays importable without PythonSCAD.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Iterable, Sequence

from pyboxbuilder.enums import ElementShape

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


@dataclass(frozen=True)
class CompartmentElement:
    """A physical game component nested inside a compartment's bounding box."""

    shape_file: str | None = None
    """Path to the SVG outline representing the component (ElementShape.SVG only)."""
    offset: tuple[float, float] = (0.0, 0.0)
    """2D offset (x, y) in mm of the element's lower-left corner, relative to the
    compartment's bottom-left origin."""
    rotation: float = 0.0
    """Rotation of the component in degrees, about the centre of its footprint."""
    size: tuple[float, float] | None = None
    """Bounding dimensions (width, length) of the component in mm."""
    shape: ElementShape = ElementShape.SVG
    """Silhouette kind. Defaults to SVG, which requires `shape_file`."""
    depth: float | None = None
    """Cutout depth in mm. None inherits the owning compartment's depth."""
    z_offset: float = 0.0
    """Extra lift of the cutout floor above the compartment floor, in mm.
    Used for pieces that sit on top of other pieces (e.g. a tile over a token)."""
    corner_radius: float = 2.0
    """Corner radius for ElementShape.ROUNDED_RECT."""
    label: str | None = None
    """Optional identifier, handy for tests and layout diagnostics."""

    def __post_init__(self) -> None:
        if self.shape is ElementShape.SVG and not self.shape_file:
            raise ValueError(
                "CompartmentElement with shape=SVG requires shape_file="
            )
        if self.size is None:
            raise ValueError(
                f"CompartmentElement {self.label or self.shape_file!r} requires size=(w, l)"
            )
        if self.size[0] <= 0 or self.size[1] <= 0:
            raise ValueError(
                f"CompartmentElement {self.label or self.shape_file!r} size must be positive"
            )

    # ---------------------------------------------------------------- geometry

    @property
    def base_footprint(self) -> tuple[float, float]:
        """Axis-aligned (width, length) of the silhouette before rotation.

        For most shapes this is just `size`. A hexagon is the exception: `size[0]`
        is its flat-to-flat width, exactly as `RegularPolygon(width=...)` reads it
        in the original toolkit, so it measures `width / cos(30°)` point-to-point
        across the other axis.
        """
        assert self.size is not None
        w, l = self.size
        if self.shape is ElementShape.HEXAGON:
            return (w / math.cos(math.radians(30)), w)
        if self.shape in (ElementShape.CIRCLE, ElementShape.SPHERE_SCOOP):
            d = min(w, l)
            return (d, d)
        return (w, l)

    @property
    def footprint(self) -> tuple[float, float]:
        """Axis-aligned (width, length) after `rotation` is applied."""
        if self.shape in (ElementShape.CIRCLE, ElementShape.SPHERE_SCOOP):
            return self.base_footprint  # rotating a disc changes nothing
        if self.shape is ElementShape.HEXAGON:
            return _hexagon_footprint(self.base_footprint[0] / 2, self.rotation)

        w, l = self.base_footprint
        rad = math.radians(self.rotation)
        cos_r, sin_r = abs(math.cos(rad)), abs(math.sin(rad))
        return (w * cos_r + l * sin_r, w * sin_r + l * cos_r)

    def bounds(self) -> tuple[float, float, float, float]:
        """Axis-aligned bounds (min_x, min_y, max_x, max_y) in the pack frame."""
        fw, fl = self.footprint
        return (
            self.offset[0],
            self.offset[1],
            self.offset[0] + fw,
            self.offset[1] + fl,
        )

    def translated(self, dx: float, dy: float) -> "CompartmentElement":
        """Return a copy shifted by (dx, dy) in the pack frame."""
        return replace(self, offset=(self.offset[0] + dx, self.offset[1] + dy))


def _hexagon_footprint(circumradius: float, rotation: float) -> tuple[float, float]:
    """Exact axis-aligned extent of a regular hexagon rotated by `rotation`.

    A rect-bbox approximation overshoots badly here — at 30 degrees it claims
    36% more width than the hexagon actually occupies.
    """
    angles = [math.radians(rotation + 60 * k) for k in range(6)]
    xs = [circumradius * math.cos(a) for a in angles]
    ys = [circumradius * math.sin(a) for a in angles]
    return (max(xs) - min(xs), max(ys) - min(ys))


def elements_bounding_box(
    elements: Sequence[CompartmentElement],
) -> tuple[float, float, float, float]:
    """Return (min_x, min_y, max_x, max_y) covering every element in the pack."""
    if not elements:
        return (0.0, 0.0, 0.0, 0.0)
    boxes = [e.bounds() for e in elements]
    return (
        min(b[0] for b in boxes),
        min(b[1] for b in boxes),
        max(b[2] for b in boxes),
        max(b[3] for b in boxes),
    )


def elements_footprint(
    elements: Sequence[CompartmentElement], margin: float = 0.0
) -> tuple[float, float]:
    """Size of the rectangular compartment that holds this element pack (FR-004b).

    Offsets are measured from the compartment's own lower-left corner, so the
    footprint spans from that corner out to the furthest element — authored
    offsets are preserved rather than collapsed against the origin. Use
    `normalize_elements` first if you want the pack shrink-wrapped instead.

    Args:
        elements: The elements in the pack, positioned in the compartment frame.
        margin: Extra clearance added past the furthest element, in mm.

    Returns:
        (width, length) of the compartment needed to hold the pack, in mm.
    """
    if not elements:
        return (0.0, 0.0)
    _, _, max_x, max_y = elements_bounding_box(elements)
    return (round(max_x + margin, 1), round(max_y + margin, 1))


def normalize_elements(
    elements: Sequence[CompartmentElement], margin: float = 0.0
) -> tuple[CompartmentElement, ...]:
    """Shift a pack so its bounding box starts at (margin, margin).

    Keeps hand-written offsets readable — you can lay elements out in whatever
    coordinates suit the source drawing and let the pack normalise itself.
    """
    min_x, min_y, _, _ = elements_bounding_box(elements)
    dx, dy = margin - min_x, margin - min_y
    return tuple(e.translated(dx, dy) for e in elements)


def grid_pack(
    prototype: CompartmentElement,
    count: int,
    *,
    origin: tuple[float, float] = (0.0, 0.0),
    pitch: tuple[float, float] = (0.0, 0.0),
    alternate_rotation: float = 0.0,
) -> tuple[CompartmentElement, ...]:
    """Repeat one element `count` times along a straight line (FR-004b).

    This is the "five owl workers stacked in a column" case: the same silhouette
    at a fixed pitch, optionally flipping every other copy so the pieces nest.

    Args:
        prototype: The element to repeat; its `offset` is ignored.
        count: How many copies to place.
        origin: Position of the first copy.
        pitch: (dx, dy) step between successive copies.
        alternate_rotation: Extra rotation applied to every odd-indexed copy.

    Returns:
        The placed copies, in order.
    """
    out = []
    for i in range(count):
        rotation = prototype.rotation + (alternate_rotation if i % 2 else 0.0)
        out.append(
            replace(
                prototype,
                offset=(origin[0] + pitch[0] * i, origin[1] + pitch[1] * i),
                rotation=rotation,
                label=f"{prototype.label}_{i}" if prototype.label else None,
            )
        )
    return tuple(out)


def elements_overlap(
    elements: Sequence[CompartmentElement], tolerance: float = 0.0
) -> list[tuple[str, str]]:
    """Return the pairs of elements whose bounding boxes intersect.

    Bounding-box based, matching how the layout engine reasons about
    non-rectangular shapes (FR-004a). `tolerance` shrinks each box before the
    test, so silhouettes that only graze one another are not reported.
    """
    hits: list[tuple[str, str]] = []
    for i, a in enumerate(elements):
        ax0, ay0, ax1, ay1 = a.bounds()
        for b in elements[i + 1 :]:
            bx0, by0, bx1, by1 = b.bounds()
            if (
                ax0 + tolerance < bx1
                and bx0 + tolerance < ax1
                and ay0 + tolerance < by1
                and by0 + tolerance < ay1
            ):
                hits.append((_name(a), _name(b)))
    return hits


def _name(element: CompartmentElement) -> str:
    return element.label or element.shape_file or element.shape.value


# ------------------------------------------------------------------ geometry


def build_element(
    element: CompartmentElement, default_depth: float
) -> "Bosl2Solid":
    """Build the cutout solid for one element, in the compartment's local frame.

    pybosl2 primitives are centre-anchored, so each branch below builds its shape
    around the origin, rotation spins it in place, and one final translate puts
    the element's lower-left corner on its `offset` with its floor at
    `z_offset`. The result can be subtracted from a box body once the compartment
    has been moved into the interior frame.
    """
    from pybosl2 import Anchor, cuboid, cylinder, regular_prism, sphere

    assert element.size is not None
    w, l = element.size
    depth = element.depth if element.depth is not None else default_depth
    base_w, _ = element.base_footprint

    # A scoop is a ball resting ON the floor, not a well sunk into it, so it
    # lifts by its radius while every other shape lifts by half its depth.
    z_lift = base_w / 2 if element.shape is ElementShape.SPHERE_SCOOP else depth / 2

    if element.shape is ElementShape.SVG:
        assert element.shape_file is not None
        solid = svg_solid(element.shape_file, w, l, depth)
    elif element.shape is ElementShape.CIRCLE:
        solid = cylinder(height=depth, radius=base_w / 2)
    elif element.shape is ElementShape.HEXAGON:
        # `w` is the flat-to-flat width, as `RegularPolygon(width=...)` reads it.
        solid = regular_prism(
            6, height=depth, radius=w / 2 / math.cos(math.radians(30))
        )
    elif element.shape is ElementShape.SPHERE_SCOOP:
        solid = sphere(radius=base_w / 2)
    elif element.shape is ElementShape.ROUNDED_RECT:
        solid = cuboid([w, l, depth], rounding=element.corner_radius, edges=Anchor.Z)
    else:
        solid = cuboid([w, l, depth])

    if element.rotation:
        solid = solid.rotate([0.0, 0.0, element.rotation])

    footprint_w, footprint_l = element.footprint
    return solid.translate([
        element.offset[0] + footprint_w / 2,
        element.offset[1] + footprint_l / 2,
        element.z_offset + z_lift,
    ])


def svg_solid(shape_file: str, width: float, length: float, depth: float) -> "Bosl2Solid":
    """Extrude an SVG outline and scale it to fill `width` x `length` x `depth`.

    Returned centred on the origin, matching every pybosl2 primitive, so callers
    can place it the same way they place a cuboid.
    """
    solid = _svg_region(shape_file).linear_extrude(height=depth)
    (cx, cy, cz), (span_x, span_y, _) = solid.bounds()
    solid = solid.translate([-float(cx), -float(cy), -float(cz)])
    return solid.scale([
        width / max(float(span_x), 1e-9),
        length / max(float(span_y), 1e-9),
        1.0,
    ])


def _svg_region(shape_file: str):
    """Parse an SVG once and reuse it — a pack repeats the same file many times."""
    from pybosl2 import Region

    region = _SVG_CACHE.get(shape_file)
    if region is None:
        region = Region.from_svg(shape_file)
        _SVG_CACHE[shape_file] = region
    return region


_SVG_CACHE: dict = {}


def build_element_pack(
    elements: Iterable[CompartmentElement], default_depth: float
) -> "Bosl2Solid | None":
    """Union every element cutout in a pack. Returns None for an empty pack."""
    return union_all([build_element(e, default_depth) for e in elements])


def union_all(solids: list) -> "Bosl2Solid | None":
    """Union a list of solids with a balanced fold.

    A left fold builds a chain as deep as the list, which the mesher pays for on
    every cell of a big pack; halving keeps the tree logarithmic.
    """
    if not solids:
        return None
    while len(solids) > 1:
        solids = [
            a | b if b is not None else a
            for a, b in zip(solids[::2], list(solids[1::2]) + [None])
        ]
    return solids[0]
