# Board game toolkit examples, makefile
include $(wildcard $(DEPS_DIR)/*.deps)

SCAD=/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD

BASEFILE=isle_of_trains.scad

#	$(shell  sed -e '/^module [a-z0-9_-]*\(.*\).*`make`.me.*$$/!d;s/module //;s/\(.*\)(.*).*/output\/$($@_BASEFILE)__\1.stl/' $($@_FILE))

define find_modules
    $(eval $@_FILE = $(1))
    $(eval $@_BASEFILE = $(basename $(1)))
	$(shell awk -f parse_mods.awk -v BASEFILE=$($@_BASEFILE) $($@_FILE) | rev | cut -c 1- | rev)
endef


FILES=18cuba.scad 1835.scad canvas.scad canvas.scad explorers_of_navoria.scad isle_of_trains.scad march_of_the_ants.scad modern_art.scad railways_of_the_world.scad root.scad russian_railroads.scad wyrmspan.scad zoovadis.scad

TARGETS=$(foreach F,$(FILES),$(call find_modules, $F))

all: $(TARGETS)

.SECONDARY: $(shell echo "${TARGETS}" | sed 's/\.stl/.scad/g')

%.scad:
	echo $(shell echo $@ | sed -e 's/__.*$$//')
	printf 'include <../$(shell echo $@ | sed -e 's/__.*$$//;s/^output.//').scad>\n$(shell echo $@ | sed -e 's/^.*__//;s/\.scad//;s/output.//')();' > $@

%.stl: %.scad
	$(SCAD) -m make -o $@ -d $@.deps $< -D FROM_MAKE=1

