# Types of lids

A few different types of lids that can be used with the system.

## Simple sliding lid

```openscad-3D;Big
include <boardgame_toolkit.scad>

SlidingLid(width = 100, length = 50);
```

## Sliding lid with label

```openscad-3D;Big
include <boardgame_toolkit.scad>

SlidingBoxLidWithLabel(
        width = 150, length = 50, lid_thickness = 3, text_width = 70,
        text_height = 20, text_str = "Happy Fluff", label_rotated = false);
```


## Simple tabbed lid

```openscad-3D;Big
include <boardgame_toolkit.scad>

InsetLidTabbed(width = 100, length = 50);
```


## Tabbed lid with label

```openscad-3D;Big
include <boardgame_toolkit.scad>

InsetLidTabbedWithLabel(
        width = 50, length = 150, lid_thickness = 3, text_width = 70,
        text_height = 20, text_str = "Happy Fluff", label_rotated = true);
```


## Sliding lid with map of australia

```openscad-3D;Big
include <boardgame_toolkit.scad>

SlidingBoxLidWithLabel(
        width = 50, length = 150, lid_thickness = 3, text_width = 70,
        text_height = 20, text_str = "Happy", label_rotated = true) {
        translate([ 45, 5, 0 ]) linear_extrude(height = 3) rotate([0,0,90]) scale(0.3) difference()
        {
            fill() import("svg/australia.svg");
            offset(-4) fill() import("svg/australia.svg");
        }
    };
```

### Capped box lid with label


Make a lid and base for a capped box.

```openscad-3D;Med
include <boardgame_toolkit.scad>

canvas_piece_box_width = 41;
canvas_piece_box_length = 73;
canvas_piece_box_height = 29;
wall_thickness = 3;

module MakeLid(str)
{
    CapBoxLidWithLabel(width = canvas_piece_box_width, length = canvas_piece_box_length,
                        text_width = len(str) * 10 + 5, text_height = 15, text_str = str, label_rotated = true,
                        wall_thickness = wall_thickness, lid_thickness = 2, lid_boundary = 5, layout_width = 5,
                        shape_type = SHAPE_TYPE_CIRCLE, shape_thickness = 2, shape_width = 7);
}
MakeLid("Red");
```
