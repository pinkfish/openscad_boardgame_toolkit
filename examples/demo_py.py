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

# LibFile: examples/demo_py.py
#    A minimal PythonSCAD example box, the .py analogue of the .scad example games. Each
#    box-producing function is tagged `# `make` me` so scripts/make_files.py generates the
#    mmu/single 3mf build rules for it (see generate_py.makefile). Run directly in the app for
#    a preview; the FROM_MAKE guard suppresses that when the Makefile drives it.

from base_bgtk import *
from cap_box import MakeBoxWithCapLid, CapBoxLidWithLabel
from labels import MakeLabelOptions

box_width = 80
box_length = 60
box_height = 25


@make_box
def TokenBox():
    """A simple cap box for tokens."""
    return MakeBoxWithCapLid(size=[box_width, box_length, box_height])


@make_box
def TokenBoxLid():
    """The labelled cap lid for TokenBox -- the blue label is a second colour, so the mmu
    build produces a multi-material 3mf."""
    return CapBoxLidWithLabel(
        size=[box_width, box_length, box_height],
        text_str="Tokens",
        label_options=MakeLabelOptions(label_colour="blue"),
    )


# Preview render when opened directly in the app; suppressed under the Makefile (FROM_MAKE=1),
# where the generated wrapper shows one specific box instead.
if FROM_MAKE != 1:
    TokenBoxLid().show()
