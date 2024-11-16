#!/bin/bash

TOP_LEVEL=$(git rev-parse --show-toplevel)

echo $TOP_LEVEL
cd $TOP_LEVEL

cd examples

for file in *.scad; do
  filename_without_ext="${file%.*}"
   echo $filename_without_ext
   sed -e "/^module [a-zA-Z0-9_-]*\(.*\).*`make`.me$$/!d;s/^module *//;s/\(.*\)(.*).*$$/${filename_without_ext}_\1/"  $file
done

# s/module //\;s/(.*).*/.stl/