# Minimal sphinx-build Makefile for pysolidfive's docs.
#
# Usage (from pysolidfive/):
#   pip install -e ".[docs]"
#   make -C docs html
#
# The built HTML lands in pysolidfive/wiki/ (a sibling of this docs/ source directory), which
# is CHECKED IN -- it's the browsable copy of the docs, kept in the repo -- so rebuild and
# commit it together with any docstring/docs-source change. Only the doctree pickles (_build/)
# and the rendered-example image cache (_generated/) stay untracked.
#
# Set PYTHONSCAD_BIN to a real PythonSCAD binary to get rendered images in the
# pythonscad-example blocks; without it, the build still succeeds but shows source code only
# (see docs/_ext/pythonscad_example.py's module docstring). Unchanged examples reuse their
# cached image in _generated/ without needing the binary at all.

SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build
WIKIDIR       = ../wiki

.PHONY: help clean html
help:
	@echo "make html   -- build the docs into $(WIKIDIR) (checked in)"
	@echo "make clean  -- remove $(WIKIDIR), the doctree cache, and the rendered-example cache"

clean:
	rm -rf "$(BUILDDIR)" "$(WIKIDIR)" _generated

html:
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(WIKIDIR)" -d "$(BUILDDIR)/doctrees" $(SPHINXOPTS) $(O)
