include <BOSL2/std.scad>
include <boardgame_toolkit.scad>

box_width = 216;
box_length = 307;
box_height = 52;
wall_thickness = 2;
inner_wall = 1;

shield_width = 100;
shield_thickness = 14;
shield_middle = 145;
shield_length = 300;

laurel_diameter = 25;
laurel_thickness = 4;
laurel_num_ones = 60;
laurel_num_others = 42;

animal_max_width = 30;
animal_length = 42;
animal_thickness = 12;

armadillo_height = 41.5;
armadilli_width = 24.4262;
ibis_height = 42;
ibis_width = 21.8766;
tiger_height = 44;
tiger_width = 21.61;
marmoset_height = 40;
marmoset_width = 20.5183;
crocodile_height = 43.974;
crocodile_width = 30.6776;
peacock_height = 43.9974;
peacock_width = 26.2399;
hyena_height = 43.9976;
hyena_width = 21.0026;
rhino_height = 43.9974;
rhino_width = 23.3841;

special_token_diameter = 30;
special_token_length = 46;
special_token_stalk_width = 15;
special_token_gap = 2;
special_token_thickness = 4;
special_token_angle_length = special_token_stalk_width / sqrt(2);

laurel_box_height = laurel_diameter + wall_thickness * 2 + 1;
laurel_box_length = laurel_diameter * 2 + wall_thickness * 4 + inner_wall * 3;
laurel_box_width = laurel_thickness * laurel_num_others / 2 + 2;
laurel_wall_height = laurel_diameter * 3 / 4 + wall_thickness;

// cyl(d = laurel_diameter, h = laurel_thickness);

module SpecialToken()
{
    cyl(d = special_token_diameter, h = special_token_thickness, $fn = 128);
    difference()
    {
        cuboid(
            [ special_token_length - special_token_diameter / 2, special_token_stalk_width, special_token_thickness ],
            anchor = LEFT);
        translate([ special_token_length - special_token_diameter / 2, 0, 0 ]) rotate([ 0, 0, 45 ])
            cuboid([ special_token_angle_length, special_token_angle_length, special_token_thickness + 1 ]);
    }
}

module MarmosetOutline()
{
    resize([ marmoset_width, marmoset_height ]) import("svg/marmoset outline.svg");
}

module RhinoOutline()
{
    resize([ rhino_width, rhino_height ]) import("svg/rhino outline.svg");
}

module IbisOutline()
{
    resize([ ibis_width, ibis_height ]) import("svg/ibis outline.svg");
}

module TigerOutline()
{
    resize([ tiger_width, tiger_height ]) offset(delta = 0.001) import("svg/tiger outline.svg");
}

module HyenaOutline()
{
    resize([ hyena_width, hyena_height ]) import("svg/hyena outline.svg");
}

module AramdiloOutline()
{
    resize([ armadilli_width, armadillo_height ]) import("svg/armadillo outline.svg");
}

module PeacockOutline()
{
    resize([ peacock_width, peacock_height ]) import("svg/peacock outline.svg");
}

module CrocodileOutline()
{
    resize([ crocodile_width, crocodile_height ]) import("svg/crocodile outline.svg");
}

module StandingBox()
{
    total_height = (animal_thickness + inner_width) * 6 + wall_thickness * 3;

    difference()
    {
        cuboid(
            [
                animal_max_width + wall_thickness * 2, (animal_thickness + inner_width) * 6 + wall_thickness * 2,
                animal_length -
                wall_thickness
            ],
            anchor = BOTTOM + FRONT);
        for (i = [0:1:5])
        {
            translate([ 0, i * (animal_thickness + inner_width) + wall_thickness, wall_thickness ])
                cuboid([ animal_max_width, animal_thickness, animal_length ], anchor = BOTTOM + FRONT);
        }
        translate([ 0, total_height - 1, animal_length ]) rotate([ 90, 0, 0 ]) linear_extrude(height = total_height)
            ellipse([ animal_max_width / 2, animal_max_width * 3 / 4 ], $fn = 64);
    }
}

module Outline(height = 5, outline = 1.5, offset = 0.5)
{

    difference()
    {
        linear_extrude(height = 5) offset(1.5) children();
        translate([ 0, 0, -1 ]) linear_extrude(height = 10) offset(0.5) children();
    }
}

module AnimalOutlines()
{
    Outline() MarmosetOutline();
    translate([ 35, 0, 0 ]) Outline() HyenaOutline();
    translate([ 70, 0, 0 ]) Outline() PeacockOutline();
    translate([ 105, 0, 0 ]) Outline() RhinoOutline();
    translate([ 140, 0 ]) Outline() IbisOutline();
    translate([ 175, 0, 0 ]) Outline() AramdiloOutline();
    translate([ 210, 0, 0 ]) Outline() CrocodileOutline();
    translate([ 245, 0, 0 ]) Outline() TigerOutline();
}

module LaurelsBox()
{
    difference()
    {
        MakeBoxWithSlipoverLid(width = laurel_box_width, length = laurel_box_length, height = laurel_box_height,
                               wall_height = laurel_wall_height, foot = 2)
        {
            for (i = [0:1:2])
            {
                translate(
                    [ laurel_diameter * (i * 2 + 1) / 2 + inner_wall * i, laurel_diameter / 2, laurel_diameter / 2 ])
                    ycyl(h = laurel_box_width, d = laurel_diameter + 1, $fn = 64);
                translate(
                    [ laurel_diameter * (i * 2 + 1) / 2 + inner_wall * i, laurel_box_length / 2, laurel_diameter / 2 ])
                    cuboid([ laurel_diameter, laurel_box_length, laurel_diameter ], anchor = BOTTOM);
            };
        }
        for (i = [0:1:2])
            translate([
                laurel_diameter * (i * 2 + 1) / 2 + wall_thickness * 2 + m_piece_wiggle_room + inner_wall * i, 10,
                laurel_wall_height
            ]) ycyl(h = 200, d = laurel_diameter / 2);
    }

    text_str = "Laurels";
    text_width = 60;
    text_length = 20;

    translate([ laurel_box_width, 0, 0 ])
        SlipoverLidWithLabel(width = laurel_box_width, length = laurel_box_length, height = laurel_box_height,
                             text_width = text_width, text_length = text_length, text_str = text_str, foot = 2);
}

LaurelsBox();