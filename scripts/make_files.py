#!/usr/bin/python

import glob
import re

class ScadFile:
   def __init__(self, filename, module, basename):
       self.filename = filename
       self.module = module
       self.basename = basename

onlyfiles =glob.glob("./*.scad")
data: list[ScadFile] = []
for fname in onlyfiles:
    with open(fname, 'r') as file:
       for line in file:
           line = line.strip()
           x = re.search("^module *([a-zA-Z_-]*)\(.*\).*`make` me", line)
           if x:
               fdata = re.search(".*/(.*).scad", fname)
               # Search and replace.
               data.append(ScadFile(fname, x.group(1), fdata.group(1)))

with open("generate.makefile", "w") as mfile:
    mfile.write("all: {0}\n\n".format(" " .join(map(lambda x: "output/" + x.basename + "__" + x.module + ".stl", data))))
    mfile.write(".SECONDARY: {0}\n\n".format(" " .join(map(lambda x: "output/" + x.basename + "__" +  x.module + ".scad", data))))

    for d in data:
        # Frog
        mfile.write("output/{0}__{1}.stl: output/{0}__{1}.scad {0}.scad\n".format(d.basename, d.module))
        mfile.write("    $(SCAD) -m make -o $@ -d $@.deps $< -D FROM_MAKE=1\n\n")
        # Create the scad file.
        with open("output/{0}__{1}.scad".format(d.basename, d.module), "w") as f:
            f.write("include <../{0}.scad>\n".format(d.basename))
            f.write("{0}();".format(d.module))
            f.close()
