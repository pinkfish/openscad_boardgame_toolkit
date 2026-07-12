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

# LibFile: pysolidfive/joiners.py
#    Joining hardware: knuckle_hinge() (a port of BOSL2 hinges.scad's knuckle_hinge, for the
#    parameter subset this toolkit uses) and rabbit_clip() (a port of BOSL2 joiners.scad's
#    rabbit_clip). Neither had a BOSL2 *function* form, so the osuse() FFI never exposed
#    them -- every _bosl2.knuckle_hinge()/_bosl2.rabbit_clip() call site in the Python port
#    raised AttributeError; these are the first working implementations.
#
# FileGroup: pysolidfive

from __future__ import annotations

import math

import numpy as np

from .paths import (
    bezpath_points,
    circle_circle_tangents,
    line_normal,
    offset_polyline,
    path_tangents,
    path_to_bezpath,
)
from .shapes2d import PyShape2D, circle2d, polygon2d, rect2d, stroke2d
from .shapes3d import PyShape

UP = [0.0, 0.0, 1.0]


def _attach(shape: PyShape, size: list[float], center_off: list[float], anchor, spin: float, orient) -> PyShape:
    """BOSL2 attachable() emulation for a shape whose declared bounding box has dimensions
    `size` and geometric center `center_off`: translate the anchor point to the origin,
    spin around Z, then rotate UP toward `orient` -- the same order attachable() applies."""
    a = [int(v) for v in anchor]
    anchor_pt = [center_off[i] + a[i] * size[i] / 2 for i in range(3)]
    if any(anchor_pt):
        shape = shape.translate([-anchor_pt[0], -anchor_pt[1], -anchor_pt[2]])
    if spin:
        shape = shape.rotate([0, 0, spin])
    o = [float(v) for v in orient]
    olen = math.sqrt(sum(v * v for v in o))
    o = [v / olen for v in o]
    if o != UP:
        if o == [0.0, 0.0, -1.0]:
            shape = shape.rotate(180, [1, 0, 0])
        else:
            axis = [UP[1] * o[2] - UP[2] * o[1], UP[2] * o[0] - UP[0] * o[2], UP[0] * o[1] - UP[1] * o[0]]
            angle = math.degrees(math.acos(max(-1.0, min(1.0, o[2]))))
            shape = shape.rotate(angle, axis)
    return shape


def knuckle_hinge(
    length: float,
    segs: int,
    offset: float,
    inner: bool = False,
    arm_height: float = 0,
    arm_angle: float = 90,
    gap: float = 0.2,
    seg_ratio: float = 1,
    knuckle_diam: float = 4,
    pin_diam: float = 1.75,
    fill: bool = True,
    clear_top: bool = False,
    anchor=(0, 0, -1),
    spin: float = 0,
    orient=(0, 0, 1),
    res: int = 10,
) -> PyShape:
    """A knuckle hinge: alternating cylinder segments (with a pin hole) on an arm, mounted
    along the +X axis -- BOSL2 hinges.scad's knuckle_hinge, ported for the parameter subset
    this toolkit uses: arm_angle=90, arm_height=0, no end rounding, plain numeric pin, and
    no print-in-place cones. `inner=True` gives the segment set that meshes into the
    `inner=False` one. anchor/spin/orient follow BOSL2 attachable() semantics against the
    same declared bounding box the original uses.
    """
    assert arm_angle == 90 and arm_height == 0, "only the arm_angle=90/arm_height=0 variant is ported"
    assert isinstance(segs, int) and segs >= 2
    assert offset >= knuckle_diam / 2, "offset must be at least the knuckle radius"

    segs1 = math.ceil(segs / 2)
    segs2 = math.floor(segs / 2)
    seglen1 = gap + (length - (segs - 1) * gap) / (segs1 + segs2 * seg_ratio)
    seglen2 = gap + (length - (segs - 1) * gap) / (segs1 + segs2 * seg_ratio) * seg_ratio
    numsegs = segs2 if inner else segs1
    z_adjust = 0.0 if segs % 2 == 1 else (seglen1 / 2 if inner else seglen2 / 2)

    extra = 0.01
    kd = knuckle_diam
    # 2-D profile (see BOSL2 _knuckle_hinge_profile at arm_angle=90/arm_height=0): the
    # straight arm from x=-extra to the knuckle center at x=offset, plus the knuckle circle,
    # optionally cleared above y=0, minus the pin hole.
    arm = rect2d([offset + extra, kd], anchor=[-1, 0], res=res).translate([-extra, 0])
    profile: PyShape2D = arm | circle2d(d=kd, res=res).translate([offset, 0])
    if clear_top:
        profile = profile - rect2d([offset + kd + 1, kd + 1], anchor=[-1, -1], res=res).translate([-0.1, 0])
    if pin_diam and pin_diam > 0:
        profile = profile - circle2d(d=pin_diam, res=res).translate([offset, 0])

    seg_h = (seglen2 if inner else seglen1) - gap
    pitch = seglen1 + seglen2
    pieces = []
    for i in range(numsegs):
        z = (i - (numsegs - 1) / 2) * pitch
        pieces.append(profile.extrude(seg_h, center=True).translate([0, 0, z]))
    stack = pieces[0]
    for piece in pieces[1:]:
        stack = stack | piece

    # transform = down(offset) * yrot(-90) * zmove(z_adjust), rightmost applied first --
    # maps the extrusion axis onto X (the hinge line) and hangs the arm down to z=-offset.
    shape = stack.translate([0, 0, z_adjust]).rotate([0, -90, 0]).translate([0, 0, -offset])

    # attachable() declared box for arm_angle=90/arm_height=0.
    size = [length, kd, offset + kd / 2]
    center_off = [0.0, 0.0, -offset / 2 + kd / 4]
    return _attach(shape, size, center_off, anchor, spin, orient)


def rabbit_clip(
    type: str,
    length: float,
    width: float,
    snap: float,
    thickness: float,
    depth: float,
    compression: float = 0.1,
    clearance: float = 0.1,
    lock: bool = False,
    lock_clearance: float = 0,
    splinesteps: int = 8,
    anchor=None,
    orient=None,
    spin: float = 0,
    res: int = 10,
) -> PyShape:
    """A rabbit-ear snap clip ("pin") or its matching cavity ("socket") -- a port of BOSL2
    joiners.scad's rabbit_clip (same path construction, bezier smoothing, and attachable
    anchoring; the "double" type isn't ported since nothing here uses it).
    """
    assert type in ("pin", "male", "socket", "female"), f"unsupported rabbit_clip type {type!r}"
    is_pin = type in ("pin", "male")
    extra = 0.02
    clearance = 0 if is_pin else clearance
    compression = compression if is_pin else 0
    orient = orient if orient is not None else (UP if is_pin else [0, 0, -1])
    anchor = anchor if anchor is not None else (0, 0, -1)

    earwidth = 2 * thickness + snap
    point_length = earwidth / 2.15
    scaled_len = length - 0.5 * (earwidth * snap + point_length * length) / math.sqrt(snap**2 + (length / 2) ** 2)
    bottom_pt = np.array([0.0, max(scaled_len * 0.15 + thickness, 2 * thickness)])
    ctr = np.array([width / 2, scaled_len]) + line_normal([width / 2 - snap, scaled_len / 2], [width / 2, scaled_len]) * (earwidth / 2)
    inside_pt = circle_circle_tangents(0, bottom_pt, earwidth / 2, ctr)[0][1]
    sidepath = np.array([
        [width / 2, 0.0],
        [width / 2 - snap, scaled_len / 2],
        [width / 2 + (compression if is_pin else 0), scaled_len],
        ctr - line_normal([width / 2, scaled_len], inside_pt) * point_length,
        inside_pt,
    ])
    fullpath = np.vstack([sidepath, [bottom_pt], sidepath[::-1] * [-1.0, 1.0]])
    assert fullpath[4][1] < fullpath[3][1], "Pin is too wide for its length"

    fulltangent = path_tangents(fullpath, closed=False, uniform=False)
    # Force vertical tangents at the outer edges of the clip to avoid overshoot.
    fulltangent[2] = [0.0, 1.0]
    fulltangent[8] = [0.0, -1.0]

    subset = list(range(11)) if is_pin else [0, 1, 2, 3, 7, 8, 9, 10]
    tangent = fulltangent[subset]
    path = fullpath[subset]

    pin_smooth = [0.075, 0.075, 0.15, 0.12, 0.06]
    if is_pin:
        smoothing = pin_smooth + list(reversed(pin_smooth))
    else:
        side_smooth = pin_smooth[:3]
        smoothing = side_smooth + [0.04] + list(reversed(side_smooth))
    bez = path_to_bezpath(path, closed=False, relsize=smoothing, tangents=tangent)
    rounded = bezpath_points(bez, splinesteps=splinesteps)
    mins = rounded.min(axis=0)
    maxs = rounded.max(axis=0)
    bounds_dx, bounds_dy = float(maxs[0] - mins[0]), float(maxs[1] - mins[1])

    if is_pin:
        # offset_stroke(rounded, width=[thickness, 0]): a ribbon between the path and its
        # offset `thickness` to the LEFT of travel -- built as a stroke2d along the midline.
        midline = offset_polyline(rounded, thickness / 2)
        profile: PyShape2D = stroke2d(midline, width=thickness, res=res)
    else:
        withclearance = offset_polyline(rounded, -clearance)
        # np.vstack, NOT `list + ndarray`: the latter silently BROADCASTS (adds the closure
        # point onto every row) instead of concatenating.
        finalpath = np.vstack(
            [[[withclearance[0][0], -extra]], withclearance, [[-withclearance[0][0], -extra]]]
        )
        profile = polygon2d(finalpath, res=res)

    if lock:
        lock_poly = np.array([
            [sidepath[1][0] - thickness / 10, sidepath[1][1] + lock_clearance],
            [sidepath[2][0] - thickness * 0.75, sidepath[2][1]],
            [sidepath[2][0], sidepath[2][1]],
            [sidepath[2][0], sidepath[1][1] + lock_clearance],
        ])
        lock_shape = polygon2d(lock_poly + [clearance, 0.0], res=res)
        # lock=True mirrors the lock tab to both sides (BOSL2 xflip_copy()).
        profile = profile | lock_shape | polygon2d(lock_poly * [-1.0, 1.0] - [clearance, 0.0], res=res)

    solid = profile.extrude(depth, center=True)
    # xrot(90) * translate([0, -dy/2, -depth/2]) on the pre-extruded profile centers the
    # declared box at the origin; extrude(center=True) already centers Z, so only the
    # profile's y needs centering before the flip.
    solid = solid.translate([0, -bounds_dy / 2, 0]).rotate([90, 0, 0])

    size = [bounds_dx, depth, bounds_dy]
    return _attach(solid, size, [0.0, 0.0, 0.0], anchor, spin, orient)
