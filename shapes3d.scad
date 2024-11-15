/**
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
 */

// LibFile: shapes3d.scad
//    This file has all the modules needed to make various 3d shapes.

include <BOSL2/polyhedra.scad>

// FileSummary: 3d Shapes for all sorts of things.
// FileGroup: Shapes3d

// Includes:
//   include <boardgame_toolkit.scad>

// Section: Shapes3d
//    3d shapes to use in boxes and stuff.

// Module: Dodecahedron()
// Description:
//   Creates a 12 sided dice/shape for use in things.
// Arguments:
//   size = the width of the do-decahedron
// Topics: Dice
// Example:
//   Dodecahedron(20);
module Dodecahedron(size)
{
    dihedral = 116.565;
    scale([ size, size, size ]) // scale by height parameter
    {
        intersection()
        {
            // make a cube
            cuboid([ 2, 2, 1 ]);
            intersection_for(i = [0:4]) // loop i from 0 to 4, and intersect results
            {
                // make a cube, rotate it 116.565 degrees around the X axis,
                // then 72*i around the Z axis
                rotate([ 0, 0, 72 * i ]) rotate([ dihedral, 0, 0 ]) cuboid([ 2, 2, 1 ]);
            }
        }
    }
}

// Module: Tetrahedron()
// Description:
//   Makes a nice d4 shape for use in games.
// Arguments:
//   size = the diameter of the dice, it fits inside this sphere.
// Topics: Dice
// Example:
//   Tetrahedron(10);
module Tetrahedron(size)
{
    side = sqrt(3) * size / 2;
    h = sqrt(2 / 3) * side;
    translate([ -(size - side) / 2, 0, (size - side) / 2 ])
    {
        cyl(d1 = size, d2 = 0, h = h, $fn = 3);
    }
}

// Module: Octahedron()
// Description:
//   Makes a nice d8 shape for use in games.
// Arguments:
//   size = the diameter of the dice, it fits inside this sphere.
// Topics: Dice
// Example:
//   Octahedron(10);
module Octahedron(size)
{
    octahedron(size = size);
}

// Module: Icosahedron()
// Description:
//   Makes a nice d20 shape for use in games.
// Arguments:
//   size = the diameter of the dice, it fits inside this sphere.
// Topics: Dice
// Example:
//   Icosahedron(10);
module Icosahedron(size)
{
    phi = 0.5 * (sqrt(5) + 1); // golden ratio
    edge_length = size / 2 / 0.951;
    st = 0.0001; // microscopic sheet thickness
    hull()
    {
        cube([ edge_length * phi, edge_length, st ], true);
        rotate([ 90, 90, 0 ]) cube([ edge_length * phi, edge_length, st ], true);
        rotate([ 90, 0, 90 ]) cube([ edge_length * phi, edge_length, st ], true);
    }
}

// Module: Trapezohedron()
// Description:
//   Makes a nice d10 shape for use in games.
// Arguments:
//   size = the diameter of the dice, it fits inside this sphere.
// Topics: Dice
// Example:
//   Trapezohedron(10);
// Example:
//   Trapezohedron(20)
//   {
//      down(.3) linear_extrude(height = 1) text(str($faceindex), halign = "center", valign = "center", size = 5);
//   }
module Trapezohedron(size, length_mod = 0)
{
    difference()
    {
        regular_polyhedron("trapezohedron", faces = 10, d = size, h = size / 2, facedown = false);
        regular_polyhedron("trapezohedron", faces = 10, d = size, h = size / 2, facedown = false, draw = false,
                           rotate_children = true)
        {
            if ($faceindex == 1 || $faceindex == 3 || $faceindex == 8 || $faceindex == 9)
            {
                rotate(-30) children();
            }
            else if ($faceindex == 0 || $faceindex == 6)
            {
                rotate(15) children();
            }
            else
            {
                rotate(240) children();
            }
        }
    }
}