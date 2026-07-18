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

"""Regenerate tests/bosl2_truth.json -- ground truth from the REAL BOSL2 via osuse().

This is the fixture tests/test_bosl2_reorient.py checks the pure-Python reorient/apply/arc
against. It needs the real app plus the patched BOSL2 (see CLAUDE.md), and must be run through
the PythonSCAD binary because osuse() only exists there:

    cd examples && TRUTH_OUT=../tests/bosl2_truth.json FROM_MAKE=1 \
      BOSL2_SCAD_DIR=~/Documents/OpenSCAD/libraries-pythonscad-patched \
      /Applications/PythonSCAD-dev.app/Contents/MacOS/PythonSCAD --trust-python \
      --enable python-engine --backend Manifold --export-format 3mf -o /tmp/t.3mf \
      ../tests/generate_bosl2_truth.py

The toolkit itself no longer calls osuse() for these; this script is the only remaining user,
kept solely so the fixture can be re-derived if BOSL2's semantics ever change.
"""
import os, sys, json
_examples = os.getcwd(); _root = os.path.dirname(_examples)
for _p in (_examples, _root):
    if _p not in sys.path: sys.path.insert(0, _p)
from base_bgtk import *
import base_bgtk

b = base_bgtk._bosl2
out = {"reorient": [], "apply": [], "arc": []}

ANCH = {"CENTER": CENTER, "BOTTOM": BOTTOM, "TOP": TOP,
        "BFL": BOTTOM+FRONT+LEFT, "TRB": TOP+RIGHT+BACK, "LEFT": LEFT}
ORI = {"TOP": TOP, "BOTTOM": BOTTOM, "LEFT": LEFT, "RIGHT": RIGHT, "FRONT": FRONT, "BACK": BACK}

def jl(x):
    try: return [jl(i) for i in x]
    except TypeError: return float(x)

for an, av in ANCH.items():
    for on, ov in ORI.items():
        for spin in (0, 45, 90, 180):
            for size in ([1,1,1], [10,20,30]):
                try:
                    m = b.reorient(anchor=av, spin=spin, orient=ov, size=size)
                    out["reorient"].append({"anchor": an, "orient": on, "spin": spin,
                                            "size": size, "m": jl(m)})
                except Exception as e:
                    out["reorient"].append({"anchor": an, "orient": on, "spin": spin,
                                            "size": size, "err": str(e)})

# apply: reuse a couple of matrices
m1 = b.reorient(anchor=CENTER, spin=30, orient=LEFT, size=[1,1,1])
for pts in ([[5,0,0],[-5,0,0]], [[0,3,-2]], [[1,2,3],[4,5,6],[-7,8,-9]]):
    out["apply"].append({"m": jl(m1), "pts": pts, "res": jl(b.apply(m1, pts))})

# arc
out["arc"].append({"kw": "r16_start0_ang60_n?", "res": jl(b.arc(r=16, start=0, angle=60))})
out["arc"].append({"kw": "r5_start30_ang90", "res": jl(b.arc(r=5, start=30, angle=90))})
out["arc"].append({"kw": "n8_pts3", "res": jl(b.arc(n=8, points=[[-0.5,0],[0,0.3],[0.5,0]]))})
out["arc"].append({"kw": "n12_pts3b", "res": jl(b.arc(n=12, points=[[-1,0],[0,1],[1,0]]))})

open(os.environ["TRUTH_OUT"], "w").write(json.dumps(out, indent=1))
cube(1).show()
