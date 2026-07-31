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
from pythonscad import *
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from openscad import PyOpenSCAD  # noqa: F401
from base_bgtk import *
from pybosl2 import shapes3d
from pybosl2 import shapes2d
from labels import LabelOptions, MakeFramedLidLabel, MakeFramelessLidLabel
from patterns import (
    DenseLattice,
    GridLattice,
    Pattern,
    PatternArea,
    TiledPattern,
    pattern_for,
)

from dataclasses import dataclass


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
    material_colour: str | None = None,
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

    # NB: not named `fill` -- that is the native builtin used by internal_build_lid().
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
    # than leaving an SDF handle to reach internal_build_lid()'s native projection().
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


def internal_build_lid(lid_thickness: float, children: list, size_spacing: float | None = None) -> PyOpenSCAD:
    """Builds a lid out of a stack of pieces, carving holes so each merges cleanly.

    Unlike the original SCAD module (which used a variable children() block),
    *children* here must be a Python list: children[0] is the base lid shape
    and children[1:] are extra pieces overlaid on top of it.

    Args:
        lid_thickness: thickness of the lid
        children:      list of solids; children[0] is the base shape
        size_spacing:  spacing between pieces (default m_piece_wiggle_room)
    """
    if size_spacing is None:
        size_spacing = m_piece_wiggle_room
    assert lid_thickness > 0, f"lid_thickness must be > 0 lid_thickness={lid_thickness}"
    assert isinstance(children, (list, tuple)) and len(children) >= 1, "children must be a non-empty list"

    n = len(children)
    # Each overlay's mask is used by the base AND by every earlier overlay -- build each
    # one ONCE (the projection + offset + extrude is the expensive part of a lid stack)
    # instead of rebuilding it inside the nested loop below.
    masks: dict[int, PyOpenSCAD] = {}

    def mask(i: int) -> PyOpenSCAD:
        cached = masks.get(i)
        if cached is None:
            piece = children[i]
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

    base = children[0]
    for i in range(1, n):
        base = base - mask(i)

    extras = None
    for i in range(1, n):
        piece = children[i]
        for j in range(i + 1, n):
            piece = piece - mask(j)
        extras = piece if extras is None else extras | piece

    return base if extras is None else base | extras


# ---------------------------------------------------------------------------
# Lid class — self-contained mesh builder
# ---------------------------------------------------------------------------


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


@dataclass
class Lid:
    """What decorates a lid: the tiled pattern, the label, the fingernail scoop.

    A ``Lid`` describes DECORATION only -- never the lid's shape. The box type supplies
    the shape as a :class:`~box_base.LidPlate`, and the single lid pipeline
    (:meth:`~box_base.BoxBaseType.make_lid`) fits this decoration to it. ``size`` and
    ``path`` are therefore filled in from that plate; setting them by hand only matters
    when calling :meth:`mesh` directly.

    Pass one to a box as ``BoxSpec(lid=...)``, or to ``make_lid(lid)``; the box never
    mutates the one you pass.

    Usage::

        lid = Lid(lid_thickness=2, boundary=10, layout_width=10,
                  shape_options=MakeShapeObject(shape_type=ShapeType.DENSE_HEX),
                  label=Label("Trains"), fingernail=True)
        box.make_lid(lid).show()
    """

    lid_thickness: float
    #: Footprint the pattern is filled over -- set from the box's LidPlate.
    size: list[float] | None = None
    #: Polygon outline of the footprint (a path lid); ``None`` -> the ``size`` rectangle.
    path: list[list[float]] | None = None
    boundary: float = 10
    layout_width: float | None = None
    aspect_ratio: float | None = None
    material_colour: str | None = None
    label: "Label | None" = None
    #: The pattern, declaratively: a :class:`~shape_type.ShapeObject` naming a ShapeType.
    shape_options: "ShapeObject | None" = None
    #: A pre-built :class:`~patterns.Pattern`, for full control. Wins over shape_options.
    pattern: "Pattern | None" = None
    #: A caller-built 2-D motif to tile instead of the one shape_options would build.
    shape_child: "PyOpenSCAD | None" = None
    #: Raw children to tile with no ShapeType at all (motif, or callable per cell).
    children: "PyOpenSCAD | None" = None
    #: Lattice for the raw-``children`` case only (with shape_options the lattice comes
    #: from the shape type -- see :func:`~patterns.lattice_for`).
    dense: bool = False
    dense_shape_edges: int = 6
    lid_rounding: float | None = None
    extra_children: list | None = None
    fingernail: "Fingernail | bool | None" = None

    def __post_init__(self) -> None:
        if self.material_colour is None:
            self.material_colour = default_material_colour
        if self.layout_width is None:
            self.layout_width = default_lid_layout_width
        if self.aspect_ratio is None:
            self.aspect_ratio = default_lid_aspect_ratio
        # A bare bool is accepted for the common "just give me a fingernail" case.
        if isinstance(self.fingernail, bool):
            self.fingernail = Fingernail(enabled=self.fingernail)

    def area(self) -> PatternArea:
        """The region this lid's pattern fills -- its plate footprint."""
        if self.path is not None:
            pts = [[float(p[0]), float(p[1])] for p in self.path]
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            return PatternArea(width=max(xs) - min(xs), length=max(ys) - min(ys), path=pts)
        assert self.size is not None, "Lid needs a size or a path to fill a pattern over"
        return PatternArea(width=self.size[0], length=self.size[1])

    def resolved_pattern(self) -> "Pattern | None":
        """The :class:`~patterns.Pattern` this lid is decorated with, or ``None``.

        An explicit :attr:`pattern` wins; otherwise one is built from :attr:`shape_options`
        (see :func:`~patterns.pattern_for`); otherwise raw :attr:`children` are tiled on the
        :attr:`dense` lattice. This is the ONE place a lid decides what its pattern is."""
        if self.pattern is not None:
            return self.pattern

        if self.shape_options is not None:
            motif = self.shape_child.color(self.material_colour) if self.shape_child is not None else None
            pattern = pattern_for(
                self.shape_options,
                layout_width=self.layout_width,
                aspect_ratio=self.aspect_ratio,
                motif=motif,
            )
            # A tiled motif is coloured once, here, rather than per cell.
            if (
                isinstance(pattern, TiledPattern)
                and motif is None
                and pattern.motif is not None
                and not callable(pattern.motif)
            ):
                pattern.motif = pattern.motif.color(self.material_colour)
            return pattern

        raw = self.shape_child if self.shape_child is not None else self.children
        if raw is None:
            return None
        if not callable(raw):
            raw = raw.color(self.material_colour)
        lattice = (
            DenseLattice(width=self.layout_width, edges=self.dense_shape_edges)
            if self.dense
            else GridLattice(width=self.layout_width, edges=4, aspect_ratio=self.aspect_ratio)
        )
        return TiledPattern(motif=raw, lattice=lattice)

    def mesh(self) -> PyOpenSCAD | None:
        """This lid's pattern layer, or ``None`` when it has no pattern.

        Resolves the pattern (:meth:`resolved_pattern`) and fills this lid's
        :meth:`area` with it via :func:`lid_pattern_mesh`.
        """
        pattern = self.resolved_pattern()
        if pattern is None:
            return None
        return lid_pattern_mesh(
            pattern=pattern,
            area=self.area(),
            lid_thickness=self.lid_thickness,
            boundary=self.boundary,
            material_colour=self.material_colour,
        )

    def fingernail_cutout(self) -> PyOpenSCAD | None:
        """Return a fingernail cutout solid, or None if the fingernail is not enabled."""
        fn = self.fingernail
        if fn is None or not fn.enabled:
            return None
        fn_w = fn.width or 10
        fn_l = fn.length or 10
        x_off = fn.x_offset if fn.x_offset is not None else fn_w / 2
        y_off = fn.y_offset if fn.y_offset is not None else fn_l - 3
        return (
            shapes3d.cuboid(
                [fn_w, fn_l, self.lid_thickness],
            ).color(self.material_colour)
            & SlidingLidFingernail(
                self.lid_thickness,
                material_colour=self.material_colour,
            )
            .translate([x_off, y_off, 0])
        )

    def overlay(
        self,
        *,
        label_builder: "Callable[[Label], PyOpenSCAD | None] | None" = None,
    ) -> list:
        """Every decoration piece for this lid, in the order
        :func:`internal_build_lid` stacks them: fingernail, pattern mesh, label, extras.

        This is the ONE place a lid's decoration list is built -- the single lid pipeline
        calls it for every box type, whatever shape that type's plate is.

        Args:
            label_builder: callable that takes a :class:`~box_base.Label` and returns its
                geometry (the box's :meth:`~box_base.BoxBaseType.make_label`, which fits
                the label to the plate)
        """
        overlay_children: list = []

        fn = self.fingernail_cutout()
        if fn is not None:
            overlay_children.append(fn)

        if self.shape_child is not None or self.shape_options is not None:
            mesh = self.mesh()
            if mesh is not None:
                overlay_children.append(mesh)

        if self.label is not None and label_builder is not None:
            label_shape = label_builder(self.label)
            if label_shape is not None:
                overlay_children.append(label_shape)

        if self.extra_children:
            overlay_children.extend(self.extra_children)

        return overlay_children


# ---------------------------------------------------------------------------
# Lid construction helpers
# ---------------------------------------------------------------------------


def SlidingLidFingernail(
    lid_thickness: float,
    radius: float = 6,
    finger_gap: float = 1.5,
    sphere: float = 12,
    finger_length: float = 10,
    material_colour: str | None = None,
) -> PyOpenSCAD:
    """Creates a finger-nail recess for lifting a sliding lid.

    Usage::

        SlidingLidFingernail(3)

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


def MakeLidTab(
    length: float,
    height: float,
    lid_thickness: float | None = None,
    prism_width: float = 0.75,
    wall_thickness: float = 2,
) -> PyOpenSCAD:
    """Makes a single lid tab (for tabbed boxes).

    Usage::

        MakeLidTab(length=5, height=10, lid_thickness=2)

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


def MakeTabs(
    size: list[float],
    lid_thickness: float | None = None,
    tab_length: float = 10,
    make_tab_width: bool = False,
    make_tab_length: bool = True,
    children: "PyOpenSCAD | Callable[[], PyOpenSCAD] | None" = None,
) -> PyOpenSCAD:
    """Layout tabs for a tabbed box lid.

    Usage::

        MakeTabs([50, 100],
                 children=MakeLidTab(length=10, height=6))

    Args:
        size:           [width, length] (or [width, length, height]) of the box
        lid_thickness:  lid height (default default_lid_thickness)
        tab_length:     tab length (default 10)
        make_tab_width: add tabs on the width sides (default False)
        make_tab_length: add tabs on the length sides (default True)
        children:       tab geometry to place (typically MakeLidTab(...))
    """
    if lid_thickness is None:
        lid_thickness = default_lid_thickness

    assert isinstance(size, (list, tuple)) and len(size) in (2, 3), (
        f"size must be [width, length] or [width, length, height], got {size}"
    )
    assert lid_thickness > 0, f"lid_thickness must be > 0 lid_thickness={lid_thickness}"
    assert children is not None, "Must specify children (e.g. MakeLidTab(...))"

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

    assert shape is not None, "MakeTabs(): at least one of make_tab_width/make_tab_length must be True"
    return shape


def MakeLidLabel(size: list[float], lid_thickness: float, text_str: str, options: LabelOptions) -> PyOpenSCAD | None:
    """Places a label on a lid at the correct position and rotation.

    Usage::

        MakeLidLabel([100, 20], lid_thickness=2, text_str="Frog",
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
