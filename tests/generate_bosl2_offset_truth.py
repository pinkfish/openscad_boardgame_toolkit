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

"""Regenerate tests/bosl2_offset_truth.json -- ground truth from the REAL BOSL2 via osuse().

The fixture tests/test_bosl2_offset.py checks pybosl2.paths.offset() against. Needs the real app
plus the patched BOSL2 (see CLAUDE.md), and must run through the PythonSCAD binary because
osuse() only exists there:

    cd examples && TRUTH_OUT=../tests/bosl2_offset_truth.json FROM_MAKE=1 \
      BOSL2_SCAD_DIR=~/Documents/OpenSCAD/libraries-pythonscad-patched \
      /Applications/PythonSCAD-dev.app/Contents/MacOS/PythonSCAD --trust-python \
      --enable python-engine --backend Manifold --export-format 3mf -o /tmp/t.3mf \
      ../tests/generate_bosl2_offset_truth.py

The paths below are the shapes the toolkit actually offsets (a plain box outline, the concave
outline from the no_lid render tests, a hex, a 6-point spacer outline, a triangle) crossed with
every r/delta/chamfer variant it uses.
"""
import os, sys, json
_examples = os.getcwd(); _root = os.path.dirname(_examples)
for _p in (_examples, _root):
    if _p not in sys.path: sys.path.insert(0, _p)
from base_bgtk import *
import base_bgtk
b = base_bgtk._bosl2
def jl(x):
    try: return [jl(i) for i in x]
    except TypeError: return float(x)

PATHS = {
  "square":  [[0,0],[80,0],[80,60],[0,60]],
  "concave": [[0,0],[80,0],[80,30],[40,30],[40,60],[0,60]],
  "hex":     [[40.0,0.0],[20.0,34.641],[-20.0,34.641],[-40.0,0.0],[-20.0,-34.641],[20.0,-34.641]],
  "gulf":    [[63,0],[63,109],[0,109],[0,204],[71,204],[71,0]],
  "tri":     [[0,0],[50,0],[25,40]],
}
CASES = [
  ("r-2",        dict(r=-2)),
  ("r-1",        dict(r=-1)),
  ("r-3",        dict(r=-3)),
  ("r-1.5",      dict(r=-1.5)),
  ("r+2",        dict(r=2)),
  ("d-2",        dict(delta=-2)),
  ("d+2",        dict(delta=2)),
  ("d-2chamf",   dict(delta=-2, chamfer=True)),
  ("d+2chamf",   dict(delta=2, chamfer=True)),
]
out = []
for pname, path in PATHS.items():
    for cname, kw in CASES:
        try:
            out.append({"path": pname, "case": cname, "kw": kw, "res": jl(b.offset(path, **kw))})
        except Exception as e:
            out.append({"path": pname, "case": cname, "kw": kw, "err": str(e)[:100]})
open(os.environ["TRUTH_OUT"], "w").write(json.dumps({"paths": PATHS, "cases": out}, indent=1))
cube(1).show()
