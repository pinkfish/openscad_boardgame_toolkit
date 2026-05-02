#!/bin/bash

for file in *.svg; do
    /Applications/Inkscape.app/Contents/MacOS/inkscape --actions="select-all;fit-canvas-to-selection;export-overwrite;export-do" "$file"
done
