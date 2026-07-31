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
    from pysolidfive import PyShape, PyShape2D  # noqa: F401
from base_bgtk import *
from pybosl2 import shapes3d
from pybosl2 import shapes2d
from labels import LabelOptions, MakeLabelOptions, MakeFramedLidLabel, MakeFramelessLidLabel
from components import RegularPolygonGridDense, RegularPolygonGrid

from dataclasses import dataclass
import copy
import math
import types


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
# Helper functions (pure Python equivalents of SCAD functions)
# ---------------------------------------------------------------------------


def IsDenseShapeType(shape_type: ShapeType | None = None) -> bool:
    """Return True if *shape_type* is a 'dense' layout type."""
    t = shape_type if shape_type is not None else default_lid_shape_type
    return t in (
        ShapeType.DENSE_HEX,
        ShapeType.DENSE_TRIANGLE,
        ShapeType.DELTOID_TRIHEXAGONAL_KITE,
        ShapeType.DELTOID_TRIHEXAGONAL,
    )


def DenseShapeEdges(shape_type: ShapeType) -> int:
    """Return the number of edges on the given dense shape type."""
    return 3 if shape_type == ShapeType.DENSE_TRIANGLE else 6


# ---------------------------------------------------------------------------
# Lid mesh modules
# ---------------------------------------------------------------------------


def LidMeshDense(
    path: list[list[float]],
    lid_thickness: float,
    boundary: float,
    radius: float,
    shape_edges: int = 6,
    material_colour: str | None = None,
    inner_control: int | bool = False,
    children: "PyOpenSCAD | PyShape2D | Callable | None" = None,
) -> "PyOpenSCAD | PyShape":
    """Make a dense hex/triangle mesh for a lid.

    Usage::

        LidMeshDense(path=[[0,0],[100,0],[100,50],[0,50]],
                     lid_thickness=3, boundary=10, radius=5, shape_edges=6)

    Args:
        path:           2-D path defining the mesh boundary
        lid_thickness:  height of the lid
        boundary:       edge boundary width
        radius:         polygon radius
        shape_edges:    edges per polygon (default 6)
        material_colour: colour (default default_material_colour, unused directly
                         here -- kept for API compatibility with callers)
        inner_control:  if True, layout is driven by a children callable
                        (see RegularPolygonGridDense)
        children:       the shape to tile (e.g. ShapeByType(...)), or a
                        callable(polygon_x, polygon_y) when inner_control is True
    """
    if material_colour is None:
        material_colour = default_material_colour

    assert lid_thickness > 0, f"lid_thickness must be > 0 lid_thickness={lid_thickness}"

    x_arr = [p[0] for p in path]
    y_arr = [p[1] for p in path]
    width = max(x_arr) - min(x_arr)
    length = max(y_arr) - min(y_arr)

    cell_width = math.cos(math.radians(180 / shape_edges)) * radius
    rows = width / cell_width + 2
    cols = length / cell_width + 2

    grid = RegularPolygonGridDense(
        radius=radius, rows=rows, cols=cols, shape_edges=shape_edges, inner_control=inner_control, children=children
    )
    return grid.linear_extrude(height=lid_thickness + 1).translate([0, 0, -0.5])


def LidMeshHex(
    size: list[float],
    lid_thickness: float,
    boundary: float,
    radius: float,
    shape_thickness: float = 2,
    inner_control: int | bool = False,
) -> "PyOpenSCAD | PyShape":
    """Make a hex mesh for a lid.

    Usage::

        LidMeshHex(size=[100, 50], lid_thickness=3, boundary=10, radius=5)

    Args:
        size:           [width, length] (or [width, length, height]) of the mesh area
        lid_thickness:  height of the lid
        boundary:       edge boundary width
        radius:         hex polygon radius
        shape_thickness: gap between hexes (default 2)
        inner_control:  driven by a children callable (default False)
    """
    assert isinstance(size, (list, tuple)) and len(size) in (2, 3), f"size must be [width, length], got {size}"
    width, length = size[0], size[1]
    assert lid_thickness > 0, f"lid_thickness must be > 0 lid_thickness={lid_thickness}"

    def shape_for(polygon_width: float) -> "PyOpenSCAD | PyShape2D":
        from shape_type import MakeShapeObject, ShapeByType

        piece = ShapeByType(MakeShapeObject(shape_type=ShapeType.DENSE_HEX, shape_width=polygon_width))
        assert piece is not None
        return piece

    children = (lambda i, j: shape_for(radius * 2)) if inner_control else shape_for(radius * 2)

    return LidMeshDense(
        path=[[0, 0], [width, 0], [width, length], [0, length]],
        lid_thickness=lid_thickness,
        boundary=boundary,
        radius=radius,
        shape_edges=6,
        inner_control=inner_control,
        children=children,
    )


def LidMeshRepeating(
    path: list[list[float]],
    lid_thickness: float,
    boundary: float,
    layout_width: float,
    aspect_ratio: float = 1.0,
    shape_edges: int = 4,
    material_colour: str | None = None,
    inner_control: int = 0,
    children: PyOpenSCAD | None = None,
) -> PyOpenSCAD:
    """Make a repeating-shape mesh for a lid.

    Usage::

        LidMeshRepeating([[0,0],[50,0],[50,20],[0,20]],
                         lid_thickness=3, boundary=5, layout_width=10)

    Args:
        path:           2-D path defining the mesh boundary
        lid_thickness:  height of the lid
        boundary:       edge boundary width
        layout_width:   spacing between pattern repeats
        aspect_ratio:   dy scale factor (default 1.0)
        shape_edges:    polygon edges for layout (default 4)
        material_colour: colour (default default_material_colour, unused directly
                         here -- kept for API compatibility with callers)
        inner_control:  0=auto, 1=children callable(polygon_x, polygon_y, cols, rows),
                        2=children callable(polygon_width, polygon_length, cols, rows)
        children:       shape solid(s) to tile, or a callable per inner_control above
    """
    if material_colour is None:
        material_colour = default_material_colour

    assert lid_thickness > 0, f"lid_thickness must be > 0 lid_thickness={lid_thickness}"

    x_arr = [p[0] for p in path]
    y_arr = [p[1] for p in path]
    width = max(x_arr) - min(x_arr)
    length = max(y_arr) - min(y_arr)

    rows = width / layout_width + 2
    cols = length / layout_width * aspect_ratio + 2

    grid = RegularPolygonGrid(
        width=layout_width,
        rows=rows + (11 if inner_control else 1),
        cols=cols + (11 if inner_control else 1),
        spacing=0,
        shape_edges=shape_edges,
        aspect_ratio=aspect_ratio,
        inner_control=inner_control,
        space_width=width,
        space_length=length,
        children=children,
    )
    return grid.linear_extrude(height=lid_thickness + 1).translate([0, 0, -0.5])


def LidMeshBasic(
    lid_thickness: float,
    boundary: float,
    layout_width: float | None,
    size: list[float] | None = None,
    path: list[list[float]] | None = None,
    aspect_ratio: float | None = 1.0,
    dense: bool = False,
    dense_shape_edges: int = 6,
    material_colour: str | None = None,
    inner_control: int | bool = False,
    children: PyOpenSCAD | None = None,
) -> PyOpenSCAD:
    """Make a lid mesh using one of the known shape types.

    Provide either *size* or *path* (but not both).

    Usage::

        LidMeshBasic(size=[100, 50], lid_thickness=2, boundary=10,
                     layout_width=10, dense=True,
                     children=ShapeByType(MakeShapeObject(
                         shape_type=ShapeType.DENSE_HEX,
                         shape_thickness=2,
                         shape_width=10)))

    Args:
        lid_thickness:    height of the lid
        boundary:         edge boundary width
        layout_width:     spacing between pattern repeats
        size:             [width, length] or [width, length, height]
        path:             explicit 2-D path (alternative to size)
        aspect_ratio:     dy scale factor (default 1.0)
        dense:            use dense layout (default False)
        dense_shape_edges: edges per dense polygon (default 6)
        material_colour:  colour (default default_material_colour)
        inner_control:    layout control mode (default False/0)
        children:         tiling shape solid(s), or callable (see LidMeshDense/LidMeshRepeating)
    """
    if material_colour is None:
        material_colour = default_material_colour

    assert size is not None or path is not None, "Must provide either size or path to LidMeshBasic"
    assert path is not None or (isinstance(size, (list, tuple)) and len(size) in (2, 3)), (
        f"Invalid size in LidMeshBasic, size={size}"
    )
    assert lid_thickness > 0, f"lid_thickness must be > 0 lid_thickness={lid_thickness}"

    calc_layout_width = layout_width
    if calc_layout_width is None:
        calc_layout_width = default_lid_layout_width
    calc_aspect_ratio = aspect_ratio
    if calc_aspect_ratio is None:
        calc_aspect_ratio = default_lid_aspect_ratio
    # calc_path must match the classic (corner-anchored, center=false) square()'s point
    # convention -- [0,0] to [width,length] -- since the mesh grid below (RegularPolygonGrid/
    # RegularPolygonGridDense) always lays its tiles out starting near the origin regardless of
    # calc_path, and needs to line up with it. shapes2d._rect_path() is BOSL2-style (centered on
    # the origin) and would leave half the boundary untiled if used here instead.
    calc_path = [[0, 0], [size[0], 0], [size[0], size[1]], [0, size[1]]] if size is not None else path
    assert calc_path is not None, "must give size or path"

    if dense:
        mesh = LidMeshDense(
            path=calc_path,
            lid_thickness=lid_thickness,
            boundary=boundary,
            radius=calc_layout_width / 2,
            shape_edges=dense_shape_edges,
            material_colour=material_colour,
            inner_control=inner_control,
            children=children,
        )
    else:
        mesh = LidMeshRepeating(
            path=calc_path,
            lid_thickness=lid_thickness,
            boundary=boundary,
            layout_width=calc_layout_width,
            shape_edges=4,
            aspect_ratio=calc_aspect_ratio,
            material_colour=material_colour,
            inner_control=inner_control,
            children=children,
        )

    # offset() is a 2-D op: it must run on the flat polygon before linear_extrude() lifts it to
    # 3-D, not after (calling offset() on an already-extruded solid silently yields nothing).
    border = shapes2d.polygon(calc_path).offset(radius=-boundary).linear_extrude(height=lid_thickness).color(
        material_colour
    ) - shapes2d.polygon(calc_path).offset(radius=-boundary - 0.02).linear_extrude(height=lid_thickness + 1).color(
        material_colour
    ).translate([0, 0, -0.5])

    bound = shapes2d.polygon(calc_path).offset(radius=-boundary).linear_extrude(height=lid_thickness).color(material_colour)
    return (mesh | border) & bound


def build_lid_overlays(
    *,
    lid_thickness: float,
    label_size: list[float] | None = None,
    size: list[float] | None = None,
    path: list[list[float]] | None = None,
    boundary: float = 10,
    layout_width: float | None = None,
    aspect_ratio: float | None = None,
    shape_child: PyOpenSCAD | None = None,
    shape_options: "ShapeObject | None" = None,
    dense: bool | None = None,
    dense_shape_edges: int | None = None,
    inner_control: "int | bool | None" = None,
    text_str: str | None = None,
    label_options: "LabelOptions | None" = None,
    label_full_height: bool | None = True,
    extra_children: list | None = None,
    material_colour: str | None = None,
) -> list:
    """The shared lid-overlay list: the pattern mesh + the label + any extras, in the
    order :func:`internal_build_lid` expects. This is the ONE place the pattern-mesh
    (:func:`LidMeshBasic`) and label (:func:`MakeLidLabel`) are built for a box lid -- every
    box type's lid pipeline feeds these overlays into ``internal_build_lid`` on top of its
    own base shell, instead of re-implementing the block in a per-box ``*LidWithLabel``.

    Provide ``size`` OR ``path`` for the mesh area; ``label_size`` is ``[width, length]``
    the label is fitted to. The dense/edges/inner-control layout is DERIVED from
    ``shape_options.shape_type`` (single source of truth), matching :meth:`Lid._pattern_layout`.
    """
    from shape_type import ShapeByType, ShapeNeedsInnerControl

    if material_colour is None:
        material_colour = default_material_colour

    piece = shape_child
    if piece is None and shape_options is not None:
        piece = ShapeByType(options=shape_options)
    piece = piece.color(material_colour) if piece is not None else shapes2d.square([10, 10]).color(material_colour)

    # Layout: explicit dense/edges/inner win (the *AndCustomShape call path already has them);
    # otherwise DERIVE from shape_options.shape_type (single source of truth); otherwise defaults.
    if dense is None and shape_options is not None:
        st = shape_options.shape_type
        dense, dense_shape_edges, inner_control = IsDenseShapeType(st), DenseShapeEdges(st), ShapeNeedsInnerControl(st)
    dense = bool(dense) if dense is not None else False
    dense_shape_edges = dense_shape_edges if dense_shape_edges is not None else 6
    inner_control = inner_control if inner_control is not None else False

    mesh = LidMeshBasic(
        lid_thickness=lid_thickness,
        boundary=boundary,
        layout_width=layout_width,
        size=size,
        path=path,
        aspect_ratio=aspect_ratio,
        dense=dense,
        dense_shape_edges=dense_shape_edges,
        material_colour=material_colour,
        inner_control=inner_control,
        children=piece,
    )
    overlays: list = [mesh]

    if text_str:
        assert label_size is not None, "build_lid_overlays: label_size is required when text_str is given"
        opts = copy.copy(label_options) if label_options is not None else LabelOptions()
        if label_full_height is not None:
            opts.full_height = label_full_height
        label = MakeLidLabel(size=label_size, lid_thickness=lid_thickness, text_str=text_str, options=opts)
        if label is not None:
            overlays.append(label)

    if extra_children:
        overlays.extend(extra_children)
    return overlays


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

    def mask(piece: PyOpenSCAD) -> PyOpenSCAD:
        native = piece.shape if isinstance(piece, shapes3d.Bosl2Solid) else piece
        # NATIVE chain: fill()/projection() are native builtins (no pybosl2 equivalent wired
        # here), so .offset() is the native method -- it takes r=, not pybosl2's radius=.
        return (
            fill(native.projection(cut=False))
            .offset(r=-size_spacing)
            .linear_extrude(height=lid_thickness + 1)
            .color("darkslategrey")
            .translate([0, 0, -0.5])
        )

    n = len(children)
    base = children[0]
    for i in range(1, n):
        base = base - mask(children[i])

    extras = None
    for i in range(1, n):
        piece = children[i]
        for j in range(i + 1, n):
            piece = piece - mask(children[j])
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


class Lid:
    """Lid mesh configuration and builder.

    Holds all lid pattern, label and shape parameters.  Call :meth:`build`
    to resolve the shape piece (via :func:`~shape_type.ShapeByType`) and
    create the actual lid mesh solid.

    Usage::

        lid = Lid(lid_thickness=2, size=[100, 50], boundary=10,
                  layout_width=10, dense=True,
                  shape_options=MakeShapeObject(shape_type=ShapeType.DENSE_HEX),
                  label=Label("Trains"))
        mesh = lid.build()
    """

    def __init__(
        self,
        *,
        lid_thickness: float,
        size: list[float] | None = None,
        path: list[list[float]] | None = None,
        boundary: float = 10,
        layout_width: float | None = None,
        aspect_ratio: float | None = None,
        dense: bool = False,
        dense_shape_edges: int = 6,
        material_colour: str | None = None,
        inner_control: int | bool = False,
        children: PyOpenSCAD | None = None,
        label: "Label | None" = None,
        shape_child: PyOpenSCAD | None = None,
        shape_options: "ShapeObject | None" = None,
        lid_rounding: float | None = None,
        extra_children: list | None = None,
        fingernail: "Fingernail | bool | None" = None,
    ) -> None:
        if material_colour is None:
            material_colour = default_material_colour
        self.lid_thickness = lid_thickness
        self.size = size
        self.path = path
        self.boundary = boundary
        self.layout_width = layout_width if layout_width is not None else default_lid_layout_width
        self.aspect_ratio = aspect_ratio if aspect_ratio is not None else default_lid_aspect_ratio
        self.dense = dense
        self.dense_shape_edges = dense_shape_edges
        self.material_colour = material_colour
        self.inner_control = inner_control
        self.children = children
        self.label = label
        self.shape_child = shape_child
        self.shape_options = shape_options
        self.lid_rounding = lid_rounding
        self.extra_children = extra_children
        # Accept a bool for back-compat (True -> an enabled Fingernail with defaulted sizes).
        if isinstance(fingernail, bool):
            fingernail = Fingernail(enabled=fingernail)
        self.fingernail = fingernail

    def build(self) -> PyOpenSCAD | None:
        """Resolve the shape piece and create the lid mesh solid.

        If :attr:`shape_child` or :attr:`shape_options` is set, the shape is
        resolved via :func:`~shape_type.ShapeByType` and tiled by :func:`LidMeshBasic`.
        Returns None if no shape could be resolved and neither is set.
        """
        piece = self.shape_child
        if piece is None and self.shape_options is not None:
            from shape_type import ShapeByType
            piece = ShapeByType(options=self.shape_options)
        if piece is None and self.children is None:
            return None
        if piece is not None:
            piece = piece.color(self.material_colour)

        dense, edges, inner = self._pattern_layout()
        # ONE mesh entry point (LidMeshBasic) -- the dense/repeating dispatch and the
        # border/bound clipping live there, not duplicated here.
        return LidMeshBasic(
            lid_thickness=self.lid_thickness,
            boundary=self.boundary,
            layout_width=self.layout_width,
            size=self.size,
            path=self.path,
            aspect_ratio=self.aspect_ratio,
            dense=dense,
            dense_shape_edges=edges,
            material_colour=self.material_colour,
            inner_control=inner,
            children=piece if piece is not None else self.children,
        )

    def _pattern_layout(self) -> tuple[bool, int, "int | bool"]:
        """The (dense, dense_shape_edges, inner_control) layout for the mesh.

        DERIVED from the pattern's shape type (the single source of truth) when a
        ``shape_options`` is given; otherwise the explicitly-set fields are used. This is
        the one place ShapeType -> layout mapping happens (was the drift-prone, never-called
        ``apply_shape_defaults`` + three parallel copies in the box lid functions)."""
        if self.shape_options is None:
            return self.dense, self.dense_shape_edges, self.inner_control
        from shape_type import ShapeNeedsInnerControl
        st = self.shape_options.shape_type
        return IsDenseShapeType(st), DenseShapeEdges(st), ShapeNeedsInnerControl(st)

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
        """Return the list of overlay children for this lid.

        Args:
            label_builder: optional callable that takes a :class:`~box_base.Label` and
                returns its geometry (e.g. :meth:`BoxBaseType.make_label`)
        """
        overlay_children: list = []

        fn = self.fingernail_cutout()
        if fn is not None:
            overlay_children.append(fn)

        if self.shape_child is not None or self.shape_options is not None:
            mesh = self.build()
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
