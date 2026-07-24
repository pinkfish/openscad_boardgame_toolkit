# Board game toolkit examples, makefile
SCAD=/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD
DEPS_DIR=output

# Python: use the cached .venv Python when available, fall back to system python3.
VENV_PYTHON ?= python3

# PythonSCAD (.py example) build config. PYSCAD is the PythonSCAD binary that can run the
# toolkit (the -dev build -- the plain build's hardened runtime rejects the numpy bosl2 needs);
# PYSCAD_BOSL2_DIR holds a BOSL2/ whose std.scad version assert is neutralised for PythonSCAD
# (see tests/render_cap_box.py). base_bgtk loads BOSL2 by absolute path from BOSL2_SCAD_DIR.
PYSCAD ?= /Applications/PythonSCAD-dev.app/Contents/MacOS/PythonSCAD
PYSCAD_BOSL2_DIR ?= $(HOME)/Documents/OpenSCAD/libraries-pythonscad-patched

include generate.makefile

# PythonSCAD (.py) examples: built dynamically by scripts/build_boxes.py, which discovers the
# @make_box sections and traces each example's transitive .py dependencies, so it rebuilds only
# what a source change affects and picks up new boxes automatically -- no makefile regeneration.
#   make py                 build/update every .py example's boxes (one by one)
#   make py-splendor        build just one game's boxes
#   make py ARGS="--force"  pass extra flags through (e.g. --jobs 4, --mmu-only, --box Name)
.PHONY: py
py:
	PYSCAD="$(PYSCAD)" PYSCAD_BOSL2_DIR="$(PYSCAD_BOSL2_DIR)" $(VENV_PYTHON) ../scripts/build_boxes.py --all $(ARGS)

py-%:
	PYSCAD="$(PYSCAD)" PYSCAD_BOSL2_DIR="$(PYSCAD_BOSL2_DIR)" $(VENV_PYTHON) ../scripts/build_boxes.py $* $(ARGS)

3mfmerge: ../scripts/colorscad/3mfmerge/build

../scripts/colorscad/3mfmerge/build:
	cd ../scripts/colorscad/3mfmerge; mkdir -p build
	cd ../scripts/colorscad/3mfmerge/build; cmake .. -DLIB3MF_TESTS=OFF
	cd ../scripts/colorscad/3mfmerge/build; cmake --build .

include $(wildcard $(DEPS_DIR)/*.deps)

lib/animal_kingdom_items_layout.scad: animal_kingdom_items.scad
	$(VENV_PYTHON) ../scripts/binpack.py -i $@ -o lib/animal_kingdom_items_layout.scad