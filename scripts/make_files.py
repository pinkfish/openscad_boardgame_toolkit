#!/usr/bin/python

import glob
import re

class ScadFile:
   def __init__(self, filename, module, basename):
       self.filename = filename
       self.module = module
       self.basename = basename

onlyfiles =glob.glob("./*.scad")
print(onlyfiles)
data: list[ScadFile] = []
for fname in onlyfiles:
    with open(fname, 'r') as file:
       for line in file:
           line = line.strip()
           x = re.search("^module\s*([a-zA-Z_-]*)\(.*\).*`make` me", line)
           if x:
               fdata = re.search(".*/(.*)\.scad", fname)
               # Search and replace.
               data.append(ScadFile(fname, x.group(1), fdata.group(1)))

for d in data:
    # Frog
    print("output/{0}__{1}.stl: output/{0}__{1}.scad".format(d.basename, d.module))
    print("    $(SCAD) -m make -o $@ -d $@.deps $< -D FROM_MAKE=1")
