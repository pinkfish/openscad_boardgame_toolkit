# More complicated boxes

- [More complicated boxes](#more-complicated-boxes)
  - [Box with two types of compartments](#box-with-two-types-of-compartments)
  - [Sliding lid by parts](#sliding-lid-by-parts)
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

## Sliding lid by parts

Generating a sliding lid using all the component parts of the lid, the lid, the label
the mesh and finger cutout.

```openscad-3D;Big

herald_width = 40;
top_length = 100;

SlidingLid(herald_width, top_length)
{
    translate([ 10, 10, 0 ])
        LidMeshHex(width = herald_width, length = top_length, lid_height = 3, boundary = 10, radius = 5);
    translate([ (herald_width + 15) / 2, (top_length - 50) / 2, 0 ]) rotate([ 0, 0, 90 ])
        MakeStripedLidLabel(width = 50, length = 15, lid_height = 3, label = "Herald", border = 2, offset = 4);
    intersection()
    {
        cube([ herald_width - 10, top_length - 5, 3 ]);
        translate([ (herald_width) / 2, top_length - 3, 0 ]) SlidingLidFingernail(3);
    }
}
```

## Box with finger cutouts

```openscad-3D;Big

train_card_thickness = 2;
player_box_width = 95.33;
player_box_length = 185;
player_box_height = 26.5;
card_height = train_card_thickness * 4.5;
wall_thickness = 2;
lid_height = 3;
inner_wall = 1;
silo_piece_width = 22;
silo_piece_height = 40;
water_height = 27;
water_width = 21;
roundhouse_height = 40;
roundhouse_total_width = 90;


difference()
{
    MakeBoxWithSlidingLid(width = player_box_width, length = player_box_length, height = player_box_height,
                            lid_height = lid_height, wall_thickness = wall_thickness)
    {
        // Roundhouse section
        translate([ wall_thickness, wall_thickness, wall_thickness ])
            cube([ player_box_width - wall_thickness * 2, roundhouse_height, player_box_height ]);
        // water towers.
        translate([ wall_thickness, wall_thickness + roundhouse_height + inner_wall, wall_thickness ]) cube([
            player_box_width - wall_thickness * 2 - water_width - inner_wall, silo_piece_height * 2,
            player_box_height
        ]);
        // silos.
        translate([
            player_box_width - wall_thickness * 2 - water_width + inner_wall,
            wall_thickness + roundhouse_height + inner_wall,
            wall_thickness
        ]) cube([ water_width, silo_piece_height * 2, player_box_height ]);
        // Train cards.
        translate([
            wall_thickness,
            wall_thickness + roundhouse_height + inner_wall * 2 + silo_piece_height * 2,
            player_box_height - lid_height - card_height,
        ]) cube([ player_box_width - wall_thickness * 2, train_card_length, player_box_height ]);
        // Recessed box for crossings.
        translate([
            player_box_width * 1 / 8,
            wall_thickness + roundhouse_height + inner_wall * 2 + silo_piece_height * 2 + 7,
            wall_thickness,
        ]) cube([ player_box_width * 3 / 4, crossing_length * 1.25, crossing_height ]);
    };
    // Finger cutout for cards
    translate([
        0,
        wall_thickness + roundhouse_height + inner_wall * 2 + silo_piece_height * 2 + crossing_length * 1.25 / 2 +
            7,
        0
    ]) cyl(h = player_box_height * 2 + 1, r = 10);
}
text_str = "Player";
text_width = 80;
text_length = 30;
translate([ player_box_width + 10, 0, 0 ]) SlidingBoxLidWithLabel(
    width = player_box_width, length = player_box_length, lid_height = lid_height, text_width = text_width,
    text_length = text_length, text_str = text_str, label_rotated = true);
```