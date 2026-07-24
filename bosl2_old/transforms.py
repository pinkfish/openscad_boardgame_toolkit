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

# LibFile: bosl2/transforms.py
#    Pure-Python port of the affine-matrix machinery from BOSL2's
#    transforms.scad (reorient()/apply(), plus the rot_from_to()/
#    axis_angle_matrix() helpers they build on) and polar_to_xy() from
#    coords.scad. No osuse()/BOSL2 runtime dependency.
#
#    The point-list transform operations themselves (move/rot/right/left/
#    back/forward/mirror/yflip) are NOT here -- they are methods on the
#    Path object (bosl2/paths.py) and on Bosl2Solid (bosl2/shapes3d.py).
#    What remains is the matrix side used for cuboid reorientation and
#    anchoring, which feeds PythonSCAD's .multmatrix().
#
# FileSummary: Affine-matrix reorient/apply and polar_to_xy (BOSL2 transforms.scad, coords.scad).
# FileGroup: BOSL2

import math

import numpy as np


def polar_to_xy(r: float, angle: float) -> list[float]:
    """Convert polar coordinates (radius, angle in degrees) to a 2-D [x, y] point."""
    rad = math.radians(angle)
    return [r * math.cos(rad), r * math.sin(rad)]


def _unit(v) -> np.ndarray:
    arr = np.asarray(v, dtype=float)
    n = float(np.linalg.norm(arr))
    return arr / n if n else arr


def rot_from_to(a, b) -> "tuple[float, np.ndarray]":
    """(angle_degrees, axis) rotating direction *a* onto direction *b*.

    Matches BOSL2's ``rot(from=, to=)`` axis choice, including the antiparallel case (180
    degrees about a perpendicular axis).
    """
    au, bu = _unit(a), _unit(b)
    dot = float(np.clip(au @ bu, -1.0, 1.0))
    if dot > 1 - 1e-9:
        return 0.0, np.array([0.0, 0.0, 1.0])
    if dot < -1 + 1e-9:
        axis = np.cross(au, [1.0, 0.0, 0.0])
        if float(np.linalg.norm(axis)) < 1e-9:
            axis = np.cross(au, [0.0, 1.0, 0.0])
        return 180.0, _unit(axis)
    return math.degrees(math.acos(dot)), _unit(np.cross(au, bu))


def axis_angle_matrix(angle: float, axis) -> np.ndarray:
    """3x3 rotation matrix for *angle* degrees about *axis* (Rodrigues' rotation formula)."""
    rad = math.radians(angle)
    x, y, z = _unit(axis)
    c, s = math.cos(rad), math.sin(rad)
    cc = 1.0 - c
    return np.array(
        [
            [x * x * cc + c, x * y * cc - z * s, x * z * cc + y * s],
            [y * x * cc + z * s, y * y * cc + c, y * z * cc - x * s],
            [z * x * cc - y * s, z * y * cc + x * s, z * z * cc + c],
        ]
    )


def rot_about_axis(angle: float, axis, cp=(0.0, 0.0, 0.0)) -> np.ndarray:
    """4x4 matrix rotating *angle* degrees about the line through *cp* in direction *axis*.

    The 4x4 form of BOSL2's ``rot(a=, v=, cp=)``: translate *cp* to the origin, rotate, translate
    back."""
    m = np.eye(4)
    m[:3, :3] = axis_angle_matrix(angle, axis)
    cpv = np.asarray(cp, dtype=float)
    m[:3, 3] = cpv - m[:3, :3] @ cpv
    return m


def rot_inverse(t) -> np.ndarray:
    """Inverse of a rigid 4x4 transform (BOSL2 rot_inverse()): transpose the rotation, un-translate."""
    t = np.asarray(t, dtype=float)
    r = t[:3, :3]
    inv = np.eye(4)
    inv[:3, :3] = r.T
    inv[:3, 3] = -r.T @ t[:3, 3]
    return inv


def rot_decode(m, long: bool = False) -> list:
    """Decode a rigid 4x4 transform into its screw motion (BOSL2 rot_decode()).

    Returns ``[angle_degrees, axis, cp, translation_along_axis]`` -- rotating by *angle* about the
    line through *cp* in direction *axis* then translating along the axis reproduces *m*. *axis*,
    *cp* and the axial translation are returned as :class:`~bosl2.constants.Vec3`. With *long*, the
    complementary (>180 degree) rotation about the reversed axis is chosen."""
    from bosl2.constants import Vec3  # local: constants is lightweight, avoid a load-order cycle

    m = np.asarray(m, dtype=float)
    r = m[:3, :3]
    translation = m[:3, 3]
    largest = int(np.argmax([r[0, 0], r[1, 1], r[2, 2]]))
    axis_matrix = r + r.T - (np.trace(r) - 1) * np.eye(3)
    q_im = axis_matrix[largest]
    q_re = r[(largest + 2) % 3][(largest + 1) % 3] - r[(largest + 1) % 3][(largest + 2) % 3]
    c_sin = float(np.linalg.norm(q_im))
    c_cos = abs(float(q_re))
    if c_sin < 1e-12:
        return [0.0, Vec3([0.0, 0.0, 1.0]), Vec3([0.0, 0.0, 0.0]), Vec3([float(v) for v in translation])]
    angle = math.degrees(2 * math.atan2(c_sin, c_cos))
    axis = (1.0 if q_re >= 0 else -1.0) * q_im / c_sin
    tproj = translation - (translation @ axis) * axis
    cp = (tproj + np.cross(axis, tproj) * c_cos / c_sin) / 2
    axial = (translation @ axis) * axis
    return [
        360 - angle if long else angle,
        Vec3([float(v) for v in (-axis if long else axis)]),
        Vec3([float(v) for v in cp]),
        Vec3([float(v) for v in axial]),
    ]


def reorient(anchor=None, spin: float = 0, orient=None, size=None) -> list[list[float]]:
    """The 4x4 matrix that reorients a cuboid of *size* onto *anchor*/*spin*/*orient*.

    The Python equivalent of BOSL2's ``reorient(anchor, spin, orient, size)``, for feeding
    PythonSCAD's ``.multmatrix()``. Composed as
    ``R(UP -> orient) * Zrot(spin) * Translate(-anchor * size / 2)``; verified to match
    BOSL2's own output exactly across every anchor/orient/spin/size combination the toolkit
    uses (see tests/test_bosl2_reorient.py).

    Returns plain nested lists, not an ndarray: the result feeds straight into the native
    ``multmatrix()``, which rejects numpy arrays ("Error during parsing multmatrix(object,
    vec16)").

    Usage::

        tmat = reorient(anchor=CENTER, spin=90, orient=LEFT, size=[10, 20, 30])
        shape.multmatrix(tmat)

    Args:
        anchor: BOSL2 anchor vector (default CENTER)
        spin:   rotation about Z in degrees, applied after the anchor move (default 0)
        orient: direction the shape's UP is rotated onto (default UP)
        size:   [x, y, z] size the anchor is resolved against (default [0, 0, 0])
    """
    anchor = (0.0, 0.0, 0.0) if anchor is None else anchor
    orient = (0.0, 0.0, 1.0) if orient is None else orient
    size = (0.0, 0.0, 0.0) if size is None else size

    angle, axis = rot_from_to((0.0, 0.0, 1.0), orient)
    rot_m = np.eye(4)
    rot_m[:3, :3] = axis_angle_matrix(angle, axis)

    rad = math.radians(spin)
    zrot = np.eye(4)
    zrot[:2, :2] = [[math.cos(rad), -math.sin(rad)], [math.sin(rad), math.cos(rad)]]

    move_m = np.eye(4)
    move_m[:3, 3] = [-float(anchor[i]) * float(size[i]) / 2 for i in range(3)]

    return (rot_m @ zrot @ move_m).tolist()


def apply(transform, points) -> list:
    """Apply a 4x4 (or 3x3, 2-D) *transform* matrix to every point in *points*.

    The Python equivalent of BOSL2's ``apply()``. Returns plain nested lists so the result can
    cross the native FFI boundary.

    Usage::

        apply(reorient(anchor=CENTER, orient=LEFT, size=[1, 1, 1]), [[5, 0, 0], [-5, 0, 0]])
    """
    m = np.asarray(transform, dtype=float)
    pts = np.asarray(points, dtype=float)
    single = pts.ndim == 1
    if single:
        pts = pts[None, :]
    dim = m.shape[0] - 1
    homogeneous = np.hstack([pts[:, :dim], np.ones((len(pts), 1))])
    out = (m @ homogeneous.T).T
    w = out[:, dim : dim + 1]
    out = out[:, :dim] / np.where(w == 0, 1.0, w)
    return out[0].tolist() if single else out.tolist()
