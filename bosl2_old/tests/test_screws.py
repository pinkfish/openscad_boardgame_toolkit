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

"""Tests for bosl2/screws.py: the metric dimension tables (transcribed verbatim from screws.scad)
and the Screws screw/nut/screw_hole builders. Native geometry is mocked, so these check the resolved
dimensions numerically and that every builder returns a Bosl2Solid; the real assembled geometry
(watertight screws with the right head/shaft, matching nuts, hole cutters) is verified in
test_stl_render.py."""

import math

import pytest

from bosl2.screws import Screws, _parse_spec, _lookup_pitch, _nut_dims
from bosl2.shapes3d import Bosl2Solid


# -- spec parsing / pitch lookup ----------------------------------------------------------

def test_parse_plain_metric_name():
    assert _parse_spec("M6") == (6.0, 1.0)
    assert _parse_spec("M8") == (8.0, 1.25)
    assert _parse_spec("M3") == (3.0, 0.5)


def test_parse_explicit_pitch():
    assert _parse_spec("M8x1") == (8.0, 1.0)
    assert _parse_spec("M6x0.75") == (6.0, 0.75)


def test_parse_number_and_dict():
    assert _parse_spec(6) == (6.0, 1.0)
    assert _parse_spec({"diameter": 10, "pitch": 1.25}) == (10.0, 1.25)


@pytest.mark.parametrize("thread,expected", [("coarse", 1.5), ("fine", 1.25), ("extra fine", 1.0),
                                             ("super fine", 0.75)])
def test_pitch_classes_M10(thread, expected):
    assert _lookup_pitch(10, thread) == expected


def test_pitch_falls_back_to_coarse_when_class_missing():
    # M6 has no super-fine pitch -> falls back to coarse (1.0)
    assert _lookup_pitch(6, "super fine") == 1.0


def test_unknown_size_raises():
    with pytest.raises(ValueError):
        _lookup_pitch(6.5, "coarse")


# -- head dimensions (verbatim from screws.scad metric tables) ----------------------------

def test_socket_head_dims():
    info = Screws.screw_info("M6", head="socket", drive="hex")
    assert info["head_size"] == 10          # ISO 4762 head diameter
    assert info["head_height"] == 6.0       # socket head height == nominal diameter
    assert info["drive_size"] == 5          # hex key across-flats
    assert info["drive_depth"] == 3.0       # diameter / 2


def test_hex_head_dims():
    info = Screws.screw_info("M8", head="hex")
    assert info["head_size"] == 13          # across-flats
    assert info["head_height"] == 5.3


def test_button_head_dims():
    info = Screws.screw_info("M6", head="button", drive="hex")
    assert info["head_size"] == 10.5
    assert info["head_height"] == 3.3
    assert info["drive_size"] == 4
    assert info["drive_depth"] == 2.08


def test_pan_head_dims():
    info = Screws.screw_info("M5", head="pan")
    assert info["head_size"] == 9.5
    assert info["head_height"] == 3.8


def test_flat_head_dims_and_angle():
    info = Screws.screw_info("M6", head="flat")
    assert info["head_size"] == 11.085          # actual (mean) diameter, ISO 10642/7046
    assert info["head_size_sharp"] == 12.6      # theoretical sharp diameter
    assert info["head_angle"] == 90.0
    # 90-degree countersink: cone height == radius drop == (head - shaft)/2
    assert math.isclose(info["head_height"], (11.085 - 6) / 2)


def test_setscrew_drive():
    info = Screws.screw_info("M6", head="none", drive="hex")
    assert info["head"] == "none"
    assert info["head_size"] is None
    assert info["drive_size"] == 3          # hex key
    assert info["drive_depth"] == 3.0       # diameter / 2


def test_head_table_nearest_size_fallback():
    # M7 has a thread pitch but no tabulated button head -> nearest head size (M6/M8) is used.
    info = Screws.screw_info("M7", head="button")
    assert info["head_size"] in (10.5, 14)  # M6 or M8 button diameter


def test_unknown_thread_size_raises():
    with pytest.raises(ValueError):
        Screws.screw_info(6.1, head="socket")


def test_unknown_head_raises():
    with pytest.raises(ValueError):
        Screws.screw_info("M6", head="wingnut")


# -- nut dimensions (ISO 4032 / 4035 / 4034) ----------------------------------------------

def test_nut_dims_normal():
    assert _nut_dims(6, "normal", None) == (10, 5.2)
    assert _nut_dims(8, "normal", None) == (13, 6.8)


def test_nut_dims_thin_and_thick():
    assert _nut_dims(6, "thin", None) == (10, 3.2)
    assert _nut_dims(6, "thick", None) == (10, 5.7)


def test_nut_dims_numeric_thickness_and_width_override():
    assert _nut_dims(6, 4.0, None) == (10, 4.0)
    assert _nut_dims(6, "normal", 11) == (11, 5.2)


def test_nut_thin_falls_back_when_undefined():
    # M8 has no thin class -> falls back to normal thickness.
    assert _nut_dims(8, "thin", None) == (13, 6.8)


# -- builders all return solids -----------------------------------------------------------

@pytest.mark.parametrize("head", ["socket", "hex", "button", "pan", "flat", "none"])
def test_screw_builds(head):
    drive = "hex" if head in ("socket", "button", "none") else "none"
    assert isinstance(Screws.screw("M6", 20, head=head, drive=drive, _fn=8), Bosl2Solid)


def test_screw_unthreaded_and_partly_threaded():
    assert isinstance(Screws.screw("M6", 20, thread=False, _fn=8), Bosl2Solid)
    assert isinstance(Screws.screw("M6", 20, thread_len=8, _fn=8), Bosl2Solid)


@pytest.mark.parametrize("shape", ["hex", "square"])
def test_nut_builds(shape):
    assert isinstance(Screws.nut("M6", shape=shape, _fn=8), Bosl2Solid)


def test_nut_thickness_classes_build():
    for t in ("normal", "thin", "thick", 4.0):
        assert isinstance(Screws.nut("M6", thickness=t, _fn=8), Bosl2Solid)


@pytest.mark.parametrize("head,counterbore", [("none", 0), ("socket", 4), ("flat", 0), ("hex", 3)])
def test_screw_hole_builds(head, counterbore):
    assert isinstance(Screws.screw_hole("M6", 20, head=head, counterbore=counterbore, _fn=8),
                      Bosl2Solid)


def test_tapped_hole_builds():
    assert isinstance(Screws.screw_hole("M6", 20, thread=True, _fn=8), Bosl2Solid)


@pytest.mark.parametrize("fit", ["close", "normal", "loose"])
def test_clearance_fits_build(fit):
    assert isinstance(Screws.screw_hole("M6", 20, fit=fit, _fn=8), Bosl2Solid)
