# Minimal sphinx-build Makefile for the bosl2 (PythonSCAD port) API docs.
#
# Usage (from the repo root):
#   python3 -m pip install sphinx
#   make -C bosl2/docs html
#
# The built HTML lands in bosl2/wiki/ (a sibling of this docs/ source directory), which is meant
# to be CHECKED IN -- the browsable copy of the docs kept in the repo -- so rebuild and commit it
# together with any docstring/docs-source change. The doctree pickles (_build/), the rendered
# preview cache (_generated/) and the exported STL cache (_stl/) stay untracked.
#
# Set PYTHONSCAD_BIN to a real PythonSCAD binary to get rendered images and downloadable STL
# meshes in the bosl2-example blocks; without it the build still succeeds and shows source only
# (see docs/_ext/bosl2_example.py). Unchanged examples reuse their cached image/STL.

SPHINXOPTS    ?=
SPHINXBUILD   ?= python3 -m sphinx
SOURCEDIR     = .
BUILDDIR      = _build
WIKIDIR       = ../wiki

.PHONY: help clean html
help:
	@echo "make html   -- build the docs into $(WIKIDIR) (checked in)"
	@echo "make clean  -- remove $(WIKIDIR), the doctree cache, and the render caches"

clean:
	rm -rf "$(BUILDDIR)" "$(WIKIDIR)" _generated _extra

html:
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(WIKIDIR)" -d "$(BUILDDIR)/doctrees" $(SPHINXOPTS) $(O)
