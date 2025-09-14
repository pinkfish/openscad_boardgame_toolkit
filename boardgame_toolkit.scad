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

// LibFile: boardgame_toolkit.scad
//    This file has all the modules needed to generate varioius inserts
//    for board games.  It makes the generation of the inserts simpler by
//    creating a number of useful base modules for making boxes and lids
//    of various types specific to board game inserts.  Specifically it
//    makes tabbed lids and sliding lids easily.
//

// FileSummary: Various modules to generate board game inserts.

// Includes:
//   include <boardgame_toolkit.scad>

assert(version_num() >= 20190500, "boardgame_toolkit requires OpenSCAD version 2019.05 or later.");

include <BOSL2/std.scad>
include <BOSL2/joiners.scad>

// shared pieces.
include <base_bgtk.scad>
include <components.scad>
include <labels.scad>
include <lids_base.scad>

// Slicing - cutting up objects to print on smaller spaces
include <slicing.scad>

// Dividers
include <dividers.scad>

// boxes
include <cap_box.scad>
include <hinge_box.scad>
include <inset_box.scad>
include <magnetic_box.scad>
include <sliding_box.scad>
include <sliding_catch_box.scad>
include <slipover_box.scad>
include <no_lid.scad>
include <cap_box_polygon.scad>
include <slipover_path_box.scad>

// extra stuff
include <flags.scad>
include <shapes.scad>
include <shapes3d.scad>
include <pentagon_tilings.scad>
include <tesselations.scad>
include <penrose_tiling.scad>
