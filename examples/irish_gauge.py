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

# LibFile: examples/irish_gauge.py
#    Irish Gauge insert, ported from examples/irish_gauge.scad to the NEW box system:
#    a BoxKit-configured SlidingBox per company, a FilamentHingeBox money tray, and
#    PathBox / NoLidBox spacers. The engraved company names + money numbers use the
#    Irish-Gauge second-colour trick (0.2mm POSITIVE_NEGATIVE text) via
#    components.EngravedLabel / text3d -- coloured under MAKE_MMU=1, a plain recess
#    otherwise. Interiors are hand-placed InnerObjects (fitted card/marker/train slots),
#    the direct analogue of the .scad children blocks.

import types

from base_bgtk import BOTTOM, FROM_MAKE, FRONT, LEFT, RIGHT, InnerObject, ObjectType, make_box
from box_base import BoxKit, BoxSpec
from sliding_box import SlidingBox
from no_lid import NoLidBox, PathBox, PathBoxOptions
from compartments import layout_compartments, Group, Compartment, Shape
from components import FingerHoleBase, CylinderWithIndents, RoundedBoxAllSides, EngravedLabel, text3d
import pybosl2.shapes3d as s3

# ---- Overall box + material (irish_gauge.scad top matter) ------------------------
box_width = 214
box_length = 302
box_height = 39

wall_thickness = 3
lid_thickness = 3

dividend_marker_diameter = 7.5
dividend_marker_thickness = 3
board_thickness = 10.5

train_width = 7.75
train_length = 5.5
train_height = 8

companies = [
    types.SimpleNamespace(shares=2, color="orange", name=["Belfast and", "County Down", "Railway"], lid="Belfast"),
    types.SimpleNamespace(shares=3, color="yellow", name=["Cork Bandon", "& South Coast", "Railway"], lid="Cork"),
    types.SimpleNamespace(shares=3, color="red", name=["Midland", "Great Western", "Railway"], lid="Midland"),
    types.SimpleNamespace(shares=4, color="purple", name=["Waterford", "Limerick", "& Western", "Railway"], lid="Waterford"),
    types.SimpleNamespace(shares=4, color="blue", name=["Great Southern", "& Western", "Railway"], lid="Great Southern"),
]

card_width = 49
card_length = 71
card_20_thickness = 14
single_card_thickness = card_20_thickness / 20
money_num = ["1", "5", "10"]

company_box_width = box_width / 4
company_box_length = card_length * 1.8 + wall_thickness * 2
company_box_height = (box_height - board_thickness) / 2

money_box_width = box_width
money_box_length = card_length + wall_thickness * 2
money_box_height = box_height - board_thickness

spacer_company_width = company_box_width
spacer_company_length = company_box_length
spacer_company_height = company_box_height

spacer_back_width = box_width
spacer_back_length = box_length - company_box_length - money_box_length - 1
spacer_back_height = box_height - board_thickness

# One kit configures the sliding-box type + shared basics for every company box.
COMPANY_KIT = BoxKit(SlidingBox, wall_thickness=wall_thickness, lid_thickness=lid_thickness)


# ---- Company box (5 of them) -----------------------------------------------------
def _company_contents(company):
    """The fitted interior of one company box, in the interior-local frame -- the
    port of the .scad CompanyBox children (card well, finger scoop, dividend-marker
    slot, train bay) plus the engraved company name."""

    def contents(inner):
        pieces = [
            # Card well: opens at the top, deep enough for `shares` share cards.
            InnerObject(
                s3.cuboid([card_width, card_length, company_box_height], anchor=BOTTOM + FRONT + LEFT).translate(
                    [0, 0, inner.height - single_card_thickness * company.shares - 1]
                ),
                ObjectType.NEGATIVE,
            ),
            # Finger scoop under the cards (breaches the floor so a finger gets under them).
            InnerObject(
                FingerHoleBase(radius=15, height=money_box_height).translate([card_width / 2, 0, -2]),
                ObjectType.NEGATIVE,
                clip=False,
            ),
            # Dividend-marker slot with two finger indents.
            InnerObject(
                CylinderWithIndents(
                    None, None, d=dividend_marker_diameter, h=company_box_height, anchor=BOTTOM,
                    finger_holes=[0, 180], finger_hole_radius=4,
                ).translate(
                    [card_width / 2, card_length + dividend_marker_diameter - 1.5,
                     inner.height - dividend_marker_thickness - 1]
                ),
                ObjectType.NEGATIVE,
            ),
            # Train bay: a block plus a rounded pocket beside it.
            InnerObject(
                s3.cuboid([train_length * 6, train_width * 4, company_box_height], anchor=BOTTOM + RIGHT).translate(
                    [inner.width - 8, inner.length - train_width * 3, inner.height - train_height - 0.5]
                ),
                ObjectType.NEGATIVE,
            ),
            InnerObject(
                RoundedBoxAllSides(
                    [train_length * 6 + 10, train_length * 4 + 20, company_box_height], radius=5
                ).translate(
                    [inner.width - 8 - train_length * 6 - 5,
                     inner.length - train_width * 3 - train_length * 2 - 10,
                     inner.height - train_height - 0.5 + train_height / 2]
                ),
                ObjectType.NEGATIVE,
            ),
        ]

        # Engraved company name across the card-well floor (revealed under the cards),
        # 0.2mm second colour, one line per row, rotated to read up the box.
        card_floor = inner.height - single_card_thickness * company.shares - 1
        n = len(company.name)
        font_size = 7.75
        for i, line in enumerate(company.name):
            x = card_width / 2 + i * (font_size + 1) - (n - 1) / 2 * (font_size + 1)
            pieces.append(
                EngravedLabel(
                    line, [x, card_length / 2 + 7, card_floor],
                    size=font_size, font="Brush Script MT", spin=90,
                )
            )
        return pieces

    return contents


def company_box(num=0):
    c = companies[num]
    return COMPANY_KIT.box(
        size=[company_box_width, company_box_length, company_box_height],
        label=f"CompanyBox{num}",
        material_colour=c.color,
        contents=_company_contents(c),
        lid=c.lid,
    )


# ---- Money box (sliding lid, interior laid out automatically) --------------------
# The three denomination slots are bin-packed by layout_compartments as one ROW of
# card wells, so every card finger hole lands on the SAME (front) wall. The box's
# LENGTH is the short dimension, so the sliding lid slides the short way. margin=0
# lets the 71mm-long cards fill the interior length (the box is card-sized in Y).
_money_contents = layout_compartments(
    [
        Group(
            [
                Compartment(
                    shape=Shape.RECT, w=card_width, l=card_length, is_card=True,
                    label=money_num[i], label_size=16, label_font="Impact",
                )
                for i in range(3)
            ]
        ),
    ],
    min_gap=4,
    margin=0,
)


def money_box():
    return SlidingBox(
        BoxSpec(
            size=[money_box_width, money_box_length, money_box_height],
            label="MoneyBox",
            wall_thickness=wall_thickness,
            lid_thickness=lid_thickness,
            lid="Bank",
            contents=_money_contents,
        )
    )


# ---- Spacers ---------------------------------------------------------------------
def spacer_box_back():
    path = [
        [company_box_width - 2, 0],
        [company_box_width - 2, company_box_length + 2],
        [box_width, company_box_length + 2],
        [box_width, box_length - money_box_length - 2],
        [0, box_length - money_box_length - 2],
        [0, 0],
    ]
    return (
        BoxSpec.box_builder()
        .size(box_width, box_length, spacer_back_height)
        .label("SpacerBoxBack")
        .wall_thickness(wall_thickness)
        .hollow(True)
        .path(path)
        .build()
    )


def spacer_box_company():
    return (
        BoxSpec.box_builder()
        .size(spacer_company_width, spacer_company_length, spacer_company_height)
        .label("SpacerBoxCompany")
        .wall_thickness(wall_thickness)
        .hollow(True)
        .no_lid()
        .build()
    )


# ---- `make` targets --------------------------------------------------------------
@make_box
def CompanyBoxBelfast():
    return company_box(0).make_box()


@make_box
def CompanyBoxCork():
    return company_box(1).make_box()


@make_box
def CompanyBoxMidland():
    return company_box(2).make_box()


@make_box
def CompanyBoxWaterford():
    return company_box(3).make_box()


@make_box
def CompanyBoxGreatSouthern():
    return company_box(4).make_box()


@make_box
def CompanyBoxLidBelfast():
    return company_box(0).make_lid()


@make_box
def CompanyBoxLidCork():
    return company_box(1).make_lid()


@make_box
def CompanyBoxLidMidland():
    return company_box(2).make_lid()


@make_box
def CompanyBoxLidWaterford():
    return company_box(3).make_lid()


@make_box
def CompanyBoxLidGreatSouthern():
    return company_box(4).make_lid()


@make_box
def MoneyBox():
    return money_box().make_box()


@make_box
def MoneyBoxLid():
    return money_box().make_lid()


@make_box
def SpacerBoxBack():
    return spacer_box_back().make_box()


@make_box
def SpacerBoxCompany():
    return spacer_box_company().make_box()


if FROM_MAKE != 1:
    CompanyBoxBelfast().show()
