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

# LibFile: bosl2/screws.py
#    Pure-Python port of the core of BOSL2's screws.scad, built on top of
#    :class:`~bosl2.threading.Threading`. The :class:`Screws` class turns a metric screw name (``"M6"``,
#    ``"M8x1"``) into ready-to-print geometry: :meth:`Screws.screw` (a threaded/plain shaft plus a
#    socket / hex / button / pan / flat / setscrew head with an optional hex or slot drive recess),
#    :meth:`Screws.nut` (a hex/square nut with a matching threaded hole), and :meth:`Screws.screw_hole`
#    (a clearance/counterbore/countersink hole cutter). :meth:`Screws.screw_info` returns the resolved
#    dimensions as a plain dict.
#
#    The dimension tables (ISO coarse/fine thread pitches, and ISO head sizes for socket cap ISO 4762,
#    hex ISO 4017, button ISO 7380, pan ISO 14583, countersunk ISO 10642/7046, setscrew, and hex/square
#    nuts ISO 4032/4035/4034) are transcribed verbatim from screws.scad and checked in
#    tests/test_screws.py. The threads themselves come from the watertight-polyhedron thread generator
#    in threading.py. Not ported (a follow-up): UTS/imperial specs, phillips/torx drive recesses, the
#    named-anchor system, shoulder screws, and per-tolerance thread-class diameters.
#
# FileSummary: Metric screws, nuts and screw holes built on the threading port.
# FileGroup: BOSL2

from __future__ import annotations

import math

__all__ = ["Screws"]


# ---------------------------------------------------------------------------
# Section: metric dimension tables (transcribed from screws.scad)
# ---------------------------------------------------------------------------

# nominal diameter -> [coarse, fine, extra-fine, super-fine] pitches (mm); None where undefined.
_ISO_THREAD = {
    1: [0.25, 0.2], 1.2: [0.25, 0.2], 1.4: [0.3, 0.2], 1.6: [0.35, 0.2],
    1.8: [0.35, 0.2], 2: [0.4, 0.25], 2.2: [0.45, 0.25], 2.5: [0.45, 0.35],
    3: [0.5, 0.35], 3.5: [0.6, 0.35], 4: [0.7, 0.5], 5: [0.8, 0.5],
    6: [1, 0.75], 7: [1, 0.75], 8: [1.25, 1, 0.75], 9: [1.25, 1, 0.75],
    10: [1.5, 1.25, 1, 0.75], 11: [1.5, 1, 0.75], 12: [1.75, 1.5, 1.25, 1],
    14: [2, 1.5, 1.25, 1], 16: [2, 1.5, 1], 18: [2.5, 2, 1.5, 1],
    20: [2.5, 2, 1.5, 1], 22: [2.5, 2, 1.5, 1], 24: [3, 2, 1.5, 1],
    27: [3, 2, 1.5, 1], 30: [3.5, 3, 2, 1.5], 33: [3.5, 3, 2, 1.5],
    36: [4, 3, 2, 1.5], 39: [4, 3, 2, 1.5], 42: [4.5, 4, 3, 2],
    48: [5, 4, 3, 2],
}

_THREAD_INDEX = {
    "coarse": 0, "fine": 1, "medium": 1,
    "extra fine": 2, "extrafine": 2, "extra-fine": 2,
    "super fine": 3, "superfine": 3, "super-fine": 3,
}

# hex cap head (ISO 4017): diameter -> (across-flats width, head height)
_HEX_HEAD = {
    5: (8, 3.5), 6: (10, 4), 8: (13, 5.3), 10: (17, 6.4), 12: (19, 7.5),
    14: (22, 8.8), 16: (24, 10), 18: (27, 11.5), 20: (30, 12.5), 24: (36, 15),
    30: (46, 18.7),
}

# socket cap head (ISO 4762): diameter -> (head diameter, hex drive across-flats).
# head height == nominal diameter; hex drive depth == diameter/2.
_SOCKET_HEAD = {
    1.6: (3, 1.5), 2: (3.8, 1.5), 2.5: (4.5, 2), 2.6: (5, 2), 3: (5.5, 2.5),
    3.5: (6.2, 2.5), 4: (7, 3), 5: (8.5, 4), 6: (10, 5), 7: (12, 6),
    8: (13, 6), 10: (16, 8), 12: (18, 10), 14: (21, 12), 16: (24, 14),
    18: (27, 14), 20: (30, 17), 22: (33, 17), 24: (36, 19), 27: (40, 19),
    30: (45, 22), 33: (50, 24), 36: (54, 27), 42: (63, 32), 48: (72, 36),
}

# button head (ISO 7380): diameter -> (head diameter, head height, hex drive, hex drive depth)
_BUTTON_HEAD = {
    1.6: (2.9, 0.8, 0.9, 0.55), 2: (3.5, 1.3, 1.3, 0.69), 2.5: (4.6, 1.5, 1.5, 0.87),
    3: (5.7, 1.65, 2, 1.04), 3.5: (5.7, 1.65, 2, 1.21), 4: (7.6, 2.2, 2.5, 1.30),
    5: (9.5, 2.75, 3, 1.56), 6: (10.5, 3.3, 4, 2.08), 8: (14, 4.4, 5, 2.60),
    10: (17.5, 5.5, 6, 3.12), 12: (21, 6.6, 8, 4.16), 16: (28, 8.8, 10, 5.2),
}

# pan head (ISO 14583): diameter -> (head diameter, head height)
_PAN_HEAD = {
    1.6: (3.2, 1.3), 2: (4, 1.6), 2.5: (5, 2), 3: (5.6, 2.4), 3.5: (7, 3.1),
    4: (8, 3.1), 5: (9.5, 3.8), 6: (12, 4.6), 8: (16, 6), 10: (20, 7.5),
}

# countersunk / flat head (ISO 10642 / ISO 7046): diameter -> (theoretical sharp diameter, actual diameter).
# 90-degree included angle.
_FLAT_HEAD = {
    1.6: (3.6, 2.85), 2: (4.4, 3.65), 2.5: (5.5, 4.55), 3: (6.3, 5.35),
    3.5: (8.2, 7.12), 4: (9.4, 8.22), 5: (10.4, 9.12), 6: (12.6, 11.085),
    8: (17.3, 15.585), 10: (20, 18.04), 12: (24, 21.75), 14: (28, 25.25),
    16: (32, 28.75), 18: (36, 32.2), 20: (40, 35.7),
}

# headless setscrew: diameter -> hex drive across-flats (depth == diameter/2)
_SETSCREW = {
    1.4: 0.7, 1.6: 0.7, 1.8: 0.7, 2: 0.9, 2.5: 1.3, 3: 1.5, 4: 2, 5: 2.5,
    6: 3, 8: 4, 10: 5, 12: 6, 16: 8, 20: 10,
}

# hex / square nut (ISO 4032 / 4035 / 4034): diameter -> (across-flats width, normal, thin, thick).
# None where that thickness class is undefined.
_NUT = {
    1.6: (3.2, 1.3, 1.0, None), 2: (4, 1.6, 1.2, None), 2.5: (5, 2, 1.6, None),
    3: (5.5, 2.4, 1.8, None), 4: (7, 3.2, 2.2, None), 5: (8, 4.7, 2.7, 5.1),
    6: (10, 5.2, 3.2, 5.7), 8: (13, 6.8, None, 7.5), 10: (16, 8.4, None, 9.3),
    12: (18, 10.8, None, 12), 16: (24, 14.8, None, 16.4), 20: (30, 18, None, 20.3),
    24: (36, 21.5, None, 23.9), 30: (46, 25.6, None, 28.6), 36: (55, 31, None, 34.7),
}

# ISO 965 clearance holes: fit name -> radial gap fraction expressed as an absolute add per size band.
# BOSL2 scales these by pitch; we approximate the common medium fit with a diameter-based add.
_CLEARANCE = {"close": 0.2, "normal": 0.5, "loose": 1.0}


def _parse_spec(spec, thread="coarse", pitch=None):
    """Resolve *spec* to ``(diameter, pitch)``.

    *spec* may be ``"M6"``, ``"M8x1"`` (explicit pitch), a bare number (treated as the metric
    nominal diameter), or a mapping already carrying ``diameter``/``pitch``.
    """
    if isinstance(spec, dict):
        d = float(spec["diameter"])
        sp = spec.get("pitch")
        return d, float(sp) if sp is not None else _lookup_pitch(d, thread)
    if isinstance(spec, (int, float)):
        d = float(spec)
        return d, float(pitch) if pitch is not None else _lookup_pitch(d, thread)
    s = str(spec).strip().upper()
    if s.startswith("M"):
        s = s[1:]
    if "X" in s:
        dpart, ppart = s.split("X", 1)
        return float(dpart), float(ppart)
    d = float(s)
    return d, float(pitch) if pitch is not None else _lookup_pitch(d, thread)


def _lookup_pitch(diam, thread):
    if diam not in _ISO_THREAD:
        raise ValueError(f"Unknown metric screw size M{diam:g}")
    row = _ISO_THREAD[diam]
    idx = _THREAD_INDEX.get(str(thread).lower(), 0)
    if idx >= len(row) or row[idx] is None:
        idx = 0
    return float(row[idx])


class Screws:
    """Metric screws, nuts and screw holes (BOSL2 screws.scad), built on :class:`~bosl2.threading.Threading`.

    Every method is a class method returning a :class:`~bosl2.shapes3d.Bosl2Solid`, except
    :meth:`screw_info`, which returns a plain ``dict`` of resolved dimensions. Screws are built
    head-up: the shaft occupies ``z in [-length, 0]`` (tip at the bottom) and the head sits above
    ``z = 0``.
    """

    # -- resolved dimensions ---------------------------------------------------------------

    @staticmethod
    def screw_info(spec, head="socket", thread="coarse", drive="none", pitch=None):
        """Resolve a screw specification to a dict of dimensions.

        Keys: ``system``, ``diameter``, ``pitch``, ``head``, ``head_size``, ``head_height``,
        ``head_angle`` (flat heads only), ``drive``, ``drive_size``, ``drive_depth``.
        """
        d, p = _parse_spec(spec, thread, pitch)
        info = {"system": "ISO", "diameter": d, "pitch": p, "head": head,
                "drive": drive, "drive_size": None, "drive_depth": None}

        if head in (None, "none"):
            info["head"] = "none"
            info["head_size"] = None
            info["head_height"] = 0.0
            if drive == "hex":
                info["drive_size"] = _closest(_SETSCREW, d)
                info["drive_depth"] = d / 2
        elif head == "hex":
            hs, hh = _closest(_HEX_HEAD, d)
            info["head_size"], info["head_height"] = hs, hh
        elif head in ("socket", "socket ribbed"):
            hs, hex_drive = _closest(_SOCKET_HEAD, d)
            info["head_size"], info["head_height"] = hs, d
            if drive == "hex":
                info["drive_size"], info["drive_depth"] = hex_drive, d / 2
        elif head == "button":
            hs, hh, hex_drive, hex_depth = _closest(_BUTTON_HEAD, d)
            info["head_size"], info["head_height"] = hs, hh
            if drive == "hex":
                info["drive_size"], info["drive_depth"] = hex_drive, hex_depth
        elif head in ("pan", "round"):
            hs, hh = _closest(_PAN_HEAD, d)
            info["head_size"], info["head_height"] = hs, hh
        elif head == "flat":
            sharp, actual = _closest(_FLAT_HEAD, d)
            info["head_size"] = actual
            info["head_size_sharp"] = sharp
            info["head_angle"] = 90.0
            info["head_height"] = (actual - d) / 2  # 90-degree cone: radius drop == height
        else:
            raise ValueError(f'Unknown head type "{head}"')
        return info

    # -- the screw -------------------------------------------------------------------------

    @staticmethod
    def screw(spec, length, head="socket", drive="none", thread=True, thread_len=None,
              pitch=None, _fn=None, _fa=None, _fs=None):
        """A metric screw: a threaded (or plain) shaft plus a head, with an optional drive recess.

        *length* is the shaft length below the head (for a flat head, below the surface). Set
        ``thread=False`` for a plain unthreaded shank, or ``thread_len`` for a partly-threaded shaft.
        """
        from bosl2.shapes3d import cyl

        info = Screws.screw_info(spec, head=head, drive=drive, thread="coarse" if thread in (True, False) else thread,
                                 pitch=pitch)
        d, p = info["diameter"], info["pitch"]
        thread_kind = thread if isinstance(thread, str) else "coarse"

        # -- shaft: top face at z=0, tip at z=-length -----------------------------------
        if thread:
            from bosl2.threading import Threading
            _, tp = _parse_spec(spec, thread_kind, pitch)
            tl = length if (thread_len is None or thread_len >= length) else thread_len
            shank_len = length - tl
            shaft = Threading.threaded_rod(d, tl, tp, _fn=_fn, _fa=_fa, _fs=_fs).down(shank_len + tl / 2)
            if shank_len > 1e-9:
                shank = cyl(d=d, h=shank_len, _fn=_fn, _fa=_fa, _fs=_fs).down(shank_len / 2)
                shaft = shaft | shank
        else:
            shaft = cyl(d=d, h=length, _fn=_fn, _fa=_fa, _fs=_fs).down(length / 2)

        result = shaft
        head_top = info["head_height"]  # top face of the head; 0 for a headless setscrew (recess into shaft)
        headobj = Screws._make_head(info, _fn, _fa, _fs)
        if headobj is not None:
            result = result | headobj

        recess = Screws._make_recess(info, head_top, _fn, _fa, _fs)
        if recess is not None:
            result = result - recess
        return result

    @staticmethod
    def _make_head(info, _fn, _fa, _fs):
        from bosl2.shapes3d import cyl, regular_prism

        head = info["head"]
        if head in (None, "none"):
            return None
        hh = info["head_height"]
        hs = info["head_size"]
        if head == "hex":
            return regular_prism(6, h=hh, id=hs, _fn=_fn, _fa=_fa, _fs=_fs).up(hh / 2)
        if head in ("socket", "socket ribbed"):
            return cyl(d=hs, h=hh, chamfer2=hs / 20, _fn=_fn, _fa=_fa, _fs=_fs).up(hh / 2)
        if head == "button":
            rnd = min(hh * 0.9, hs / 2 * 0.9)
            return cyl(d=hs, h=hh, rounding2=rnd, _fn=_fn, _fa=_fa, _fs=_fs).up(hh / 2)
        if head in ("pan", "round"):
            return cyl(d=hs, h=hh, rounding2=0.2 * hs, _fn=_fn, _fa=_fa, _fs=_fs).up(hh / 2)
        if head == "flat":
            # 90-degree countersunk cone: shaft diameter at the bottom, head diameter at the surface.
            return cyl(d1=info["diameter"], d2=hs, h=hh, _fn=_fn, _fa=_fa, _fs=_fs).up(hh / 2)
        return None

    @staticmethod
    def _make_recess(info, head_top, _fn, _fa, _fs):
        from bosl2.shapes3d import cuboid, regular_prism

        drive = info.get("drive")
        size = info.get("drive_size")
        depth = info.get("drive_depth")
        if drive in (None, "none") or not size or not depth:
            return None
        eps = 0.02
        if drive == "hex":
            rec = regular_prism(6, h=depth + eps, id=size, _fn=_fn, _fa=_fa, _fs=_fs)
        elif drive == "slot":
            width = size if size else max(0.6, info["diameter"] / 6)
            length = (info["head_size"] or info["diameter"]) + 2
            rec = cuboid([length, width, depth + eps])
        else:
            return None
        # place the recess so its open mouth is flush with the top of the head (or shaft top for setscrews)
        return rec.up(head_top - (depth + eps) / 2 + eps / 2)

    # -- the nut ---------------------------------------------------------------------------

    @staticmethod
    def nut(spec, thickness="normal", shape="hex", thread="coarse", nutwidth=None,
            slop=0.0, pitch=None, _fn=None, _fa=None, _fs=None):
        """A hex or square nut with a threaded hole matching *spec* (BOSL2 nut()).

        *thickness* is ``"normal"``, ``"thin"``, ``"thick"`` or a number (mm). *nutwidth* overrides
        the standard across-flats width. *slop* adds radial clearance to the threaded hole.
        """
        from bosl2.threading import Threading

        d, p = _parse_spec(spec, thread, pitch)
        width, th = _nut_dims(d, thickness, nutwidth)
        return Threading.threaded_nut(width, d, th, p, shape=shape, slop=slop,
                                      _fn=_fn, _fa=_fa, _fs=_fs)

    # -- clearance / countersink / counterbore hole cutter ---------------------------------

    @staticmethod
    def screw_hole(spec, length, head="none", counterbore=0.0, fit="normal", thread=False,
                   pitch=None, _fn=None, _fa=None, _fs=None):
        """A hole cutter for a screw: clearance shaft, plus optional countersink (flat head) or
        counterbore.

        Returns a solid to *subtract* from your part. The clearance shaft occupies ``z in [-length, 0]``
        with its mouth at ``z = 0``; countersinks/counterbores open upward from there. Set
        ``thread=True`` for a tapped (threaded) hole instead of a clearance hole.
        """
        from bosl2.shapes3d import cyl

        d, p = _parse_spec(spec, "coarse" if thread in (True, False) else thread, pitch)
        if thread:
            from bosl2.threading import Threading
            # a tapped hole: cut with the rod's thread tap (major + a touch of clearance)
            cutter = Threading.threaded_rod(d + 0.0, length, p, _fn=_fn, _fa=_fa, _fs=_fs).down(length / 2)
        else:
            gap = _CLEARANCE.get(str(fit).lower(), 0.5)
            cutter = cyl(d=d + 2 * gap, h=length, _fn=_fn, _fa=_fa, _fs=_fs).down(length / 2)

        if head == "flat":
            info = Screws.screw_info(spec, head="flat", pitch=pitch)
            hs = info["head_size"]
            csk_h = (hs - d) / 2
            csink = cyl(d1=d, d2=hs, h=csk_h + 0.02, _fn=_fn, _fa=_fa, _fs=_fs).up((csk_h + 0.02) / 2 - 0.01)
            cutter = cutter | csink
        elif counterbore and counterbore > 0:
            info = Screws.screw_info(spec, head=head if head not in (None, "none") else "socket", pitch=pitch)
            hd = info["head_size"] if head == "hex" else (info["head_size"] or 2 * d)
            if head == "hex":
                hd = 2 * hd / math.sqrt(3)  # across-corners for a hex head pocket
            cb = cyl(d=hd, h=counterbore + 0.02, _fn=_fn, _fa=_fa, _fs=_fs).up((counterbore + 0.02) / 2 - 0.01)
            cutter = cutter | cb
        return cutter


# ---------------------------------------------------------------------------
# Section: table helpers
# ---------------------------------------------------------------------------

def _closest(table, diam):
    """Look *diam* up in *table*, falling back to the nearest tabulated size."""
    if diam in table:
        return table[diam]
    key = min(table, key=lambda k: abs(k - diam))
    return table[key]


def _nut_dims(diam, thickness, nutwidth):
    """Resolve a nut's ``(across-flats width, thickness)`` for the given size and thickness class."""
    width, normal, thin, thick = _closest(_NUT, diam)
    if nutwidth is not None:
        width = float(nutwidth)
    if isinstance(thickness, (int, float)):
        return width, float(thickness)
    t = str(thickness).lower()
    if t == "thin" and thin is not None:
        return width, thin
    if t == "thick" and thick is not None:
        return width, thick
    return width, normal
