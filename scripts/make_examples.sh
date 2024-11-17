#!/bin/bash

TOP_LEVEL=$(git rev-parse --show-toplevel)

echo $TOP_LEVEL
cd $TOP_LEVEL

cd examples

#for file in *.scad; do
#   filename_without_ext="${file%.*}"
#   awk -f parse_mods.awk BASEFILE=${filename_without_ext} ${file}
#done

python ../scripts/make_files.py

# s/module //\;s/(.*).*/.stl/