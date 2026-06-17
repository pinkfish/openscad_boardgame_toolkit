#!/bin/bash

TOP_LEVEL=$(git rev-parse --show-toplevel)

echo $TOP_LEVEL
cd "$TOP_LEVEL"

openscad-docsgen *.scad tesselations/*.scad
openscad-mdimggen
