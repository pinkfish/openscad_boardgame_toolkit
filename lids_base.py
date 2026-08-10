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

# LibFile: lids_base.py
#    Shared lid building-blocks for all box types.
#
# FileSummary: Shared lid pieces for making lids.
# FileGroup: Basics

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace
from typing import Callable, Sequence, TYPE_CHECKING

# `fill` is a NATIVE builtin (no pybosl2 equivalent is wired up for it) and is imported by
# name rather than via `from pythonscad import *`: a star import here is what made a local
# variable called `fill` in lid_pattern_mesh() silently shadow it.
from pythonscad import fill

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid  # noqa: F401
    from openscad import PyOpenSCAD  # noqa: F401

# Explicit imports, matching box_base.py -- every name below is traceable to its source.
from base_bgtk import (
    BOTTOM,
    FRONT,
    LEFT,
    CatchType,
    LabelType,
    ShapeType,
    default_label_type,
    default_lid_thickness,
    default_material_colour,
    m_piece_wiggle_room,
    native_colour,
)
from pybosl2 import Color
from pybosl2 import shapes3d
from pybosl2 import shapes2d
from labels import LabelOptions, MakeFramedLidLabel, MakeFramelessLidLabel
from patterns import (
    DenseLattice,
    GridLattice,
    Lattice,
    Pattern,
    PatternArea,
    TiledPattern,
    pattern_for,
)


# ---------------------------------------------------------------------------
# Lid defaults (can be overridden at the file level by the user)
# ---------------------------------------------------------------------------

default_lid_shape_width = 12
default_lid_layout_width = 12
default_lid_aspect_ratio = 1.0
default_lid_shape_thickness = 2
default_lid_shape_rounding = 0
default_lid_shape_type = ShapeType.DENSE_HEX
default_lid_supershape_m1 = 4
default_lid_supershape_m2 = 4
default_lid_supershape_n1 = 1
default_lid_supershape_n2 = 1
default_lid_supershape_n3 = 1
default_lid_supershape_a = 1
default_lid_supershape_b = 1
default_lid_catch_type = CatchType.BUMPS_SHORT

# ---------------------------------------------------------------------------
# Lid pattern layer
# ---------------------------------------------------------------------------


def lid_pattern_mesh(
    *,
    pattern: "Pattern",
    area: "PatternArea",
    lid_thickness: float,
    boundary: float = 10,
    material_colour: Color | None = None,
) -> "PyOpenSCAD | None":
    """The lid's pattern layer: *pattern* filling *area*, extruded and trimmed to the lid.

    The ONE place a lid pattern becomes lid geometry. The pattern only ever produces flat
    2-D fill (see :mod:`patterns`); everything that makes it a LID -- lifting it to the lid
    thickness, the border ring around the edge, and clipping both to the boundary inset --
    happens here, so no pattern has to know what it is decorating.

    Returns ``None`` when the pattern is empty (``ShapeType.NONE``).

    Args:
        pattern:        the :class:`~patterns.Pattern` to fill with
        area:           the :class:`~patterns.PatternArea` to fill (the lid plate's footprint)
        lid_thickness:  height of the lid
        boundary:       width of the solid border left around the edge
        material_colour: colour (default default_material_colour)
    """
    if material_colour is None:
        material_colour = default_material_colour

    assert lid_thickness > 0, f"lid_thickness must be > 0 lid_thickness={lid_thickness}"

    # NB: not named `fill` -- that is the native builtin used by build_lid().
    filled = pattern.fill(area)
    if filled is None:
        return None

    # calc_path follows the classic corner-anchored square() convention -- [0,0] to
    # [width,length] -- because the lattices lay their cells out from near the origin and
    # have to line up with it. shapes2d._rect_path() is BOSL2-style (centred on the origin)
    # and would leave half the boundary untiled.
    calc_path = area.outline()

    mesh = filled.linear_extrude(height=lid_thickness + 1)
    # The pentagon/Penrose tilings are built as SDF (_sdf) shapes, so extruding one gives an
    # SDF solid; the rest of the lid is direct CSG. Cross the boundary once, here, rather
    # than leaving an SDF handle to reach build_lid()'s native projection().
    if hasattr(mesh, "to_csg"):
        mesh = mesh.to_csg()
    mesh = mesh.translate([0, 0, -0.5])

    # offset() is a 2-D op: it must run on the flat polygon before linear_extrude() lifts it
    # to 3-D, not after (calling offset() on an already-extruded solid silently yields nothing).
    border = shapes2d.polygon(calc_path).offset(radius=-boundary).linear_extrude(height=lid_thickness).color(
        material_colour
    ) - shapes2d.polygon(calc_path).offset(radius=-boundary - 0.02).linear_extrude(height=lid_thickness + 1).color(
        material_colour
    ).translate([0, 0, -0.5])

    bound = shapes2d.polygon(calc_path).offset(radius=-boundary).linear_extrude(height=lid_thickness).color(material_colour)
    # border (always a pybosl2 solid) on the LEFT: a pattern may hand back a raw native
    # handle (RHOMBI_TRI_HEXAGONAL does), and a native left operand rejects a pybosl2 right
    # one -- "invalid argument left to operator". Union is commutative; the operands are not.
    return (border | mesh) & bound


def build_lid(
    base: PyOpenSCAD,
    overlays: Sequence,
    *,
    lid_thickness: float,
    size_spacing: float | None = None,
) -> PyOpenSCAD:
    """Stack *overlays* onto *base*, carving holes so each piece merges cleanly.

    The base slab and the decoration are different KINDS of thing, so they are different
    arguments. (This used to be one ``children`` list whose element 0 was secretly the
    base -- a convention that had to be explained in prose because the signature could
    not express it.)

    Args:
        base:          the lid slab everything is cut into
        overlays:      decoration pieces, in stacking order
        lid_thickness: thickness of the lid
        size_spacing:  spacing between pieces (default m_piece_wiggle_room)
    """
    if size_spacing is None:
        size_spacing = m_piece_wiggle_room
    assert lid_thickness > 0, f"lid_thickness must be > 0 lid_thickness={lid_thickness}"

    # EVERY piece is a pybosl2 solid from here on. A native left operand rejects a pybosl2
    # right one -- native `__or__`/`__sub__` RAISE rather than returning NotImplemented, so
    # Python never gets to try the wrapper's reflected method -- which made the unions below
    # depend on the order overlays happened to arrive in. Normalising once here is what makes
    # them order-independent; do not push raw handles past this line.
    pieces = [p if isinstance(p, shapes3d.Bosl2Solid) else shapes3d.Bosl2Solid(p) for p in overlays]
    if not isinstance(base, shapes3d.Bosl2Solid):
        base = shapes3d.Bosl2Solid(base)
    n = len(pieces)
    # Each overlay's mask is used by the base AND by every earlier overlay -- build each
    # one ONCE (the projection + offset + extrude is the expensive part of a lid stack)
    # instead of rebuilding it inside the nested loop below.
    masks: dict[int, PyOpenSCAD] = {}

    def mask(i: int) -> PyOpenSCAD:
        cached = masks.get(i)
        if cached is None:
            piece = pieces[i]
            native = piece.shape if isinstance(piece, shapes3d.Bosl2Solid) else piece
            # NATIVE chain: fill()/projection() are native builtins (no pybosl2 equivalent
            # wired here), so .offset() is the native method -- it takes r=, not pybosl2's
            # radius=.
            cached = masks[i] = (
                fill(native.projection(cut=False))
                .offset(r=-size_spacing)
                .linear_extrude(height=lid_thickness + 1)
                .translate([0, 0, -0.5])
            )
        return cached

    for i in range(n):
        base = base - mask(i)

    extras = None
    for i in range(n):
        piece = pieces[i]
        for j in range(i + 1, n):
            piece = piece - mask(j)
        extras = piece if extras is None else extras | piece

    return base if extras is None else base | extras


# ---------------------------------------------------------------------------
# Lid class — self-contained mesh builder
# ---------------------------------------------------------------------------


class Decoration(ABC):
    """WHAT a lid is patterned with -- one of a closed set of alternatives.

    This is a sum type on purpose. The four ways a lid used to describe its pattern
    (``pattern`` / ``shape_options`` / ``shape_child`` / ``children``, plus ``dense`` and
    ``dense_shape_edges`` which applied to only one of them) were flat fields ranked by
    precedence, so giving two of them silently discarded one -- a lid that renders
    perfectly and is not the lid you asked for. Exactly one of these values IS the
    decoration, so there is nothing to rank and nothing to discard.

    Build one directly, or let :class:`Lid` build it from the ``shape_options=`` /
    ``pattern=`` / ``children=`` keyword sugar (which rejects conflicting combinations
    rather than resolving them)."""

    @abstractmethod
    def pattern(self, lid: "Lid") -> Pattern | None:
        """The :class:`~patterns.Pattern` to fill the lid's area with, or ``None``."""


class NoDecoration(Decoration):
    """A plain lid: no pattern at all."""

    def pattern(self, lid: "Lid") -> Pattern | None:
        return None


@dataclass(frozen=True)
class ShapePattern(Decoration):
    """The declarative case: a :class:`~shape_type.ShapeObject` naming a ``ShapeType``.

    The lattice and the layout context come from the shape type
    (:func:`~patterns.pattern_for`) -- which is why there is no lattice field here."""

    shape_options: "ShapeObject"
    #: A caller-built 2-D motif to stamp instead of the one the shape type would build.
    motif: "PyOpenSCAD | None" = None

    def pattern(self, lid: "Lid") -> Pattern | None:
        motif = self.motif.color(lid.material_colour) if self.motif is not None else None
        built = pattern_for(
            self.shape_options,
            layout_width=lid.layout_width,
            aspect_ratio=lid.aspect_ratio,
            motif=motif,
        )
        # Colour a tiled motif ONCE here rather than per cell. Returns a new pattern
        # rather than mutating the one pattern_for() built -- a resolve step that
        # mutates its own result is how a shared Lid ends up decorated differently the
        # second time it is used.
        if (
            isinstance(built, TiledPattern)
            and motif is None
            and built.motif is not None
            and not callable(built.motif)
        ):
            # native_colour(): a motif may be EITHER a pybosl2 wrapper or a raw native handle
            # (shapes.py returns natives), and native color() rejects a Color. The native form
            # is accepted by both, so it is the safe choice at a polymorphic site like this.
            return TiledPattern(
                motif=built.motif.color(native_colour(lid.material_colour)), lattice=built.lattice
            )
        return built


@dataclass(frozen=True)
class CustomPattern(Decoration):
    """A pre-built :class:`~patterns.Pattern`, for full control."""

    value: Pattern

    def pattern(self, lid: "Lid") -> Pattern | None:
        return self.value


@dataclass(frozen=True)
class TiledMotif(Decoration):
    """Raw children tiled on a lattice, with no ``ShapeType`` involved.

    *motif* is a 2-D shape or a callable per cell; *lattice* is explicit, because this is
    the only case where the caller -- not the shape type -- chooses it."""

    motif: "PyOpenSCAD | Callable"
    lattice: Lattice

    def pattern(self, lid: "Lid") -> Pattern | None:
        motif = self.motif
        if not callable(motif):
            # POLYMORPHIC receiver: `motif` is whatever the caller passed -- a pybosl2
            # wrapper or (as the type says) a raw native handle. A pybosl2 Color reaches
            # a native .color() as "TypeError: Unknown color representation", so the
            # colour goes through native_colour(), whose [R, G, B] list BOTH accept.
            motif = motif.color(native_colour(lid.material_colour))
        return TiledPattern(motif=motif, lattice=self.lattice)


@dataclass
class Fingernail:
    """Fingernail-scoop cutout config for a sliding lid (the dip you push to slide it open).

    ``enabled`` turns it on; the size/offsets default from the box dimensions (filled in by
    the box's lid pipeline) when left ``None``."""

    enabled: bool = False
    width: float | None = None
    length: float | None = None
    x_offset: float | None = None
    y_offset: float | None = None


@dataclass(frozen=True)
class Lid:
    """What decorates a lid: the pattern, the label, the fingernail scoop.

    A ``Lid`` describes DECORATION only -- never the lid's shape, and never its
    thickness. The box type supplies both as a :class:`~box_base.LidPlate`, and the
    single lid pipeline (:meth:`~box_base.LiddedBox.make_lid`) fits this decoration to
    that plate, passing the plate's footprint in as a :class:`LidFit`.

    **Frozen.** The pipeline used to write the plate's ``size``/``path`` back onto the
    ``Lid`` before building, guarded by a shallow copy -- so a ``Lid`` shared between two
    boxes was safe only by luck. Nothing mutates a ``Lid`` now; the per-box values travel
    in the :class:`LidFit`.

    Usage::

        lid = Lid(boundary=10, layout_width=10,
                  shape_options=MakeShapeObject(shape_type=ShapeType.DENSE_HEX),
                  label=Label("Trains"), fingernail=True)
        box.make_lid(lid).show()
    """

    #: WHAT the lid is patterned with. Defaults to nothing; the keyword sugar below
    #: builds one for the common cases.
    decoration: Decoration = field(default_factory=NoDecoration)
    boundary: float = 10
    layout_width: float = default_lid_layout_width
    aspect_ratio: float = default_lid_aspect_ratio
    material_colour: Color = default_material_colour
    label: "Label | None" = None
    lid_rounding: float | None = None
    extra_children: tuple = ()
    fingernail: "Fingernail | None" = None

    def __init__(
        self,
        *,
        decoration: Decoration | None = None,
        boundary: float = 10,
        layout_width: float | None = None,
        aspect_ratio: float | None = None,
        material_colour: Color | None = None,
        label: "Label | None" = None,
        lid_rounding: float | None = None,
        extra_children: "Sequence | None" = None,
        fingernail: "Fingernail | bool | None" = None,
        # ---- sugar: the three common decorations, spelled directly ----
        shape_options: "ShapeObject | None" = None,
        pattern: "Pattern | None" = None,
        children: "PyOpenSCAD | Callable | None" = None,
        shape_child: "PyOpenSCAD | None" = None,
        dense: bool = False,
        dense_shape_edges: int = 6,
        lid_thickness: float | None = None,
    ) -> None:
        """Build a lid, from a :class:`Decoration` or from the keyword sugar.

        The sugar covers the three usual cases -- ``shape_options=`` (a ShapeType),
        ``pattern=`` (a pre-built Pattern), ``children=`` (raw motif + ``dense=``) -- and
        **rejects** any combination of them. Ranking them by precedence, as this used to,
        meant ``Lid(pattern=X, shape_options=Y)`` silently threw Y away and produced a
        lid that renders perfectly and is not the one that was asked for.
        """
        given = {
            "decoration": decoration,
            "shape_options": shape_options,
            "pattern": pattern,
            "children": children if children is not None else shape_child,
        }
        named = [k for k, v in given.items() if v is not None]
        if len(named) > 1:
            raise TypeError(
                f"Lid: give exactly one decoration, got {sorted(named)}. "
                "These are alternatives, not layers -- pick the one you meant."
            )
        if shape_options is None and (dense or dense_shape_edges != 6) and children is None:
            raise TypeError(
                "Lid: dense/dense_shape_edges choose the lattice for children=, and do "
                "nothing on their own (with shape_options= the lattice comes from the "
                "shape type). Pass children=, or drop them."
            )
        if lid_thickness is not None:
            raise TypeError(
                "Lid: thickness belongs to the box's LidPlate, not to the decoration -- "
                "it comes from BoxSpec(lid_thickness=...). Remove lid_thickness=."
            )

        layout = default_lid_layout_width if layout_width is None else layout_width
        aspect = default_lid_aspect_ratio if aspect_ratio is None else aspect_ratio

        if decoration is None:
            if shape_options is not None:
                decoration = ShapePattern(shape_options=shape_options, motif=shape_child)
            elif pattern is not None:
                decoration = CustomPattern(value=pattern)
            elif children is not None or shape_child is not None:
                motif = children if children is not None else shape_child
                lattice = (
                    DenseLattice(width=layout, edges=dense_shape_edges)
                    if dense
                    else GridLattice(width=layout, edges=4, aspect_ratio=aspect)
                )
                decoration = TiledMotif(motif=motif, lattice=lattice)
            else:
                decoration = NoDecoration()

        # A bare bool is accepted for the common "just give me a fingernail" case.
        if isinstance(fingernail, bool):
            fingernail = Fingernail(enabled=fingernail)

        object.__setattr__(self, "decoration", decoration)
        object.__setattr__(self, "boundary", boundary)
        object.__setattr__(self, "layout_width", layout)
        object.__setattr__(self, "aspect_ratio", aspect)
        object.__setattr__(self, "material_colour",
                           default_material_colour if material_colour is None else material_colour)
        object.__setattr__(self, "label", label)
        object.__setattr__(self, "lid_rounding", lid_rounding)
        object.__setattr__(self, "extra_children", tuple(extra_children or ()))
        object.__setattr__(self, "fingernail", fingernail)

    def with_label(self, text: str) -> "Lid":
        """A copy of this lid whose label reads *text*, keeping everything else.

        This is what makes ONE ``BoxSpec.lid`` field as convenient as the five it
        replaced: a :class:`~box_base.BoxKit` carries the shared lid (pattern, label
        styling, fingernail) and each box supplies only its own words::

            kit = BoxKit(SlidingBox, lid=Lid(shape_options=HEX,
                                             label=Label("", options=BLUE)))
            kit.box(size=..., label="Seals", lid="Seals")   # -> with_label("Seals")

        The existing label's OPTIONS and placement survive -- only ``text`` changes. A
        lid with no label yet gets a default-styled one.
        """
        # Label lives in box_base, which imports this module -- so the import has to be
        # here rather than at module scope. It is the only direction the cycle allows.
        from box_base import Label

        label = replace(self.label, text=text) if self.label is not None else Label(text)
        return replace(self, label=label)

    def pattern(self) -> "Pattern | None":
        """The :class:`~patterns.Pattern` this lid is decorated with, or ``None``."""
        return self.decoration.pattern(self)

    def mesh(self, fit: "LidFit") -> PyOpenSCAD | None:
        """This lid's pattern layer fitted to *fit*, or ``None`` when it has no pattern."""
        pattern = self.pattern()
        if pattern is None:
            return None
        return lid_pattern_mesh(
            pattern=pattern,
            area=fit.area(),
            lid_thickness=fit.thickness,
            boundary=self.boundary,
            material_colour=self.material_colour,
        )

    def fingernail_cutout(self, fit: "LidFit") -> "Bosl2Solid | None":
        """The fingernail scoop sized/placed from *fit*, or ``None`` when disabled.

        Defaults that used to be written back onto the caller's :class:`Fingernail` are
        resolved locally here, so nothing is mutated."""
        fn = self.fingernail
        if fn is None or not fn.enabled:
            return None
        ox, oy = fit.origin
        fn_w = fn.width if fn.width is not None else fit.width
        fn_l = fn.length if fn.length is not None else fit.length
        x_off = fn.x_offset if fn.x_offset is not None else ox + fn_w / 2
        y_off = fn.y_offset if fn.y_offset is not None else oy + fn_l - 3
        return (
            shapes3d.cuboid([fn_w, fn_l, fit.thickness]).color(self.material_colour)
            & sliding_lid_fingernail(
                fit.thickness,
                material_colour=self.material_colour,
            ).translate([x_off, y_off, 0])
        )

    def overlay(
        self,
        fit: "LidFit",
        *,
        label_builder: "Callable[[Label], PyOpenSCAD | None] | None" = None,
    ) -> list:
        """Every decoration piece for this lid, in the order :func:`build_lid` stacks
        them: fingernail, pattern mesh, label, extras.

        This is the ONE place a lid's decoration list is built -- the single lid pipeline
        calls it for every box type, whatever shape that type's plate is.

        Args:
            fit:           the plate footprint this decoration is fitted to
            label_builder: callable taking a :class:`~box_base.Label` and returning its
                geometry (the box's :meth:`~box_base.LiddedBox.make_label`)
        """
        overlay_children: list = []

        fn = self.fingernail_cutout(fit)
        if fn is not None:
            overlay_children.append(fn)

        mesh = self.mesh(fit)
        if mesh is not None:
            overlay_children.append(mesh)

        if self.label is not None and label_builder is not None:
            label_shape = label_builder(self.label)
            if label_shape is not None:
                overlay_children.append(label_shape)

        overlay_children.extend(self.extra_children)
        return overlay_children


@dataclass(frozen=True)
class LidFit:
    """The plate footprint a lid's decoration is fitted to.

    Everything here belongs to the BOX's plate, not to the decoration, and used to be
    written onto the :class:`Lid` before building. Passing it as a value keeps ``Lid``
    immutable and makes the direction of the dependency obvious.

    Attributes:
        width/length: footprint the pattern fills
        thickness:    the plate's thickness -- the ONE source for it
        origin:       ``(x, y)`` of the footprint's minimum corner in plate coordinates
        path:         outline when it isn't the ``width`` x ``length`` rectangle
    """

    width: float
    length: float
    thickness: float
    origin: tuple[float, float] = (0.0, 0.0)
    path: "Sequence | None" = None

    def area(self) -> PatternArea:
        """The region the pattern fills."""
        if self.path is not None:
            pts = [[float(p[0]), float(p[1])] for p in self.path]
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            return PatternArea(width=max(xs) - min(xs), length=max(ys) - min(ys), path=pts)
        return PatternArea(width=self.width, length=self.length)



# ---------------------------------------------------------------------------
# Lid construction helpers
# ---------------------------------------------------------------------------


def sliding_lid_fingernail(
    lid_thickness: float,
    radius: float = 6,
    finger_gap: float = 1.5,
    sphere: float = 12,
    finger_length: float = 10,
    material_colour: Color | None = None,
) -> "Bosl2Solid":
    """Creates a finger-nail recess for lifting a sliding lid.

    Usage::

        sliding_lid_fingernail(3)

    Args:
        lid_thickness:  height of the lid
        radius:         radius of the fingernail circle (default 6)
        finger_gap:     gap for the finger (default 1.5)
        sphere:         sphere inset size (default 12)
        finger_length:  length of the finger section (default 10)
        material_colour: colour (default default_material_colour)
    """
    if material_colour is None:
        material_colour = default_material_colour

    assert lid_thickness > 0, f"lid_thickness must be > 0 lid_thickness={lid_thickness}"

    cyl_part = shapes3d.cyl(height=lid_thickness, radius=radius).color(material_colour).translate([0, 0, lid_thickness / 2])

    cut_box = (
        shapes3d.cuboid([finger_length, finger_length, finger_gap], anchor=FRONT + LEFT + BOTTOM)
        .color(material_colour)
        .translate([-finger_length / 2, -finger_length, -finger_length])
    )
    cut_sphere = shapes3d.sphere(radius=finger_length).color(material_colour)
    cutter = (cut_box & cut_sphere).translate([0, 0, finger_length + lid_thickness - finger_gap + 0.1])

    return cyl_part - cutter


def make_lid_tab(
    length: float,
    height: float,
    lid_thickness: float | None = None,
    prism_width: float = 0.75,
    wall_thickness: float = 2,
) -> "Bosl2Solid":
    """Makes a single lid tab (for tabbed boxes).

    Usage::

        make_lid_tab(length=5, height=10, lid_thickness=2)

    Args:
        length:         length of the tab
        height:         height of the tab
        lid_thickness:  thickness of the lid (default default_lid_thickness)
        prism_width:    prism width factor (default 0.75)
        wall_thickness: wall thickness (default 2)
    """
    if lid_thickness is None:
        lid_thickness = default_lid_thickness

    assert lid_thickness > 0, f"lid_thickness must be > 0 lid_thickness={lid_thickness}"

    base = shapes3d.cuboid([length, wall_thickness, lid_thickness], anchor=FRONT + LEFT + BOTTOM)

    stalk = shapes3d.cuboid([length, wall_thickness / 2, height - wall_thickness + 0.1], anchor=FRONT + LEFT + BOTTOM)
    wedge = (
        shapes3d.xcyl(height=length, radius=0.1)
        .translate([length / 2, wall_thickness * prism_width - 0.1, height - wall_thickness + 0.1])
        .hull(
            shapes3d.cuboid([length, 0.1, 0.1], anchor=FRONT + LEFT + BOTTOM).translate(
                [0, 0, height - wall_thickness]
            ),
            shapes3d.xcyl(height=length, radius=0.1).translate([length / 2, 0.1, height - 0.1]),
        )
    )

    return (base | stalk | wedge).mirror([0, 0, 1])


def make_tabs(
    size: list[float],
    lid_thickness: float | None = None,
    tab_length: float = 10,
    make_tab_width: bool = False,
    make_tab_length: bool = True,
    children: "PyOpenSCAD | Callable[[], PyOpenSCAD] | None" = None,
) -> PyOpenSCAD:
    """Layout tabs for a tabbed box lid.

    Usage::

        make_tabs([50, 100],
                 children=make_lid_tab(length=10, height=6))

    Args:
        size:           [width, length] (or [width, length, height]) of the box
        lid_thickness:  lid height (default default_lid_thickness)
        tab_length:     tab length (default 10)
        make_tab_width: add tabs on the width sides (default False)
        make_tab_length: add tabs on the length sides (default True)
        children:       tab geometry to place (typically make_lid_tab(...))
    """
    if lid_thickness is None:
        lid_thickness = default_lid_thickness

    assert isinstance(size, (list, tuple)) and len(size) in (2, 3), (
        f"size must be [width, length] or [width, length, height], got {size}"
    )
    assert lid_thickness > 0, f"lid_thickness must be > 0 lid_thickness={lid_thickness}"
    assert children is not None, "Must specify children (e.g. make_lid_tab(...))"

    box_width, box_length = size[0], size[1]

    shape = None

    # `children` may be a plain solid or a zero-argument factory returning one. The factory
    # form exists because PythonSCAD SEGFAULTS if one frep()-meshed handle is transformed in
    # more than one CSG branch (plain CSG handles reuse fine) -- callers placing a
    # pysolidfive-meshed tab pass a lambda so every placement below gets a fresh mesh.
    def tab_piece() -> PyOpenSCAD:
        return children() if callable(children) else children

    def add(piece: PyOpenSCAD) -> None:
        nonlocal shape
        shape = piece if shape is None else shape | piece

    if make_tab_length:
        add(tab_piece().rotate([0, 0, 270]).translate([0, (box_length + tab_length) / 2, lid_thickness]))
        add(tab_piece().rotate([0, 0, 90]).translate([box_width, (box_length - tab_length) / 2, lid_thickness]))

    if make_tab_width:
        add(tab_piece().translate([(box_width - tab_length) / 2, 0, lid_thickness]))
        add(tab_piece().rotate([0, 0, 180]).translate([(box_width + tab_length) / 2, box_length, lid_thickness]))

    assert shape is not None, "make_tabs(): at least one of make_tab_width/make_tab_length must be True"
    return shape


def make_lid_label(size: list[float], lid_thickness: float, text_str: str, options: LabelOptions) -> PyOpenSCAD | None:
    """Places a label on a lid at the correct position and rotation.

    Usage::

        make_lid_label([100, 20], lid_thickness=2, text_str="Frog",
                     options=MakeLabelOptions(text_length=50, text_scale=1.0,
                                              border=2, offset=4, radius=2,
                                              label_type=LabelType.FRAMED,
                                              full_height=True))

    Args:
        size:          [width, length] (or [width, length, height]) of the lid interior
        lid_thickness: thickness of the lid
        text_str:      text to display
        options:       :class:`~labels.LabelOptions` (from :func:`~labels.MakeLabelOptions`)
    """
    assert isinstance(size, (list, tuple)) and len(size) in (2, 3), (
        f"size must be [width, length] or [width, length, height], got {size}"
    )
    assert text_str is not None, "Must specify text_str"
    assert options is not None, "Must specify label options"
    assert lid_thickness > 0, f"lid_thickness must be > 0 lid_thickness={lid_thickness}"

    calc_label_type = options.label_type
    if calc_label_type is None:
        calc_label_type = default_label_type
    if calc_label_type in (
        LabelType.FRAMED,
        LabelType.FRAMED_SHORT,
        LabelType.FRAMED_SHORT_SOLID,
        LabelType.FRAMED_SOLID,
    ):
        return MakeFramedLidLabel(size=size, lid_thickness=lid_thickness, label=text_str, options=options)
    elif calc_label_type in (LabelType.FRAMELESS_ANGLE, LabelType.FRAMELESS, LabelType.FRAMELESS_SHORT):
        return MakeFramelessLidLabel(size=size, label=text_str, lid_thickness=lid_thickness, options=options)
    return None
