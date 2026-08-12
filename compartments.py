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
from pybosl2 import Color
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


class PackingBin(str, Enum):
    """How compartments are distributed across ROWS when a group wraps.

    A row is the bin: it is one band of interior width, and a compartment either fits in
    what is left of it or it does not. The names and behaviours follow ``rectpack``'s
    ``PackingBin`` so the choice means the same thing here as it does there.

    Leaving this unset keeps the historical behaviour -- a ``row`` group is exactly one row
    and overflowing it is a :class:`LayoutError`. That is deliberate: wrapping by default
    would re-arrange compartments in boxes people have already printed.
    """

    BNF = "bnf"        #: Bin Next Fit: if it does not fit the current row, close that row and start another.
    BFF = "bff"        #: Bin First Fit: put it in the first row it fits; earlier rows stay open.
    BBF = "bbf"        #: Bin Best Fit: put it in the row it leaves the least room in.
    GLOBAL = "global"  #: fill each row with the best-fitting compartment left, then move on.


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
    row. ``rotate=True`` lets the packer turn the compartment a quarter turn when that
    is what makes a row fit -- off by default, because turning one silently would move
    every compartment in an existing box. ``removal`` is how you get pieces out (see :data:`SCOOP_MIN_DEPTH`):

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
    rotate: bool = False               # the packer MAY turn this 90 degrees to make it fit
    radius: float = 2.0
    solid: object = None               # for Shape.CUSTOM: the well solid or callable(depth)
    # --- label engraving (Irish-Gauge style): 0.2mm second-colour text/image on the floor ---
    label_colour: Color | None = None    # MMU fill colour for the label (None -> positive_colour)
    label_size: float | None = None    # font size; None -> auto-fit to the well
    label_depth: float = default_label_layer_depth   # cut depth (default 0.2mm = one layer)
    label_font: str | None = None      # None -> default_label_font
    label_spin: float = 0              # rotate the text/image in the floor plane (deg)
    label_shape: object = None         # a SHAPE image engraved on the floor instead of/with text
                                       # (a 2-D shape e.g. shapes.coin2d(14), a callable(depth), or a solid)

    def cell(self, rotated: bool = False) -> tuple[float, float]:
        """The (width, length) bounding cell this compartment occupies for packing.

        *rotated* turns it a quarter turn, swapping the two. Only ``rect`` and ``custom``
        have a cell that is not square, so only they can change shape by turning."""
        if self.shape == Shape.CIRCLE:
            assert self.d, f"circle compartment needs d=, got {self.d}"
            return self.d, self.d
        if self.shape in (Shape.HEX, Shape.POLY):
            assert self.across, f"{self.shape.value} compartment needs across=, got {self.across}"
            return self.across, self.across
        # rect and custom both pack by their w x l bounding cell.
        assert self.w and self.l, f"{Shape(self.shape).value} compartment needs w= and l=, got {self.w}x{self.l}"
        return (self.l, self.w) if rotated else (self.w, self.l)

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
    packing: "PackingBin | None" = None   # wrap into rows with this strategy; None = one row


# ---------------------------------------------------------------------------
# Geometry: one compartment -> its well + removal cutout (local frame)
# ---------------------------------------------------------------------------


def _well_solid(c: Compartment, cw: float, cl: float, depth: float, rotated: bool = False) -> object:
    """The well cavity solid, cell-corner-anchored at (0,0,0), spanning up to z=depth.

    *rotated* means the packer turned this compartment a quarter turn. The cell dimensions
    arrive already swapped, which is all a rect/circle/hex needs -- they are built TO the
    cell. A custom silhouette is not, so it has to be turned itself."""
    if c.shape == Shape.CUSTOM:
        assert c.solid is not None, "custom compartment needs solid= (a Bosl2Solid or callable(depth))"
        shape = c.solid(depth) if callable(c.solid) else c.solid
        if rotated:
            shape = shape.rotate([0, 0, 90])
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
    c: Compartment, x: float, y: float, cw: float, cl: float, IH: float, rotated: bool = False
) -> tuple[list[InnerObject], object | None, InnerObject | None]:
    """Place one compartment -> (well InnerObjects, scoop solid to be merged, other
    removal InnerObject). The scoop is returned raw so a row of them can be merged
    into one contiguous cut; card_hole/finger are self-contained."""
    depth = IH if c.depth is None else min(c.depth, IH)
    z0 = IH - depth                 # well floor: wells open at the interior top
    top = IH
    wells = [InnerObject(_well_solid(c, cw, cl, depth, rotated).translate([x, y, z0]), ObjectType.NEGATIVE)]

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


# ---------------------------------------------------------------------------
# The packing result, and its cache
# ---------------------------------------------------------------------------

#: Bumped whenever the PACKING changes -- new orientation rules, different gap handling,
#: anything that could put a compartment somewhere else for the same input. It is part of
#: every cache key, so a bump invalidates every cached plan rather than silently serving a
#: layout the current code would not produce.
BIN_PACKING_VERSION = 3


@dataclass(frozen=True)
class Placement:
    """Where the packer put one compartment. Pure data -- no geometry."""

    group: int          #: index into the groups list
    item: int           #: index into that group's EXPANDED items
    row: int            #: which row of the group (scoops merge per row)
    x: float
    y: float
    width: float
    length: float
    rotated: bool


def _compartment_signature(c: Compartment) -> tuple:
    """The parts of a compartment that decide where it lands.

    Deliberately NOT the whole object: `solid`, `label_shape` and the colours are geometry,
    they cannot be hashed, and they cannot move a cell. Two compartments with different
    artwork pack identically and should share a cached plan.
    """
    return (
        str(c.shape), c.w, c.l, c.d, c.across, c.sides,
        max(1, c.count), bool(c.fill), bool(c.rotate),
    )


def _layout_key(
    groups: list[Group], inner: "InnerSize", edge: float, min_gap: float,
    justify: Justify, region: list | None,
) -> tuple:
    """The cache key for one packing run: every input that can change the answer.

    The version goes in the key rather than being checked alongside it, so a stale plan is
    unreachable instead of merely detectable.
    """
    return (
        BIN_PACKING_VERSION,
        round(float(inner.width), 6), round(float(inner.length), 6), round(float(inner.height), 6),
        round(float(edge), 6), round(float(min_gap), 6), str(justify),
        tuple(
            (str(g.direction), g.cols, bool(g.fill), str(g.packing),
             tuple(_compartment_signature(c) for c in g.items))
            for g in groups
        ),
        None if region is None else tuple((round(float(x), 6), round(float(y), 6)) for x, y in region),
    )


#: Packing plans already worked out, by :func:`_layout_key`. The PLAN is cached, never the
#: geometry: a solid handle reused across two CSG branches crashes the renderer (see
#: CLAUDE.md), so every build makes its own solids from the same, cheap, plan.
_PLAN_CACHE: "dict[tuple, tuple[Placement, ...]]" = {}


def layout_cache_clear() -> None:
    """Empty the packing cache. For tests, and for anyone editing the packer."""
    _PLAN_CACHE.clear()


def layout_cache_info() -> dict:
    """How many plans are cached, and under which version."""
    return {"entries": len(_PLAN_CACHE), "version": BIN_PACKING_VERSION}


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

    **Wrapping:** a ``row`` group is one row and overflowing it is an error. Give the group
    a :class:`PackingBin` strategy (``Group(items, packing=PackingBin.BBF)``) and it wraps
    into as many rows as it needs instead, each row being a bin of interior width. Pair it
    with ``Compartment(rotate=True)`` to let the packer turn compartments to fit more in.

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

    def pack(inner: InnerSize) -> "tuple[Placement, ...]":
        """Work out where every compartment goes. Pure arithmetic, cached by the caller."""
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
        fixed = [None if g.fill else _group_band_length(g, min_gap, AW) for g in groups]
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
        plan: list[Placement] = []
        for gi, (g, band, y) in enumerate(zip(groups, bands, ypos)):
            plan.extend(_plan_group(g, gi, y=edge + y, band=band, AW=AW, x_off=edge,
                                    min_gap=min_gap, justify=justify, interior_width=inner.width,
                                    region=region_use))
        return tuple(plan)

    def build(inner: InnerSize) -> list[InnerObject]:
        region_use = region if region is not None else getattr(inner, "region", None)
        key = _layout_key(groups, inner, edge, min_gap, justify, region_use)
        plan = _PLAN_CACHE.get(key)
        if plan is None:
            plan = _PLAN_CACHE[key] = pack(inner)
        # The PLAN is cached; the geometry never is. Building the solids again each time is
        # what keeps two boxes (or a box and its lid) from sharing a handle.
        return _realise(groups, plan, inner.height)

    return build


def _name(g: Group, it: Compartment, gi: int) -> str:
    """A human label for a compartment in error messages."""
    return it.label or g.label or f"{Shape(it.shape).value} in group {gi}"


def _group_band_length(g: Group, min_gap: float, available_width: float | None = None) -> float:
    """Y-extent of a group's band from its (non-fill) compartments' cells.

    *available_width* is needed whenever anything in the group may be turned: turning swaps
    a cell's width for its LENGTH, so it changes the band's depth as much as the row's
    width, and the band has to be measured on the orientation the row will actually use.
    """
    items = _expand(g.items)
    if g.direction == Direction.GRID:
        cols = g.cols or max(1, len(items))
        rows = (len(items) + cols - 1) // cols
        row_h = 0.0
        for i in range(0, len(items), cols):
            row = items[i : i + cols]
            turns = _row_turns(row, available_width, min_gap) if available_width else [False] * len(row)
            row_h = max(row_h, max((it.cell(t)[1] for it, t in zip(row, turns)), default=0.0))
        return rows * row_h + (rows - 1) * min_gap
    if g.packing is not None and available_width:
        # Wrapped: the band has to cover every row the strategy produces, not just one.
        total, rows = 0.0, _assign_rows(items, available_width, min_gap, g.packing)
        for assigned in rows:
            total += max((items[i].cell(t)[1] for i, t in assigned), default=0.0)
        return total + min_gap * max(0, len(rows) - 1)
    # row: band = deepest cell in Y
    turns = _row_turns(items, available_width, min_gap) if available_width else [False] * len(items)
    return max((it.cell(t)[1] for it, t in zip(items, turns)), default=0.0)


def _fit_width(item: Compartment, used: float, available: float, min_gap: float) -> "tuple[float, bool] | None":
    """The width *item* would take in a row already holding *used*, and whether it is turned.

    ``None`` when it will not fit either way round. A turnable item is offered both ways and
    the NARROWER one that fits wins, because the width is what the row is short of.
    """
    gap = min_gap if used > 0 else 0.0
    options = [(item.cell()[0], False)]
    if item.rotate:
        options.append((item.cell(True)[0], True))
    options.sort()
    for width, turned in options:
        if used + gap + width <= available + 1e-6:
            return width + gap, turned
    return None


def _assign_rows(
    items: list[Compartment], available: float, min_gap: float, strategy: "PackingBin",
) -> list[list[tuple[int, bool]]]:
    """Distribute *items* across rows of *available* width, by *strategy*.

    Each row is a bin. Returns a list of rows, each a list of ``(item index, turned)`` in
    the order they sit along X. Items keep their given order except under
    :attr:`PackingBin.GLOBAL`, which is explicitly about choosing what goes next.

    An item too wide for an EMPTY row can never be placed; that is a real overflow and is
    left to the caller's fit check to report, so the message stays the one users know.
    """
    rows: list[list[tuple[int, bool]]] = []
    used: list[float] = []

    def open_row() -> int:
        rows.append([])
        used.append(0.0)
        return len(rows) - 1

    if strategy == PackingBin.GLOBAL:
        remaining = list(range(len(items)))
        while remaining:
            r = open_row()
            placed_any = True
            while placed_any and remaining:
                placed_any = False
                best = None   # (leftover, index-in-remaining, width, turned)
                for slot, i in enumerate(remaining):
                    fit = _fit_width(items[i], used[r], available, min_gap)
                    if fit is None:
                        continue
                    width, turned = fit
                    leftover = available - (used[r] + width)
                    if best is None or leftover < best[0]:
                        best = (leftover, slot, width, turned)
                if best is not None:
                    _leftover, slot, width, turned = best
                    rows[r].append((remaining.pop(slot), turned))
                    used[r] += width
                    placed_any = True
            if not rows[r]:
                # Nothing left fits an empty row: emit the rest so the fit check reports it.
                rows[r].extend((i, False) for i in remaining)
                break
        return rows

    for i, item in enumerate(items):
        if strategy == PackingBin.BNF:
            candidates = [len(rows) - 1] if rows else []
        elif strategy == PackingBin.BFF:
            candidates = list(range(len(rows)))
        else:  # BBF -- every open row, best fitness wins
            candidates = list(range(len(rows)))

        chosen = None
        best_leftover = None
        for r in candidates:
            fit = _fit_width(item, used[r], available, min_gap)
            if fit is None:
                continue
            width, turned = fit
            if strategy in (PackingBin.BNF, PackingBin.BFF):
                chosen = (r, width, turned)
                break
            leftover = available - (used[r] + width)
            if best_leftover is None or leftover < best_leftover:
                best_leftover, chosen = leftover, (r, width, turned)

        if chosen is None:
            r = open_row()
            fit = _fit_width(item, 0.0, available, min_gap)
            # Too wide even for an empty row: place it anyway and let the fit check speak.
            width, turned = fit if fit is not None else (item.cell()[0], False)
            chosen = (r, width, turned)

        r, width, turned = chosen
        rows[r].append((i, turned))
        used[r] += width
    return rows


def _row_turns(items: list[Compartment], available: float, min_gap: float) -> list[bool]:
    """Which items in a row to turn a quarter turn.

    Rows are laid out along X, so a row fits when the cell WIDTHS plus their gaps fit in
    *available*. Turning a rotatable item swaps its width for its length, so it is worth
    doing exactly when it makes the row narrower -- and only until the row fits, because
    turning more than that is churn that changes a layout for no reason.

    Greedy, largest saving first: a row is a handful of compartments, and taking the
    biggest saving each time reaches a fitting row in as few turns as possible.
    """
    turns = [False] * len(items)
    savings = [
        (it.cell()[0] - it.cell(True)[0], i)
        for i, it in enumerate(items)
        if it.rotate and not it.fill and it.cell(True)[0] < it.cell()[0]
    ]
    if not savings:
        return turns
    need = _tight([it.cell()[0] for it in items], min_gap)
    for saving, i in sorted(savings, reverse=True):
        if need <= available + 1e-6:
            break
        turns[i] = True
        need -= saving
    return turns


def _row_widths(items: list[Compartment], available: float, min_gap: float,
                turns: list[bool] | None = None) -> list[float]:
    """Cell widths for a row: fixed items keep their bbox width; fill items split the
    leftover width after reserving the minimum gaps between items."""
    if turns is None:
        turns = [False] * len(items)
    fixed_w = sum(it.cell(t)[0] for it, t in zip(items, turns) if not it.fill)
    n_fill = sum(1 for it in items if it.fill)
    gaps = min_gap * (len(items) - 1)
    fill_w = max(0.0, available - fixed_w - gaps) / n_fill if n_fill else 0.0
    return [fill_w if it.fill else it.cell(t)[0] for it, t in zip(items, turns)]


def _check_row_fits(g: Group, row_items: list[Compartment], widths: list[float], AW: float,
                    min_gap: float, interior_width: float, edge: float) -> None:
    need = _tight(widths, min_gap)
    if need > AW + 1e-6:
        raise LayoutError(
            f"compartments overflow the box WIDTH: a row (group {g.label or ''}) needs "
            f"{need + 2 * edge:.1f}mm but only {interior_width:.1f}mm is available "
            f"(over by {need - AW:.1f}mm)"
        )


def _plan_group(g: Group, gi: int, *, y: float, band: float, AW: float, x_off: float,
                min_gap: float, justify: Justify, interior_width: float,
                region: list | None = None) -> list[Placement]:
    """Where every compartment of one group goes. Pure arithmetic -- no geometry."""
    items = _expand(g.items)
    out: list[Placement] = []

    if g.direction == Direction.GRID:
        cols = g.cols or max(1, len(items))
        cy = y
        for row_index, i in enumerate(range(0, len(items), cols)):
            row = items[i : i + cols]
            turns = _row_turns(row, AW, min_gap)
            row_h = max(it.cell(t)[1] for it, t in zip(row, turns))
            widths = _row_widths(row, AW, min_gap, turns)
            _check_row_fits(g, row, widths, AW, min_gap, interior_width, x_off)
            xpos = _positions(AW, widths, min_gap, justify)
            for j, (cw, x, turned) in enumerate(zip(widths, xpos, turns)):
                if not _cell_in_region(x_off + x, cy, cw, row_h, region):
                    continue   # cell falls outside the polygon outline -- skip it
                out.append(Placement(gi, i + j, row_index, x_off + x, cy, cw, row_h, turned))
            cy += row_h + min_gap
        return out

    # row: distribute items along X. With a packing strategy the row WRAPS -- items that
    # do not fit start another row, chosen by that strategy -- otherwise it is one row and
    # overflowing it is an error, which is what it has always been.
    if g.packing is not None:
        cy = y
        for row_index, assigned in enumerate(_assign_rows(items, AW, min_gap, g.packing)):
            row = [items[i] for i, _t in assigned]
            turns = [t for _i, t in assigned]
            widths = _row_widths(row, AW, min_gap, turns)
            _check_row_fits(g, row, widths, AW, min_gap, interior_width, x_off)
            row_h = max((it.cell(t)[1] for it, t in zip(row, turns)), default=0.0)
            xpos = _positions(AW, widths, min_gap, justify)
            for (i, turned), cw, x in zip(assigned, widths, xpos):
                if not _cell_in_region(x_off + x, cy, cw, row_h, region):
                    continue   # cell falls outside the polygon outline -- skip it
                out.append(Placement(gi, i, row_index, x_off + x, cy, cw, row_h, turned))
            cy += row_h + min_gap
        return out

    turns = _row_turns(items, AW, min_gap)
    widths = _row_widths(items, AW, min_gap, turns)
    _check_row_fits(g, items, widths, AW, min_gap, interior_width, x_off)
    xpos = _positions(AW, widths, min_gap, justify)
    for j, (it, cw, x, turned) in enumerate(zip(items, widths, xpos, turns)):
        cl = band if it.fill else it.cell(turned)[1]
        if not _cell_in_region(x_off + x, y, cw, cl, region):
            continue   # cell falls outside the polygon outline -- skip it
        out.append(Placement(gi, j, 0, x_off + x, y, cw, cl, turned))
    return out


def _realise(groups: list[Group], plan: "tuple[Placement, ...]", IH: float) -> list[InnerObject]:
    """Turn a packing plan into geometry.

    Separate from the packing on purpose: the plan is cheap, deterministic and cacheable,
    while the solids must be built fresh every time -- one solid handle used by two CSG
    branches crashes the renderer.
    """
    expanded = [_expand(g.items) for g in groups]
    pieces: list[InnerObject] = []
    scoops: "dict[tuple[int, int], list]" = {}
    for place in plan:
        item = expanded[place.group][place.item]
        wells, scoop, other = _place_one(
            item, place.x, place.y, place.width, place.length, IH, place.rotated
        )
        pieces.extend(wells)
        if other is not None:
            pieces.append(other)
        if scoop is not None:
            scoops.setdefault((place.group, place.row), []).append(scoop)
    for key in sorted(scoops):
        pieces.extend(_merge_scoops(scoops[key]))   # one contiguous scoop per row
    return pieces


def pack_3d_boxes(container_size: list[float], items: list[dict]) -> dict:
    """Generic 3D First-Fit Decreasing box packer with Z-axis rotation and AABB height/width expansion.

    Args:
        container_size: [width, length, height] of the game box interior.
        items: list of dicts:
            {
                "name": str,
                "size": [w, l, h],         # minimum dimensions
                "expandable": list[str]     # list containing "h" (height) and/or "w" (width) to expand
            }

    Returns:
        A dictionary mapping item names to their packing configuration:
            {
                name: {
                    "pos": [x, y, z],
                    "size": [w, l, h],
                    "rotated": bool
                }
            }
    """
    import itertools
    container_w, container_l, container_h = container_size

    def overlaps(b1, b2):
        x1, y1, z1, w1, l1, h1 = b1
        x2, y2, z2, w2, l2, h2 = b2
        return (x1 < x2 + w2 and x1 + w1 > x2 and
                y1 < y2 + l2 and y1 + l1 > y2 and
                z1 < z2 + h2 and z1 + h1 > z2)

    best_solution = None
    for perm in itertools.permutations(items):
        placements = []
        extreme_points = [(0.0, 0.0, 0.0)]
        success = True
        
        for item in perm:
            placed = False
            extreme_points = sorted(list(set(extreme_points)), key=lambda p: (p[2], p[1], p[0]))
            
            orientations = [(item["size"], False)]
            if item["size"][0] != item["size"][1]:
                orientations.append(([item["size"][1], item["size"][0], item["size"][2]], True))
                
            for (w, l, h), rotated in orientations:
                for ep in extreme_points:
                    x, y, z = ep
                    if x + w <= container_w and y + l <= container_l and z + h <= container_h:
                        candidate = (x, y, z, w, l, h)
                        if not any(overlaps(candidate, other[1:7]) for other in placements):
                            placements.append((item["name"], x, y, z, w, l, h, rotated))
                            extreme_points.append((x + w, y, z))
                            extreme_points.append((x, y + l, z))
                            extreme_points.append((x, y, z + h))
                            placed = True
                            break
                if placed:
                    break
            if not placed:
                success = False
                break
        if success:
            best_solution = placements
            break
            
    if not best_solution:
        raise LayoutError(f"Could not pack components in 3D game box of size {container_size}!")
        
    # AABB Height (Z) and Width (X) expansion pass
    expanded = list(best_solution)
    for idx, (name, x, y, z, w, l, h, rotated) in enumerate(expanded):
        expandable = next(item["expandable"] for item in items if item["name"] == name)
        if "h" in expandable:
            min_upper_z = float(container_h)
            for other_name, ox, oy, oz, ow, ol, oh, orot in expanded:
                if other_name == name:
                    continue
                if (x < ox + ow and x + w > ox) and (y < oy + ol and y + l > oy):
                    if oz >= z + h:
                        if oz < min_upper_z:
                            min_upper_z = oz
            new_h = min_upper_z - z
            expanded[idx] = (name, x, y, z, w, l, new_h, rotated)
            
    for idx, (name, x, y, z, w, l, h, rotated) in enumerate(expanded):
        expandable = next(item["expandable"] for item in items if item["name"] == name)
        if "w" in expandable:
            min_right_x = float(container_w)
            for other_name, ox, oy, oz, ow, ol, oh, orot in expanded:
                if other_name == name:
                    continue
                if (y < oy + ol and y + l > oy) and (z < oz + oh and z + h > oz):
                    if ox >= x + w:
                        if ox < min_right_x:
                            min_right_x = ox
            new_w = min_right_x - x
            expanded[idx] = (name, x, y, z, new_w, l, h, rotated)
            
    return {name: {"pos": [x, y, z], "size": [w, l, h], "rotated": rotated} for name, x, y, z, w, l, h, rotated in expanded}


def pack_multibin_3d(container_size: list[float], items: list[dict], num_containers: int) -> dict | None:
    """Packs items across multiple containers of the same size.

    Args:
        container_size: [width, length, height] of each container.
        items: list of dicts: {"name": str, "size": [w, l, h], ...}
        num_containers: number of containers available.

    Returns:
        A dict mapping container index to its placements, or None if not packable.
    """
    sorted_items = sorted(items, key=lambda x: x["size"][0] * x["size"][1] * x["size"][2], reverse=True)
    bins_content = [[] for _ in range(num_containers)]
    
    def search(item_idx):
        if item_idx == len(sorted_items):
            solution = {}
            for i, bin_items in enumerate(bins_content):
                packed = pack_3d_boxes(container_size, bin_items)
                if len(packed) < len(bin_items):
                    return None
                solution[i] = packed
            return solution
            
        item = sorted_items[item_idx]
        for i in range(num_containers):
            bins_content[i].append(item)
            tot_vol = sum(x["size"][0] * x["size"][1] * x["size"][2] for x in bins_content[i])
            c_vol = container_size[0] * container_size[1] * container_size[2]
            if tot_vol <= c_vol:
                res = search(item_idx + 1)
                if res is not None:
                    return res
            bins_content[i].pop()
            
        return None

    return search(0)
