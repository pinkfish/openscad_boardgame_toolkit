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