# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

# LibFile: compartments.py
#    Declarative automatic layout of interior compartments.
#
#    You describe WHAT compartments you want (shape, size, depth, grouping) and how
#    pieces come out (scoop / wall finger / card finger-hole), and this lays them out
#    in the box interior for you. It plugs straight into the existing box pipeline:
#    layout_compartments(...) returns a ``contents`` callable, so
#
#        box = kit.box(size=[...], contents=layout_compartments([...]))
#
#    Each Compartment is self-contained: it emits its own well cavity AND its own
#    removal cutout as NEGATIVE InnerObjects in the compartment's local frame, so the
#    finger holes are attached to the compartments, not the box -- pack/move a
#    compartment and its finger hole travels with it.
#
# FileSummary: Automatic interior compartment layout.
# FileGroup: Basics

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from functools import reduce
from typing import Callable

import pybosl2.shapes3d
from base_bgtk import BACK, BOTTOM, FRONT, LEFT, RIGHT, InnerObject, InnerSize, ObjectType
from components import FingerHoleWall, EngravedLabel, EngravedShape, default_label_layer_depth

# A well at least this deep (mm) can be emptied with a floor scoop; shallower wells
# (and cards) need a finger channel/notch in the wall instead.
SCOOP_MIN_DEPTH = 8.0


class LayoutError(ValueError):
    """Raised when the requested compartments cannot fit the box interior -- they
    overflow the length/width, or one is deeper than the interior (would cut through
    the floor so the piece falls out the bottom)."""


# ---------------------------------------------------------------------------
# Type selectors (enums, not bare strings). All are str-enums, so a plain string
# literal ("rect", "center", ...) still works, but the enum members are canonical.
# ---------------------------------------------------------------------------


class Shape(str, Enum):
    """Compartment footprint shape."""

    RECT = "rect"
    CIRCLE = "circle"
    HEX = "hex"
    POLY = "poly"
    CUSTOM = "custom"     # use a supplied ``solid`` (e.g. a ported marker silhouette)


class Removal(str, Enum):
    """How pieces are removed from a compartment."""

    AUTO = "auto"         # scoop if deep enough, card_hole if is_card, else finger
    SCOOP = "scoop"       # rounded dip in the floor
    FINGER = "finger"     # notch in the front wall
    CARD_HOLE = "card_hole"  # finger channel down through the card stack, through the floor
    NONE = "none"


class Direction(str, Enum):
    """How the compartments inside a group are arranged."""

    ROW = "row"           # side by side along the width
    GRID = "grid"         # wrapped into ``cols`` columns


class Justify(str, Enum):
    """How leftover space is distributed when packing (all keep the minimum gap)."""

    SPACE_EVENLY = "space-evenly"    # slack shared across all gaps and edges
    SPACE_BETWEEN = "space-between"  # items to both edges, slack shared between them
    CENTER = "center"               # min gap between items, block centred
    START = "start"                 # min gap between items, packed at the start

# ---------------------------------------------------------------------------
# Declarative model
# ---------------------------------------------------------------------------


@dataclass
class Compartment:
    """One interior compartment (well) plus how pieces are removed from it.

    Shape + bounding size:
      * ``shape="rect"``   -> ``w`` x ``l``
      * ``shape="circle"`` -> ``d`` (diameter), packs in a ``d`` x ``d`` cell
      * ``shape="hex"`` / ``"poly"`` -> ``across`` (corner-to-corner), ``sides``
      * ``shape="custom"`` -> ``solid`` is the well cavity (a Bosl2Solid, or a
        ``callable(depth) -> Bosl2Solid``, built around its own origin and centred in
        a ``w`` x ``l`` bounding cell). Lets a real ported marker silhouette be a well.

    ``depth`` is the well depth (``None`` = the full interior height). ``count``
    repeats the compartment. ``fill=True`` makes it absorb the leftover width in its
    row. ``removal`` is how you get pieces out (see :data:`SCOOP_MIN_DEPTH`):

      * ``"auto"``      -> ``card_hole`` if ``is_card`` else ``scoop`` if the well is
                           deep enough (>= SCOOP_MIN_DEPTH) else ``finger``
      * ``"scoop"``     -> a rounded dip in the floor to slide a finger under pieces
      * ``"finger"``    -> a finger notch in the front wall
      * ``"card_hole"`` -> a finger channel down THROUGH the card stack (for cards)
      * ``"none"``      -> no removal cutout
    """

    shape: Shape = Shape.RECT
    w: float | None = None
    l: float | None = None
    d: float | None = None
    across: float | None = None
    sides: int = 6
    depth: float | None = None
    count: int = 1
    label: str | None = None           # engraved into this well's floor (also names it in errors)
    is_card: bool = False
    removal: Removal = Removal.AUTO
    scoop_depth: float | None = None   # how far the scoop dips below the well floor; None = auto
    fill: bool = False
    radius: float = 2.0
    solid: object = None               # for Shape.CUSTOM: the well solid or callable(depth)
    # --- label engraving (Irish-Gauge style): 0.2mm second-colour text/image on the floor ---
    label_colour: str | None = None    # MMU fill colour for the label (None -> positive_colour)
    label_size: float | None = None    # font size; None -> auto-fit to the well
    label_depth: float = default_label_layer_depth   # cut depth (default 0.2mm = one layer)
    label_font: str | None = None      # None -> default_label_font
    label_spin: float = 0              # rotate the text/image in the floor plane (deg)
    label_shape: object = None         # a SHAPE image engraved on the floor instead of/with text
                                       # (a 2-D shape e.g. shapes.coin2d(14), a callable(depth), or a solid)

    def cell(self) -> tuple[float, float]:
        """The (width, length) bounding cell this compartment occupies for packing."""
        if self.shape == Shape.CIRCLE:
            assert self.d, f"circle compartment needs d=, got {self.d}"
            return self.d, self.d
        if self.shape in (Shape.HEX, Shape.POLY):
            assert self.across, f"{self.shape.value} compartment needs across=, got {self.across}"
            return self.across, self.across
        # rect and custom both pack by their w x l bounding cell.
        assert self.w and self.l, f"{Shape(self.shape).value} compartment needs w= and l=, got {self.w}x{self.l}"
        return self.w, self.l

    def resolved_removal(self, depth: float) -> Removal:
        if self.removal != Removal.AUTO:
            return Removal(self.removal)
        if self.is_card:
            return Removal.CARD_HOLE
        return Removal.SCOOP if depth >= SCOOP_MIN_DEPTH else Removal.FINGER


@dataclass
class Group:
    """A row (or grid) of compartments laid out together. Groups stack along the box
    length; ``fill=True`` makes the group's band absorb the leftover length."""

    items: list[Compartment]
    direction: Direction = Direction.ROW
    cols: int | None = None     # for Direction.GRID
    label: str | None = None
    fill: bool = False


# ---------------------------------------------------------------------------
# Geometry: one compartment -> its well + removal cutout (local frame)
# ---------------------------------------------------------------------------


def _well_solid(c: Compartment, cw: float, cl: float, depth: float) -> object:
    """The well cavity solid, cell-corner-anchored at (0,0,0), spanning up to z=depth."""
    if c.shape == Shape.CUSTOM:
        assert c.solid is not None, "custom compartment needs solid= (a Bosl2Solid or callable(depth))"
        shape = c.solid(depth) if callable(c.solid) else c.solid
        # The ported silhouette is built around its own origin -> centre it in the cell.
        return shape.translate([cw / 2, cl / 2, 0])
    if c.shape == Shape.CIRCLE:
        return pybosl2.shapes3d.cyl(diameter=c.d, height=depth, anchor=BOTTOM).translate([c.d / 2, c.d / 2, 0])
    if c.shape in (Shape.HEX, Shape.POLY):
        return pybosl2.shapes3d.cyl(
            diameter=c.across, height=depth, anchor=BOTTOM, fn=c.sides
        ).translate([c.across / 2, c.across / 2, 0])
    # rect: rounded vertical edges
    return pybosl2.shapes3d.cuboid(
        [cw, cl, depth],
        anchor=BOTTOM + FRONT + LEFT,
        rounding=c.radius,
        edges=[FRONT + LEFT, FRONT + RIGHT, BACK + LEFT, BACK + RIGHT],
    )


def _scoop_solid(c: Compartment, cw: float, cl: float, z0: float) -> object:
    """A rounded floor dip at the front-centre of the well. ``scoop_depth`` sets how
    far it dips below the well floor (vertical scale of the ball)."""
    r = max(3.5, min(min(cw, cl) * 0.4, 8.0))
    sd = c.scoop_depth if c.scoop_depth is not None else r
    k = max(0.35, sd / r)
    return pybosl2.shapes3d.sphere(radius=r).scale([1.0, 1.0, k]).translate([cw / 2, 0, z0])


def _card_hole_solid(cw: float, cl: float, top: float) -> object:
    """FingerHoleWall scallop in the card compartment's front wall, tall enough to run
    from the top of the cards DOWN THROUGH THE FLOOR (extends below z=0 -- emitted
    unclipped) so a finger pushes the stack up and out."""
    r = min(8.0, cw * 0.32)
    h = top + 30.0
    return FingerHoleWall(radius=r, height=h, depth_of_hole=min(cl, 14.0), orient=BACK).translate(
        [cw / 2, 0, top - h / 2]
    )


def _finger_solid(cw: float, depth: float, top: float) -> object:
    """A finger notch in the front wall reaching part-way down a shallow well."""
    r = min(7.0, cw * 0.3)
    h = min(depth, 12.0) + 1
    return pybosl2.shapes3d.cyl(radius=r, height=h, anchor=BOTTOM).translate([cw / 2, 0, top - h + 1])


def _label_engraving(c: Compartment, x: float, y: float, cw: float, cl: float, z0: float) -> InnerObject:
    """A 0.2mm second-colour label engraved into the centre of this well's floor (``z0``).

    Auto-sizes to the well when ``label_size`` is unset. ``clip`` is only enabled when the
    engraving stays inside the interior (``z0 >= label_depth``); a full-depth well cuts into
    the box floor itself, which must be an unclipped (breaching) cut -- 0.2mm never
    perforates the floor. See :func:`~components.EngravedLabel`."""
    size = c.label_size if c.label_size is not None else max(4.0, min(cw, cl) * 0.5)
    return EngravedLabel(
        c.label,
        [x + cw / 2, y + cl / 2, z0],
        depth=c.label_depth,
        size=size,
        font=c.label_font,
        spin=c.label_spin,
        colour=c.label_colour,
        clip=z0 >= c.label_depth,
    )


def _place_one(
    c: Compartment, x: float, y: float, cw: float, cl: float, IH: float
) -> tuple[list[InnerObject], object | None, InnerObject | None]:
    """Place one compartment -> (well InnerObjects, scoop solid to be merged, other
    removal InnerObject). The scoop is returned raw so a row of them can be merged
    into one contiguous cut; card_hole/finger are self-contained."""
    depth = IH if c.depth is None else min(c.depth, IH)
    z0 = IH - depth                 # well floor: wells open at the interior top
    top = IH
    wells = [InnerObject(_well_solid(c, cw, cl, depth).translate([x, y, z0]), ObjectType.NEGATIVE)]

    # Engrave the compartment's label/image into its floor (Irish-Gauge style): a 0.2mm
    # second-colour impression, centred, revealed when the pieces are lifted out.
    if c.label:
        wells.append(_label_engraving(c, x, y, cw, cl, z0))
    if c.label_shape is not None:
        wells.append(
            EngravedShape(
                c.label_shape,
                [x + cw / 2, y + cl / 2, z0],
                depth=c.label_depth,
                spin=c.label_spin,
                colour=c.label_colour,
                clip=z0 >= c.label_depth,
            )
        )

    kind = c.resolved_removal(depth)
    scoop = None
    other = None
    if kind == Removal.SCOOP:
        scoop = _scoop_solid(c, cw, cl, z0).translate([x, y, 0])
    elif kind == Removal.CARD_HOLE:
        other = InnerObject(_card_hole_solid(cw, cl, top).translate([x, y, 0]), ObjectType.NEGATIVE, clip=False)
    elif kind == Removal.FINGER:
        other = InnerObject(_finger_solid(cw, depth, top).translate([x, y, 0]), ObjectType.NEGATIVE)
    return wells, scoop, other


def _point_in_poly(px: float, py: float, poly) -> bool:
    """Ray-casting point-in-polygon test. *poly* is a list of ``[x, y]`` points."""
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = float(poly[i][0]), float(poly[i][1])
        xj, yj = float(poly[j][0]), float(poly[j][1])
        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def _cell_in_region(x: float, y: float, cw: float, cl: float, region) -> bool:
    """Whether a ``cw`` x ``cl`` cell at (x, y) sits fully inside *region* (a polygon in
    the layout's local frame). ``region=None`` -> always True (rectangular interior).
    Samples the corners, edge mid-points and centre -- enough to reject a cell that
    pokes out past a polygon edge without a full polygon-clip test."""
    if region is None:
        return True
    samples = (
        (x, y), (x + cw, y), (x, y + cl), (x + cw, y + cl),
        (x + cw / 2, y), (x + cw / 2, y + cl), (x, y + cl / 2), (x + cw, y + cl / 2),
        (x + cw / 2, y + cl / 2),
    )
    return all(_point_in_poly(px, py, region) for px, py in samples)


def _merge_scoops(scoops: list) -> list[InnerObject]:
    """Merge a line of adjacent scoop solids into ONE contiguous cut (convex hull), so
    scoops sitting next to each other don't leave ridges between them."""
    if not scoops:
        return []
    merged = scoops[0] if len(scoops) == 1 else reduce(lambda a, b: a.hull(b), scoops)
    return [InnerObject(merged, ObjectType.NEGATIVE)]


# ---------------------------------------------------------------------------
# Layout: groups -> a ``contents`` callable
# ---------------------------------------------------------------------------


def _expand(items: list[Compartment]) -> list[Compartment]:
    out: list[Compartment] = []
    for it in items:
        out.extend(it for _ in range(max(1, it.count)))
    return out


def _tight(sizes: list[float], min_gap: float) -> float:
    """Minimum span needed to lay *sizes* out with just ``min_gap`` between them."""
    n = len(sizes)
    return (sum(sizes) + min_gap * (n - 1)) if n else 0.0


def _positions(available: float, sizes: list[float], min_gap: float, justify: Justify) -> list[float]:
    """Start coordinates for laying *sizes* out in *available* span, packed as tightly
    as ``min_gap`` allows (efficient -- no wasted edge gaps) and distributing any slack
    per ``justify`` (a :class:`Justify`). The caller guarantees the items fit."""
    n = len(sizes)
    if n == 0:
        return []
    slack = max(0.0, available - _tight(sizes, min_gap))
    if justify == Justify.START:
        lead, gap = 0.0, min_gap
    elif justify == Justify.SPACE_BETWEEN and n > 1:
        lead, gap = 0.0, min_gap + slack / (n - 1)
    elif justify == Justify.SPACE_EVENLY:
        extra = slack / (n + 1)
        lead, gap = extra, min_gap + extra
    else:  # center (and space-between with a single item)
        lead, gap = slack / 2.0, min_gap
    pos, x = [], lead
    for s in sizes:
        pos.append(x)
        x += s + gap
    return pos


def layout_compartments(
    groups: list[Group],
    *,
    min_gap: float = 2.0,
    margin: float | None = None,
    justify: Justify = Justify.SPACE_EVENLY,
    region: list | None = None,
) -> Callable[[InnerSize], list[InnerObject]]:
    """Return a ``contents`` callable that lays *groups* out in the box interior.

    Groups stack along the interior length (Y); within a ``row`` group compartments
    sit side by side along the width (X); a ``grid`` group wraps into ``cols`` columns.
    Compartments are DISTRIBUTED across the available space -- gaps are at least
    ``min_gap`` and grow to fill slack (see ``justify``), rather than being crammed at
    one end. ``fill`` compartments/groups still expand to absorb leftover space first.

    **Polygon outlines:** packing happens in the interior's bounding rectangle, but if a
    boundary polygon is known -- passed explicitly as ``region`` or carried on
    ``InnerSize.region`` (a path box supplies its inset outline automatically) -- any
    compartment whose cell would poke outside the polygon is DROPPED, so a box with a
    non-rectangular outline still bin-packs cleanly. The explicit ``region`` argument
    wins over ``InnerSize.region``.

    Args:
        min_gap:  the minimum gap between compartments and at the edges (mm).
        margin:   edge margin; defaults to ``min_gap`` when not given.
        justify:  how slack is distributed -- see :func:`_positions`.
        region:   optional boundary polygon (``[[x, y], ...]`` in the interior-local
                  frame) that compartments must stay inside; ``None`` = full rectangle.

    Usage::

        contents = layout_compartments([
            Group([Compartment(shape="circle", d=22, depth=12, count=4)]),
            Group([Compartment(shape="hex", across=26, depth=10, count=6)], direction="grid", cols=3),
            Group([Compartment(fill=True, depth=6, is_card=True)], fill=True),
        ], min_gap=3)
        box = kit.box(size=[100, 90, 25], label="Player", contents=contents)
    """
    edge = min_gap if margin is None else margin

    def build(inner: InnerSize) -> list[InnerObject]:
        AW = inner.width - 2 * edge
        AL = inner.length - 2 * edge
        IH = inner.height
        region_use = region if region is not None else getattr(inner, "region", None)

        # A compartment can't be deeper than the interior, or its well would cut
        # through the floor and the piece would fall out the bottom.
        for gi, g in enumerate(groups):
            for it in g.items:
                if it.depth is not None and it.depth > IH + 1e-6:
                    raise LayoutError(
                        f"compartment {_name(g, it, gi)} depth {it.depth:g}mm is deeper than the "
                        f"interior height {IH:g}mm -- it would cut through the floor"
                    )

        # Band length (Y-extent) of each group; fill groups expand into the leftover
        # length after reserving the minimum gaps.
        fixed = [None if g.fill else _group_band_length(g, min_gap) for g in groups]
        n_fill = sum(1 for b in fixed if b is None)
        fixed_len = sum(b for b in fixed if b is not None)
        gaps_len = min_gap * (len(groups) - 1)
        fill_band = max(0.0, AL - fixed_len - gaps_len) / n_fill if n_fill else 0.0
        bands = [fill_band if b is None else b for b in fixed]

        need_l = _tight(bands, min_gap)
        if need_l > AL + 1e-6:
            raise LayoutError(
                f"compartments overflow the box LENGTH: need {need_l + 2 * edge:.1f}mm of interior "
                f"but only {inner.length:.1f}mm is available (over by {need_l - AL:.1f}mm)"
            )

        ypos = _positions(AL, bands, min_gap, justify)
        pieces: list[InnerObject] = []
        for g, band, y in zip(groups, bands, ypos):
            pieces.extend(_place_group(g, y=edge + y, band=band, AW=AW, x_off=edge, IH=IH,
                                       min_gap=min_gap, justify=justify, interior_width=inner.width,
                                       region=region_use))
        return pieces

    return build


def _name(g: Group, it: Compartment, gi: int) -> str:
    """A human label for a compartment in error messages."""
    return it.label or g.label or f"{Shape(it.shape).value} in group {gi}"


def _group_band_length(g: Group, min_gap: float) -> float:
    """Y-extent of a group's band from its (non-fill) compartments' cells."""
    items = _expand(g.items)
    cells = [it.cell() for it in items]
    if g.direction == Direction.GRID:
        cols = g.cols or max(1, len(items))
        rows = (len(items) + cols - 1) // cols
        row_h = max((cl for (_cw, cl) in cells), default=0.0)
        return rows * row_h + (rows - 1) * min_gap
    # row: band = deepest cell in Y
    return max((cl for (_cw, cl) in cells), default=0.0)


def _row_widths(items: list[Compartment], available: float, min_gap: float) -> list[float]:
    """Cell widths for a row: fixed items keep their bbox width; fill items split the
    leftover width after reserving the minimum gaps between items."""
    fixed_w = sum(it.cell()[0] for it in items if not it.fill)
    n_fill = sum(1 for it in items if it.fill)
    gaps = min_gap * (len(items) - 1)
    fill_w = max(0.0, available - fixed_w - gaps) / n_fill if n_fill else 0.0
    return [fill_w if it.fill else it.cell()[0] for it in items]


def _check_row_fits(g: Group, row_items: list[Compartment], widths: list[float], AW: float,
                    min_gap: float, interior_width: float, edge: float) -> None:
    need = _tight(widths, min_gap)
    if need > AW + 1e-6:
        raise LayoutError(
            f"compartments overflow the box WIDTH: a row (group {g.label or ''}) needs "
            f"{need + 2 * edge:.1f}mm but only {interior_width:.1f}mm is available "
            f"(over by {need - AW:.1f}mm)"
        )


def _place_group(g: Group, *, y: float, band: float, AW: float, x_off: float, IH: float,
                 min_gap: float, justify: Justify, interior_width: float,
                 region: list | None = None) -> list[InnerObject]:
    items = _expand(g.items)
    pieces: list[InnerObject] = []

    if g.direction == Direction.GRID:
        cols = g.cols or max(1, len(items))
        cy = y
        for i in range(0, len(items), cols):
            row = items[i : i + cols]
            row_h = max(it.cell()[1] for it in row)
            widths = _row_widths(row, AW, min_gap)
            _check_row_fits(g, row, widths, AW, min_gap, interior_width, x_off)
            xpos = _positions(AW, widths, min_gap, justify)
            row_scoops: list = []
            for it, cw, x in zip(row, widths, xpos):
                if not _cell_in_region(x_off + x, cy, cw, row_h, region):
                    continue   # cell falls outside the polygon outline -- skip it
                wells, scoop, other = _place_one(it, x_off + x, cy, cw, row_h, IH)
                pieces.extend(wells)
                if other is not None:
                    pieces.append(other)
                if scoop is not None:
                    row_scoops.append(scoop)
            pieces.extend(_merge_scoops(row_scoops))   # contiguous scoop per row
            cy += row_h + min_gap
        return pieces

    # row: distribute items along X.
    widths = _row_widths(items, AW, min_gap)
    _check_row_fits(g, items, widths, AW, min_gap, interior_width, x_off)
    xpos = _positions(AW, widths, min_gap, justify)
    scoops: list = []
    for it, cw, x in zip(items, widths, xpos):
        cl = band if it.fill else it.cell()[1]
        if not _cell_in_region(x_off + x, y, cw, cl, region):
            continue   # cell falls outside the polygon outline -- skip it
        wells, scoop, other = _place_one(it, x_off + x, y, cw, cl, IH)
        pieces.extend(wells)
        if other is not None:
            pieces.append(other)
        if scoop is not None:
            scoops.append(scoop)
    pieces.extend(_merge_scoops(scoops))   # one contiguous scoop along the row
    return pieces
