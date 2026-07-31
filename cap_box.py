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

# LibFile: cap_box.py
#    Cap-style box and lid generators.
#
# FileSummary: Cap box pieces for the cap boxes.
# FileGroup: Boxes

from __future__ import annotations
import copy

from pythonscad import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openscad import PyOpenSCAD  # noqa: F401
from base_bgtk import *
from pybosl2 import shapes3d
from pybosl2 import transforms
from pybosl2 import masking
from lids_base import (
    default_lid_catch_type,
    internal_build_lid,
    IsDenseShapeType,
    DenseShapeEdges,
    MakeLidLabel,
    LidMeshBasic,
    build_lid_overlays,
)
from labels import MakeLabelOptions, LabelOptions
from shape_type import MakeShapeObject, ShapeObject, ShapeByType, ShapeNeedsInnerControl
from box_base import BoxBaseType, BoxSpec
from dataclasses import dataclass

from typing import Callable


# ---------------------------------------------------------------------------
# Helper functions (pure Python equivalents)
# ---------------------------------------------------------------------------


def CapBoxDefaultCapHeight(height: float) -> float:
    """Default cap height for a box of given *height*."""
    return min(10, height / 2)


def CapBoxDefaultFingerHoldHeight(height: float) -> float:
    """Default finger hold height for a box of given *height*."""
    return min(5, height / 4)


def CapBoxDefaultFingerHoldLen(width: float, length: float) -> float:
    """Default finger hold length for a box of given *width* and *length*."""
    return min(width, length) / 5


def CapBoxDefaultLidWallThickness(wall_thickness: float) -> float:
    """Default lid wall thickness derived from *wall_thickness*."""
    return wall_thickness / 2


def CapBoxDefaultLidFingerHoldRounding(cap_height: float) -> float:
    """Default rounding on the lid finger hold."""
    return min(3, cap_height / 2)


def _resolve_child(c: PyOpenSCAD, inner_width: float, inner_length: float, inner_height: float) -> PyOpenSCAD:
    """Resolve a child entry: a plain solid, or a callable(inner_width, inner_length, inner_height)."""
    return c(inner_width, inner_length, inner_height) if callable(c) else c


def _catch_bump(wall_thickness: float, radius: float, anchor_dir: list[int]) -> PyOpenSCAD:
    """A rounded catch nub: a sphere clipped to a small cube on one face."""
    box = wall_thickness * 6 / 4
    # Bosl2Solid on the left so its __and__ (not sphere()'s native __and__) handles the mixed operand.
    return shapes3d.cuboid([box, box, box], anchor=anchor_dir) & sphere(r=radius)


# ---------------------------------------------------------------------------
# Box and lid modules
# ---------------------------------------------------------------------------


@dataclass
class CapBoxOptions:
    """Cap-box-specific options; pass via ``BoxSpec(type_options=MakeCapBoxOptions(...))``."""

    cap_height: float | None = None                 # None -> min(10, height/2)
    catch: CatchType = CatchType.BUMPS_SHORT        # snap-fit style (BUMPS_* / SHORT/LONG/ALL / NONE)
    finger_holds: bool = True                       # grip scoops so you can lift the cap


def MakeCapBoxOptions(**kwargs) -> CapBoxOptions:
    return CapBoxOptions(**kwargs)


class CapBox(BoxBaseType):
    """A box with a cap lid on the new box system: the cap slides down over the box's
    top rim. The top ``cap_height`` mm of the box wall is stepped in by the cap wall
    thickness so the cap sits flush. The cap has finger-hold scoops and a snap-fit
    catch (bumps or wedges) that clicks into matching recesses in the box rim.

    Cap-box options go through :func:`MakeCapBoxOptions`
    (``BoxSpec(type_options=MakeCapBoxOptions(cap_height=3, catch=CatchType.LONG))``);
    a bare number in ``type_options`` is treated as ``cap_height`` (back-compat). Like
    any lidded box it is hollow when empty (``BoxSpec(hollow=...)`` / ``contents=...``).

    Usage::

        from box_base import BoxSpec
        from cap_box import CapBox, MakeCapBoxOptions

        box = CapBox(BoxSpec(size=[100, 50, 20], label="cap"))
        box.make_box().show()
        box.make_lid().show()
    """

    @property
    def inner_height(self) -> float:
        # The cap covers the outside of the top rim; the interior runs floor-to-top.
        return self.height - self.floor_thickness

    def _opts(self) -> CapBoxOptions:
        o = self._spec.type_options
        if isinstance(o, CapBoxOptions):
            return o
        if isinstance(o, (int, float)) and o:
            return CapBoxOptions(cap_height=float(o))
        return CapBoxOptions()

    def _cap_height(self) -> float:
        h = self._opts().cap_height
        return float(h) if h else CapBoxDefaultCapHeight(self.height)

    def _lid_wall(self) -> float:
        return CapBoxDefaultLidWallThickness(self.wall_thickness)

    def _rim_frame(self, height: float, extra: float = 0.0):
        """A wall-thick frame (outer minus inner) of the given height -- the cap rim."""
        w, l, lw = self.width, self.length, self._lid_wall()
        outer = shapes3d.cuboid([w, l, height], anchor=BOTTOM + FRONT + LEFT)
        inner = shapes3d.cuboid(
            [w - lw * 2, l - lw * 2, height + 1], anchor=BOTTOM + FRONT + LEFT
        ).translate([lw, lw, -0.5])
        return outer - inner

    def _finger_hold_height(self) -> float:
        return CapBoxDefaultFingerHoldHeight(self.height)

    def _finger_hold_cut(self):
        """The cap finger-hold cutter: a wall-band recess below the rim with a rounded
        scoop in the middle of each wall so you can grip and lift the cap off. Ported
        from MakeBoxWithCapLid's finger cutouts."""
        w, l = self.width, self.length
        lw = self._lid_wall()
        sp = self.size_spacing
        cap_h = self._cap_height()
        fh_h = self._finger_hold_height()
        fh_len = CapBoxDefaultFingerHoldLen(w, l)
        fh_round = CapBoxDefaultLidFingerHoldRounding(cap_h)
        wt = self.wall_thickness

        # Outer wall band minus the inner keep-away -> the reduced-wall band.
        outer = shapes3d.cuboid([w + sp * 2, l + sp * 2, fh_h + 1], anchor=BOTTOM + FRONT + LEFT).translate([-sp, -sp, 0])
        inner = shapes3d.cuboid(
            [w - lw * 2 - sp * 2, l - lw * 2 - sp * 2, fh_h + 2], anchor=BOTTOM + FRONT + LEFT,
            rounding=wt / 2, edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK],
        ).translate([lw + sp, lw + sp, 0])
        cut = outer - inner

        # Scoops in the middle of each wall (leave fh_len of wall at each end).
        hole_a = shapes3d.cuboid([w - fh_len * 2 + 0.1, wt + 1, fh_h + 0.2], rounding=fh_round,
                                 edges=[TOP + LEFT, TOP + RIGHT], anchor=BOTTOM + LEFT + FRONT, fn=32).translate([fh_len, 0, -0.2])
        hole_b = shapes3d.cuboid([w - fh_len * 2 + 0.1, wt + 1, fh_h + 0.2], rounding=fh_round,
                                 edges=[TOP + LEFT, TOP + RIGHT], anchor=BOTTOM + LEFT + FRONT, fn=32).translate([fh_len, l - lw - sp, -0.2])
        hole_c = shapes3d.cuboid([wt + 1, l - fh_len * 2 + 0.1, fh_h + 0.2], rounding=fh_round,
                                 edges=[TOP + FRONT, TOP + BACK], anchor=BOTTOM + LEFT + FRONT, fn=32).translate([0, fh_len, -0.2])
        hole_d = shapes3d.cuboid([wt + 1, l - fh_len * 2 + 0.1, fh_h + 0.2], rounding=fh_round,
                                 edges=[TOP + FRONT, TOP + BACK], anchor=BOTTOM + LEFT + FRONT, fn=32).translate([w - lw - sp, fh_len, -0.2])
        cut = cut - hole_a - hole_b - hole_c - hole_d
        return cut.translate([0, 0, self.height - cap_h - fh_h])

    def _bump_catches(self, catch: CatchType, radius: float):
        """Two rounded catch nubs on each of the chosen walls, at z = wall_thickness.
        BUMPS_SHORT puts them on the shorter walls, BUMPS_LONG on the longer."""
        w, l, wt = self.width, self.length, self.wall_thickness
        catches = None

        def add(p):
            nonlocal catches
            catches = p if catches is None else catches | p

        front_back = (catch == CatchType.BUMPS_SHORT and w <= l) or (catch == CatchType.BUMPS_LONG and w > l)
        left_right = (catch == CatchType.BUMPS_SHORT and l < w) or (catch == CatchType.BUMPS_LONG and l > w)
        if front_back:
            off = w - wt * 2
            for frac in (6 / 8, 2 / 8):
                x = off * frac + wt
                pair = _catch_bump(wt, radius, FRONT) | _catch_bump(wt, radius, BACK).translate([0, l, 0])
                add(pair.translate([x, 0, wt]))
        if left_right:
            off = l - wt * 2
            for frac in (6 / 8, 2 / 8):
                y = off * frac + wt
                pair = _catch_bump(wt, radius, LEFT) | _catch_bump(wt, radius, RIGHT).translate([w, 0, 0])
                add(pair.translate([0, y, wt]))
        return catches

    def _wedge_catches(self, catch: CatchType, depth: float):
        """A sloped wedge along the middle of each chosen wall, at z=0 (relative to the
        rim). SHORT = shorter walls, LONG = longer, ALL = every wall. The box subtracts
        these (recesses); the cap adds slightly-shallower ones (protrusions)."""
        w, l, wt = self.width, self.length, self.wall_thickness
        catches = None

        def add(p):
            nonlocal catches
            catches = p if catches is None else catches | p

        front_back = catch == CatchType.ALL or (catch == CatchType.SHORT and w < l) or (catch == CatchType.LONG and w > l)
        left_right = catch == CatchType.ALL or (catch == CatchType.SHORT and l < w) or (catch == CatchType.LONG and l > w)
        if front_back:
            cw = w - wt * 2
            add(shapes3d.wedge([cw / 2, wt, depth]).translate([cw / 4 + wt, 0, 0]))
            add(shapes3d.wedge([cw / 2, wt, depth]).rotate([0, 0, 180]).translate([cw * 3 / 4 + wt, l, 0]))
        if left_right:
            cl = l - wt * 2
            add(shapes3d.wedge([cl / 2, wt, depth]).rotate([0, 0, 90]).translate([w, cl / 4 + wt, 0]))
            add(shapes3d.wedge([cl / 2, wt, depth]).rotate([0, 0, 270]).translate([0, cl * 3 / 4 + wt, 0]))
        return catches

    def _catches(self, is_lid: bool):
        """The catch solid for the box (is_lid=False -> recesses) or cap (is_lid=True ->
        matching, slightly smaller protrusions), placed at z=0 relative to the rim."""
        catch = self._opts().catch
        wt, sp = self.wall_thickness, self.size_spacing
        if catch in (CatchType.BUMPS_SHORT, CatchType.BUMPS_LONG):
            return self._bump_catches(catch, wt * 3 / 4 if is_lid else wt * 5 / 6 + sp)
        if catch in (CatchType.SHORT, CatchType.LONG, CatchType.ALL):
            return self._wedge_catches(catch, wt * 5 / 8 if is_lid else wt)
        return None  # CatchType.NONE

    def _build_box_body(self) -> "Bosl2Solid":
        cap_h = self._cap_height()
        body = shapes3d.cuboid(
            [self.width, self.length, self.height],
            anchor=BOTTOM + FRONT + LEFT,
            rounding=self.wall_thickness / 2,
            edges=[BOT, LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK],
        )
        # Step the top cap_height of the outer wall in by the cap wall thickness.
        body = body - self._rim_frame(cap_h + 0.1).translate([0, 0, self.height - cap_h])
        if self._opts().finger_holds:
            body = body - self._finger_hold_cut()   # grip scoops
        recesses = self._catches(is_lid=False)       # catch recesses in the rim
        if recesses is not None:
            body = body - recesses.translate([0, 0, self.height - cap_h])
        return body.color(self.material_colour)

    def create_lid(self, lid=None) -> "Bosl2Solid":
        """Build the cap: a wall frame that fits over the box's top rim, closed by a
        top plate, with the matching catch protrusions. When the lid carries a label /
        shape pattern / fingernail, the top plate is the decorated flat-lid slab
        (see :meth:`BoxBaseType._decorated_flat_lid`); otherwise it is a plain rounded plate."""
        cap_h = self._cap_height()
        walls = self._rim_frame(cap_h)
        slab, slab_lt = self._decorated_flat_lid(lid, [self.width, self.length])
        if slab is None:
            top = shapes3d.cuboid(
                [self.width, self.length, self.lid_thickness],
                anchor=BOTTOM + FRONT + LEFT,
                rounding=self.wall_thickness / 2,
                edges=[TOP, LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK],
            ).translate([0, 0, cap_h])
        else:
            top = slab.translate([0, 0, cap_h])
        cap = walls | top
        catches = self._catches(is_lid=True)   # protrusions at the cap wall bottom
        if catches is not None:
            cap = cap | catches
        return cap.color(self.material_colour)
