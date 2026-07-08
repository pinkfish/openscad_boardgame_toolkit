# Minimal sphinx-build Makefile for pysolidfive's docs.
#
# Usage (from pysolidfive/):
#   pip install -e ".[docs]"
#   make -C docs html
#
# Set PYTHONSCAD_BIN to a real PythonSCAD binary to get rendered images in the
# pythonscad-example blocks; without it, the build still succeeds but shows source code only
# (see docs/_ext/pythonscad_example.py's module docstring).

SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

.PHONY: help clean html
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

clean:
	rm -rf "$(BUILDDIR)" _generated

html:
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
