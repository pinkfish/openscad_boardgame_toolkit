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

// LibFile: slicing.scad
//    This file has all the shared pieces for slicing a model into sections.

// FileSummary: Pieces for slicing a model into sections to print on smaller print areas.
// FileGroup: Slicing

// Includes:
//   include <boardgame_toolkit.scad>

// Section: Slicing
// Description:
//    Ways of slicing up the created objects so they can be printed in smaller bed spaces.

// Module: SplitBox()
// Topics: Slicing
// Description:
//   Slices up the box making a left and right part of the object.  First child is the object to slice up
//   second child is the piece to use for making the join (this should be in 2d).
// Usage: LeftRight() MakeBox() MakePuzzleJoin()
// Arguments:
//   width = width of the box
//   length = lenght of the box
//   height = height of the box
//   orient = orientation of the box (default UP)
//   spin = spin of the join point (default 0)
//   apart = how far apart to move the pieces on the split (default = 10)
//   minX = the minX to cut at (default = -200)
//   maxX = the maxX to cut at (default = 200)
//   minY = the minY to cut at (default = -200)
//   maxY = the maxY to cut at (default = 200)
//   minZ = the minZ to cut at (default = -200)
//   maxZ = the maxZ to cut at (default = 200)
//   play = the offset on the piece to add as play (default 0.1)
//   y = specific places to do the join points at (default [ minY : ( maxY - minY ) / 10 : maxY ])
// Example:
//   SplitBox(100, 50, 20, spin = 90) {
//        MakeBoxWithSlipoverLid(width = 100, length = 50, height = 20,
//            foot = 2, floor_thickness = 1.5, lid_thickness = 1.5, wall_thickness = 1.5)
//        {
//            cube(97, 47, 20);
//        }
//        MakePuzzleJoin();
//   }
// Example:
//   SplitBox(100, 50, 20, orient = LEFT, spin = 90) {
//        MakeBoxWithSlipoverLid(width = 100, length = 50, height = 20,
//            foot = 2, floor_thickness = 1.5, lid_thickness = 1.5, wall_thickness = 1.5)
//        {
//            cube(97, 47, 20);
//        }
//        MakePuzzleJoin();
//   }
// Example:
//   SplitBox(100, 50, 20, orient = FRONT) {
//        MakeBoxWithSlipoverLid(width = 100, length = 50, height = 20,
//        foot = 2, floor_thickness = 1.5, lid_thickness = 1.5, wall_thickness = 1.5)
//        {
//            cube(97, 47, 20);
//        }
//        MakePuzzleJoin();
//   }
module SplitBox(width, length, height, apart = 10, minX = -200, maxX = 200, minY = -200, maxY = 200, minZ = -200,
                maxZ = 200, play = .1, y = [], orient = UP, spin = 0)
{

    module Right(y, tmat)
    {
        difference()
        {
            intersection()
            {
                children(0);
                multmatrix(tmat) translate([ 0, minY, minZ ])
                {
                    cube([ maxX, maxY - minY, maxZ - minZ ]);
                }
            }

            for (yy = y)
            {
                y_pts = apply(tmat, [[ 0, yy, minZ ]]);
                translate(y_pts[0])
                {
                    multmatrix(tmat) minkowski()
                    {
                        linear_extrude(height = maxZ - minZ)
                        {
                            children(1);
                        };
                        sphere(r = play);
                    }
                }
            }
        }
    }

    module Left(y, tmat)
    {
        difference()
        {
            children(0);
            difference()
            {
                multmatrix(tmat) translate([ 0, minY, minZ ])
                {
                    cube([ maxX, maxY - minY, maxZ - minZ ]);
                }

                for (yy = y)
                {
                    y_pts = apply(tmat, [[ 0, yy, minZ ]]);
                    translate(y_pts[0])
                    {
                        multmatrix(tmat) linear_extrude(height = maxZ - minZ)
                        {
                            children(1);
                        }
                    }
                }
            }
        }
    }
    translate([ width / 2, length / 2, height / 2 ])
    {
        yy = len(y) == 0 ? [minY:(maxY - minY) / 10:maxY] : y;

        // geom = attach_geom(size = [ 1, 1, 1 ]);
        tmat = reorient(anchor = CENTER, spin = spin, orient = orient, size = [ 1, 1, 1 ]);
        new_pts = apply(tmat, [[apart / 2, 0, 0], [-apart / 2, 0, 0]]);

        translate(new_pts[0]) Right(y = yy, tmat = tmat)
        {
            translate([ -width / 2, -length / 2, -height / 2 ]) children(0);
            children(1);
        }

        translate(new_pts[1]) Left(y = yy, tmat = tmat)
        {
            translate([ -width / 2, -length / 2, -height / 2 ]) children(0);
            children(1);
        }
    }
}

// Module: MakePuzzleJoin()
// Topics: Slicing
// Description:
//   Makes a join like a puzzle piece.  This is the a way to join together two pieces of the system along the middle
//   line using the puzzle piece shape.
// Usage: MakePuzzleJoin()
// Arguments:
//   height = height of the piece (defaulg 10)
//   width = width of the piece (default 10)
//   base = base of the peice (default 5)
//   stem = stem of the piece (default 6)
// Example:
//   MakePuzzleJoin();
// Example:
//   MakePuzzleJoin(height = 20, width = 5, base = 10, stem = 5);
module MakePuzzleJoin(height = 10, width = 10, base = 5, stem = 6)
{
    union()
    {
        translate([ 0, -base / 2, 0 ]) square([ stem, base ]);

        translate([ stem, 0, 0 ]) scale([ (height - stem) * 2 / width, 1, 0 ])
        {
            circle(d = width); // looks clumsy but renders better
        }
    }
}