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

# LibFile: examples/earth_animal_kingdom.py
#    PythonSCAD port of earth_animal_kingdom.scad.
#    Uses layout_compartments with custom 2D packed solids to fit in 2 boxes.

from base_bgtk import FROM_MAKE, MAKE_MMU, InnerObject, LabelType, make_box, ObjectType
from box_base import BoxSpec, Label, Lid
from components import FingerHoleBase, RoundedBoxAllSides
from labels import MakeLabelOptions
from shape_type import ShapeType
from compartments import Compartment, Group, Shape, Removal, PackingBin, layout_compartments
import pybosl2 as s3

# ---- Retail box & constants --------------------------------------------------
box_width = 288
box_length = 158
box_height = 47

default_wall_thickness = 2.0
default_floor_thickness = 2.0
default_lid_thickness = 2.0

default_label_type = LabelType.FRAMED_SOLID if MAKE_MMU == 1 else LabelType.FRAMED
default_lid_shape_type = ShapeType.BIRD
default_lid_shape_width = 20
default_lid_shape_thickness = 1.5

score_pad_width = 81
score_pad_length = 99
score_pad_thickness = 5
score_pad_number = 1

canopies_num = 20
animal_token_thickness = 8.0

sprout_cube_width = 8
sprout_cube_number = 50

animal_card_num = 36
card_10_thickness = 6
single_card_thickness = card_10_thickness / 10.0

# 72 x 123 card size
card_box_width = default_wall_thickness * 2 + 72
card_box_length = box_length - 2
animal_cards_height = single_card_thickness * animal_card_num + 2

score_pad_box_width = score_pad_width + default_wall_thickness * 4
score_pad_box_length = box_length - card_box_length * 2 - 1
score_pad_box_height = score_pad_thickness * score_pad_number + default_floor_thickness

sprout_box_length = box_length
sprout_box_width = card_box_width
sprout_box_height = box_height - animal_cards_height - 1

canopy_box_length = box_length
canopy_box_width = 38
canopy_box_height = box_height - 1

animal_box_width = box_width - card_box_width - 38
animal_box_length = box_length
animal_box_height = default_floor_thickness + default_lid_thickness + animal_token_thickness + 0.5

spacer_box_width = animal_box_width
spacer_box_length = animal_box_length
spacer_box_height = box_height - animal_box_height * 2 - 1

# ---- Items list (name, width, length, num) -----------------------------------
ANIMAL_PIECES = [
    ("elephant", 43.5, 54.0, 1),
    ("polar_bear", 36.5, 53.0, 1),
    ("cow", 36.5, 47.5, 1),
    ("pig", 24.5, 35.0, 1),
    ("gazelle", 41.0, 35.0, 1),
    ("turkey", 24.0, 25.0, 5),
    ("fly", 11.0, 11.0, 1),
    ("capybara", 16.5, 32.0, 2),
    ("capybara_2", 16.5, 32.0, 3),
    ("monkey", 29.0, 24.0, 1),
    ("pangolin", 16.0, 21.0, 5),
    ("deer", 47.0, 25.5, 1),
    ("goanna", 25.0, 30.0, 1),
    ("fox", 16.0, 35.0, 1),
    ("snake", 14.0, 41.5, 1),
    ("rabbit", 18.5, 21.0, 1),
    ("termite", 12.0, 12.0, 5),
    ("ornyx", 39.0, 40.0, 1),
    ("platypus", 14.5, 25.0, 1),
    ("lemur", 22.0, 30.0, 1),
    ("peacock", 30.0, 27.0, 1),
    ("gopher", 17.5, 17.0, 5),
    ("crocodile", 16.0, 85.0, 1),
    ("goat", 37.0, 36.0, 1),
    ("jaguar", 20.0, 49.0, 1),
    ("rhino", 36.0, 64.0, 1),
    ("goose", 25.0, 21.0, 1),
    ("eagle", 31.0, 43.0, 1),
    ("spider_monkey", 26.5, 25.0, 1),
    ("hoopoe", 17.0, 16.0, 1),
    ("kangaroo", 37.0, 39.0, 1),
    ("loon", 26.5, 13.0, 1),
    ("tarsier", 29.0, 12.5, 1),
    ("jay", 12.5, 12.0, 1),
    ("chipmunk", 15.0, 14.0, 1),
    ("quokka", 24.0, 15.0, 1),
    ("beaver", 15.5, 35.0, 1),
]

_PACKING_SOLUTION = None
_METADATA = None

# ---- Load & Run Hyperpack ----------------------------------------------------
def get_layout(container_id: str):
    global _PACKING_SOLUTION, _METADATA
    
    if _PACKING_SOLUTION is None:
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            
            spacing = 3.0
            container_w = 170.0
            container_l = 152.0
            
            # Build items and metadata
            items = {}
            metadata = {}
            for name, w, l, num in ANIMAL_PIECES:
                if num > 1:
                    items[name] = {
                        "w": int((w + spacing / 2.0) * 10),
                        "l": int((l * num + spacing / 2.0) * 10)
                    }
                    metadata[name] = {"num": num, "w": w, "l": l, "ltotal": l * num}
                else:
                    items[name] = {
                        "w": int((w + spacing / 2.0) * 10),
                        "l": int((l + spacing / 2.0) * 10)
                    }
                    metadata[name] = {"num": 1, "w": w, "l": l}
            
            containers = {
                "container0": {"W": int((container_w - spacing) * 10), "L": int((container_l - spacing) * 10)},
                "container1": {"W": int((container_w - spacing) * 10), "L": int((container_l - spacing) * 10)}
            }
            
            from hyperpack import HyperPack
            problem = HyperPack(containers=containers, items=items, settings={"rotation": True})
            problem.hypersearch()
            
            _PACKING_SOLUTION = problem.solution
            _METADATA = metadata

    spacing = 3.0
    sol = _PACKING_SOLUTION.get(container_id, {})
    layout_objs = []
    
    for name, rect in sol.items():
        # rect: [x, y, w_packed, l_packed]
        x, y, wp, lp = rect
        meta = _METADATA[name]
        
        # Position calculations
        x_pos = (x + spacing * 5.0 + wp / 2.0) / 10.0
        y_pos = (y + spacing * 5.0 + lp / 2.0) / 10.0
        
        # Rotation detection: if packed width is total length of item
        is_rotated = False
        if "ltotal" in meta:
            if abs(wp - int((meta["ltotal"] + spacing / 2.0) * 10)) <= 2:
                is_rotated = True
        else:
            if abs(wp - int((meta["l"] + spacing / 2.0) * 10)) <= 2:
                is_rotated = True
        
        # Build negative cuboids for the tokens
        num = meta["num"]
        item_w = meta["w"]
        item_l = meta["l"]
        
        if num > 1:
            for i in range(num):
                offset = (i - num / 2.0 + 0.5) * (item_l + spacing)
                if is_rotated:
                    c = s3.cuboid([item_l, item_w, animal_token_thickness + 1.0], rounding=1, edges=s3.Anchor.Z, anchor=s3.BOTTOM)
                    c = c.translate([x_pos + offset, y_pos, 0])
                    layout_objs.append(c)
                    
                    t = s3.text(name.replace("_", " ").title(), size=4, halign="center", valign="center").linear_extrude(height=0.201)
                    t = t.translate([x_pos + offset, y_pos, -0.2])
                    layout_objs.append(t)
                else:
                    c = s3.cuboid([item_w, item_l, animal_token_thickness + 1.0], rounding=1, edges=s3.Anchor.Z, anchor=s3.BOTTOM)
                    c = c.translate([x_pos, y_pos + offset, 0])
                    layout_objs.append(c)
                    
                    t = s3.text(name.replace("_", " ").title(), size=4, halign="center", valign="center").linear_extrude(height=0.201)
                    t = t.translate([x_pos, y_pos + offset, -0.2])
                    layout_objs.append(t)
        else:
            if is_rotated:
                c = s3.cuboid([item_l, item_w, animal_token_thickness + 1.0], rounding=1, edges=s3.Anchor.Z, anchor=s3.BOTTOM)
                c = c.translate([x_pos, y_pos, 0])
                layout_objs.append(c)
                
                t = s3.text(name.replace("_", " ").title(), size=4, halign="center", valign="center").linear_extrude(height=0.201)
                t = t.translate([x_pos, y_pos, -0.2])
                layout_objs.append(t)
            else:
                c = s3.cuboid([item_w, item_l, animal_token_thickness + 1.0], rounding=1, edges=s3.Anchor.Z, anchor=s3.BOTTOM)
                c = c.translate([x_pos, y_pos, 0])
                layout_objs.append(c)
                
                t = s3.text(name.replace("_", " ").title(), size=4, halign="center", valign="center").linear_extrude(height=0.201)
                t = t.translate([x_pos, y_pos, -0.2])
                layout_objs.append(t)
                
    return layout_objs

def make_custom_compartment(container_id, inner_w, inner_l):
    import functools
    import operator
    layout_objs = get_layout(container_id)
    # Center the solid around origin (0,0) based on container size (170 x 152)
    translated = [obj.translate([-170.0 / 2.0, -152.0 / 2.0, 0]) for obj in layout_objs]
    solid = functools.reduce(operator.or_, translated)
    return Compartment(
        shape=Shape.CUSTOM,
        w=inner_w - 4.0,
        l=inner_l - 4.0,
        solid=solid,
        removal=Removal.NONE,
        depth=animal_token_thickness
    )

# ---- Boxes -------------------------------------------------------------------
_animal_cards_box = (
    BoxSpec.box_builder()
    .size(card_box_width, card_box_length, animal_cards_height)
    .label("PiecesBox")
    .wall_thickness(default_wall_thickness)
    .lid_thickness(default_lid_thickness)
    .contents(lambda inner: [
        InnerObject(s3.cube([72, 123, animal_cards_height])),
        InnerObject(
            FingerHoleBase(radius=17, height=animal_cards_height - default_lid_thickness, spin=0)
            .translate([inner.width / 2, 0, -2]),
            type=ObjectType.NEGATIVE
        )
    ])
    .lid_label("Animal Cards", options=MakeLabelOptions(label_type=default_label_type))
    .sliding()
    .build()
)

_sprout_box = (
    BoxSpec.box_builder()
    .size(sprout_box_width, sprout_box_length, sprout_box_height)
    .label("SproutBox")
    .wall_thickness(default_wall_thickness)
    .floor_thickness(default_floor_thickness)
    .lid_thickness(default_lid_thickness)
    .hollow(False)
    .contents(lambda inner: [
        InnerObject(
            s3.cuboid([inner.width, inner.length, sprout_box_height], anchor=s3.BOTTOM)
            & RoundedBoxAllSides([inner.width - 2, inner.length - 2, sprout_box_height], radius=5).translate([1, 1, 0]),
            type=ObjectType.NEGATIVE
        )
    ])
    .lid_label("Sprouts", options=MakeLabelOptions(label_type=default_label_type))
    .filament_hinge()
    .build()
)

_canopy_box = (
    BoxSpec.box_builder()
    .size(canopy_box_width, canopy_box_length, canopy_box_height)
    .label("CanopyBox")
    .wall_thickness(default_wall_thickness)
    .floor_thickness(default_floor_thickness)
    .lid_thickness(default_lid_thickness)
    .hollow(False)
    .contents(lambda inner: [
        InnerObject(
            s3.cuboid([inner.width, inner.length, canopy_box_height], anchor=s3.BOTTOM)
            & RoundedBoxAllSides([inner.width - 2, inner.length - 2, canopy_box_height], radius=5).translate([1, 1, 0]),
            type=ObjectType.NEGATIVE
        )
    ])
    .lid_label("Canopies", options=MakeLabelOptions(label_type=default_label_type))
    .filament_hinge()
    .build()
)

_animal_box = (
    BoxSpec.box_builder()
    .size(animal_box_width, animal_box_length, animal_box_height)
    .label("AnimalBox")
    .wall_thickness(1.5)
    .floor_thickness(default_floor_thickness)
    .lid_thickness(default_lid_thickness)
    .hollow(False)
    .contents(lambda inner: [
        # Large upper cutout
        InnerObject(
            RoundedBoxAllSides([inner.width - 2, inner.length - 2, animal_box_height], radius=3)
            .translate([1, 1, inner.height - animal_token_thickness / 2.0]),
            type=ObjectType.NEGATIVE
        )
    ] + layout_compartments([
        Group([make_custom_compartment("container0", inner.width, inner.length)])
    ])(inner))
    .lid_label("Animals", options=MakeLabelOptions(label_type=default_label_type))
    .lid_shape_type(default_lid_shape_type)
    .lid_shape_width(default_lid_shape_width)
    .lid_shape_thickness(default_lid_shape_thickness)
    .slipover()
    .build()
)

_animal_box_2 = (
    BoxSpec.box_builder()
    .size(animal_box_width, animal_box_length, animal_box_height)
    .label("AnimalBox2")
    .wall_thickness(1.5)
    .floor_thickness(default_floor_thickness)
    .lid_thickness(default_lid_thickness)
    .hollow(False)
    .contents(lambda inner: [
        # Large upper cutout
        InnerObject(
            RoundedBoxAllSides([inner.width - 2, inner.length - 2, animal_box_height], radius=3)
            .translate([1, 1, inner.height - animal_token_thickness / 2.0]),
            type=ObjectType.NEGATIVE
        )
    ] + layout_compartments([
        Group([make_custom_compartment("container1", inner.width, inner.length)])
    ])(inner))
    .lid_label("Animals", options=MakeLabelOptions(label_type=default_label_type))
    .lid_shape_type(default_lid_shape_type)
    .lid_shape_width(default_lid_shape_width)
    .lid_shape_thickness(default_lid_shape_thickness)
    .slipover()
    .build()
)

_spacer_box = (
    BoxSpec.box_builder()
    .size(spacer_box_width, spacer_box_length, spacer_box_height)
    .label("SpacerBox")
    .wall_thickness(default_wall_thickness)
    .floor_thickness(default_floor_thickness)
    .hollow(True)
    .no_lid()
    .build()
)

@make_box
def AnimalCardsBox():
    return _animal_cards_box.make_box()

@make_box
def AnimalCardsBoxLid():
    return _animal_cards_box.make_lid()

@make_box
def SproutBox():
    return _sprout_box.make_box()

@make_box
def SproutBoxLid():
    return _sprout_box.make_lid()

@make_box
def CanopyBox():
    return _canopy_box.make_box()

@make_box
def CanopyBoxLid():
    return _canopy_box.make_lid()

@make_box
def AnimalBox():
    return _animal_box.make_box()

@make_box
def AnimalBoxLid():
    return _animal_box.make_lid()

@make_box
def AnimalBox2():
    return _animal_box_2.make_box()

@make_box
def AnimalBox2Lid():
    return _animal_box_2.make_lid()

@make_box
def SpacerBox():
    return _spacer_box.make_box()
