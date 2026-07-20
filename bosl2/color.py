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

# LibFile: bosl2/color.py
#    Pure-Python port of BOSL2's color.scad: the HSL/HSV -> RGB colorspace conversions and the
#    rainbow() helper for colouring a list of objects. The colour-application operators
#    (color/recolor/color_this/hsl/hsv/highlight/ghost) live on :class:`~bosl2.shapes3d.Bosl2Solid`
#    via the :class:`Colorable` mixin defined here; each resolves to the native PythonSCAD
#    ``color()`` / ``highlight()`` (# modifier) / ``background()`` (% modifier) calls.
#
#    Only pure math is imported at load time, so shapes3d.py can pull in the mixin during its own
#    import without a cycle.
#
# FileSummary: HSL/HSV colour conversion, rainbow(), and the Colorable colour operators.
# FileGroup: BOSL2

from __future__ import annotations

from collections.abc import Sequence
import random

__all__ = ["hsl", "hsv", "rainbow", "rainbow_colors", "Colorable"]


# ---------------------------------------------------------------------------
# Section: colorspace conversion
# ---------------------------------------------------------------------------


def hsl(h: float, s: float = 1.0, l: float = 0.5, a: float | None = None) -> list[float]:
    """Convert HSL to an ``[R, G, B]`` colour (or ``[R, G, B, A]`` if *a* is given) -- BOSL2 hsl().

    Args:
        h: hue in degrees (0=red, 60=yellow, 120=green, 180=cyan, 240=blue, 300=magenta)
        s: saturation 0..1 (0 = grey, 1 = vivid). Default 1
        l: lightness 0..1 (0 = black, 0.5 = bright, 1 = white). Default 0.5
        a: optional alpha 0..1; when given the result is ``[R, G, B, A]``

    Returns:
        ``[R, G, B]`` (each 0..1), or ``[R, G, B, A]`` when *a* is given.
    """
    hm = h % 360
    rgb = []
    for n in (0, 8, 4):
        k = (n + hm / 30) % 12
        rgb.append(l - s * min(l, 1 - l) * max(min(k - 3, 9 - k, 1), -1))
    return rgb + ([a] if a is not None else [])


def hsv(h: float, s: float = 1.0, v: float = 1.0, a: float | None = None) -> list[float]:
    """Convert HSV to an ``[R, G, B]`` colour (or ``[R, G, B, A]`` if *a* is given) -- BOSL2 hsv().

    Args:
        h: hue in degrees (0=red, 60=yellow, 120=green, 180=cyan, 240=blue, 300=magenta)
        s: saturation 0..1 (0 = grey, 1 = vivid). Default 1
        v: value 0..1 (0 = black, 1 = bright). Default 1
        a: optional alpha 0..1; when given the result is ``[R, G, B, A]``

    Returns:
        ``[R, G, B]`` (each 0..1), or ``[R, G, B, A]`` when *a* is given.
    """
    assert 0 <= s <= 1, "hsv(): saturation must be in 0..1."
    assert 0 <= v <= 1, "hsv(): value must be in 0..1."
    assert a is None or 0 <= a <= 1, "hsv(): alpha must be in 0..1."
    hm = h % 360
    c = v * s
    hp = hm / 60
    x = c * (1 - abs(hp % 2 - 1))
    if hp <= 1:
        rp = [c, x, 0.0]
    elif hp <= 2:
        rp = [x, c, 0.0]
    elif hp <= 3:
        rp = [0.0, c, x]
    elif hp <= 4:
        rp = [0.0, x, c]
    elif hp <= 5:
        rp = [x, 0.0, c]
    elif hp <= 6:
        rp = [c, 0.0, x]
    else:
        rp = [0.0, 0.0, 0.0]
    m = v - c
    rgb = [rp[0] + m, rp[1] + m, rp[2] + m]
    return rgb + ([a] if a is not None else [])


# ---------------------------------------------------------------------------
# Section: rainbow
# ---------------------------------------------------------------------------


def rainbow_colors(n: int, stride: int = 1, maxhues: int | None = None, shuffle: bool = False,
                   seed=None) -> list[list[float]]:
    """The list of ``n`` ``[R, G, B]`` colours stepped around the ROYGBIV wheel (BOSL2 rainbow()).

    Args:
        n:       how many colours to generate
        stride:  consecutive colours stride this many steps around the wheel
        maxhues: cap the number of distinct hues (default: *n*)
        shuffle: shuffle the hue order
        seed:    seed for the shuffle
    """
    if n <= 0:
        return []
    mh = maxhues if maxhues is not None else n
    huestep = 360 / mh
    hues = [(i * huestep + i * 360 / stride) % 360 for i in range(n)]
    if shuffle:
        random.Random(seed).shuffle(hues)
    return [hsv(h=hue) for hue in hues]


def rainbow(items: Sequence, stride: int = 1, maxhues: int | None = None, shuffle: bool = False,
            seed=None) -> list:
    """Colour each object in *items* a different hue, returning the coloured list (BOSL2 rainbow()).

    Each item must support ``.color([r, g, b])`` (a :class:`~bosl2.shapes3d.Bosl2Solid` or a native
    solid). Useful for telling apart the parts of a multi-piece model or debugging a list of paths.

    Args:
        items:   the objects to colour
        stride:  consecutive colours stride this many steps around the wheel
        maxhues: cap the number of distinct hues (default: ``len(items)``)
        shuffle: shuffle the hue order
        seed:    seed for the shuffle
    """
    items = list(items)
    colors = rainbow_colors(len(items), stride=stride, maxhues=maxhues, shuffle=shuffle, seed=seed)
    return [obj.color(col) for obj, col in zip(items, colors)]


# ---------------------------------------------------------------------------
# Section: Colorable mixin
# ---------------------------------------------------------------------------


class Colorable:
    """Mixin adding the color.scad colour operators as methods.

    Inherited by :class:`~bosl2.shapes3d.Bosl2Solid`. Every operator resolves to the host's native
    colour primitives, which the host provides as ``_color_native`` (PythonSCAD ``color()``),
    ``_highlight_native`` (the ``#`` modifier) and ``_ghost_native`` (the ``%`` modifier). Because
    the toolkit builds native geometry rather than a BOSL2 ``$color`` attachment tree,
    :meth:`recolor` and :meth:`color_this` both apply the colour directly (an object's
    already-coloured children keep their colour, matching OpenSCAD's ``color()`` semantics).
    """

    def _color_native(self, c=None, alpha=None):  # pragma: no cover - overridden by the host class
        raise NotImplementedError

    def _highlight_native(self):  # pragma: no cover - overridden by the host class
        raise NotImplementedError

    def _ghost_native(self):  # pragma: no cover - overridden by the host class
        raise NotImplementedError

    def color(self, c=None, alpha: float | None = None):
        """Colour this object. *c* is a name (``"red"``), ``[R, G, B]``, or ``[R, G, B, A]``."""
        if c is None and alpha is None:
            return self
        return self._color_native(c, alpha)

    def recolor(self, c="default", alpha: float | None = None):
        """Set the colour of this object and its uncoloured descendants (BOSL2 recolor()).

        ``"default"`` / ``None`` leaves the colour unchanged (there is no ``$color`` scheme to
        revert to in the native backend)."""
        if c is None or c == "default":
            return self
        return self._color_native(c, alpha)

    def color_this(self, c="default", alpha: float | None = None):
        """Colour just this object (BOSL2 color_this()); equivalent to :meth:`color` in the native
        backend, where there is no ``$color`` attachment tree to preserve separately."""
        if c is None or c == "default":
            return self
        return self._color_native(c, alpha)

    def hsl(self, h: float, s: float = 1.0, l: float = 0.5, a: float | None = None):
        """Colour this object from an HSL hue/saturation/lightness (BOSL2 hsl())."""
        return self._color_native(hsl(h, s, l), a)

    def hsv(self, h: float, s: float = 1.0, v: float = 1.0, a: float | None = None):
        """Colour this object from an HSV hue/saturation/value (BOSL2 hsv())."""
        return self._color_native(hsv(h, s, v), a)

    def highlight(self, highlight: bool = True):
        """Apply the ``#`` debug modifier (BOSL2 highlight()); ``False`` leaves it unmodified."""
        return self._highlight_native() if highlight else self

    def ghost(self, ghost: bool = True):
        """Apply the ``%`` (transparent, non-interacting) modifier (BOSL2 ghost()); ``False`` leaves
        it unmodified."""
        return self._ghost_native() if ghost else self
