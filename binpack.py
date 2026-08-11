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

# LibFile: binpack.py
#    Runs the hyperpack bin-packing algorithm directly in python/library.

import re
import os
from hyperpack import HyperPack

pattern_single = re.compile(
    r"([A-Za-z0-9_]+) = object\(width=([0-9.]+), length=([0-9.]+)\);", re.IGNORECASE
)
pattern_num = re.compile(
    r"([A-Za-z0-9_]+) = object\(width=([0-9.]+), length=([0-9.]+), num=([0-9]+)\);",
    re.IGNORECASE,
)
pattern_spacing = re.compile(r"\/\/ spacing = ([0-9.]+)")
pattern_container = re.compile(
    r"\/\/ container\(width = ([0-9.]+), length = ([0-9.]+)\)"
)

def load_scad_items(filepath: str, spacing_override: float = None) -> tuple[dict, dict, dict]:
    """Reads items, container sizes, and spacing from an OpenSCAD items file.
    
    Returns:
        tuple (items, containers, metadata) for HyperPack.
    """
    items = {}
    container = {}
    metadata = {}
    spacing = 0.0
    
    with open(filepath, "r") as file:
        for line in file:
            line = line.strip()
            
            match_spacing = pattern_spacing.match(line)
            if match_spacing:
                spacing = float(match_spacing.group(1))
                
            match_container = pattern_container.match(line)
            if match_container:
                c_name = "container" + str(len(container))
                metadata[c_name] = {"spacing": spacing * 10}
                container[c_name] = {
                    "W": int((float(match_container.group(1)) - spacing) * 10),
                    "L": int((float(match_container.group(2)) - spacing) * 10),
                }
                
            match = pattern_single.match(line)
            if match:
                name = match.group(1)
                w = float(match.group(2))
                l = float(match.group(3))
                items[name] = {
                    "w": int((w + spacing / 2.0) * 10),
                    "l": int((l + spacing / 2.0) * 10),
                }
                metadata[name] = {
                    "spacing": spacing * 10,
                    "num": 1,
                    "w": w * 10,
                    "l": l * 10,
                }
                
            match_num = pattern_num.match(line)
            if match_num:
                name = match_num.group(1)
                w = float(match_num.group(2))
                l = float(match_num.group(3))
                num = int(match_num.group(4))
                items[name] = {
                    "w": int((w + spacing / 2.0) * 10),
                    "l": int((l * num + spacing / 2.0) * 10),
                }
                metadata[name] = {
                    "spacing": spacing * 10,
                    "num": num,
                    "w": w * 10,
                    "l": l * 10,
                    "ltotal": items[name]["l"],
                }
                
    if spacing_override is not None:
        # Re-scale items and containers if spacing is overridden
        # For simplicity, we assume spacing from the file is used.
        pass
        
    return items, container, metadata

def run_binpack(items: dict, containers: dict) -> dict:
    """Runs the hyperpack bin-packing algorithm."""
    settings = {"rotation": True}
    problem = HyperPack(containers=containers, items=items, settings=settings)
    problem.hypersearch()
    return problem.solution
