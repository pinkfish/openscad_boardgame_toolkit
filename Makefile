# -*- makefile -*-
# Top-level Makefile: venv bootstrap + project-wide targets.
# `make venv` (or any target that depends on it) creates a cached .venv/
# with all Python dependencies. The venv is only rebuilt when
# scripts/requirements.txt or bosl2/pyproject.toml changes.

ROOT_DIR := $(shell git rev-parse --show-toplevel 2>/dev/null || pwd)

VENV        ?= $(ROOT_DIR)/.venv
VENV_PYTHON := $(VENV)/bin/python
VENV_PIP    := $(VENV)/bin/pip
VENV_STAMP  := $(VENV)/.installed
REQ_FILE    := $(ROOT_DIR)/scripts/requirements.txt

# venv creation (cached unless deps change)
.PHONY: venv
venv: $(VENV_STAMP)

$(VENV_STAMP): $(REQ_FILE) $(ROOT_DIR)/pyproject.toml $(ROOT_DIR)/bosl2/pyproject.toml
	@echo "=== setting up venv ($(VENV)) ==="
	python3 -m venv $(VENV)
	$(VENV_PIP) install --upgrade pip setuptools wheel
	$(VENV_PIP) install -e $(ROOT_DIR)/bosl2
	$(VENV_PIP) install -r $(REQ_FILE)
	@touch $(VENV_STAMP)
	@echo "=== venv ready ==="

.PHONY: clean-venv
clean-venv:
	rm -rf $(VENV)

# Generate the SCAD makefile
.PHONY: makefiles
makefiles: venv
	cd $(ROOT_DIR)/scripts && $(VENV_PYTHON) make_files.py

# Build PythonSCAD examples
.PHONY: py
py: venv
	@$(MAKE) -C examples py VENV_PYTHON="$(VENV_PYTHON)"

.PHONY: py-%
py-%: venv
	@$(MAKE) -C examples py-$* VENV_PYTHON="$(VENV_PYTHON)"

.PHONY: docs
docs: venv
	cd $(ROOT_DIR)/scripts && bash generate_docs.sh

.PHONY: all
all: makefiles py
