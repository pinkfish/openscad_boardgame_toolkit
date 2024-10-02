# openscad_boardgame_toolkit
Toolkit for use with openscad that makes designing inserts and other pieces easier for the openscad.

This will build inserts using openscad in an openscad forward way.  You use object building and connections
rather than a large config file to build the inserts.  This allows for more flexibility in arrangements.

This only works with the current dev versions of openscad since it uses the fill() method to handle some of the
construction.

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

![example1](https://github.com/pinkfish/openscad_boardgame_insert/blob/master/images/sweden_box.png)

```
SlidingBoxLidWithLabel(
        width = card_box_width, length = eastern_us_card_box_length, lid_height = lid_height, text_width = text_width,
        text_length = text_length, text_str = text_str, label_rotated = false);
```

![example1](https://github.com/pinkfish/openscad_boardgame_insert/blob/master/images/sweden_lid.png)
