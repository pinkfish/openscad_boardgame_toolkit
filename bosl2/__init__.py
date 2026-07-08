# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

# LibFile: bosl2/__init__.py
#    Python ports of the BOSL2 OpenSCAD library, one file per wrapped/ported
#    .scad file, so each Python file can be read side by side with its .scad
#    source:
#      bosl2/constants.py    <- BOSL2/constants.scad   (pure Python)
#      bosl2/math.py         <- BOSL2/math.scad         (pure Python)
#      bosl2/vectors.py      <- BOSL2/vectors.scad      (pure Python)
#      bosl2/lists.py        <- BOSL2/lists.scad        (pure Python)
#      bosl2/comparisons.py  <- BOSL2/comparisons.scad  (pure Python)
#      bosl2/geometry.py     <- BOSL2/geometry.scad     (pure Python, partial)
#      bosl2/paths.py        <- BOSL2/paths.scad        (pure Python)
#      bosl2/shapes2d.py     <- BOSL2/shapes2d.scad     (pure Python)
#      bosl2/shapes3d.py     <- BOSL2/shapes3d.scad     (thin osuse() wrapper)
#
#    shapes3d.py is a thin wrapper that forwards every call to BOSL2 already
#    loaded via osuse() -- it only works inside the real PythonSCAD app.
#    Every other file here, including shapes2d.py, is a real, standalone
#    port with no osuse()/BOSL2 runtime dependency at all, so it works in
#    plain Python (useful for testing) as well as inside PythonSCAD:
#    shapes2d.py computes each shape's outline in pure Python and then
#    builds it with direct openscad primitive calls (square()/circle()/
#    polygon()/text()/hull()/.offset()) instead of delegating to BOSL2.
#
#    Names like square(), circle(), cube() and text() in shapes2d/shapes3d
#    intentionally shadow the plain OpenSCAD builtins with BOSL2's
#    anchor/spin/orient-aware versions, so this package is always imported
#    by submodule (`from bosl2 import shapes3d`) rather than re-exported
#    with a wildcard here. Submodules are also deliberately NOT imported
#    eagerly below: shapes3d.py calls osuse() at import time and would
#    raise outside the real PythonSCAD app, which would otherwise break
#    `from bosl2 import <pure-python-module>` too.
#
# FileSummary: BOSL2 library ports, one file per wrapped/ported .scad file.
# FileGroup: BOSL2
