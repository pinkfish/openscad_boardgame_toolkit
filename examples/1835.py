# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

#from bosl2 import cuboid
from pythonscad import union, cube, text
from cap_box import MakeBoxWithCapLid
from base_bgtk import InnerObject, InnerSize, ObjectType

box_length = 298;
box_width = 216;
box_height = 50;

default_wall_thickness = 2;
default_lid_thickness = 2;
default_floor_thickness = 2;

default_label_type = MAKE_MMU == 1 ? LABEL_TYPE_FRAMED_SOLID : LABEL_TYPE_FRAMED;

inner_wall = 1;

share_width = 46;
share_length = 66;
share_thickness_twenty = 7;
money_width = 52;
money_length = 98;
money_one_thickness = 5;
money_total = 22;
company_card_bmb_length = 151;
company_card_bmb_width = 106;
company_card_bmb_thickness_six = 2.5;
company_card_length = 200;
company_card_lenght = 131;
token_diameter = 6;
token_thickness = 2;
large_marker_diameter = 20;
large_marker_length = 41;
tile_width = 40;
tile_radius = tile_width / 2 / cos(180 / 6);
train_tile_thickness_10 = 6;
board_thickness = 15;

num_train_cards = 33;
num_shares = 68;
num_private_railroad = 6;

main_height = box_height - board_thickness;

hex_box_width = tile_radius * 6 + default_wall_thickness * 2;
hex_box_height = main_height / 4;
hex_box_length = box_width - 1;

money_box_width = box_width - 1;
money_box_length = money_length + default_wall_thickness * 2;
money_box_height_1 = default_floor_thickness + default_lid_thickness + money_one_thickness + 0.5;
money_box_height_2 = money_box_height_1 - 1;

money_names = ["1", "5", "10", "20", "50", "100", "200", "500"];
share_names = [
  "Bayerische Eisenbahn",
  "Sächsische Eisenbahn",
  "Badische Eisenbahn",
  "Württembergische",
  "Hessische Eisenbahn",
  "Preußische Eisenbahn",
  "Mecklenburg-Schwerin",
  "Oldenburgische",
];

shares_box_width = box_length - hex_box_width - money_box_length - 1;
shares_box_length = share_length * 2 + 3 * 2;

first_player_box_length = box_width - shares_box_length - 1;
first_player_box_width = shares_box_width;
first_player_box_height = large_marker_diameter + 4;

shares_height = main_height / 4;

middle_height = main_height - money_box_height_1 - money_box_height_2;
middle_width = money_box_length;
middle_length = money_box_width;

insert_width = middle_width - default_wall_thickness * 2;
insert_length = middle_length - default_wall_thickness * 3 - large_marker_diameter;
insert_height = middle_height - default_lid_thickness - default_floor_thickness;

spacer_box_width = first_player_box_width;
spacer_box_length = first_player_box_length;
spacer_box_height = main_height - first_player_box_height;

def MoneyBox1:
  def GenerateChildren(size: InnerSize): list[InnerObject]:  
    ret:list[InnerObject] = []
    for i in range(4):
       ret.append(
          InnerObject(value=
            cube([money_width, money_length, money_box_height_1]),
            type=ObjectType.NEGATIVE))
       ret.append(
              
              text(money_names[i], font="Stencil Std:style=Bold", anchor=CENTER).          
              translate([money_width / 2, money_length / 2, 0]))

            linear_extrude(height=0.2)
            FingerHoleBase(radius=10, height=$inner_height, spin=0).          translate([money_width / 2, 1.2, 0]) if show_everything
          ]).translate([(money_width + inner_wall) * i, 0, 0]))
  
  MakeBoxWithCapLid(
    size=[money_box_width, money_box_length, money_box_height_1],
    children=GenerateChildren
  ) {
    InnerPieces(show_everything=true);
    color("black") InnerPieces(show_everything=false);
  }
}
