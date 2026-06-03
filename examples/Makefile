# Board game toolkit examples, makefile
SCAD=/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD
DEPS_DIR=output

include generate.makefile

3mfmerge: ../scripts/colorscad/3mfmerge/build

../scripts/colorscad/3mfmerge/build:
	cd ../scripts/colorscad/3mfmerge; mkdir -p build
	cd ../scripts/colorscad/3mfmerge/build; cmake .. -DLIB3MF_TESTS=OFF
	cd ../scripts/colorscad/3mfmerge/build; cmake --build .

include $(wildcard $(DEPS_DIR)/*.deps)

lib/animal_kingdom_items_layout.scad: animal_kingdom_items.scad
	python3 ../scripts/binpack.py -i $@ -o lib/animal_kingdom_items_layout.scad