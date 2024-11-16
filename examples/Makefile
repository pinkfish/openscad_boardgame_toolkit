# Board game toolkit examples, makefile

SCAD=/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD

BASEFILE=isle_of_trains.scad

define find_modules
    $(eval $@_FILE = $(1))
    $(eval $@_BASEFILE = $(basename $(1)))
	$(shell  sed -e '/^module [a-z0-9_-]*\(.*\).*`make`.me.*$$/!d;s/module //;s/\(.*\)(.*).*/output\/$($@_BASEFILE)__\1.stl/' $($@_FILE))
endef

TARGETS=$(call find_modules, isle_of_trains.scad) \
   $(call find_modules, 18cuba.scad) \
   $(call find_modules, 1835.scad) \
   $(call find_modules, canvas.scad) \
   $(call find_modules, cascadero.scad) \
   $(call find_modules, explorers_of_navoria.scad) \
   $(call find_modules, march_of_the_ants.scad) \
   $(call find_modules, modern_art.scad) \
   $(call find_modules, railways_of_the_world.scad) \
   $(call find_modules, root.scad) \
   $(call find_modules, russian_railroads.scad) \
   $(call find_modules, wyrmspan.scad) \
   $(call find_modules, zoovadis.scad)

all: $(TARGETS)

.SECONDARY: $(shell echo "${TARGETS}" | sed 's/\.stl/.scad/g')

%.scad: Makefile
	echo $(shell echo $@ | sed -e 's/__.*$$//')
	printf 'include <../$(shell echo $@ | sed -e 's/__.*$$//;s/^output.//').scad>\n$(shell echo $@ | sed -e 's/^.*__//;s/\.scad//;s/output.//')();' > $@

%.stl: %.scad
	$(SCAD) -m make -o $@ -d $@.deps $< -D FROM_MAKE=1
