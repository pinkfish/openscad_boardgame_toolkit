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

# LibFile: flags.py
#    This file has all the modules needed to make some fun flags.

from __future__ import annotations
import pathlib
import re
import urllib.error
import urllib.request
from base_bgtk import (
    BACK,
    BOTTOM,
    FRONT,
    LEFT,
    RIGHT,
    TOP,
    Color,
    default_material_colour,
    default_slicing_layer_height,
    union_all_2d,
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openscad import PyOpenSCAD  # noqa: F401
from pybosl2 import shapes2d
_SVG_DIR = pathlib.Path(__file__).resolve().parent / "svg"
_FLAG_SVG_DIR = _SVG_DIR / "flags"
from pybosl2 import Region
from pybosl2 import shapes3d
from pybosl2.shapes3d import Bosl2Solid
from labels import Make3dStripedGrid


# module converted separately.


def FlagBackgroundAndBorder(
    length: float,
    height: float,
    background_color: Color,
    width: float | None = None,
    background: bool = True,
    border: float = 0,
    solid_background: bool = False,
    grid_spacing: float = 1.5,
    children: list | None = None,
) -> PyOpenSCAD:
    """Makes a background to the flag with the specified border.

    The first entry of ``children`` is used to subtract from the background while the
    second entry renders the inside of the flag.

    Usage::

        FlagBackgroundAndBorder(100, 4, "blue", children=[cutout, inside])

    Args:
        length: length of the background
        height: height of the background
        background_color: color of the background
        width: width of background (default length/2)
        background: generate the background (default True)
        border: size of border to generate (default 0)
        solid_background: generate a solid background for MMU (default False)
        grid_spacing: spacing for the striped grid (default 1.5)
        children: [cutout, inside] pair of shapes
    """
    calc_width = width
    assert children is not None and len(children) >= 2, (
        "FlagBackgroundAndBorder(): children[0] (cutout) and children[1] (face) are required"
    )
    if calc_width is None:
        calc_width = length / 2
    shape = None
    if border > 0:
        piece = shapes3d.cuboid([length + border, calc_width + border, height], anchor=BOTTOM) - shapes3d.cuboid(
            [length - 0.02, calc_width - 0.02, height + 1], anchor=BOTTOM
        ).translate([0, 0, -0.5])
        shape = piece.color(default_material_colour)
    if background:
        if solid_background:
            base = shapes3d.cuboid([length, calc_width, height], anchor=BOTTOM)
        else:
            base = shapes3d.cuboid([length, calc_width, height], anchor=BOTTOM) & Make3dStripedGrid(
                size=[length, calc_width], height=height, spacing=grid_spacing
            ).translate([-length * 5.5 / 4, -calc_width / 2, 0])
        piece = (base - children[0].translate([0, 0, -0.5])).color(background_color)
        shape = piece if shape is None else shape | piece
    piece = children[1]
    return piece if shape is None else shape | piece


# ---------------------------------------------------------------------------
# Flags, from their drawings
# ---------------------------------------------------------------------------
#
# Every flag below is its real drawing, loaded from svg/flags/ -- see the README there. They
# used to be built by hand out of stroked beziers and composed crosses, which is why this file
# was 1464 lines and why the Portuguese one alone carried ~800 lines of traced coordinates.
#
# Region.from_svg resolves a drawing's colours into DISJOINT regions in SVG paint order, so a
# flag comes out as one multi-colour solid with no overlapping colour bodies -- which is what
# MMU needs. Region.geometry() then colours each region individually.

#: The flag-icons drawing (svg/flags/<code>.svg) behind each flag.
_FLAG_CODES = {
    "australia": "au",
    "portugal": "pt",
    "sweden": "se",
    "united_states": "us",
    "union_jack": "gb",
    "st_georges_cross": "gb-eng",
    "st_andrews_cross": "gb-sct",
    "st_patricks_cross": "st-patrick",
}

#: Upstream for :func:`flag_for_country` -- flag-icons' 4x3 set, MIT licensed.
FLAG_ICONS_URL = "https://raw.githubusercontent.com/lipis/flag-icons/main/flags/4x3/{code}.svg"


def flag_viewbox(path: "pathlib.Path") -> tuple[float, float]:
    """The (length, width) an SVG declares in its ``viewBox``.

    SVG calls these two "width" and "height"; a flag's are its LENGTH (along the fly) and its
    WIDTH (along the hoist), which is what every function here takes, so they are named that
    way on the way out.

    Read from the file rather than assumed, because it is what sets the flag's ASPECT and its
    scale. flag-icons draws everything in 640x480, but a drawing from anywhere else (Wikimedia
    uses each flag's official ratio) has its own, and hardcoding 640x480 would silently
    stretch it.
    """
    text = path.read_text(errors="replace")
    match = re.search(r'viewBox\s*=\s*"\s*([-\d.eE]+)[ ,]+([-\d.eE]+)[ ,]+([-\d.eE]+)[ ,]+([-\d.eE]+)', text)
    if match is None:
        raise ValueError(f"{path.name} declares no viewBox, so its size and aspect are unknown")
    _min_x, _min_y, view_length, view_width = (float(v) for v in match.groups())
    assert view_length > 0 and view_width > 0, f"{path.name}: viewBox has a non-positive size"
    return view_length, view_width


def _ssl_context():
    """An SSL context that can actually verify github's certificate.

    A python.org build on macOS ships no CA bundle of its own and does not read the system
    keychain, so a plain urlopen() fails with CERTIFICATE_VERIFY_FAILED even though curl
    works. certifi's bundle is what pip and requests use; fall back to the default context
    when it is not installed rather than disabling verification, which would be worse than
    failing.
    """
    import ssl

    try:
        import certifi
    except ImportError:
        return ssl.create_default_context()
    return ssl.create_default_context(cafile=certifi.where())


def flag_svg_for_country(code: str, refresh: bool = False) -> "pathlib.Path":
    """The drawing for an ISO 3166-1 alpha-2 country code, downloading it if needed.

    Fetched once from flag-icons and cached in ``svg/flags/``, so a build only ever touches
    the network for a flag it has never seen. Everything already vendored there is a cache
    hit and never hits the network at all.

    Usage::

        flag_svg_for_country("fr")

    Args:
        code: an ISO 3166-1 alpha-2 code, e.g. ``"fr"``, ``"jp"``, or a flag-icons
            subdivision code like ``"gb-sct"``. Case-insensitive.
        refresh: re-download even when it is already cached.

    Returns:
        Path to the cached SVG.

    Raises:
        ValueError: if there is no such flag upstream.
    """
    key = code.strip().lower()
    assert key, "a country code is required"
    cached = _FLAG_SVG_DIR / f"{key}.svg"
    if cached.is_file() and not refresh:
        return cached

    url = FLAG_ICONS_URL.format(code=key)
    try:
        with urllib.request.urlopen(url, timeout=30, context=_ssl_context()) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise ValueError(f"no flag for country code {code!r} in flag-icons ({url})") from exc
        raise
    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"could not fetch {url}: {exc.reason}. Every flag this project ships is already "
            f"cached in {_FLAG_SVG_DIR}; only a code that has never been used needs the "
            "network. If this is a certificate error on macOS, run "
            '"/Applications/Python 3.x/Install Certificates.command" once.'
        ) from exc
    _FLAG_SVG_DIR.mkdir(parents=True, exist_ok=True)
    cached.write_text(body)
    return cached


def flag_from_svg(
    source: "str | pathlib.Path",
    length: float,
    width: float | None = None,
    thickness: float = 2,
    border: float = 0,
) -> "Bosl2Solid":
    """Build a flag from a drawing in ``svg/flags/``.

    The one place a flag becomes geometry. Every named flag below is a call to this.

    The drawing is SCALED by its own viewBox, never resized to fit its geometry's bounding
    box: some flags are drawn with parts that run past the viewBox (Scotland's saltire by 6%,
    the US flag by 2%), and fitting the bounding box to the requested size would shrink the
    whole flag to make room for that overhang -- so a 60mm flag would not be 60mm of flag.
    Scaling by the viewBox makes the FLAG exactly *length* wide, which is what the dimension
    means. Nothing is clipped; any overhang is drawn where the drawing puts it.

    Usage::

        flag_from_svg("au", 60)
        flag_from_svg("pt", 60, thickness=3, border=2)

    Args:
        source: a code cached in ``svg/flags/`` (``"au"``), or a path to any SVG
        length: length of the flag, exactly
        width: width of the flag (default: the drawing's own viewBox aspect)
        thickness: how thick to extrude it
        border: if > 0, put a frame of this width around the flag

    Returns:
        One multi-colour solid, the flag's corner at the origin, extending +x/+y and
        0..*thickness* in z.
    """
    assert length > 0, f"length must be > 0, got {length}"
    assert thickness > 0, f"thickness must be > 0, got {thickness}"
    path = pathlib.Path(source)
    if not path.suffix:
        path = _FLAG_SVG_DIR / f"{path.name}.svg"
    view_len, view_wide = flag_viewbox(path)
    calc_width = length * view_wide / view_len if width is None else width

    shape = Region.from_svg(str(path)).geometry()
    flag = (
        shape.scale([length / view_len, calc_width / view_wide, 1])
        .linear_extrude(height=thickness)
        .translate([0, calc_width, 0])
    )
    if border > 0:
        frame = shapes3d.cuboid(
            [length + border * 2, calc_width + border * 2, thickness], anchor=BOTTOM + FRONT + LEFT
        ) - shapes3d.cuboid(
            [length, calc_width, thickness + 1], anchor=BOTTOM + FRONT + LEFT
        ).translate([border, border, -0.5])
        flag = flag.translate([border, border, 0]) | frame.color(default_material_colour)
    return flag


def flag_for_country(
    code: str,
    length: float,
    width: float | None = None,
    thickness: float = 2,
    border: float = 0,
) -> "Bosl2Solid":
    """Any country's flag, by ISO 3166-1 alpha-2 code.

    Looks the drawing up in flag-icons (downloading and caching it the first time) and builds
    it at the drawing's own aspect ratio, exactly *length* wide.

    Usage::

        flag_for_country("fr", 60)
        flag_for_country("jp", 60, thickness=3, border=1)

    Args:
        code: ISO 3166-1 alpha-2 code, e.g. ``"fr"``; flag-icons subdivision codes
            (``"gb-sct"``) work too. Case-insensitive.
        length: length of the flag, exactly
        width: width of the flag (default: the drawing's own aspect)
        thickness: how thick to extrude it
        border: if > 0, put a frame of this width around the flag

    Returns:
        The flag as one multi-colour solid.

    Raises:
        ValueError: if there is no such flag upstream.
    """
    return flag_from_svg(flag_svg_for_country(code), length, width, thickness, border)


def StAndrewsCross(length: float, width: float | None = None, thickness: float = 2, border: float = 0):
    """Flag of Scotland -- the white saltire of St Andrew on blue.

    Usage::

        StAndrewsCross(60)
    """
    return flag_from_svg(_FLAG_CODES["st_andrews_cross"], length, width, thickness, border)


def StPatricksCross(length: float, width: float | None = None, thickness: float = 2, border: float = 0):
    """St Patrick's Saltire -- the red saltire on white.

    Usage::

        StPatricksCross(60)
    """
    return flag_from_svg(_FLAG_CODES["st_patricks_cross"], length, width, thickness, border)


def StGeorgesCross(length: float, width: float | None = None, thickness: float = 2, border: float = 0):
    """Flag of England -- the red cross of St George on white.

    Usage::

        StGeorgesCross(60)
    """
    return flag_from_svg(_FLAG_CODES["st_georges_cross"], length, width, thickness, border)


def UnionJack(length: float, width: float | None = None, thickness: float = 2, border: float = 0):
    """Flag of the United Kingdom.

    Usage::

        UnionJack(60)
        UnionJack(60, border=2)
    """
    return flag_from_svg(_FLAG_CODES["union_jack"], length, width, thickness, border)


def AustralianFlag(length: float, width: float | None = None, thickness: float = 2, border: float = 0):
    """Flag of Australia.

    Usage::

        AustralianFlag(60)
    """
    return flag_from_svg(_FLAG_CODES["australia"], length, width, thickness, border)


def SwedenFlag(length: float, width: float | None = None, thickness: float = 2, border: float = 0):
    """Flag of Sweden.

    Usage::

        SwedenFlag(60)
    """
    return flag_from_svg(_FLAG_CODES["sweden"], length, width, thickness, border)


def UnitedStatesFlag(length: float, width: float | None = None, thickness: float = 2, border: float = 0):
    """Flag of the United States.

    Usage::

        UnitedStatesFlag(60)
    """
    return flag_from_svg(_FLAG_CODES["united_states"], length, width, thickness, border)


def PortugeseFlag(length: float, width: float | None = None, thickness: float = 2, border: float = 0):
    """Flag of Portugal.

    Usage::

        PortugeseFlag(60)
    """
    return flag_from_svg(_FLAG_CODES["portugal"], length, width, thickness, border)
