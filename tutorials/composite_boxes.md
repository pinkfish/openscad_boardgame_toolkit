# More complicated boxes

- [More complicated boxes](#more-complicated-boxes)
  - [Box with two types of compartments](#box-with-two-types-of-compartments)
  - [Box with finger cutouts](#box-with-finger-cutouts)


## Box with two types of compartments

Create a sliding lid box with more complicated cutouts, a hex grid and spaces for specific sized items.  This also adds in 
some finger cutouts to get the items out.


```openscad-3D;Big
include <boardgame_toolkit.scad>

wall_thickness = 2;

sweden_box_width = 138;
sweden_box_length = 108;
sweden_bonus_length = 35;
sweden_bonus_width = 16;
tile_thickness = 2;
top_section_height = 20;
lid_height = 3;
tile_width = 29;

module SwedenBox()
{
    apothem = tile_width / 2;
    radius = apothem / cos(180 / 6);

    MakeBoxWithSlidingLid(width = sweden_box_width, length = sweden_box_length, height = top_section_height,
                          lid_height = lid_height, wall_thickness = wall_thickness)
    {
        translate([ wall_thickness, wall_thickness, wall_thickness ]) intersection()
        {
            translate([ 0, 0, -3 ]) cube([ radius * 4 * 2, tile_width * 3, top_section_height + 1 ]);
            HexGridWithCutouts(rows = 4, cols = 3, tile_width = tile_width, spacing = 0,
                               wall_thickness = wall_thickness, push_block_height = 0.75, height = top_section_height);
        }
        // bonus bit (top)
        translate([
            wall_thickness * 2, sweden_box_length - wall_thickness - sweden_bonus_width,
            top_section_height - lid_height - tile_thickness * 2.4
        ]) cube([ sweden_bonus_length, sweden_bonus_width, tile_thickness * 2.5 ]);
        translate([
            wall_thickness * 2 + (sweden_bonus_length - 10) / 2,
            sweden_box_length - wall_thickness - sweden_bonus_width - 5,
            top_section_height - lid_height - tile_thickness * 2.4
        ]) cube([ 10, 10, 10 ]);

        // bonus bit (middle)
        translate([
            sweden_box_width - wall_thickness * 2 - sweden_bonus_length,
            sweden_box_length - wall_thickness - sweden_bonus_width,
            top_section_height - lid_height - tile_thickness * 2.4
        ]) cube([ sweden_bonus_length, sweden_bonus_width, tile_thickness * 2.5 ]);
        translate([
            sweden_box_width - wall_thickness * 2 - sweden_bonus_length + (sweden_bonus_length - 10) / 2,
            sweden_box_length - wall_thickness - sweden_bonus_width - 5,
            top_section_height - lid_height - tile_thickness * 2.4
        ]) cube([ 10, 10, 10 ]);

        // bonus bit (bottom)
        translate([
            (sweden_box_width - wall_thickness * 2 - sweden_bonus_length) / 2,
            sweden_box_length - wall_thickness - sweden_bonus_width,
            top_section_height - lid_height - tile_thickness * 2.4
        ]) cube([ sweden_bonus_length, sweden_bonus_width, tile_thickness * 2.5 ]);
        translate([
            (sweden_box_width - wall_thickness * 2 - sweden_bonus_length) / 2 + (sweden_bonus_length - 10) / 2,
            sweden_box_length - wall_thickness - sweden_bonus_width - 5,
            top_section_height - lid_height - tile_thickness * 2.4
        ]) cube([ 10, 10, 10 ]);
    }
    text_str = "Sweden";
    text_width = 80;
    text_length = 20;
    translate([ sweden_box_width + 10, 0, 0 ]) SlidingBoxLidWithLabel(
        width = sweden_box_width, length = sweden_box_length, lid_height = lid_height, text_width = text_width,
        text_length = text_length, text_str = text_str, label_rotated = false);
}

SwedenBox();
```

## Box with finger cutouts

