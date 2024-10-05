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
        width = 150, length = 50, lid_height = 3, text_width = 70,
        text_length = 20, text_str = "Happy Fluff", label_rotated = false);
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
        width = 50, length = 150, lid_height = 3, text_width = 70,
        text_length = 20, text_str = "Happy Fluff", label_rotated = true);
```


## Sliding lid with map of australia

```openscad-3D;Big
include <boardgame_toolkit.scad>

SlidingBoxLidWithLabel(
        width = 50, length = 150, lid_height = 3, text_width = 70,
        text_length = 20, text_str = "Happy", label_rotated = true) {
        translate([ 45, 5, 0 ]) linear_extrude(height = 3) rotate([0,0,90]) scale(0.3) difference()
        {
            fill() import("svg/australia.svg");
            offset(-4) fill() import("svg/australia.svg");
        }
    };
```
