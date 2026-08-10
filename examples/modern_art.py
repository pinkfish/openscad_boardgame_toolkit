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

# LibFile: examples/modern_art.py
#    PythonSCAD port of modern_art.scad: an insert for Modern Art -- one cap box of
#    cards and one of tokens.
#
#    The .scad built the card wells as raw cubes plus hand-placed FingerHoleBase calls at
#    computed offsets. Here they are two `Compartment`s and the layout places them, so the
#    positions follow from the card size instead of being arithmetic in the example. The
#    lid decoration moves from a per-file `default_lid_shape_type` global onto the BoxKit's
#    Lid, which is the one place a project's lids are described.
#
# FileSummary: Modern Art insert -- card box and token box.
# FileGroup: Examples

from base_bgtk import FROM_MAKE, MAKE_MMU, InnerObject, LabelType, make_box
from box_base import BoxKit, Label, Lid
from cap_box import CapBox
from compartments import Compartment, Group, Justify, Removal, Shape, layout_compartments
from components import FingerHoleBase, RoundedBoxAllSides
from labels import MakeLabelOptions
from shape_type import MakeShapeObject, ShapeType

# ---- The retail box, and what has to go in it ------------------------------------
box_length = 208
box_width = 154
box_height = 44
board_thickness = 6

wall_thickness = 3
floor_thickness = 2
lid_thickness = 2

card_width = 61
card_length = 93

# Two boxes side by side along the retail box's length, both as deep as the space under
# the board. 3mm of slack across the pair so the insert drops in.
card_box_width = wall_thickness * 2 + card_length
card_box_length = box_width - 3
card_box_height = box_height - board_thickness

token_box_width = box_length - card_box_width - 3
token_box_length = box_width - 3
token_box_height = card_box_height

# MMU prints get a solid label background; a single-colour print gets the framed outline,
# which is the .scad's `MAKE_MMU == 1 ? LABEL_TYPE_FRAMED_SOLID : LABEL_TYPE_FRAMED`.
_LABEL = MakeLabelOptions(
    label_type=LabelType.FRAMED_SOLID if MAKE_MMU else LabelType.FRAMED,
)

# ---------------------------------------------------------------------------
# One kit: both boxes are cap boxes with the same walls and the same lid style.
# ---------------------------------------------------------------------------
KIT = BoxKit(
    CapBox,
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    lid=Lid(
        shape_options=MakeShapeObject(
            shape_type=ShapeType.PENROSE_TILING_5, shape_width=25, shape_thickness=0.75
        ),
        label=Label("", options=_LABEL),
    ),
)

# Two card wells stacked along the box's length. Removal.NONE, because the finger holes go
# in the LEFT WALL rather than each well's front: the wells are stacked front-to-back, so a
# front notch on the far one would only cut the divider between the two decks, which is no
# help in lifting either of them out. The left wall runs the length of the box and reaches
# both, which is where the .scad put them.
_card_wells = layout_compartments(
    [
        Group([
            Compartment(
                shape=Shape.RECT, w=card_length, l=card_width, removal=Removal.NONE,
            )
        ])
        for _ in range(2)
    ],
    # margin=0 and space-between: the cards are exactly as wide as the interior, and the
    # .scad put one well at y=0 and the other hard against the far wall.
    min_gap=wall_thickness,
    margin=0,
    justify=Justify.SPACE_BETWEEN,
)


def _cards(inner):
    """The two card wells, plus a finger scallop through the left wall of each."""
    pieces = list(_card_wells(inner))
    for y in (card_width / 2, inner.length - card_width / 2):
        pieces.append(
            InnerObject(
                FingerHoleBase(radius=15, height=card_box_height).translate(
                    [0, y, -floor_thickness - 0.5]
                )
            )
        )
    return pieces


_card_box = KIT.box(
    size=[card_box_width, card_box_length, card_box_height],
    label="ModernArtCards",
    contents=_cards,
    lid="Cards",
)

_token_box = KIT.box(
    size=[token_box_width, token_box_length, token_box_height],
    label="ModernArtTokens",
    contents=lambda inner: [
        InnerObject(RoundedBoxAllSides([inner.width, inner.length, inner.height], radius=15))
    ],
    lid=Lid(
        shape_options=MakeShapeObject(
            shape_type=ShapeType.PENROSE_TILING_5, shape_width=25, shape_thickness=0.75
        ),
        label=Label("Modern Art", options=MakeLabelOptions(
            font="Marker Felt:style=Regular",
            label_type=LabelType.FRAMED_SOLID if MAKE_MMU else LabelType.FRAMED,
        )),
    ),
)


@make_box
def CardBox():
    return _card_box.make_box()


@make_box
def CardBoxLid():
    return _card_box.make_lid()


@make_box
def TokensBox():
    return _token_box.make_box()


@make_box
def TokensBoxLid():
    return _token_box.make_lid()


if FROM_MAKE != 1:
    TokensBoxLid()
