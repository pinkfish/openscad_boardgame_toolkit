# openscad_boardgame_toolkit
Toolkit for use with openscad that makes designing inserts and other pieces easier for the openscad.

[API Docs](https://github.com/pinkfish/openscad_boardgame_toolkit/wiki)

## Description
This will build inserts using openscad in an openscad forward way.  You use object building and connections
rather than a large config file to build the inserts.  This allows for more flexibility in arrangements.

This only works with the current dev versions of openscad since it uses the fill() method to handle some of the
construction.

## Installation
Pre-requisite for using this toolkit is to install [BSOL2](https://github.com/BelfrySCAD/BOSL2/wiki).

Copy the boardgame_toolkit.scad file into the same directory as the inserts you wish to create, you can also
install it into the shared directory on the mac or windows to use with all flows and no need to import directly.

## Examples
Some simple apis for building a board game insert.  Shows a simple sliding box design, lid and box.

```
MakeBoxWithSlidingLid(width = card_box_width, length = eastern_us_card_box_length,
                                  height = all_boxes_height, lid_height = lid_height, wall_thickness = wall_thickness)
            {
                translate([ wall_thickness, wall_thickness, wall_thickness ]) cube([
                    card_box_width - wall_thickness * 2, eastern_us_card_box_length - wall_thickness * 2,
                    all_boxes_height -
                    lid_height
                ]);
            }
```

![Example 1](https://github.com/pinkfish/openscad_boardgame_toolkit/blob/1551a84035fcff4df72fa05b08b7e455c29a6249/images/sweden_box.png)

```
SlidingBoxLidWithLabel(
        width = card_box_width, length = eastern_us_card_box_length, lid_height = lid_height, text_width = text_width,
        text_length = text_length, text_str = text_str, label_rotated = false);
```

![Example 2](https://github.com/pinkfish/openscad_boardgame_toolkit/blob/98951343adbd1eb39ea67898d21e884ff3710134/images/sweden_lid.png)
