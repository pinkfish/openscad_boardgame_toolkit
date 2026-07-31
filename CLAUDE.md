# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A toolkit for designing board game inserts (boxes, lids, dividers, trays) in OpenSCAD/PythonSCAD, built on BOSL2. There are three parallel geometry stacks:

1. **Classic OpenSCAD** — `boardgame_toolkit.scad` plus per-module `.scad` files (`cap_box.scad`, `sliding_box.scad`, ...). Used by `examples/*.scad` via the `examples/Makefile` and classic OpenSCAD.app.
2. **PythonSCAD ports** — each `foo.scad` has a `foo.py` port that runs inside the PythonSCAD app's embedded Python. These build on `base_bgtk.py` (which loads real BOSL2 via `osuse("BOSL2/std.scad")` at import time) and on `bosl2/` (a pure-Python numpy port of the BOSL2 pieces the toolkit needs), with shared lid machinery in `lids_base.py` and decorative parts in `components.py`, `labels.py`, `shapes.py`, `tesselations*`.

   **Every box type is a `BoxBaseType` subclass** (`box_base.py`) built from one frozen `BoxSpec`, with two public methods: `make_box()` and `make_lid()`. `box_base.py` owns both pipelines; a subclass supplies geometry only, through at most three hooks:
   - `_build_box_body(contents)` — the raw body (required). The base then hollows, carves contents, adds MMU colour copies, cuts finger holes and positions it. A type whose legacy geometry already hollows or already embeds contents declares `body_hollows_itself` / `body_carves_contents` instead of overriding `make_box`.
   - `_lid_plate(lid) -> LidPlate` — the flat face the decoration goes on, plus `shell` / `offset` / `origin` / `path` / `cutouts`. There is ONE lid pipeline: `make_lid` fits the `Lid`'s pattern + label + fingernail to that plate via `internal_build_lid`. Do not assemble overlays in a box type. `_lid_adjustment(stack)` is the print-orientation hook.
   - `_compute_interior() -> Interior` (and `interior_mask()` only when the clip volume isn't the box of that frame) — the single source for `inner_*`, where content is placed, and what it is clipped to.

   Per-type options are a `BoxTypeOptions` dataclass named by the class's `options_class`; `BoxSpec.type_options` is type-checked at construction. `has_lid = False` for single-piece / lidless types.
3. **pysolidfive/** — an independent libfive/F-Rep (signed-distance-function) shape library. It does NOT import bosl2. Every shape is a `PyShape`: a *symbolic* SDF (a Python callable of (x, y, z) libfive trees) plus bounds; nothing touches the native C extension until `.mesh()` (or a fall-through native attribute like `.show()`) calls `frep()`. Booleans compose SDFs via `lv.min`/`lv.max`; transforms rewrite the coordinate arguments. `pysolidfive/_edges.py` vendors bosl2's `edges=` mini-language.

The `bosl2/` port wraps native solids in `Bosl2Solid`, which carries optional cuboid `size`/`anchor` metadata AND a bbox-backed anchoring layer: `bounds()`/`anchor_point()`/`reanchor()`/`position()`/`attach()`/`align()` read PythonSCAD's native `obj.position`/`obj.size`/`obj.bbox` (the AABB, computed by meshing) so anchoring/attachment/edge-masking work on ANY object without threading a size through the calls. `bounds()` prefers the native bbox (always correct after transforms/CSG), falling back to tracked metadata only under the numeric mock. Direct-CSG shapes are strongly preferred over pysolidfive SDF solids (see the SDF-vs-direct note below); pysolidfive is reserved for constructs with no bosl2 equivalent (`knuckle_hinge`, `rabbit_clip`) or that need symbolic SDF composition.

Historically some box modules used pysolidfive SDF solids for rounded parts; SDF meshing is ~10-20x slower than native CSG, so render helpers give any remaining SDF renders longer timeouts.

## Commands

```sh
# Fast unit tests (numeric mock, no PythonSCAD app needed) — repo root:
python3 -m unittest discover -s tests -p "test_*.py"
# Single test file / case:
python3 -m unittest discover -s tests -p "test_cap_box_render.py"
# pysolidfive's own bundled tests:
cd pysolidfive && python3 -m unittest discover -s tests

# Syntax check a module:
python3 -m py_compile cap_box.py

# Type check (pyrightconfig.json points at venv/openscad, Python 3.14):
npx --yes pyright cap_box.py

# (Re)generate golden render images (needs real app + patched BOSL2, see below):
PYTHONSCAD_BIN=/Applications/PythonSCAD-dev.app/Contents/MacOS/PythonSCAD \
  python3 tests/generate_golden_images.py [--force]
```

## Real-render environment (macOS, this machine)

- Use `/Applications/PythonSCAD-dev.app/Contents/MacOS/PythonSCAD` via `PYTHONSCAD_BIN`. The plain `PythonSCAD.app` build's hardened runtime rejects the installed numpy (`dlopen ... _multiarray_umath ...` failures in anything importing bosl2/pysolidfive), so nearly all renders fail under it.
- Modules that `osuse()` BOSL2 need a patched copy whose `assert(version_num()>=20210100)` line is neutralized: `~/Documents/OpenSCAD/libraries-pythonscad-patched/BOSL2` (override with `BOSL2_SCAD_DIR`). `osuse()` resolves relative to the process CWD, so render helpers run the binary with `cwd=` that directory.
- `render_script()` (in `pysolidfive/tests/render_pysolidfive.py`) is the one subprocess entry point every render test shares; it pins `--backend Manifold` and parses `Triangles:`/`Facets:` from stderr to detect real geometry. Render tests skip gracefully when the binary or BOSL2 dir is missing.

## Testing architecture

Every library has two test flavors:
- `test_foo.py` — pure Python, runs anywhere. These import `mock_libfive` FIRST (it installs numeric stand-ins for the native `openscad`/`libfive` modules) and then import the module under test. **Most of these no longer import**: `mock_libfive` / `render_pysolidfive` died with pysolidfive, so ~20 test modules error at collection. The box/shape suites below are the live net.
- `test_foo_render.py` — shells out to the real PythonSCAD binary through `tests/render_app.py`.
  - `render_python(body)` answers "did it produce geometry" (`facets > 0`). That is a *smoke* test: it cannot see a lid whose label floats 10mm off it, or a part flipped below the bed. Both shipped.
  - `measure_python(body)` (same module) runs the script with `measure(name, solid)` / `report(name, value)` helpers and returns the REAL measured bounding boxes — PythonSCAD computes `.position`/`.size` by meshing. `tests/test_box_geometry.py` uses it to assert what the box system promises: decoration never changes a lid's bbox, lids sit at z >= 0, the `Interior` frame agrees with the clip volume, `spin`/`finger_holes` apply to every box type, and wrong `type_options` raise. **Assert measurements, not facet counts, for anything positional.**
  - Never `measure()` and then `show()` the same solid when it contains frep/SDF geometry (the handle-reuse segfault below); show a throwaway primitive instead. This is why `filament_hinge` / `card_library` lids are render-only.

## Hard-won constraints (do not regress)

- **frep handle reuse segfaults**: referencing one frep-meshed handle from two CSG branches crashes the app. Build shapes through factory lambdas so each branch gets its own handle (see `tests/repro_frep_reuse_segfault.py` and the MakeTabs pattern).
- **numpy is the currency** for path/vector/sequence data throughout `bosl2/` and `pysolidfive/`; convert to plain Python floats only at native boundaries — `frep()` bounds, `polygon()`, `translate()`, and the `osuse()` FFI reject or corrupt raw ndarrays/np scalars.
- **SDF mesher cost** scales ~res² on curved bands; `res=10` is right for box-sized rounded solids. Merge a cuboid's edge treatments into ONE single-pass SDF (as `PyShape.round()/chamfer()` do) — stacked coincident zero sets make libfive's mesher explode.
- `typings/*.pyi` holds the stubs for the app's embedded `openscad`/`pythonscad`/`libfive` modules; keep them in sync when the native surface changes.
- Licensing: every source file carries the Apache-2.0 header; new files should too.
