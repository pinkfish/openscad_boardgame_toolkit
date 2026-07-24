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

# LibFile: bosl2/threading.py
#    Pure-Python port of the core of BOSL2's threading.scad: screw threads built by sweeping a 2-D
#    thread profile helically (via the toolkit's :func:`~bosl2.skin.spiral_sweep`) and unioning a
#    core cylinder. The :class:`Threading` class exposes the thread generators as methods:
#    ``threaded_rod`` (ISO/UTS), ``trapezoidal_threaded_rod``, ``acme_threaded_rod``,
#    ``square_threaded_rod``, ``buttress_threaded_rod``, the matching ``*_nut`` builders,
#    ``generic_threaded_rod`` / ``generic_threaded_nut``, and ``thread_helix``.
#
#    The thread *profiles* are ported verbatim from BOSL2 (checked in tests/test_threading.py) and
#    the resulting geometry is verified against a real-app BOSL2 render (matching major/minor
#    diameter, length, thread pitch, and watertightness). This is a clean, geometrically-correct
#    port; the elaborate BOSL2 refinements -- blunt-start / lead-in tapers, teardrop threads, and
#    the bevel machinery -- are NOT ported (a follow-up), so ends are cut flush.
#
# FileSummary: Screw threading: threaded rods and nuts (ISO/trapezoidal/acme/square/buttress).
# FileGroup: BOSL2

from __future__ import annotations

from collections.abc import Sequence
import math

__all__ = ["Threading"]


# ---------------------------------------------------------------------------
# Section: thread profiles (in pitch units: x in [-1/2, 1/2], y the depth fraction)
# ---------------------------------------------------------------------------


def _iso_profile():
    depth = math.cos(math.radians(30)) * 5 / 8
    cw = 1 / 8
    return [[-depth / math.sqrt(3) - cw / 2, -depth], [-cw / 2, 0], [cw / 2, 0],
            [depth / math.sqrt(3) + cw / 2, -depth]]


def _trapezoidal_profile(pitch, thread_angle: float = 30, thread_depth=None):
    depth = thread_depth if thread_depth is not None else pitch / 2
    pa_delta = 0.5 * depth * math.tan(math.radians(thread_angle / 2)) / pitch
    assert pa_delta <= 0.25, "trapezoidal thread geometry is impossible (angle/depth too large)."
    rr1 = -depth / pitch
    z1, z2 = 0.25 - pa_delta, 0.25 + pa_delta
    return [[-z2, rr1], [-z1, 0], [z1, 0], [z2, rr1]]


def _buttress_profile():
    return [[-1 / 2, -0.77], [-7 / 16, -0.75], [5 / 16, 0], [7 / 16, 0], [7 / 16, -0.75], [1 / 2, -0.77]]


# ---------------------------------------------------------------------------
# Section: geometry
# ---------------------------------------------------------------------------


def _quantup(x, n):
    return int(math.ceil(x / n) * n)


def _thread_grid(profile, pitch, r, l, starts, left_handed, sides):
    """One angular sector (360/starts) of the thread surface as a column grid for vnf_vertex_array.

    Each column is a vertical stack of vertices for one angle: bottom axis point, the thread profile
    repeated up every turn, and the top axis point. Sweeping the columns around builds the whole
    rod (core + helical thread) as one closed, manifold polyhedron -- no CSG union of the thread
    with a coaxial core (which Manifold cannot do cleanly)."""
    prof = [[float(x), float(y)] for x, y in profile]
    start_steps = sides // starts
    direction = -1 if left_handed else 1
    len1, len2 = -l / 2 - pitch, l / 2 + pitch
    turns1 = int(math.floor(len1 / pitch)) - 1
    turns2 = int(math.ceil(len2 / pitch)) + 1
    grid = []
    for step in range(start_steps + 1):
        ang = math.radians(360 * step / sides * direction)
        dz = step / start_steps
        ca, sa = math.cos(ang), math.sin(ang)
        col = [[0.0, 0.0, len1]]
        for turn in range(turns1, turns2 + 1):
            for px, py in prof:
                z = max(len1, min(len2, (px + turn + dz) * pitch))
                rad = r + py * pitch
                col.append([rad * ca, rad * sa, z])
        col.append([0.0, 0.0, len2])
        grid.append(col)
    return grid


def _rot_z(pts, deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return [[x * c - y * s, x * s + y * c, z] for x, y, z in pts]


def _rod_solid(d, l, pitch, profile, starts=1, left_handed=False, _fn=None, _fa=None, _fs=None):
    """The external threaded-rod solid, built as a direct manifold polyhedron, trimmed to length.

    Each of the *starts* thread starts is one angular sector's vertex-array surface; the sectors are
    merged at the VNF level (not by CSG union, which Manifold cannot do on coaxial helical solids)
    into one polyhedron, then trimmed to length with an intersection."""
    from bosl2.shapes3d import cyl, Bosl2Solid
    from bosl2.shapes2d import _frag_count
    from bosl2.vnf import VNF

    r = d / 2
    sides = _quantup(_frag_count(r, _fn, _fa, _fs), starts)
    verts, faces = [], []
    for k in range(starts):
        grid = _thread_grid(profile, pitch, r, l, starts, left_handed, sides)
        vnf = VNF.vertex_array(grid, col_wrap=False, style="convex")
        rv = _rot_z(list(vnf.vertices), k * 360 / starts) if starts > 1 else list(vnf.vertices)
        off = len(verts)
        verts += [list(v) for v in rv]
        faces += [[i + off for i in f] for f in vnf.faces]
    thread = Bosl2Solid(VNF(verts, faces).polyhedron())
    return thread & cyl(h=l, r=r + 1, _fn=_fn, _fa=_fa, _fs=_fs)


def _profile_depth_abs(profile, pitch):
    ys = [float(p[1]) for p in profile]
    return (max(ys) - min(ys)) * pitch


def _nut_solid(nutwidth, idia, h, pitch, profile, shape="hex", starts=1, left_handed=False,
               slop=0.0, _fn=None, _fa=None, _fs=None):
    """A nut: a hex/square body with a threaded hole cut by a matching thread 'tap'."""
    from bosl2.shapes3d import regular_prism, cuboid

    if shape == "hex":
        body = regular_prism(6, h=h, id=nutwidth)
    elif shape == "square":
        body = cuboid([nutwidth, nutwidth, h])
    else:
        raise AssertionError('nut shape must be "hex" or "square".')
    if pitch == 0:
        from bosl2.shapes3d import cyl
        return body - cyl(h=h + 2, r=idia / 2 + slop, _fn=_fn, _fa=_fa, _fs=_fs)
    depth_abs = _profile_depth_abs(profile, pitch)
    tap = _rod_solid(idia + 2 * depth_abs + 2 * slop, h + 2 * pitch, pitch, profile,
                     starts=starts, left_handed=left_handed, _fn=_fn, _fa=_fa, _fs=_fs)
    return body - tap


# ---------------------------------------------------------------------------
# Section: Threading class
# ---------------------------------------------------------------------------


class Threading:
    """Screw-thread generators (BOSL2 threading.scad). Every method returns a
    :class:`~bosl2.shapes3d.Bosl2Solid`; call them on the class, e.g. ``Threading.threaded_rod(...)``.

    A *rod* is a threaded cylinder; a *nut* is a hex/square block with a matching threaded hole
    (cut by a thread 'tap', with *slop* clearance). *pitch* is the axial distance between threads,
    *starts* the number of thread starts, and *left_handed* flips the helix.
    """

    # -- generic ---------------------------------------------------------------------------

    @staticmethod
    def generic_threaded_rod(d, l, pitch, profile, starts=1, left_handed=False,
                             _fn=None, _fa=None, _fs=None):
        """A threaded rod from an explicit 2-D thread *profile* (x in [-1/2, 1/2], y the depth
        fraction, both in pitch units) -- the core every other rod builds on (BOSL2 generic_threaded_rod())."""
        assert pitch > 0 and l > 0 and d > 0, "generic_threaded_rod(): d, l and pitch must be positive."
        return _rod_solid(d, l, pitch, profile, starts, left_handed, _fn, _fa, _fs)

    @staticmethod
    def generic_threaded_nut(nutwidth, id, h, pitch, profile, shape="hex", starts=1,
                             left_handed=False, slop=0.0, _fn=None, _fa=None, _fs=None):
        """A nut from an explicit thread *profile* (BOSL2 generic_threaded_nut())."""
        return _nut_solid(nutwidth, id, h, pitch, profile, shape, starts, left_handed, slop, _fn, _fa, _fs)

    # -- ISO / UTS -------------------------------------------------------------------------

    @staticmethod
    def threaded_rod(d, l, pitch, starts=1, left_handed=False, _fn=None, _fa=None, _fs=None):
        """An ISO (metric) / UTS (imperial) 60-degree triangular threaded rod (BOSL2 threaded_rod())."""
        return _rod_solid(d, l, pitch, _iso_profile(), starts, left_handed, _fn, _fa, _fs)

    @staticmethod
    def threaded_nut(nutwidth, id, h, pitch, shape="hex", starts=1, left_handed=False, slop=0.0,
                     _fn=None, _fa=None, _fs=None):
        """A hex/square nut for an ISO/UTS threaded rod (BOSL2 threaded_nut())."""
        return _nut_solid(nutwidth, id, h, pitch, _iso_profile(), shape, starts, left_handed, slop, _fn, _fa, _fs)

    # -- trapezoidal / metric trapezoidal --------------------------------------------------

    @staticmethod
    def trapezoidal_threaded_rod(d, l, pitch, thread_angle=30, thread_depth=None, starts=1,
                                 left_handed=False, _fn=None, _fa=None, _fs=None):
        """A symmetric trapezoidal threaded rod (metric trapezoidal by default) (BOSL2 trapezoidal_threaded_rod())."""
        prof = _trapezoidal_profile(pitch, thread_angle, thread_depth)
        return _rod_solid(d, l, pitch, prof, starts, left_handed, _fn, _fa, _fs)

    @staticmethod
    def trapezoidal_threaded_nut(nutwidth, id, h, pitch, thread_angle=30, thread_depth=None,
                                 shape="hex", starts=1, left_handed=False, slop=0.0,
                                 _fn=None, _fa=None, _fs=None):
        """A nut for a trapezoidal threaded rod (BOSL2 trapezoidal_threaded_nut())."""
        prof = _trapezoidal_profile(pitch, thread_angle, thread_depth)
        return _nut_solid(nutwidth, id, h, pitch, prof, shape, starts, left_handed, slop, _fn, _fa, _fs)

    # -- ACME ------------------------------------------------------------------------------

    @staticmethod
    def acme_threaded_rod(d, l, pitch, thread_depth=None, starts=1, left_handed=False,
                          _fn=None, _fa=None, _fs=None):
        """A 29-degree ACME threaded rod (BOSL2 acme_threaded_rod())."""
        prof = _trapezoidal_profile(pitch, 29, thread_depth if thread_depth is not None else pitch / 2)
        return _rod_solid(d, l, pitch, prof, starts, left_handed, _fn, _fa, _fs)

    @staticmethod
    def acme_threaded_nut(nutwidth, id, h, pitch, thread_depth=None, shape="hex", starts=1,
                          left_handed=False, slop=0.0, _fn=None, _fa=None, _fs=None):
        """A nut for an ACME threaded rod (BOSL2 acme_threaded_nut())."""
        prof = _trapezoidal_profile(pitch, 29, thread_depth if thread_depth is not None else pitch / 2)
        return _nut_solid(nutwidth, id, h, pitch, prof, shape, starts, left_handed, slop, _fn, _fa, _fs)

    # -- square ----------------------------------------------------------------------------

    @staticmethod
    def square_threaded_rod(d, l, pitch, starts=1, left_handed=False, _fn=None, _fa=None, _fs=None):
        """A square-profile threaded rod (BOSL2 square_threaded_rod())."""
        prof = _trapezoidal_profile(pitch, 0.1)
        return _rod_solid(d, l, pitch, prof, starts, left_handed, _fn, _fa, _fs)

    @staticmethod
    def square_threaded_nut(nutwidth, id, h, pitch, shape="hex", starts=1, left_handed=False,
                            slop=0.0, _fn=None, _fa=None, _fs=None):
        """A nut for a square threaded rod (BOSL2 square_threaded_nut())."""
        prof = _trapezoidal_profile(pitch, 0.1)
        return _nut_solid(nutwidth, id, h, pitch, prof, shape, starts, left_handed, slop, _fn, _fa, _fs)

    # -- buttress --------------------------------------------------------------------------

    @staticmethod
    def buttress_threaded_rod(d, l, pitch, starts=1, left_handed=False, _fn=None, _fa=None, _fs=None):
        """An asymmetric buttress threaded rod (BOSL2 buttress_threaded_rod())."""
        return _rod_solid(d, l, pitch, _buttress_profile(), starts, left_handed, _fn, _fa, _fs)

    @staticmethod
    def buttress_threaded_nut(nutwidth, id, h, pitch, shape="hex", starts=1, left_handed=False,
                              slop=0.0, _fn=None, _fa=None, _fs=None):
        """A nut for a buttress threaded rod (BOSL2 buttress_threaded_nut())."""
        return _nut_solid(nutwidth, id, h, pitch, _buttress_profile(), shape, starts, left_handed, slop, _fn, _fa, _fs)

    # -- single thread helix ---------------------------------------------------------------

    @staticmethod
    def thread_helix(d, pitch, thread_depth=None, flank_angle=15, turns=1, starts=1,
                     left_handed=False, profile=None, _fn=None, _fa=None, _fs=None):
        """A single helical thread ridge (no core), for adding threads onto your own cylinder
        (BOSL2 thread_helix()). The thread crest is at diameter *d*; give *thread_depth* and
        *flank_angle*, or an explicit *profile*."""
        from bosl2.shapes3d import Bosl2Solid
        from bosl2.skin import spiral_sweep

        assert pitch > 0 and d > 0, "thread_helix(): d and pitch must be positive."
        if profile is None:
            depth = thread_depth if thread_depth is not None else pitch / 2
            profile = _trapezoidal_profile(pitch, 2 * flank_angle, depth)
        prof = [[float(x), float(y)] for x, y in profile]
        ys = [p[1] for p in prof]
        pmax = max(ys)
        r = d / 2
        section = [[(py - pmax) * pitch, px * pitch] for px, py in prof]
        lead = starts * pitch
        h = turns * lead
        thread = None
        for k in range(starts):
            sec = [[x, y + k * pitch] for x, y in section]
            piece = Bosl2Solid(spiral_sweep(sec, h=h, r=r, turns=turns * (-1 if left_handed else 1),
                                            center=True).polyhedron())
            if starts > 1:
                piece = piece.rotate([0, 0, k * 360 / starts])
            thread = piece if thread is None else (thread | piece)
        return thread
