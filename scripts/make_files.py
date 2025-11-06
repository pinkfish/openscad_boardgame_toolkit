#!/usr/bin/python

import glob
import re
import os.path

class ScadFile:
   def __init__(self, filename:str, module:str, basename:str):
       self.filename = filename
       self.module = module
       self.basename = basename

onlyfiles =glob.glob("./*.scad")
data: list[ScadFile] = []
for fname in onlyfiles:
    with open(fname, 'r') as file:
       for line in file:
           line = line.strip()
           x = re.search("^module *([a-zA-Z0-9_-]*)\\(.*\\).*`make` me", line)
           if x:
               fdata = re.search(".*/(.*).scad", fname)
               # Search and replace.
               data.append(ScadFile(fname, x.group(1), fdata.group(1)))

with open("generate.makefile", "w") as mfile:
    mfile.write("all: 3mfmerge {0} {1}\n\n".format(" " .join(map(lambda x: "release/" + x.basename + "/" + x.module + ".3mf", data)), " " .join(map(lambda x: "release/" + x.basename + "/" + x.module + ".stl", data))))
    mfile.write(".SECONDARY: {0}\n\n".format(" " .join(map(lambda x: "output/" + x.basename + "__" +  x.module + ".scad", data))))

    for d in data:
        # Frog
        mfile.write("release/{0}/{1}.3mf: output/{0}__{1}.scad {0}.scad\n".format(d.basename, d.module))
        mfile.write("\t-mkdir -p release/{0}\n\t../scripts/colorscad/colorscad.sh -f -p $(SCAD) -c \"[0.184314, 0.309804, 0.309804, 1]\" -i $< -o $@ --  --backend=manifold --enable predictible-output --enable textmetrics --enable object-function -d output/{0}__{1}.deps  -D FROM_MAKE=1 -D MAKE_MMU=1\n".format(d.basename, d.module))
        # Extra frogs
        mfile.write("release/{0}/{1}.stl: output/{0}__{1}.scad {0}.scad\n".format(d.basename, d.module))
        mfile.write("\t-mkdir -p release/{0}\n\t$(SCAD) -m make --export-format binstl  --backend=manifold --enable predictible-output --enable textmetrics --enable object-function -o $@ -d output/{0}__{1}.deps $< -D FROM_MAKE=1 -D MAKE_MMU=0\n".format(d.basename, d.module))
        # Create the scad file.
        scad_script = "MAKE_MMU = 0;\nFROM_MAKE = 0;\n$fn = 128;\ninclude <../{0}.scad>\n{1}();\n".format(d.basename, d.module)
        file_data = ""
        output_fname = "output/{0}__{1}.scad".format(d.basename, d.module)
        if os.path.exists(output_fname):
            with open(output_fname, 'r') as file:
                file_data = file.read()
        # Only write the file if it is different.
        if file_data != scad_script:
            with open(output_fname, "w") as f:
                f.write(scad_script)
                f.close()
