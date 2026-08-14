# Implementation Plan: Board Game Box Library

**Branch**: `001-board-game-box-library` | **Date**: 2026-08-11 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-board-game-box-library/spec.md`

## Summary

Build a new strictly-typed PythonSCAD library under `pyboxbuilder/` with a single-import API. The design is fresh — not wrapping the existing box pipeline. Borrowed from the existing codebase: tessellation algorithms (penrose, pentagon families, voronoi), 2D shape generators (coin, hexagon, rounded rects), and pybosl2 CSG primitives. Everything else — the box construction pipeline, lid decoration pipeline, builder API, compartment layout, export, and caching — is designed from scratch to avoid constraints inherited from the legacy codebase.

## Technical Context

**Language/Version**: Python 3.12+ with strict type annotations (`py.typed` marker)

**Primary Dependencies**: pybosl2 >= 0.7.8 (CSG geometry), numpy, pymeshlab >= 0.2.0 (Hausdorff mesh comparison)

**Borrowed from existing code**: Tessellation generators (`penrose_tiling.py`, `pentagon_tilings.py`, `tesselations/`), shape generators (`shapes.py` coin/hex/etc.), and pybosl2's `cuboid()`/`cylinder()`/boolean CSG. These are algorithm libraries, not architecture constraints.

**Storage**: Disk JSON cache (`pyboxbuilder/.layout_cache.json`), 3MF files + `layout.pdf` in `{out_dir}/{game}/mmu/`, `{out_dir}/{game}/single/`, and `{out_dir}/{game}/layout.pdf`

**Testing**: `unittest` two-tier: fast pure-Python and full PythonSCAD render with golden-image comparison. `pyright` strict mode for type checking.

**Target Platform**: macOS (PythonSCAD.app), cross-platform Python

**Project Type**: Greenfield Python library inside `pyboxbuilder/`, single-import strictly-typed API

**Performance Goals**: Full bin-packing may take longer on first run (complex layouts). Once cached (SHA-256 hit), regeneration completes in: 20-compartment layout < 1s, 6-sub-box auto-size < 2s, Hausdorff-based 3MF write-if-changed. Cached re-exports with zero geometry changes complete in < 0.5s.

**Constraints**: Enums for all type selections, no bare strings, no dict parameter objects, typed builders per box type, no import of existing `box_base.py`/`lids_base.py` architecture, CSG over SDF, Apache-2.0 header. **Do not reinvent the wheel — use classes that already exist in pybosl2 wherever possible.** ALL geometry MUST use pybosl2 solids (`cuboid`, `cylinder`, `sphere`, `prismoid`, etc.) and pybosl2 2D shapes/paths — never import `pythonscad` or any native OpenSCAD built-in directly. Use bosl2 basic pieces (`cube`, `cylinder`, `sphere`, `linear_extrude`, etc.) wherever possible instead of higher-level shape generators. **Do NOT implement a Color class. Use `pybosl2.Color` directly.** No wrapper, no custom implementation, no fallback. pybosl2's Color supports webcolor names: use names like `Color("darkgreen")`, `Color("gold")` instead of hardcoding RGB values. **Do NOT define preset constants** (no `WHITE`, `BLACK`, etc.) — just use `Color("white")`, `Color("black")` directly at the call site. The `pyboxbuilder/color.py` file must not exist. Minimum dimensional precision is 0.1mm — no rounding to whole millimetres. Compartments support ratio-based sizing (`width_ratio`, `length_ratio`) as an alternative to absolute dimensions; ratios are validated to sum ≤ 1.0 per row. Lid labels support per-export-mode overrides: `mmu_label` and `single_label` sub-configurations enable different label styles per material mode (e.g., frameless for MMU, framed for single). Compartment labels render as single-layer engraved cutouts for single-color and raised MMU second-color text for multi-color. Boxes support a `no_rotate` flag (default `False`) so directionally-constrained boxes opt out of packer rotation (FR-013c). When the packer rotates a box, its compartments are re-laid-out in the rotated interior frame (FR-013b). Standalone boxes export without a game box/packing (FR-037). No-lid boxes support stackable rims (inside/outside, FR-038) and round/rectangular side magnet slots (FR-039).

**Scale/Scope**: 14 box types (new implementations), 12 typed builders, 4 public enums, single public import surface, 3 reference examples (Earth Animal Kingdom, Stackable Hexes, Irish Gauge)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Developer Experience First | PASS | Single `from pyboxbuilder import Project, BoxType, ...`; enums prevent typos; typed builders give IDE autocomplete; fresh lid design not constrained by legacy |
| II. Single Source of Truth | PASS | Each box type's config lives on its typed builder; `BoxSpec` equivalent is frozen; lid decoration is one `LidBuilder` |
| III. Performance by Design | PASS | Layout cache with SHA-256 hash, Hausdorff skip-if-unchanged, CSG over SDF |
| IV. Test-First | PASS | All new code tested; measurement-based geometry assertions; regression tests |
| V. Documented by Default | PASS | All enums/builders/functions fully docstringed; Earth Animal Kingdom is reference |

**Gate Result**: All pass.

## Testing Policy — Full Detailed Unit Tests for All Code Changes

Every change to the codebase MUST be accompanied by full, detailed unit tests. This is non-negotiable and applies to every commit, bug fix, and feature addition:

1. **Every code change has a test**: no module, function, class, or builder is added or modified without a corresponding unit test. A code change without a test is incomplete and MUST NOT be marked done.
2. **Detailed, not smoke tests**: tests MUST assert specific behaviour — exact dimensions (to 0.1mm), exact placements, exact enum values, exact error messages — not merely that "a solid was returned" or "no exception was raised".
3. **Fast pure-Python tests first**: logic that does not require pybosl2/PythonSCAD MUST be covered by fast tests runnable via `python3 -m pytest tests/test_pyboxbuilder/` (no render binary). Geometry-layout math, packing, builders, enums, and validation all belong here.
4. **Render tests for geometry**: any change that produces CSG geometry MUST also include a render test (or be marked `bosl2`-skipped) that verifies real faceted output when the PythonSCAD binary is available.
5. **Edge cases and negative paths**: tests MUST cover error/validation paths (e.g., ratio sums > 1.0, zero rows/cols, oversized compartments, no-lid + lid conflict) in addition to happy paths.
6. **Test task per change**: every implementation task in `tasks.md` is paired with a test task (or the task description explicitly states the test it adds). The `[P]` test tasks run before their implementation counterpart (TDD where practical).
7. **pybosl2/PythonSCAD render tests MUST run — not just be skipped**: the pieces that cannot be tested in pure Python (CSG geometry — `build_body`/`build_lid`, pattern fills, hex-grid cutouts, tessellation wraps, stackable rims, magnet slots, lid labels) MUST be exercised under the real pybosl2 inside PythonSCAD.app. These tests run via the PythonSCAD binary (`/Applications/PythonSCAD-dev.app/Contents/MacOS/PythonSCAD`) and MUST NOT silently `skipTest` in CI when the binary is present. A `skip` is only acceptable when the binary is genuinely unavailable.
8. **Golden-image render tests**: every render test that produces a mesh MUST render it to an image and compare against a committed **golden image** (PNG) using a pixel-difference threshold. This catches visual regressions (wrong orientation, missing cutout, mis-sized feature) that mesh-count or bounding-box assertions miss. Golden images live under `tests/test_pyboxbuilder/golden/` and are regenerated intentionally (not automatically) when the reference geometry changes.

Rationale: the pyboxbuilder library is geometry-heavy and correctness-critical (a wrong 0.1mm offset produces an unprintable box). Detailed unit tests are the only reliable guard against silent regression.

## Documentation Policy — Detailed Python Docs for All Public Methods

Every public method, class, function, enum, and dataclass field MUST carry a detailed Python docstring:

1. **Every public method documented**: no public `def`/`class` ships without a docstring. Private helpers (`_leading_underscore`) are exempt but MUST have descriptive names.
2. **Detailed docstrings, not one-liners**: docstrings MUST document every parameter (name, type, meaning, valid range, default rationale), the return value (type + meaning), raised exceptions, and a 1–2 line usage example where non-obvious.
3. **`Args:` and `Returns:` sections are mandatory**: any public method/function that has arguments MUST include an `Args:` section documenting each parameter, and any that returns a value MUST include a `Returns:` section documenting the return type and meaning. A method with both gets both; a method with neither omits both. These sections follow the Google/NumPy docstring style so the API generator renders them as structured parameter/return tables.
4. **Dataclass fields documented**: every `dataclass` field has a `# comment` or docstring stating its meaning, valid range, and default.
5. **Auto-generated API docs**: the docstrings feed an API documentation generator (Sphinx/pdoc) — they are the source of truth, not prose separate from the code.
6. **`py.typed` + full annotations**: every public signature is fully type-annotated so the API docs render accurate parameter types.

## CI/CD — GitHub Actions

The repository MUST have GitHub Actions workflows that run on every push:

1. **Test verification** (`.github/workflows/test.yml`): runs the fast pure-Python suite (`pytest tests/test_pyboxbuilder/`) and `pyright` type checking on every push and PR. It runs at **draft curve precision** and produces no printable output — see *Curve Precision: Export vs Preview*.
2. **Rendering verification** (`.github/workflows/render.yml`): runs the pybosl2/PythonSCAD render tests (golden-image comparison) on push — these exercise the CSG geometry (`build_body`/`build_lid`, pattern fills, hex-grid cutouts, tessellation wraps, stackable rims, magnet slots, lid labels) that pure Python cannot validate. The workflow provisions the PythonSCAD binary and fails on any render regression.
3. **Docs generation** (`.github/workflows/docs.yml`):
   - **Dev docs on checkin**: every push to a non-release branch regenerates and publishes the API docs under a `dev/` prefix (development documentation).
   - **Release docs**: a release (git tag / GitHub Release) regenerates and publishes the full versioned release docs, and promotes them as the stable documentation.
   - Docs are generated from the docstrings (no hand-maintained API reference), so the docs can never drift from the code.
4. **Spacer/artifact hygiene** is covered by the export step's `_delete_stale_spacers()` (no orphaned 3MF files), enforced by the render/export tests.

## Project Structure

### Examples Must Run In Both Plain Python and Jupyter

Every example under `boxes/` MUST work identically when run two ways:

1. **Plain Python**: `python3 boxes/<game>/<game>.py` — the script guards its entry point with `if __name__ == "__main__":` and only calls `project.export(...)` there.
2. **Jupyter notebook**: `%run boxes/<game>/<game>.py` or `import boxes.<game>.<game>` — the module must import and build the `Project` cleanly without forcing an export, and without requiring `__file__` to exist.

Concretely:

- **No bare `__file__`**: example scripts MUST NOT assume `__file__` is defined (it is `NameError`-undefined in Jupyter cells and `exec()`/PythonSCAD script runners). Path setup for the repo root MUST be guarded — e.g. `ROOT = Path(__file__).resolve().parents[2] if "__file__" in globals() else Path.cwd()` — so `import pyboxbuilder` resolves in both environments.
- **Export only under `__main__`**: the `project.export(...)` call lives inside `if __name__ == "__main__":`, so importing the example (from Jupyter) builds the project but does not write files; running it as a script exports.
- **Same `Project` object**: whether imported or run, the module produces the same `Project` (same boxes, same sizes) — the environment must not change the geometry.

### Make vs. Interactive: `FROM_MAKE` selects export vs. `show()`

The `__main__` guard branches on the `FROM_MAKE` environment variable so the same
file does the right thing in both contexts:

```python
if __name__ == "__main__":
    import os
    if os.environ.get("FROM_MAKE") == "1":
        result = project.export("output/")   # batch build: writes 3MF + PDF
        # ... report written/skipped pieces ...
    else:
        project.show()                        # interactive: renders the layout
```

- **Inside make** (`FROM_MAKE=1`): the example runs the export flow — `project.export("output/")` writes the 3MF files and layout PDF. The make build sets `FROM_MAKE=1` (as `tests/render_app.py` does) so the dependency-driven build regenerates box output without popping up a render window.
- **Not inside make** (PythonSCAD GUI, Jupyter, or a plain `python3` shell): `FROM_MAKE` is unset, so the example calls `project.show()`, which builds every box body at its final packed position and shows them for interactive preview.
- **`Project.show(show_lids=False, remove_layers=0)`** is a read-only preview: it resolves the layout (reusing the same `_resolve_final_layout()` packing as `export()`), builds each body, and places it at its packed position. It does NOT write files or produce a PDF. `export()` is unchanged and remains the batch path.
- **Each box stays a separate object — `show()` MUST NOT union the bodies.** Every box (and every lid, and every spacer) is shown as its own solid, so the preview keeps one part per box. This is not a stylistic preference; unioning defeats the rest of this section. A union is a single solid with a single colour, so per-box colours (below), the lid's lighter translucent shade, and the spacer grey all collapse into whatever the first operand happened to carry. It also fuses touching boxes into one indivisible blob, which is exactly the thing a packing preview exists to let you see the seams of — and it pays a full CSG merge over the whole insert for a picture that renders fine without one. `show()` therefore builds a list of independently coloured, independently placed solids and shows each.
- **Lids are hidden by default** — lids obscure the layout (they cover the compartments and neighbouring boxes), so `show()` renders bodies only. Pass `project.show(show_lids=True)` to also place each lid in its seated position (inside/on its body — `build_lid()` already positions it relative to the box origin, so the lid uses the same translation as the body; no extra Z offset). When a lid is shown it MUST be rendered **semi-transparent with a 50% alpha channel** so the box underneath remains visible through it, and it MUST use a **slightly lighter version of its box's colour** (not the exact same colour) so the lid reads as a distinct piece sitting on the box rather than blending into it.
- **Layer removal for viewing beneath.** `show()` MUST accept `remove_layers=N` (default 0): when N > 0, the top `N` vertical layers of the packed layout are omitted from the render, revealing the boxes underneath. "Layer" is defined by Z position — boxes whose top surface sits above the N-th vertical slice are removed, so stacked boxes (and boxes under lids/boards) become visible. This is the interactive equivalent of the exploded PDF view, but for the live preview.
- **Per-box colors for distinguishing boxes.** Every box SHOULD carry an associated color (its material/body colour). When a box has no explicit colour, `show()` MUST assign it a distinct, stable pseudo-random color (deterministic per box label — e.g. hashed to a hue) so adjacent boxes are visually distinguishable in the preview. The colour is a **view-time** attribute: it does NOT change the exported geometry or the material the box prints in.
- **Spacers are shown, always grey.** `show()` MUST also render the spacer boxes at their generated positions so the preview shows the complete filled layout (not just the real boxes). Spacers MUST always use a **variant of grey** for their colour — never the same palette as the real boxes — so a viewer can instantly tell a spacer (dead fill) from a box (holds pieces). The spacer colour is fixed and is not drawn from the per-box pseudo-random palette.
- **Curve precision (`fn`/`fa`/`fs`).** `export()` (and `show()`) MUST accept optional `fn`, `fa`, and `fs` parameters — the OpenSCAD/BOSL2 tessellation controls — and thread them into **every** geometry call that renders a curve: cylinder/sphere facets (`fn`/`fa`/`fs`), `cuboid(..., rounding=...)`, fillets/chamfers, the finger-scoop and finger-hole profiles, hex/tessellation edges, and lid-pattern curves. Defaults are a sensible balance (e.g. `fa=12, fs=2`, or an explicit `fn` for small radii) but must be overridable so a user can raise precision for print-quality curves or lower it for a fast preview. No geometry call hardcodes its own facet count in a way the caller cannot override.

### Getting A Slipover Sleeve Back Off (FR-002f, FR-002g, FR-002h)

A slipover sleeve is a smooth box with nothing to hold: four covered sides, flush faces, no lip. The original cuts a notch into two **diagonally opposite** corners — diagonal so a pair of fingers pulls along the sleeve's axis instead of twisting it — placed just under the lid plate, where the notch exposes the body's corner for a thumb to push against.

The notch itself is not a new shape, and that is the part worth copying: the original's `CornerCatch` is **two `FingerHoleWall` scoops meeting at the corner**, one through each wall. `features.corner_catch` does the same with the same `build_wall_scoop`, so the notch arrives with the r1 roll, the floor fillet and the face fillets already correct and cannot drift from the finger cuts elsewhere in the box. Sizing follows the original too: half the skirt's height capped at 20mm, and a radius of at least 7mm so a shallow sleeve still admits a fingertip.

### The Hinge Goes Inside The Box (FR-002c, FR-002d, FR-002e)

The hinge used to stand off the back of the box — `axis_y = length + radius + gap` — and Phase 18 recorded that as the one bounded exception to "a closed box is the size it declares". It is not a good exception: a box with a barrel hanging off it cannot be packed against its neighbours, and nothing tells the packer to reserve the room. The pin axis now sits **inside** the back wall (`axis_y = length - radius`), and is sunk far enough (`height + leaf_thickness - radius`) that the barrel's crown is flush with the closed box's top rather than standing 1mm proud of it. Measured: both hinged types are now exactly their declared size in all three axes, and nothing anywhere reaches outside the footprint.

Two consequences follow, and neither is optional:

- **Each half must be relieved out of the other (FR-002e).** Inside the box, the lid's knuckles occupy space the body's wall fills, and the body's knuckles occupy space the lid's plate fills. `Closure` carries `body_cut` and `lid_cut` for this. Relieving one side only is worse than a trap — it looks fixed, because the obvious symptom (the lid fused to the wall) disappears while the other half stays welded.
- **The interior loses that room, so the contents mask has to know (FR-002d).** The barrel and webs stand in the back of the interior, right where a compartment would go. `interior_mask` is a per-type hook — `None` for every type whose interior is simply its interior — and the hinge types return the interior less the hinge's intrusion. `build_contents` clips the **wells** to it and leaves the finger scoops alone, since breaching a wall is a scoop's whole job. This is what the original does through `FilamentBoxInsideMask`, which subtracts the barrel's clearance cylinder and a chamfered support web from the interior cuboid.

### A Sliding Box Needs Somewhere For The Lid To Go In (FR-002a)

**The lid leaves through the shorter face (FR-002b)** — it slides along the longer horizontal axis. This applies to `SlidingBox`; `SlidingCatchBox` and `CardLibraryBox` share the `sliding_track` feature, which currently always slides along X. Their channel was opened at the same time (they had the same blocked-end defect, so FR-002a was only half implemented) but the axis choice has not been carried across — a known limitation, not a decision. That puts the grooves in the long walls, which have the most material to carry them, and the opening at the narrow end, which is the end a card box is opened from. The channel geometry is computed once as though the slide were along X and the two axes swapped when it is not, so there is one set of numbers rather than two chances to get them wrong.

The sliding box cut two grooves into its side walls and left both end walls solid, which makes a box whose lid can be dropped in but never slid — the one thing the type exists to do. The grooves and the opening are the same slot, so one subtraction now makes both: it bites `groove_depth` into each side wall and runs out through the **+X end wall**. The far end keeps its wall, because that is the stop the closed lid seats against, and the lid is sized to fill the channel from that stop to the open end so it finishes flush rather than short.

### The Dovetail Profile: Angled, Interior Over Half Wall Width (FR-002c–FR-002f)

The grooves and the lid edge are not square slots — they are an **angled dovetail**, so the lid is trapped in its grooves rather than riding on two square tongues. In cross-section, perpendicular to the slide axis, the lid is a trapezoid that is **the box interior at the top and reaches half a wall width into each wall at the bottom**:

```
     ┌──────────────────┐   top face: the box interior (width − 2 × wall)
    /                    \
   /                      \  straight angled flanks
  └────────────────────────┘  bottom face: half a wall into each side
```

- **Top = the box interior.** The lid's top face is the box width minus **twice** the wall thickness — no key at the top.
- **Bottom = half the wall width.** The lid reaches `wall_thickness / 2` into each wall at its underside.
- **Straight angled flanks** join the two, so the profile is a trapezoid, not a square rib.

The flanks angle *outward* from the interior top to the half-wall bottom, which is the whole point of a dovetail: the groove's floor is wider than its opening, so the lid **can slide along the axis but cannot be lifted straight out** — and the groove never reaches the outer face, so half the wall always stays behind it for support. The first pass got the taper the wrong way round — wide at the top, narrow at the bottom — which made a lid the box could not hold: it lifted straight off. The next pass cut the key through to the outer face (full wall width at the bottom), which left no wall behind the groove; and a later pass made the flank too steep. The settled profile is interior at the top, half a wall width at the bottom.

Both long edges of the lid carry this profile for their whole sliding length, and the two long walls carry the **mirror-image groove**. The lid is the **same shape** as the groove it runs in — one set of numbers describes both halves, and there is no room for the two to drift apart. The same geometry is emitted by the `sliding_track` closure feature, which returns the body groove and the lid edge from one function.

The **stop wall is dovetailed to the same depth** as the two sides, so the lid's leading end seats there rather than leaning on a flat face — see "The Back Is A Seat, Not A Wedge" below for why that is safe and how it is told apart from the shape it resembles. The open end runs straight out, so the lid finishes flush with the mouth. The lid is cut smaller than the channel by `sliding_slack` on every mating face — default **0.1mm per side** — so it slides freely rather than binding (FR-002f); a caller can open the gap up for a loose slide or tighten it for a close one without touching the geometry. The lid's leading end and corners are eased so it starts into the grooves instead of catching on their mouths — "Getting The Lid Started" below. The flanks themselves stay square (FR-044i's square-edges rule is untouched: the easements live only on the end that enters first).

### The Back Is A Seat, Not A Wedge (FR-002e, FR-002e0)

The stop wall carries the dovetail too, cut to the same depth as the sides: full thickness at the channel opening, half of it at the channel floor. The lid's leading end is tapered to match and slides into it. Without that seat the leading end rests on nothing — the lid is held along its flanks and free at the back, so it lifts and rattles there.

The reason to be careful here is that this shape has a dangerous twin. A **wedge catch** — a taper the lid has to be driven under to close and sprung back out to open — looks identical in a render, and it is the one thing a sliding lid must not have: the part that flexes is the lid's leading lip, the thinnest section of the part at the end of the longest lever, and it is printed, so it flexes by opening the bond between layers.

What separates them is not the cross-section but the **travel**. Because the lid's leading taper has the same slope as the seat's, the two faces stay parallel, `sliding_slack` apart, for the whole way in — nothing ever has to deform. So the plan's check is the travel itself: slide the closed lid out along its axis and at every point it must share **zero** volume with the body, while lifting the closed lid straight up must drive it into the body within half a millimetre (SC-048). The first number says it is not a wedge; the second says it is still a seat. A cross-section measurement alone cannot tell the two apart, which is why the first version of this section removed the back dovetail outright on the strength of one.

Holding the closed lid *shut* is a separate job, and it belongs to the bump catch below — not to the seat.

### Getting The Lid Started (FR-002d, FR-002e4)

Two easements, because two different things snag when a lid is offered up to the mouth.

**The vertical corners are rounded.** Those are the corners that arrive first, and square ones catch on the groove mouths. The radius defaults to a quarter of the wall and is capped at the dovetail's depth, so it can never eat the key that retains the lid. It is applied uniformly to all four corners rather than only the leading pair — partly because the trailing pair is the exposed end and wants rounding anyway, and partly because pybosl2 0.7.8's *per-corner* rounding list translates the whole solid: a lid asked for `[0, 0, r, r]` came out 23mm down the slide axis, leading end buried in the box and trailing end hanging outside it. A scalar is correct.

**Both horizontal edges of the leading end are chamfered.** The underside one keeps the thin leading lip off the groove floor; the top one keeps the lid's top corner off the wall lip. The chamfer is a **quarter** of the lid's thickness — it was half, which takes a 2mm lid down to a 1mm knife edge, a taper big enough to read as exactly the wedge this section is at pains to avoid.

The top chamfer has a subtlety the underside one does not: the leading face slopes (that is the seat), and it leans *away* from a vertical cut going down. A vertical cutter therefore does not take the corner off — it removes a wedge from inside the lid and leaves a feather edge hanging on the face. Its inner vertex has to ride the sloped face instead. Riding it exactly then makes the two surfaces coincident, which CSG resolves by keeping a zero-width sliver, so the cut measures as though it never ran; the cutter is backed off by 0.02mm to land clearly outside. Both failures produced a lid that looked chamfered and measured unchamfered.

### If A Sliding Lid Needs Holding Shut, It Is A Bump (FR-002e1, FR-002e2, FR-002e3)

A lid that only needs to not slide out in a bag wants a **detent**, and a detent is a bump and a dimple — a hemisphere on the lid dropping into a slightly larger hemisphere in the wall. The deflection is the bump's own height, a few tenths of a millimetre, taken across the lid's thickness rather than by peeling its leading edge, and it is a click rather than a press-fit because the dimple is cut larger than the bump by the fit clearance.

**The catch belongs at the outlet, not at the stop.** The bump rides on the lid's trailing end and the dimple sits in the wall beside the mouth, so the two meet only in the last few millimetres of travel. Put the catch at the closed end instead and the bump is dragged the whole length of the groove on every open and close — it wears the groove, it makes a long lid stiff to start, and it gives no clue to the hand about when the lid is home. At the mouth, the click happens exactly when the lid is closed.

The catch is generated from the same slide-axis frame as the channel, so it lands on the correct pair of walls whichever way round the box is. It is **off by default** on a plain sliding box — the original toolkit's sliding box has no catch, and a dovetail on its own already holds a lid in — and always on for the sliding-catch and card-library types, which exist for it. Setting a catch radius on a plain sliding box turns it on.

### Rounding a Lid Without Rounding Away Its Support (FR-044h, FR-044i)

A lid's outer edges are rounded because they are the outside of the closed box — but a lid is thin, and its edges are also what hold it. Two limits keep the second from being sacrificed to the first:

- **The radius is capped at half the lid's thickness.** A body's radius is sized off the *wall*, which on a 2mm lid can be most of the plate; what it removes is exactly the material doing the bearing. Half leaves the other half square.
- **Only the edges that finish outside get rounded**, decided by the type through a `lid_rounded_edges` hook. A cap or magnetic lid sits on top, so its four vertical corners and top face all qualify. A **sliding** lid does not: three of its four sides live inside the channel — two in the grooves, one against the stop — so only the end it slides out through is rounded, along with its top edge and the two vertical corners there (FR-044i).

### Tray Wells, and Where Rounding Stops (FR-044f, FR-044g)

**Rounding is off by default and opted into** (FR-044f). A well is square unless its builder sets `holds_pieces`, because most wells are shaped by what they hold — a card slot, a token silhouette, a board recess — and softening those changes a fit rather than improving it. The case that benefits is a tray of loose pieces you have to pick out, and it says so. This is the same principle as the mating surfaces: rounding is for geometry the toolkit invents, never for geometry the game dictates.

A well that does opt in gets **both its vertical corners and its floor edges** rounded (FR-044f1) — corners alone leave the piece sitting in a square trough, which is the shape the rounding existed to remove. The radius comes from the **well's own depth, `depth × 2/3`**, not from the box: what makes a piece retrievable is the curve the finger follows, so a deep well wants a big sweep and a shallow token tray a small one, and a box-wide constant gets both wrong. It is capped so it can exceed neither the footprint nor the depth. An SVG silhouette or element pack stays square even when declared a tray (FR-044g) — FR-045's fidelity rule overrides the default rather than combining with it.

One trap sits underneath this. The obvious guard on "is this radius buildable" is `radius < min(size) / 2`, and it is wrong often enough to matter: it rejects an 8mm floor fillet in a 12mm-deep tray — perfectly buildable — because the *depth* is the smallest dimension. What actually constrains a fillet is the dimensions **perpendicular** to the edge it runs along, halved only where the opposite edge is rounded too (two fillets growing towards each other meet at half the gap; one growing alone can use all of it). `rounding.max_radius` computes that from the resolved edge matrix.

### Curve Precision: Export vs Preview (FR-046)

`export()` and `show()` deliberately default differently:

- **`export()` → 256 facets per circle.** This is the geometry that gets printed, so it is worth paying for, and the cost is paid once per build.
- **`show()` → no fixed facet count**, deferring to `fa`/`fs` so each curve is faceted according to its actual size. That is what keeps an interactive preview responsive.

Both accept an explicit `fn`/`fa`/`fs` override. The cost is real and worth knowing: Irish Gauge's 32 files take about **90 seconds** at 256 facets against a few seconds at the `fa`/`fs` default, so a quick throwaway build should pass a smaller `fn` rather than take the default.

**Print quality is for the 3MFs, not for CI (FR-046a).** A CI pass is not a build. What the export tests actually check is which files get written, skipped, cached and deleted — decisions that do not depend on how finely a cylinder is tessellated — so CI sets `PYBOXBUILDER_EXPORT_FN` coarse, writes only to temporary directories, and produces no printable output. Left at the shipped default the suite went from about a minute to over five, all of it spent tessellating geometry no one was going to print. The override is external so the library's own default is unaffected by how it is tested.

**CI's geometry coverage comes from the preview path, not from export (FR-046b).** `Project.preview_pieces()` — what `show()` renders — resolves the layout, packs it, and builds every body, lid and spacer, without a file, a render binary, or a high facet count. All twelve example projects build that way in about ten seconds, which catches the failures that only appear on real projects: a packing that no longer fits, a box type that raises on a combination an example uses, a compartment that overflows its interior. Export's job in CI is narrower — proving the *file* decisions are right — and it does not need geometry anyone would print.

### Finger Holes & Box Edge Smoothing

All cutouts and outer edges MUST be smooth — no sharp 90° corners that catch a finger or a card.

1. **Card finger holes (top-to-floor scoop).** A finger cutout on a card box (or any box holding cards) MUST run from the top rim down to the floor, so a finger can reach the last card at the bottom of the stack. The scoop profile is one continuous smooth curve, not a rectangular notch:
   - The top opening **curves smoothly into the box wall** — no right-angle lip at the rim.
   - The bottom **curves into the floor**, blending the wall cutout into the box bottom without a sharp corner.
   - The entire profile is **filleted** — no sharp edges anywhere along the scoop.

1a. **An edge scoop is two radii and three straight runs (FR-043a).** Read from the top down::

        ===========...                      ...===========   flat top surface
                     ''..                ..''                r1: top face into wall
                         \              /
                          |            |                     straight throat
                          '..      ..''                      r2: wall into floor
                             ''--''                          flat bottom

   **r1** leaves the top face *horizontally* and arrives at the wall *vertically*, so the top surface rolls over the rim instead of meeting the cut at an edge. **r2** turns the wall into the floor. Each arc is tangent at both of its ends, which is what makes the whole outline smooth — two radii state that more directly than a curve fitted between them, and each is a number a designer can set.

   The bottom is a **flat run**, not the meeting point of two fillets: a piece rests on it and a finger slides along it to get underneath. r2 is capped so at least a quarter of each half-width stays straight, because a fillet grown to the full half-width closes the flat into the U-shaped trough the flat bottom exists to avoid.

   An earlier attempt used a `3t² - 2t³` smoothstep for the mouth. It is worth recording why that was wrong, since it looked right on paper: the smoothstep is vertical at *both* ends, so while it matched the throat perfectly it arrived at the rim vertical too — leaving exactly the hard edge against the flat top face that the transition was supposed to remove.

1a1. **Every radius has a derived default (FR-043a2).** Nothing here should need an override to look right: `r1` and `r2` are each half the throat's half-width, the cut's height follows its radius, and the face fillet follows the wall. Fixed constants were the previous approach and they do not survive contact with scale — a 3mm roll is invisible on a 14mm finger hole and overwhelming on a 4mm one, and a 6mm default height (inherited from the original's *wall depth* parameter, which is a different quantity) made every hole a shallow nick whatever finger it was cut for.

   When the throat and its roll cannot both fit the span, they shrink **together** (FR-043a3). Capping the throat first and handing `r1` the remainder reads as the obvious order and is a trap: a throat already at half the span leaves `r1` exactly zero, so the top roll — the most visible part of the scoop — disappears on precisely the narrow compartments that most need the smoothing.

1a4. **The straight run between the arcs is a solved common tangent (FR-043a4).** Both circles are placed tangent to the throat line, so the tangent solver returns that vertical and the geometry is unchanged today — the point is that it no longer *depends* on that placement. Move either centre and the profile stays tangent at both joins instead of stepping, and a step in a scoop's wall is exactly what a non-tangent join looks like.

   Selecting the right tangent matters: it is an **internal** one. The cut's boundary wraps the *outside* of the floor circle and the *inside* of the rim circle — the arcs curve opposite ways — so the run touches the floor circle on its right and the rim circle on its left. Filtering for "outside both", which is the natural first guess, picks an external tangent and throws the profile 12mm wide.

1a5. **A compartment scoop runs to the box's top face, not the interior ceiling (FR-043b3).** The ceiling is where the *well* stops, not where the wall does: a lidded box carries a lid band above the interior, and a scoop that stops at the ceiling leaves that band standing over the cut as a step, with the r1 roll buried inside the wall where nothing can reach it. Running to the top face puts the roll on the box's own edge, which is where it is meant to merge.

1a8. **Wall tops are per side, not per box (FR-043b7/b8).** The four walls need not end level: a sliding box's channel runs out through its exit wall, so that wall stops a lid thickness below the box's top. A scoop aligned to a single box-wide "top" is then built at the wrong height — and does it silently, which is how it survived being moved onto the exit wall.

   `box/base.wall_tops(box, spec)` returns `{side: z}`, defaulting to the box's top less any lid band and overridable per type through a `wall_tops` hook. The map is put on the spec, so both paths that align to a top read the same numbers: exterior finger holes in `apply_finger_holes`, and compartment scoops through `build_contents`. The sliding family declares all four sides at the channel floor — the exit wall because its material is gone, the other three because a cut above that line breaks into the channel the lid slides in.

1a7. **A sliding box overrides that: the scoop goes in the wall the lid leaves by (FR-043b6).** The cards come out the same way the lid does, and only that wall will do — the other three carry the lid, two of them holding the grooves it rides in, so a scoop cut into a groove takes away the bearing that keeps the lid straight. The type states this through a `preferred_scoop_side` hook rather than the compartment guessing from its own proportions; the shape cannot know what the lid needs.

1a6. **A scoop defaults to the shorter wall (FR-043b4).** A card stack is lifted out across its narrow dimension. In the long wall the cut is in the wrong place and the user reaches across the whole box for the cards, which is what Emberleaf's card boxes were doing. Overridable per compartment, since a box that holds something other than cards may want otherwise.

1a2. **An exterior finger hole hangs from the top of the *interior* (FR-043b1).** Not from the rim: on a lidded box the lid or its track occupies the band above the interior, so a hole aligned to the rim starts inside solid material and comes out as a nick in the top edge instead of a cut into the well. The generic rule is `height - lid_thickness`, and the types whose body is *already* shortened for their lid — cap, slipover — pass their own `interior_top` so the allowance is not taken twice. That is what makes the same one-line `finger_hole(side)` land correctly on no-lid, sliding, cap and slipover alike (FR-043b2).

1a3. **The face fillet is swept along the outline, by BOSL2's own `offset_sweep` (FR-044e1).** The scoop's profile is kept as a **point ring**, not as a 2-D shape built by unioning two mirrored halves, because the ring is what the sweep offsets: run around the outline, the fillet traces the scoop's own curve on each face.

   A hand-rolled stand-in stood here first and got this wrong twice, both times plausibly. Stacked prisms, one per offset slice, left a visible staircase across the fillet. Replacing them with a **chain of convex hulls** removed the staircase and broke something worse: the convex hull of a U-shaped outline fills the U in, so the fillet came out as a straight ramp from the bottom of the cut to the top instead of following it round. Convexity is the assumption to watch — every hull-based smoothing carries it silently, and a scoop is the shape that fails it.

   **`os_circle` is not the rim profile this needs**, which is the third way the same fillet has gone wrong. Its arc is tangent to the cut's *wall* and meets the end face at 90°, so on a subtractive solid it hollows a cove **inside** the wall and leaves the opening at nominal width — a cutout, not a roundover. The roundover is the mirrored arc, tangent to the **face**: `z = r·(1 - cos a)`, `inset = r·sin a`, supplied as an `os_profile`. Measured on a 4mm wall with a 2mm fillet, the cut is 45.9mm across at the face against 42.0mm mid-wall; the cove had those the other way round.

   One consequence of the implementation's convention is worth stating, because it is the opposite of what the name suggests: the path handed to `offset_sweep` is the cross-section **at the end face**, and the rim profile moves it as you travel inward. So the *widened* outline is the path, and the rim brings it back in — that is what puts the extra material at the face where a roundover belongs.

   One detail the outline has to get right: it continues `RIM_OVERSHOOT_MM` **above** the rim rather than closing flush across the top. Closing flush puts a zero-angle cusp at each end of the r1 arc — the arc arrives travelling horizontally outward, the closing edge leaves horizontally back inward — and offsetting a cusp miters to infinity. Measured, a ±15mm profile came back ±55mm. Where there is material above the interior (a lid band, a sliding track) that overshoot is trimmed back off, so the cut stops at the interior top instead of carving through the band the lid seats in.

1a9. **Width and curve are independent (FR-043c3).** The top roll is an **ellipse quadrant**, not a circle: its outward flare sets how wide the mouth is, its downward rise sets how gently the top surface turns into the wall. A circle ties the two together, so the only way to get a gentler curve is a wider cut — backwards on a shallow wall, where there is height to spare for the curve and none to spare for the mouth. Only the *vertical* extents compete for the wall's height, so a shallow wall shortens the rise and leaves the width alone: Emberleaf's 6.5mm player-box wall and its 48mm card-box wall now cut the same 36mm-wide scoop, each with as much curve as it has room for.

   The floor fillet is separately generous (0.65 of the throat half-width) because it lives *inside* the throat and so costs no width at all.

1a10. **A silhouette slot needs a pull-out, and it is part of the slot (FR-043c1, FR-043c2).** Cutting a slot to a piece's outline is what makes it hold the piece — and what leaves nowhere to get a fingertip under it. So every element slot carries a finger dish by default, half the piece's depth: deep enough to reach under, shallow enough that the piece still seats flat instead of tipping into the dish. It is rounded on every edge, curving in from the floor around it, because a dish with a square step around it is worse than no dish — the step is what a fingernail catches on. Depth, width and opting out are per slot.

1b. **A floor finger hole is not an edge scoop (FR-043a1).** They were briefly built from one profile, which put a flat-bottomed pan where a bowl belongs. An edge scoop is a channel you sweep a finger *along*; a floor hole is a bore you push a piece *up* through, so its bottom is tangent to the floor. The two share `_sweep_through_wall` — the depth matching, face fillets, floor clip and side placement are genuinely common — and differ only where they should, in the profile.

2. **Main box edges are smooth (FR-043d).** Every exposed edge of every printed piece is rounded over at `wall_thickness / 2` by default (FR-044):
   - The vertical corners of the box, and the bottom base edges.
   - The top edges — but **only where nothing has to mate there**. On a lidded box the rim is a sealing surface, so the body's rim stays square and the *lid* carries the rounding; the closed box still reads as rounded top, sides and bottom. On a lidless box the rim is exposed, so the body rounds it directly.
   - The internal wall/floor junction, filleted by rounding the bottom edges of the *void* that gets subtracted.
   - **Not** the internal vertical corners. Rounding those is one more `edges=` entry and looks like an obvious win, but the fillets run the full height of the box — including the band where a sliding lid seats — and add material exactly where the plate has to pass. Measured, it put 0.59mm³ of body inside the lid on all three sliding types (FR-044a).

   Rounding is applied by **subtracting the corner slivers** (`pyboxbuilder/rounding.py`), not by intersecting with a rounded envelope. The two are equivalent on an ordinary box, but the intersection also silently trims anything reaching outside the declared envelope — and a hinge barrel legitimately does. Subtracting only what the rounding removes leaves the flat faces untouched, which is what keeps the Phase 18 invariant intact: a rounded box still measures its declared size, to the faceting tolerance below.

2a. **Partial lids: the grip is rounded smaller, on both halves (FR-044b).** A cap's skirt grips a stepped band on the body; a slipover's sleeve grips the whole body. Those surfaces are a *fit*, not a finish, so they take `inner_rounding` — half the outer radius by default — and, critically, **both halves take the same value**, so the lid's inner corners nest over the body's instead of meeting them at a gap. The radius is smaller for a physical reason as well as an aesthetic one: a skirt wall is `wall_thickness / 2`, and a full-size fillet would consume most of it. Everything outside the grip (the cap body below its band, the slipover's foot, the lid's own outer corners) keeps the full radius, because that is what a hand touches. The **interior cavity keeps square vertical edges** throughout (FR-044c) — only its wall/floor junction is filleted.

2b. **Two traps in the mini-language and the tessellation**, both of which produce geometry that looks plausible and is wrong:

   - `Anchor.Z` reads as "the four vertical edges" and is **not**: it is an *axis* anchor, which the edge language resolves to a **single** edge. A box rounded with it comes back with one rounded corner and three square ones, which is exactly how this was found. The four two-face anchors (`FRONT_LEFT`, `FRONT_RIGHT`, `BACK_LEFT`, `BACK_RIGHT`) give the full `[1, 1, 1, 1]` vertical row (FR-044d). The same mistake was already present at both compartment-well call sites.
   - The default `fs = 2mm` sizes a facet by arc *length*, which is right for a cylinder and wrong for a fillet: a 1mm roundover has a 1.6mm quarter-arc, so it gets **one segment** and comes out a chamfer. Edge rounding therefore has a floor of 48 facets per circle. That number is set by a second effect rather than by appearance: a rounded edge is an *inscribed* polygon, so it pulls its face inwards by the sagitta `r · (1 - cos(180°/fn))` — 0.029mm at 16 facets, 0.003mm at 48. Declared sizes are exact to that tolerance, which is well inside the library's 0.1mm precision but is not zero, and no faceted fillet can make it zero.

3. **Implementation.** Box bodies use pybosl2 `cuboid(..., rounding=...)` for their outer edges. The finger scoops are ported from the original's `FingerHoleWall` / `FingerHoleBase` (`components.scad`), which are the reference for what "smooth" means here, and they carry **three separate roundings** that are easy to conflate:

   - **The mouth** (`rounding_radius`, default 3mm) — the top of the swept profile flares outward into the rim with a concave fillet on each shoulder, so the opening curves into the wall instead of ending in a right-angle lip. This is the part a fingertip rides over.
   - **The faces** (`rounding_edge`, default `wall_thickness / 2`) — the sweep's two ends get a *negative* `os_circle` rim, which flares the cut outward tangent to each face so it flows onto the side of the box rather than leaving a sharp shadow line. Independently switchable per face (`round_inner` / `round_outer`).

     **Which surface the arc is tangent to is the whole feature** (FR-044e), and it is easy to get backwards, because the two candidates are indistinguishable in a parameter list: both run from the full radius at the face to zero at depth `r`. `sqrt(r² - d²)` is tangent to the *cut's own wall* and meets the face at 90°, which on a subtractive solid scoops a **cove** — a groove gouged in a ring around the opening, material taken out of the box rather than an edge softened. `r - sqrt(r² - (r - d)²)` is tangent to the *face*, and that is the roundover: the face rolls into the cut. The two are mirror images, so picking the wrong one yields geometry that is smooth, symmetric, plausible — and a defect.
   - **The base** — the bore is a circle tangent to the floor plane, so a card scoop's bottom curves into the floor rather than meeting it at a corner; a shallow floor scoop adds a `-fillet` cuboid pad blending the cut into the floor surface.

   Two constraints on this are load-bearing rather than incidental, and both were found by measuring rather than by looking:

   - **The sweep must be exactly the wall thickness** (`depth_of_hole = wall_thickness + 0.03`, centred on the wall), because a face fillet is produced by flaring the sweep's *end* — the end has to coincide with the face. Overshooting the wall by a millimetre, the obvious way to make sure a boolean leaves no skin, puts both fillets out in the air beyond the box and leaves the cut meeting the faces at a hard edge after all. It also fails to pierce any wall thicker than the overshoot.
   - **The cut stops a controlled distance *below* the well floor**, not flush with it. Flush leaves the cut's bottom face coplanar with the floor, and a coincident face renders as speckle and is the classic way a boolean leaves a zero-thickness skin. The dip defaults to 0.2mm, or half the floor thickness (capped at 1mm) when the floor is known — the original's `height - floor_thickness + 1` is the same trick. It is a *limit* on the flare, not an offset applied regardless: with the roundings off there is no flare and the cut bottoms out exactly at the floor.

   `pyboxbuilder/sweep.py` provides the `offset_sweep` these need. Its rim arcs are built as a **chained hull** of offset slices, not as stacked prisms: one prism per slice is the obvious approach and what the legacy helper does, but it leaves an eight-step staircase across the fillet, which is visible in a Manifold render at print scale and is not a fillet at all.

   A card finger hole runs the compartment's full depth so a finger reaches the last card at the bottom of the stack; an exterior box hole instead hangs from the rim, capped at the interior depth so it can never open the base.

4. **Sliding boxes: chamfer/round on the lower lid-track wall.** On a sliding-lid box the two lid-track walls are asymmetric — one wall sits lower so the lid can slide into its dovetail groove. Where possible, the chamfering/rounding MUST be applied on that lower wall (the one the lid slides over), not the higher wall, so the rounded edge does not interfere with the sliding track. To make this true the lid section SHOULD be rotated to a different side (swap which side the lower track wall is on) — so the smooth edge always lands on the lower, non-track side — **unless the box's length/width offset is too large for the rotation to work well** (a long, narrow card box rotated 90° would waste footprint and the lid would slide along the short axis). In that case keep the original orientation and accept the rounding on whichever side geometry dictates.

### Source Code (repository root)

```text
pyboxbuilder/                    # NEW: Greenfield package
├── __init__.py                 # Re-exports public surface
├── py.typed                    # PEP 561 marker for downstream type checking
├── enums.py                    # BoxType, LabelMode, PatternType, ScoopSide
├── project.py                  # Project class (top-level API)
├── builders/                   # Typed per-box-type builders
│   ├── _base.py                # BoxBuilder base
│   ├── sliding.py              # SlidingBoxBuilder
│   ├── cap.py                  # CapBoxBuilder
│   ├── hinge.py                # HingeBoxBuilder
│   ├── filament_hinge.py       # FilamentHingeBoxBuilder
│   ├── magnetic.py             # MagneticBoxBuilder
│   ├── inset.py                # InsetBoxBuilder
│   ├── sliding_catch.py        # SlidingCatchBoxBuilder
│   ├── slipover.py             # SlipoverBoxBuilder
│   ├── slipover_path.py        # SlipoverPathBoxBuilder
│   ├── cap_path.py             # CapPathBoxBuilder
│   ├── no_lid.py               # NoLidBoxBuilder, PathBoxBuilder
│   └── card_library.py         # CardLibraryBoxBuilder
├── lid/                        # NEW: Fresh lid decoration pipeline
│   ├── builder.py              # LidBuilder, PatternBuilder
│   ├── label.py                # Label generation (framed, frameless, diagonal)
│   ├── pattern.py              # Pattern fill: full ShapeType catalog (dense/lattice shapes, pentagon tilings, tessellations) as through-holes
│   └── color_layers.py         # Color layer assignment for MMU
├── box/                        # NEW: Fresh box construction pipeline
│   ├── base.py                 # Abstract box type definition
│   ├── registry.py             # BoxType enum → box class dispatch
│   ├── types/                  # 14 box type implementations
│   │   ├── sliding.py, cap.py, hinge.py, ...
│   └── interior.py             # Interior frame and hollowing
├── compartments/               # NEW: Fresh compartment layout
│   ├── builder.py              # CompartmentBuilder
│   ├── finger_hole.py          # Finger scoop/notch geometry
│   ├── layout.py               # 2D shelf-based auto-layout
│   └── sizing.py               # Auto-sizing expansion logic
├── packing/                    # NEW: Fresh nested box packing
│   ├── layout.py               # 3D box packing into game box
│   ├── spacer.py               # Spacer tray generation
│   └── cache.py                # Two-level cache (memory + disk JSON)
├── export/                     # NEW: Fresh 3MF export
│   ├── exporter.py             # BoxExporter
│   ├── result.py               # ExportResult
│   ├── hausdorff.py            # pymeshlab-based conditional write
│   └── layout_pdf.py           # PDF packing guide generation
├── shapes/                     # BORROWED: Existing shape generators
│   └── (coin, hexagon, rounded rect, etc. from shapes.py)
└── tesselations/               # BORROWED: Existing tessellation generators
    └── (penrose, pentagon, voronoi, etc.)

pyboxbuilder/__init__.py         # SINGLE IMPORT entry point (the package itself):
                                 #   from pyboxbuilder import Project, BoxType, ...

boxes/                          # Per-game insert projects
├── earth_animal_kingdom/
│   └── earth_animal_kingdom.py

tests/
├── test_pyboxbuilder/           # NEW: Tests for pyboxbuilder
│   ├── test_enums.py
│   ├── test_builders.py
│   ├── test_project.py
│   ├── test_lid_label.py
│   ├── test_lid_pattern.py
│   ├── test_compartments.py
│   ├── test_packing.py
│   ├── test_export.py
│   └── render/
│       ├── test_box_render.py
│       ├── test_lid_render.py
│       └── test_export_render.py
```

**Structure Decision**: `pyboxbuilder/` is a greenfield, **installable mypy-typed Python package** sharing the repo with the existing codebase. It borrows tessellation and shape algorithms but defines its own box pipeline, lid pipeline, builders, packing, and export. The single public import is `from pyboxbuilder import Project, ...` (served by `pyboxbuilder/__init__.py`). The package ships a `py.typed` marker (PEP 561) so downstream users get full mypy type checking, is declared under `[tool.setuptools.packages.find]` in `pyproject.toml`, and is installed with `pip install -e .` so examples and tests import it as a regular site-packages dependency. The existing root `.py` files remain untouched — they continue to work for existing users. This is an additive package, not a replacement.

## Borrowed vs. Fresh

| Component | Status | Rationale |
|-----------|--------|-----------|
| Tessellations (penrose, pentagon R1–R15, voronoi, lizard, goose, chicken, kite, hex, quad) | Borrowed | Pure algorithms, no pipeline coupling. Ported from `tesselations/`, `pentagon_tilings.py`, and `patterns.py` `ShapeType` enum (42 members) |
| 2D shape generators (coin, hex, rounded rect) | Borrowed | Pure geometry functions |
| pybosl2 CSG (cuboid, cylinder, boolean ops) | Dependency | External library, not our code |
| Box construction pipeline | **Fresh** | New base class, new builder→geometry mapping |
| Lid decoration pipeline | **Fresh** | Not constrained by `LidPlate`/`build_lid()` contract |
| Compartment layout | **Fresh** | New auto-layout with row alignment |
| Nested box packing | **Fresh** | Fill-to-fit rows, spacer generation. Integrates dynamic dimension expansion based on 3D packing solvers, and propagates resolved sizes back to builders using a `final_size` attribute. |
| 3MF export | **Fresh** | New exporter, same pymeshlab backend |
| Typed builder API | **Fresh** | Enums, typed dataclasses, `@overload` dispatch. Adds a unique `box_id` field to distinguish duplicate instances. |
| Caching strategy | **Fresh** | Same SHA-256 approach, new cache file. Stores 3D box packing layouts in `.layout_cache.json` to bypass solver on subsequent runs. |
| PDF packing guide | **Fresh** | Standards-compliant valid PDF with scaled 2D top-down box layout, labels, dimensions, packing order numbers. Layered exploded breakdown with arrow connectors. Cached regeneration via SHA-256 layout hash. |

## Earth Animal Kingdom Example Migration

The reference example under `boxes/earth_animal_kingdom/` must faithfully port the original design (`examples/earth_animal_kingdom.py` / `.scad`) to the new `pyboxbuilder` Project API. The original design is more complex than the initial simplified port and must include all components.

### Game Box

- **Retail box**: 288mm × 158mm × 47mm (W × L × H)
- **Defaults**: wall_thickness=2.0, floor_thickness=1.6, lid_thickness=2.0, gap_threshold=10.0, min_spacer_dim=15.0
- **Design principle**: All box dimensions are **generated** from the game box size and content constraints — no fixed sizes. The example demonstrates the `size=None` auto-compute pattern: each box's minimum is derived from its compartments, and the packing solver expands boxes to fill available space within the 288×158mm game box interior.

```python
box_width  = 288
box_length = 158
box_height = 47

# Additional items that share the game box interior
score_pad_width     = 81
score_pad_length    = 99
score_pad_thickness = 5
score_pad_number    = 1

# Card dimensions (computed from card count, not hardcoded box size)
animal_card_num = 36
card_10_thickness = 6
single_card_thickness = card_10_thickness / 10
animal_card_size = MakeCardSize(
    length=123,
    width=72,
    single_card_thickness=single_card_thickness
)
# Box auto-sized: card box height = animal_card_num × single_card_thickness + clearance
#                  card box width  = animal_card_size.width + 2 × wall_thickness + clearance
#                  card box length = animal_card_size.length + 2 × wall_thickness + clearance
```

### Boxes (7 total, all sizes generated — no hardcoded dimensions)

Each box uses a distinct body color so they can be told apart at a glance during unpacking and assembly.

| Box | Type | Color | Sizing Strategy | Contents |
|-----|------|-------|-----------------|----------|
| AnimalCardsBox | Sliding | `Color("darkgreen")` | Width = card width + 2×wt + tolerance. Length = card length + 2×wt + tolerance. Height = card_stack + floor + lid + finger clearance | 36 animal cards |
| SproutBox | Filament Hinge | `Color("lightgreen")` | Min width = 72, min length = 158. Height = sprout height + floor + lid | 50 sprout cubes (8mm³) |
| CanopyBox | Filament Hinge | `Color("olive")` | Width = canopy footprint + 2×wt. Length = card length + 2×wt. Height = canopy stack + floor + lid | 20 canopy tokens |
| AnimalBox1 | Slipover | `Color("gold")` | Width, length, height **generated by 3D bin-packing solver** from half of ANIMAL_PIECES list | 18–19 animal token compartments |
| AnimalBox2 | Slipover | `Color("orange")` | Same as AnimalBox1 — second half of animals, different color for distinction | 18–19 animal token compartments |
| SpacerBox | No Lid | `Color("lightgrey")` | Auto-generated by packing solver to fill remaining game box gaps | Hollow tray |
| Boards | No Lid | `Color("darkgrey")` | Width = 174, length = 150, height = score_pad_thickness × score_pad_number | Score pad + board stack |

**Color specification**: pybosl2's `Color` supports webcolor names (e.g., `Color("darkgreen")`, `Color("gold")`, `Color("orange")`). Do NOT hardcode RGB numbers in project files — use webcolor names. See pybosl2's color table for supported names.

### Animal Token Inventory (37 entries, 31 unique species)

Ported from `ANIMAL_PIECES` in `examples/earth_animal_kingdom.py`. Each entry: `object(width=W, length=L[, num=N])`. Tokens are 8mm thick. Species with `num > 1` share a single compartment sized to fit all copies.

```python
elephant       = object(width=43.5, length=54)
polar_bear     = object(width=36.5, length=53)
cow            = object(width=36.5, length=47.5)
pig            = object(width=24.5, length=35)
gazelle        = object(width=41,   length=35)
turkey         = object(width=24,   length=25, num=5)
fly            = object(width=11,   length=11)
capybara       = object(width=16.5, length=32, num=2)
capybara_2     = object(width=16.5, length=32, num=3)
monkey         = object(width=29,   length=24)
pangolin       = object(width=16,   length=21, num=5)
deer           = object(width=47,   length=25.5)
goanna         = object(width=25,   length=30)
fox            = object(width=16,   length=35)
snake          = object(width=14,   length=41.5)
rabbit         = object(width=18.5, length=21)
termite        = object(width=12,   length=12, num=5)
ornyx          = object(width=39,   length=40)
platypus       = object(width=14.5, length=25)
lemur          = object(width=22,   length=30)
peacock        = object(width=30,   length=27)
gopher         = object(width=17.5, length=17, num=5)
crocodile      = object(width=16,   length=85)
goat           = object(width=37,   length=36)
jaguar         = object(width=20,   length=49)
rhino          = object(width=36,   length=64)
goose          = object(width=25,   length=21)
eagle          = object(width=31,   length=43)
spider_monkey  = object(width=26.5, length=25)
hoopoe         = object(width=17,   length=16)
kangaroo       = object(width=37,   length=39)
loon           = object(width=26.5, length=13)
tarsier        = object(width=29,   length=12.5)
jay            = object(width=12.5, length=12)
chipmunk       = object(width=15,   length=14)
quokka         = object(width=24,   length=15)
beaver         = object(width=15.5, length=35)
```

### Animal Bin-Packing Strategy

Animal tokens are split into two halves via a best-fit-decreasing 2D bin-packing pass over the two `AnimalBox` containers (each ~165×150mm usable). Within each container, compartments are arranged with 3mm spacing. Multi-quantity species (qty > 1) are stacked in a single compartment whose depth = quantity × 8mm (token thickness). Each compartment floor has the animal name extruded as a 0.2mm raised label. Finger scoops are placed on all compartment front walls.

### 3D Oblique Exploded PDF Guide Layout
To satisfy the layout guide requirements, `layout_pdf.py` renders the game box and nested sub-boxes in a 3D Cabinet Oblique Projection across multiple pages representing distinct stacking layers:
* **Projection Math**: 
  * `X` maps to `x + y * cos(30) * 0.45`
  * `Y` (Z-axis height / layers) maps to `-z - y * sin(30) * 0.45`
  * This projects coordinates from 3D space onto the 2D PDF plane looking slightly from above and to the side.
* **Layer-by-Layer Stacking Breakdown**:
  * Placements are grouped dynamically into three primary layers:
    1. **Base Layer** (`z < 0.1` mm): Boxes sitting directly on the box floor.
    2. **Middle Layer** (`0.1 <= z < H * 0.7` mm): Stacked middle boxes.
    3. **Top Layer** (`z >= H * 0.7` mm): Top-level boards and cards.
  * For each layer, a separate page is generated in the PDF guide:
    * The boxes and spacers belonging to the active layer are drawn in full color.
    * The boxes belonging to the lower layers (already packed in previous steps) are drawn in light gray to provide background context.
    * Boxes belonging to upper layers are hidden.
  * Each box is drawn as a 3D-shaded block, complete with a label and packing order index.
  * The text labels on the boxes in the layout PDF must be visible, larger, and highly readable. If a label is blocked/hidden because another box is stacked on top of it, the label text must be shifted to the side. The text label must only display the box's label, and not display its size/dimensions.
  * Hollow spacer boxes (which can be non-rectangular using 2D polygon paths) are generated to fill all open spaces/gaps, making the insert layout complete to the full extent of the game box. Spacer boxes/trays cannot be thinner than 5mm in any dimension (width, length, or height) to prevent printing extremely fragile slivers. For vertical gaps along the Z-axis, a spacer box is generated if the gap height is >= 3mm (subject to the 5mm minimum thickness rule). If the gap height is < 3mm, the adjacent box's height expands to absorb the gap, prioritizing expansion on the X and Y axes over the Z-axis.

### Spacer Generation: Sweep, then Merge (FR-014a/b/c)

Spacers come out of a three-stage pass in `pyboxbuilder/packing/spacer.py`, driven from `Project.export()`.

**1. Sweep.** Every placed box contributes its six face planes to a global X/Y/Z grid. The grid is swept for cells no box occupies, and the free cells are grown greedily into maximal boxes.

**2. Merge.** The sweep alone does not satisfy FR-014a, and the reason is worth stating because it is not obvious: the plane grid is *global*, so a box in one corner of the game box contributes cut planes that slice free space everywhere else. In the Emberleaf layout the player-box column at `x = 0..98` puts a plane at `z = 39.375`, and that plane cuts the unrelated void at `x = 196` clean in half — two spacers where the space wants one. The number of pieces therefore depends on how many boxes the layout happens to contain, which is exactly what FR-014a forbids.

The fix is a merge pass rather than a smarter sweep. Two spacers are **mergeable** when their union is itself a box: they are flush along one axis (one's max face equals the other's min face) and identical on the other two (same origin, same extent). Fusing such a pair is always safe — the union covers exactly the two originals and nothing more, so it cannot swallow an occupied cell.

The pass fuses repeatedly until a full sweep over the list finds no mergeable pair. Since every merge reduces the count by one, it terminates in at most N rounds. Voids are visited in a canonical (position, size) order, which is what makes the output depend only on the geometry and not on the order the sweep found them in (FR-014b, SC-010b).

Note that this is *determinism*, not *uniqueness*. Three voids in an L can fuse two different ways, and both leave two boxes behind — an L is not a box, so two is the true minimum there and the choice of which pair fuses is arbitrary. Canonical ordering makes that arbitrary choice a stable one.

Merging runs *before* the minimum-dimension filter, so two slivers that are individually too thin to print can combine into one tray that is not.

**2b. Rectilinear merge.** Rectangle fusion cannot reduce an L, T or U, because none of those is a box — but they still want to be one part. `merge_rectilinear` groups the survivors by identical Z span, finds the connected clusters within each group by footprint adjacency, and traces the union outline. The result is a single tray with a polygon footprint, built as a `PathBox` (FR-014d, FR-018).

Outline tracing works by edge cancellation: walk each grid cell's border counter-clockwise, drop any edge that also appears reversed — those are the seams between two filled cells — and chain what survives into a loop, collapsing collinear runs so an L comes back as six points. One subtlety: a reflex corner is the start of *two* boundary edges, so the edge table has to be a multimap. Keying it by start vertex alone silently drops one of them, and the trace then never closes.

Only regions at the **same height** are combined. Two leftovers at different heights can also form an L — in the vertical plane — and fusing those is a mistake: each tray currently rests on whatever is beneath it, and the fused part's upper arm would have nothing under it at all. Irish Gauge has exactly this shape above `CompanyBox2`, and it stays as two trays on purpose (FR-014e).

**3. Clearance and filtering.** Surviving spacers are shrunk by the project's `clearance_slack` (FR-014c) — the sweep measures the true void, but a tray milled to that exact size is an interference fit — and then dropped if any dimension falls below the minimum.

Insetting a polygon footprint is exact rather than approximate, because every edge the packer produces is axis-aligned: a corner's new position is the old one moved by the slack along each incident edge's inward normal (`pyboxbuilder/paths.inset_rectilinear`). A reflex corner correctly moves *out* into its notch, which is what keeps an L's arm the right width — a centroid scale, the obvious shortcut, thins one arm while fattening the other. The normals come from the *directed* edges, since which side is inward depends on the direction the ring is traversed, not on where a corner's neighbours happen to sit.

### When Auto-Packing Works, and When It Does Not

`pack_3d_boxes` is an extreme-point First-Fit-Decreasing heuristic: sort by footprint area descending, and drop each box at the lowest-then-nearest free corner. That is a good fit for loosely-filled inserts, and it is what Earth Animal Kingdom uses.

It has a ceiling. Emberleaf's 18 boxes fill **77%** of the usable volume, and the original layout only achieves that because the box sizes were designed to tile exactly in three columns. Measured against that layout, the solver fails on all five sort strategies, on all twelve variants crossing them with different extreme-point orderings, best-fit selection and corner extreme-point generation, and on 266,000 random permutations. Greedy extreme-point placement fragments the space instead of aligning columns, so the ordering is not the problem.

The practical rules:

* Below roughly 70% fill, hand the boxes to the packer and let it place them.
* Above that, the arrangement is load-bearing and needs to be expressed, not searched for. Give the boxes explicit positions, or make them expandable so the solver has slack to work with.
* A failure is reported as `PackingError` with the fill ratio and any oversized boxes named — never as an empty layout, which is how it used to surface and made an export silently write nothing.

Two things would raise the ceiling: a declarative column/stack layout (the structure is the part worth writing down, not the coordinates), and a stronger solver for the axis-aligned tiling sub-problem. Both are open.

### Compartment Auto-Layout with Rotation
To ensure dense packing of compartments (like the animal compartments in `AnimalBox1` and `AnimalBox2`), `layout_compartments` implements a shelf-packing algorithm with 90-degree rotation support:
* **Sorting Heuristic**: Compartments are sorted by their maximum dimension (width or length) in descending order to establish a clean starting baseline.
* **Rotation Evaluation**: For each compartment, the engine evaluates both the original orientation `(w, l)` and the rotated orientation `(l, w)`. It prefers the orientation that fits in the current row while minimizing row height increase. If neither fits in the current row, it wraps to a new row and evaluates both orientations there.
* **Non-Rectangular Shapes**: The layout engine supports bin-packing for non-rectangular compartment shapes (such as hexagons, circular slots, or custom polygonal/silhouette shapes like those in the Emberleaf insert). The engine utilizes the rectangular bounding box of these non-rectangular shapes to determine placement constraints, ensuring they are packed without overlaps.
* **Element Pack Bounding Boxes**: The library supports element packing where multiple individual shape elements (such as worker or hero tokens) are arranged within a local bounding box using a list of X/Y offsets and rotation sets. This bounding box is then treated as a single unified standard rectangular compartment or sub-box layout in the main box container. This is utilized for packing Emberleaf's species worker and hero tokens inside the player box interior.

### Box Rotation Propagation to Compartments
When the 3D box packer rotates a sub-box by 90 degrees (swapping width and length), the compartment layout MUST be re-generated in the rotated interior frame:
* **Post-Rotation Interior**: `Project.export()` uses the placement's `rotation` flag and final (possibly swapped) `final_size` to compute the interior, then re-runs `layout_compartments` against that rotated interior.
* **Content Alignment**: Compartments are laid out using the box's post-rotation width/length so contents stay aligned with the actual printed box walls.
* **`no_rotate` Opt-Out**: A box whose contents are directionally constrained (e.g., the Irish Gauge money box, whose 3 card slots span the width) sets `no_rotate=True`. The packer then only considers the original orientation for that box, and the compartment layout always matches its natural direction.

### Multi-Bin Compartment Packing API
To allow compartments to be dynamically partitioned across multiple boxes (like the two animal boxes), the `Project` class implements `project.share_compartments(boxes, compartments)`:
* **Boxes Registration**: Registers a list of box labels (e.g. `["AnimalBox1", "AnimalBox2"]`) and a shared list of compartments.
* **Auto-Partitioning during Export**: During `Project.export()`, the engine automatically computes the interior sizes of these boxes, runs the multi-bin backtracking shelf-packer solver to partition the shared compartments across the boxes, and populates the compartments of each box builder before geometry generation!

### Main Earth Insert Sizing Rules
To match the original layout in the main game box:
* **Card Boxes Footprint**: All card boxes (both Earth and non-Earth/small card boxes) and player boxes MUST have a fixed, identical footprint of `(68.0, 99.0)`.
* **Full Height Card Boxes**: The primary card boxes (`EarthCardBox1`, `EarthCardBox2`, `EarthCardBox3`, and `EarthCardBox4`/`EarthCardBox` in the second row) MUST have a fixed height of exactly `55.2` mm to sit directly under the player boards (which occupy the remaining `16.8` mm height).
* **Non-Earth Card Boxes Stack**: The non-Earth card boxes (Ecosystem, Fauna, Island, Climate, Solo, Season, Abundance, and Start) MUST declare their exact minimum heights based on card counts, plus floor and lid thicknesses. The layout engine will stack them into columns that sum to exactly `55.2` mm.
* **Player Boxes Stack**: The 6 player boxes MUST also have a footprint of `(68.0, 99.0)`. Their heights MUST be flexible (defaulting to `9.2` mm each) so they stack exactly 6-high to sum to the `55.2` mm column height.

### Height Constraints & Packing Tradeoffs
Since the game box height is `47.0` mm, raising the sprout box height to `30.0` mm and locking the card box to `29.2` mm makes it impossible to stack the two `12.5` mm animal boxes on top of the sprout box (`12.5 + 12.5 + 34.1 = 59.1` mm). The system must be configured to place these boxes side-by-side or adjust heights/footprints accordingly.

### Migration Checklist

- [x] Port all 37 animal entries from `ANIMAL_PIECES` into the `earth_animal_kingdom.py` data list using `object(width=, length=, num=)` format
- [x] Implement multi-quantity compartment stacking (same W×L, depth = qty × 8mm)
- [x] ~~Wire the 3D bin-packing solver to distribute animals across the two AnimalBox containers~~ *(superseded by T193: the solver's split differed from the original, so the precomputed partition from `lib/animal_kingdom_items_layout.scad` is reproduced verbatim — 26 slots in AnimalBox1, 30 in AnimalBox2, 56 across 37 species)*
- [x] Generate labeled compartment floors (0.2mm extruded text per animal name) — `pyboxbuilder/compartments/labels.py` (T090)
- [x] Port the card box with correct 36-card count and finger hole scoop
- [x] Port the sprout box (50 cubes) and canopy box (20 tokens)
- [x] Verify all boxes pack within the 288×158mm game box interior *(six boxes, not seven — T191 replaced the invented `Boards` box with the original's `SpacerBox` 174 × 158 × 21; positions come from `columns(stack(...), stack(...), "CanopyBox")` per T208)*
- [x] Export all files and verify against original `examples/release/earth_animal_kingdom/` output

## Stackable Hexes Example

The `boxes/stackable_hexes/` example ports `examples/stackable_hexes.py` to the new `pyboxbuilder` Project API. It demonstrates three new features: standalone boxes, stackable no-lid boxes, and side magnets.

### Reference (from `examples/stackable_hexes.py`)

The original design creates hexagonal boxes (`PathBox.regular_polygon(sides=6)`) that are:
- **Standalone** — each box is a single `PathBox` generated independently via `@make_box`, with no game box and no packing phase.
- **Stackable** — `stackable=STACKABLE_TYPE_INSIDE` (recess on the top rim nests into the box above; outside-fit `STACKABLE_TYPE_OUTSIDE` also available).
- **Magnetic** — round magnets (default 6×3mm) or rectangular magnets (default 10×5×2mm) in the side walls via `magnet=SimpleNamespace(type=..., size=[...])`.
- **Divisible** — `HexBoxDivisions` partitions the interior into 1–4 equal hex-sectors with a configurable `bottom_radius`.
- **Hollow or divided** — `hollow(divisions <= 1)`: a single-compartment hex is hollow; multi-compartment hexes use divisions.

### Box Configuration Matrix

| Box | Divisions | Magnet Type | Magnet Size | bottom_radius |
|-----|-----------|-------------|-------------|---------------|
| HexBoxSingle6x3RoundMagnet | 1 | round | [h/2-1, 7, 2.9] | — |
| HexBoxSingle6x3RoundMagnetWithTwoPartitions | 2 | round | [h/2-1, 7, 2.9] | 5 |
| HexBoxSingle6x3RoundMagnetWithThreePartitions | 3 | round | [h/2-1, 7, 2.9] | — |
| HexBoxSingle6x3RoundMagnetWithFourPartitions | 4 | round | [h/2-1, 7, 2.9] | — |
| HexBoxSingle10x5x2RectMagnet | 1 | rect | [12, 6, 1.65] | — |
| HexBoxSingle10x5x2RectMagnetWithTwoPartitions | 2 | rect | [12, 6, 1.65] | 10 |
| HexBoxSingle10x5x2RectMagnetWithThreePartitions | 3 | rect | [12, 6, 1.65] | 10 |
| HexBoxSingle10x5x2RectMagnetWithFourPartitions | 4 | rect | [12, 6, 1.65] | 10 |

### Key Parameters

- `stackable_width = 100`, `stackable_height = 24`, `wall_thickness = 4`
- Hexagon: `regular_polygon(sides=6)`, no finger cutouts (`make_finger_x=False`, `make_finger_y=False`)
- Hollow radius: top=2, bottom=stackable_height × 3/4, radius=2
- Magnet slot types: `MAGNET_SLOT_TYPE_ROUND`, `MAGNET_SLOT_TYPE_RECT` (plus `MAGNET_SLOT_TYPE_NONE`)

### pyboxbuilder Migration

- **Standalone boxes**: `Project` must allow a standalone mode where `project.box(...)` is exported directly without a game box. A standalone box skips packing, auto-sizing, layout PDF, and spacer generation (FR-037).
- **Stackable no-lid boxes**: `BoxType.NO_LID` (or a path-box variant) gains `stackable` (inside/outside) with configurable `stackable_thickness` and `stackable_fit_offset` (FR-038).
- **Magnets**: builders gain a `magnet` sub-configuration with `type` (round/rect), `size`, and `count`, placed on opposing sides (FR-039).
- **Hex/polygon path boxes**: `BoxType.SLIPOVER_PATH` / `BoxType.CAP_PATH` / path-box support `regular_polygon(sides=N)` — this is already covered by the non-rectangular box outline support (FR-018).
- **Divisions**: `HexBoxDivisions` maps to `box.compartment(...)` × N where N partitions divide the hexagon into equal sectors.

### Migration Checklist

- [x] Create `boxes/stackable_hexes/stackable_hexes.py` with all 8 hex box variants from the matrix (T110)
- [x] Implement standalone box export path (no game box, no packing) in `pyboxbuilder/project.py` (T102)
- [x] Implement stackable inside/outside rim generation for no-lid boxes (T103)
- [x] Implement round and rectangular magnet slots on opposing sides (T104)
- [x] Verify hex boxes stack, magnets align, and divisions clip to the hex interior
- [ ] Replace the `stackable` / `magnet_type` bare strings on `BoxBuilder` with `StackableMode` / `MagnetType` enums (the "no bare strings" constraint above) — see *Typed Options*
- [ ] Reject a magnet configuration whose slot count exceeds the available straight-wall length, rather than placing a slot across a corner — see *Validation, Errors and Warnings*

## Irish Rails (Irish Gauge) Example

The `boxes/irish_gauge/` example ports `examples/irish_gauge.scad` to the new `pyboxbuilder` Project API. This is a game-box insert with mixed box types and hand-placed spacer boxes. The port demonstrates: mixed lid types in one game box, company boxes with shared footprint but different contents, and spacer boxes derived from the leftover space.

### Game Box

- **Retail box**: 214 × 302 × 39mm (W × L × H)
- **Defaults**: wall_thickness=3, lid_thickness=3, board_thickness=10.5

### Box Sizes (pulled from the original layout, computed from game box dimensions)

| Box | Type | Width | Length | Height | Count | Color |
|-----|------|-------|--------|--------|-------|-------|
| CompanyBox | Sliding lid | `box_width / 4` = 53.5 | `card_length * 1.8 + 2*wt` = 133.8 | `(box_height - board_thickness) / 2` = 14.25 | 5 | orange, yellow, red, purple, blue |
| MoneyBox | Filament hinge | `box_width` = 214 | `card_length + 2*wt` = 77 | `box_height - board_thickness` = 28.5 | 1 | — |
| SpacerBoxBack | No-lid path | fills back area | fills back area | `box_height - board_thickness` | 1 | — |
| SpacerBoxCompany | No-lid | `box_width/4` | `company_box_length` | `company_box_height` | 1 | — |

### Company Boxes (5, shared footprint, distinct contents and colors)

Each company box has the same footprint (`53.5 × 133.8 × 14.25`) but different contents driven by its `shares` count:

| Company | Lid label | Color | Shares |
|---------|-----------|-------|--------|
| Belfast and County Down Railway | Belfast | orange | 2 |
| Cork Bandon & South Coast Railway | Cork | yellow | 3 |
| Midland Great Western Railway | Midland | red | 3 |
| Waterford Limerick & Western Railway | Waterford | purple | 4 |
| Great Southern & Western Railway | Great Southern | blue | 4 |

Each company box holds:
- **Share cards**: 49 × 71mm cards, stacked `shares` high (single card thickness = 14/20 = 0.7mm)
- **Dividend markers**: 7.5mm diameter × 3mm thick, in a `CylinderWithIndents` slot with finger holes
- **Trains**: 19 trains per company, each 7.75 × 5.5 × 8mm, in a 6×4 grid well
- **Company name label**: 3-line text (font size 7.75) extruded 0.2mm on the floor

### Money Box

- Filament-hinge lid, 214 × 77 × 28.5mm
- Three card slots (49 × 71mm each) labeled "1", "5", "10" for money denominations (25 cards total)
- "Irish" / "Gauge" text labels extruded on the floor

### Spacer Boxes — automatic definitions (not hand-coded paths)

The original `.scad` hard-codes the `SpacerBoxBack` polygon path and `SpacerBoxCompany` size. In the port, spacer definitions MUST be automatic:

- **SpacerBoxCompany**: generated by the packing solver to fill the vertical gap above the company box columns (a simple rectangular no-lid tray).
- **SpacerBoxBack**: generated automatically by the packing solver as the remaining free area in the game box after the MoneyBox and CompanyBox columns are placed — no hand-written polygon path. The solver derives the polygonal outline from the game box interior minus the placed boxes.

This means `Project.export()` must emit spacer trays (both rectangular and polygon-path) from the leftover space, matching FR-014/FR-030 (hollow spacer trays) and FR-018 (polygon-path clipping).

### Migration Checklist

- [x] Create `boxes/irish_gauge/irish_gauge.py` porting the 5 company boxes, money box, and spacers (T105)
- [x] Derive all box sizes from `box_width`, `box_length`, `box_height`, `board_thickness`, `card_length`, `wall_thickness` — no hardcoded absolute sizes
- [x] Implement company box contents: share-card stack, dividend-marker cylinder with indents, 6×4 train grid well, 3-line name label
- [x] Implement money box: 3 card slots with "1"/"5"/"10" labels + "Irish Gauge" floor text
- [x] Auto-generate SpacerBoxBack (polygon path) and SpacerBoxCompany (rectangular) from leftover space (T106, T174–T180)
- [x] Verify all boxes + spacers pack within 214 × 302mm interior — the port yields **four** spacers, not two: the extra pair is a vertical step above `CompanyBox2`, which FR-014e keeps separate on purpose (T173)

## 1835 Example (Hex Tiles)

The `boxes/1835/` example ports `examples/1835.scad` to the new `pyboxbuilder` Project API. This is the reference for hex-grid tile compartments with finger holes and raised pillars.

### Game Box

- **Retail box**: 216 × 298 × 50mm (W × L × H)
- **Defaults**: wall_thickness=2, lid_thickness=2, floor_thickness=2, board_thickness=15
- `main_height = box_height - board_thickness` = 35mm

### Hex Box

The `HexBox` is a box with an inset tabbed lid holding hexagonal train tiles:

- **Tile**: `tile_width = 40` (apothem-to-apothem), `tile_radius = tile_width / 2 / cos(30°)` ≈ 23.09
- **Hex box size**: `hex_box_width = tile_radius * 6 + 2*wt`, `hex_box_length = box_width - 1`, `hex_box_height = main_height / 4`
- **Hex grid**: `HexGridWithCutouts(rows=3, cols=5, height=hex_box_height, spacing=0, push_block_height=0, tile_width=40)` — a 3×5 array of 15 hexagonal cutouts per box
- **Four stacked HexBoxes**: placed at `z = hex_box_height * 0..3`, giving 60 hex tiles total

### Hex Cell Features (FR-040/041/042)

The `HexGridWithCutouts` cell is a hexagonal prism cutout. Optional features:
- **Push block (raised pillar)**: when `push_block_height > 0`, a smaller hexagon (`width=15`) is subtracted from the cell center, leaving a raised central post so the tile rests elevated for easy grasping.
- **Finger hole in the floor**: a circular cutout through the cell floor (configurable diameter) so a finger can push the tile up from underneath. When combined with a push block, the finger hole is offset to the cell edge.

### pyboxbuilder Migration

- **Hex grid compartment**: `box.compartment(...)` gains a `hex_grid` mode with `rows`, `cols`, `tile_width`, `spacing`, `push_block_height`, and `finger_hole_diameter` parameters (FR-040–FR-042).
- **Hex cell geometry**: borrowed `HexGridWithCutouts` / `RegularPolygonGrid` from `components.py` for the hexagonal cutout layout.
- **Box types**: `HexBox` uses inset-tabbed lid (`BoxType.INSET` with tabbing) — maps to the existing inset box type with tabs.

### Porting `BoxLayout` — the layout is data, not a solver problem

The original `.scad` files end with a `BoxLayout` module that encodes the EXACT
positions of every box (via `translate([x, y, z])` and `rotate([0, 0, -90])`).
This is the source of truth for the game-box layout. When porting an example:

1. **Port `BoxLayout` verbatim as manual `position=` values** on each `project.box(...)` call (with `no_rotate=True`, and the 90° rotation baked into the `size` by swapping width/length).
2. **Do NOT rely on the 3D auto-packer to rediscover the layout** — the original layout is a known-valid packing with specific Z-floating (e.g., 1835's `MiddleBox` floats at `z = money_box_height_1 + money_box_height_2` above the money boxes) that a greedy first-fit solver may not reproduce.
3. **Spacers are derived from the leftover space** after the manual layout is applied — the auto spacer generation fills any remaining gaps.

This is why the 1835 port uses explicit `position=` for all 12 boxes (MoneyBox1–2, HexBox1–4, ShareBox1–4, MiddleBox, FirstPlayer), reproducing the original `BoxLayout` coordinates. The auto-packer is only a fallback for boxes with no manual position.

### Generated Boxes Are Always Accurate — Stale Boxes Are Deleted

Generated box output (boxes, spacers, lids) MUST always accurately reflect the current layout:

1. **Spacer accuracy**: spacer generation MUST produce only the spacers the layout actually needs. The original 1835 layout produces exactly ONE spacer (`SpacerBox` — the 11mm gap above the `FirstPlayer` box). The generator MUST NOT emit spurious spacers for reserved regions — in particular, the **board area** (`board_thickness`, e.g. 15mm) is reserved for the game board, which sits on TOP of the box, and MUST NOT be treated as a spacer gap. Model `board_thickness` explicitly so the spacer pass only considers the usable box volume (`game_box_height - board_thickness`), with the board occupying the top `z = height - board_thickness .. height`.
2. **Stale-file cleanup**: when a re-export produces fewer spacers than a previous run, the obsolete spacer 3MF files on disk (e.g. `spacer_3_body.3mf` when only `spacer_1`/`spacer_2` are now generated) MUST be deleted. The export step MUST NOT leave orphaned spacer files that no longer correspond to a generated spacer.
3. **Deterministic naming**: spacers are numbered `spacer_1..spacer_N` in generation order; a spacer that is removed shifts no other spacer's numbering (renumbering happens naturally each run).

### Migration Checklist

- [x] Create `boxes/1835/1835.py` with hex box, money boxes, share boxes, middle box, first-player box, spacer
- [x] Implement hex-grid compartment layout (`HexGridWithCutouts` port) in `pyboxbuilder/compartments/`
- [x] Implement push block (raised central pillar) in hex cells
- [x] Implement hex-cell floor finger holes (offset from pillar when both present)
- [x] Port the money box (8 denominations), share box (8 companies), middle box (tokens/trains), first-player box
- [x] Port `BoxLayout` as manual `position=` values (all 12 boxes), reproducing the original layout
- [x] Verify all boxes + spacers pack within 216 × 298mm interior

## Box Type Catalogue and Closure Features (FR-001, FR-002)

A box type is nothing but a pair — how the body's rim is shaped, and what mates with it — so the two halves come out of **one** function per closure in `pyboxbuilder/box/features.py` and cannot drift apart. The 14 types:

| Type | Closure feature | Lid | Notes |
|---|---|---|---|
| `SLIDING` | `sliding_track` | slides out along the length | angled dovetail (top = interior width, bottom = half wall width), see *The Dovetail Profile*; asymmetric track walls — see the chamfer rule in *Finger Holes & Box Edge Smoothing* |
| `SLIDING_CATCH` | `sliding_track` + `sliding_catch` | slides, clicks | bump on the lid drops into a slightly larger dimple |
| `CARD_LIBRARY` | `sliding_track` + heavier latch | slides | catch bump trimmed to the box envelope (T234) |
| `CAP` / `CAP_PATH` | `cap_metrics`/`cap_body`/`cap_lid` | friction-fit cap over the rim | body stops a lid thickness short; `_PATH` follows a polygon footprint |
| `SLIPOVER` / `SLIPOVER_PATH` | `slipover_metrics` | sleeve down over the body | body inset all round, `foot` keeps the full footprint to seat on |
| `INSET` | `rabbet` | plate drops flush into a ledge in the rim | keeps stacking flat |
| `HINGE` | `knuckle_hinge` (printed pin) | pivots at the back | barrel may stand proud **behind** the footprint, nothing else may |
| `FILAMENT_HINGE` | `filament_hinge` | pivots on a filament pin | interleaved knuckles, each leaf webbed to its own half |
| `MAGNETIC` | magnet slots + flush plate | lifts off | body stops a lid thickness short so it closes flush |
| `NO_LID` | none | — | stackable rim + side magnets live here (FR-038/039) |
| `PATH` | none | — | polygon footprint, lidless; also the carrier for polygon spacers (FR-014d) |

**A closed box is exactly the size it declares** — over its declared footprint, at its declared height. That is the invariant the packer, `arrange()` and the spacer pass all depend on; it is stated here because seven types once broke it (Phase 18) and the "lid does not overlap body" test cannot catch it.

## Compartment Sizing and Placement (FR-003, FR-005, FR-008)

- **Absolute or ratio.** A compartment takes either `size=(w, l)` or `width_ratio`/`length_ratio`, resolved against the interior at layout time (`CompartmentBuilder.resolve_size`). Mixing the two in one box is legal; a ratio always resolves against the *post-rotation* interior (FR-013b).
- **0.1mm is the floor.** No dimension is ever rounded to a whole millimetre — not on resolve, not on placement, not on export. Precision is asserted, not assumed (T088, T094).
- **Manual beats automatic.** A compartment with an explicit `position=(x, y)` is placed there verbatim and excluded from the shelf packer; the remaining compartments pack around it. Overlaps among manual placements are an error, not a warning (FR-007).
- **Groups.** Compartments sharing a group are packed as one unit — placed adjacently before free compartments fill what is left — so "card slot + token well stay together" is expressible without coordinates.
- **Element packs.** A compartment whose contents are individual `CompartmentElement` slots derives its own size from the pack's bounding box (FR-004b) and then packs as an ordinary rectangle.

## Box Expansion and Gap Absorption (FR-012, FR-015, FR-016, FR-017)

Expansion is per-axis and off by default at the master switch:

- `expandable=False` disables **all** growth. `expandable_width` / `expandable_length` add fill-to-fit growth on their axis; `expandable` alone still permits the sub-3mm height absorb. (These were once OR'd together, which silently stretched every box declared fixed — T181/T182.)
- **X and Y first.** Height is the last axis to grow: a Z gap ≥ 3mm becomes a spacer, a gap < 3mm is absorbed into the adjacent box's height.
- **Rows share a length.** Every box in a row takes the row's longest length; row *widths* are variable, set by the widest box in that row, never equalised across rows (FR-013, FR-016).
- **Gap thresholds.** A horizontal gap below `gap_threshold` (10mm) is absorbed by an adjacent expandable box. At or above it, a spacer is emitted — unless the tray would fall below `min_spacer_dim` (15mm W/L), in which case the minimum wins and the gap is absorbed anyway. Height has no such floor beyond `min_spacer_height`.
- **Standalone boxes ignore expansion entirely** — there is no container to fill, so `expandable=True` is a no-op rather than an error.

## Clearance and Fit Model (FR-019, FR-014c)

One number, `Project.clearance_slack` (default 1.0mm, sane range 1–2mm), applied in one direction: **shrink the part, never grow the hole**.

- A sub-box's footprint is reduced by the slack against the game box walls and its neighbours, so it lifts in and out instead of being an interference fit.
- A spacer's footprint is inset by the same slack after merging (`apply_clearance`), so a tray is liftable too.
- Polygon footprints inset **exactly**, per-edge along the inward normals of the *directed* edges (`paths.inset_rectilinear`) — a centroid scale thins one arm of an L while fattening the other.
- Compartment-to-compartment and compartment-to-wall clearance is a separate, smaller constant in `compartments/builder.py`; it is a print tolerance, not a handling allowance.

## Lid Decoration Design (FR-020, FR-021, FR-022, FR-023, FR-024, FR-035, FR-036)

`pyboxbuilder/lid/decorate.py` applies a `LidBuilder` to **any** type's lid, deriving the decoratable face from the lid's own bounding box so no box type declares one.

**Label sizing is measured, never estimated.** Text is set at a nominal size, measured with `textmetrics`, and scaled to the label area (the lid face minus `border_margin`, default 5mm per side). A character-count estimate once put 102mm of text on a 100mm lid (T199). If the scaled character height lands below `min_text_height` (default 4mm, `0` disables the guard) the label is **skipped entirely** — no geometry, no colour assignment — rather than printed illegibly.

**Two layout modes, one orientation switch.**
- *Frameless*: text only.
- *Framed*: a rectangular frame with diagonal hatching behind the text (bed adhesion for text islands, spaced so the text bridges without supports) plus a small outer border. The backing plate hugs the text rather than filling the label area, so a lid can carry a frame **and** a pattern (T200).
- *Diagonal* is an orientation available in both modes: corner-to-corner at the lid's natural angle, which is 45° only when the lid is square.

**Patterns cut through.** A pattern is a through-hole fill over the lid face — maximum filament saving — clipped twice: at the lid outline, and at the label area, which takes precedence (FR-023 note, and the reason a framed label does not lose its border). The catalogue is the full ported `ShapeType` set: dense/lattice shapes, `PENTAGON_R1`–`R15`, and the tessellation families; `build_pattern` dispatches every member with **no fallback to grid** (T116/T117).

**Three accent colours, independently settable**: label text, frame top layer, pattern top layer — each defaulting to a value distinct from the body colour. Patterns may assign different colours to different elements (FR-024).

**Per-mode overrides (FR-035, FR-036).** `mmu_label` and `single_label` override the parent `LidBuilder` when set and fall back to it when not; specifying one does not require the other. Beyond that, the two modes differ structurally:
- *MMU*: the label is a separate raised insert in its own material; compartment floor labels are raised 0.2mm in a second colour.
- *Single*: the label is **engraved** into the face, and a framed label degrades to engraved text — a frame is a colour feature, and keeping it lifted the text 0.4mm clear so the engraving cut nothing (T202). Compartment floor labels are 0.2mm recessed cutouts.

## Material and Colour Model (FR-009, FR-024, FR-025)

- **`pybosl2.Color` only.** No `Color` class, no presets, no RGB literals in project files — webcolor names at the call site (`Color("darkgreen")`). `pyboxbuilder/color.py` must not exist.
- **One coordinate frame.** Every piece of a box — body, lid, inserts, spacers — is built in the box's own frame with its origin at the packed position, so parts align when assembled and a lid needs no extra Z offset to sit on its body.
- **MMU is object separation, not painting.** `BoxExporter._compose` keeps positive inserts as distinct objects with their own material in the `mmu/` pass and fuses them into the body for the `single/` pass. The 3MF carries the material assignment; nothing is baked into the mesh.
- A body colour equal to all three accent colours is legal but pointless — it degenerates to one material and warrants a warning (see *Validation*).

## Builder API Shape (FR-026)

`project.box(BoxType.X, "Label", ...)` returns a **type-specific** builder — `SlidingBoxBuilder`, `CapBoxBuilder`, … — chosen by the registry and narrowed by `@overload` so an IDE offers only the options that type actually has. Chaining happens on the returned builder (`.compartment(...)`, `.finger_hole(...)`), each call registering into the builder rather than returning a new one; builders are frozen for their declared fields and mutated only by the packer through `final_size` / `position`. A `box_id` distinguishes duplicate instances of the same label-less box. The whole public surface is the package: `from pyboxbuilder import Project, BoxType, LidBuilder, columns, rows, stack, …`.

## Typed Options — No Bare Strings

The constraint above says enums for all type selections. Two fields on `BoxBuilder` still hold `str | None` and must be converted: `stackable` (→ `StackableMode.INSIDE` / `OUTSIDE`) and `magnet_type` (→ `MagnetType.ROUND` / `RECT` / `NONE`). `ScoopSide` exists but defaults to `None` where it should default to a member. These are public API, so the conversion is a breaking change for the six example projects that set them, and is done in one pass.

## Export Pipeline and Caching (FR-029, FR-030, FR-031, FR-032)

`Project.export(out_dir)` runs: resolve layout (pack → expand → propagate `final_size`) → generate spacers → build each piece per colour mode → write conditionally → delete stale → PDF.

- **Files.** `{out_dir}/{game}/mmu/` and `{out_dir}/{game}/single/`, named `<label>_body.3mf` / `<label>_lid.3mf`. A lidless type produces a body only. Each spacer gets its own file. So a kit of 1 outer + 3 sub-boxes + 2 spacers is (4 × 2 + 2) × 2 = 20 files (SC-011).
- **Write-if-different.** A 3MF stamps a fresh timestamp and UUIDs on every write, so byte comparison never matches. The gate is a 3D Hausdorff distance against the mesh already on disk (tolerance 0.001mm, user-settable), measured **in both directions** and sampled over faces and edges, not vertices — one-sided vertex sampling reported 0.0 for boxes differing by 0.5mm (T211). Without pymeshlab the exporter falls back to a `<mesh>`-only digest.
- **Reporting.** `ExportResult` lists written and skipped paths; `Project.piece_bounds` carries every piece's measured bounding box (below).
- **Stale files.** `BoxExporter.delete_stale` removes `spacer_*` files a run no longer produces, so a layout that drops from four spacers to three leaves no orphan.
- **A corrupt cache is a miss**, silently regenerated — never an error.

## Print-Bed Reporting (FR-027)

Every exported piece's bounding box is measured (not computed from the declared size — the hinge barrel stands outside the footprint) and surfaced as `Project.piece_bounds`, so a user can check a piece against their bed before slicing.

## Silhouette Fidelity (FR-045)

Smoothing and silhouette fidelity are in direct tension, so the rule is explicit: **the outline of a piece shape is never modified.** SVG silhouettes, animal outlines, token cutouts and engraved shapes are reproduced exactly as authored, even where the result is awkward to print — thin features, overhangs, sharp interior corners all stand. The fillets and chamfers of FR-043/FR-044 apply only to structural edges the toolkit itself creates: box rims and corners, compartment wall/floor junctions, finger scoops and finger holes. No global smoothing pass may run over element geometry, and the SVG parse cache stores the path as parsed.

## Validation, Errors and Warnings

Rejected at specification/export time with a descriptive `ValueError` (or `PackingError`) naming the offender:

| Condition | Behaviour |
|---|---|
| Compartment deeper than the interior, or overflowing it | error naming the compartment/group and the overflow amount |
| Compartment width ratios summing > 1.0 in a row | error listing each over-allocated compartment and its ratio |
| Manually positioned compartments overlapping | error, never silent geometry |
| Sub-boxes not fitting the outer interior (footprint or height, lid thickness included) | error naming each box and by how much |
| Packing failure | `PackingError` with the fill ratio and any oversized boxes — never an empty layout |
| Box with neither compartments nor an explicit `size` | error |
| Hex grid with `rows` or `cols` ≤ 0 | error |
| Hex tile larger than the interior, zero cells fitting | error (cells that merely overhang are clipped) |
| Magnet slot count exceeding the available straight-wall length | error — slots may not cross a corner |
| Spacer whose computed height is ≤ 0 | error |
| Rotated box whose compartments no longer fit the rotated interior | re-layout, then error if still overflowing (or set `no_rotate`) |

Emitted as a **warning**, with the run continuing:

| Condition | Behaviour |
|---|---|
| `LidBuilder` set on a lidless box type | warn, drop the decoration |
| Exported mesh empty (no geometry) | warn, do **not** write the file |
| Body colour equal to all three accent colours | warn — the multi-colour 3MF degenerates to one material |
| Overlapping finger cutouts | warn |
| Empty project (no sub-boxes) | no files, no PDF, empty `ExportResult` — not an error |
| `expandable=True` on a standalone box | ignored silently (documented, not warned) |

Zero-thickness walls between adjacent compartments are **not** an error: the compartments merge into a single cavity, which is a legitimate way to express an L-shaped well.

## Example Inventory

Twelve projects live under `boxes/`. The five documented in detail above are the reference ports; the rest exercise the same API and are ported from their `examples/*.scad` originals.

| Project | Demonstrates |
|---|---|
| `earth_animal_kingdom` | auto-sized card/sprout/canopy boxes, 56 animal slots from a precomputed partition, `columns`/`stack` layout |
| `emberleaf` | element packs (per-worker silhouette slots), 21 boxes at 77% fill, derived spacers |
| `irish_gauge` | mixed lid types in one game box, shared-footprint company boxes, polygon spacers |
| `1835` | hex-grid compartments, push blocks, floor finger holes, `BoxLayout` ported as manual positions |
| `stackable_hexes` | standalone boxes, stackable rims, round/rect magnets, hex divisions |
| `earth` | the FR-013a fixed 68 × 99 footprint and 55.2mm column rules |
| `arkham_horror`, `dominion`, `first_class`, `magical_athlete`, `nippon` | additional ports; each must satisfy the dual-run rule below |
| `_template` | the starting point for a new game |

Every one of them obeys *Examples Must Run In Both Plain Python and Jupyter* and the `FROM_MAKE` branch, and that is verified by test, not by inspection.

## Requirements Coverage Map

Where each requirement is designed, and where it is verified. Sections named below are in this document unless prefixed `spec:`.

| FR | Plan section | Module |
|---|---|---|
| FR-001, FR-002, FR-002a–FR-002f | Box Type Catalogue; The Dovetail Profile | `box/types/*`, `box/features.py` |
| FR-003, FR-005 | Compartment Sizing and Placement | `compartments/builder.py`, `compartments/layout.py` |
| FR-003a | Validation | `project.py` |
| FR-004, FR-004a | Compartment Auto-Layout with Rotation | `compartments/layout.py` |
| FR-004b | Compartment Auto-Layout (Element Pack Bounding Boxes) | `compartments/element.py` |
| FR-006 | Finger Holes & Box Edge Smoothing | `compartments/finger_hole.py` |
| FR-007, FR-011 | Validation | `compartments/layout.py`, `packing/layout.py` |
| FR-008 | Compartment Sizing and Placement (Groups) | `compartments/layout.py` |
| FR-008a | Multi-Bin Compartment Packing API | `project.py` |
| FR-009 | Material and Colour Model | `export/exporter.py` |
| FR-010 | When Auto-Packing Works | `packing/layout.py`, `packing/guillotine.py` |
| FR-012, FR-015–FR-017 | Box Expansion and Gap Absorption | `packing/layout.py` |
| FR-013, FR-013a | Box Expansion; Main Earth Insert Sizing Rules | `packing/layout.py`, `boxes/earth/` |
| FR-013b, FR-013c | Box Rotation Propagation to Compartments | `project.py`, `packing/layout.py` |
| FR-014, FR-014a–e | Spacer Generation: Sweep, then Merge | `packing/spacer.py`, `paths.py` |
| FR-018 | Spacer Generation (rectilinear merge) | `paths.py`, `box/types/path.py` |
| FR-019 | Clearance and Fit Model | `packing/spacer.py`, `compartments/builder.py` |
| FR-020–FR-024 | Lid Decoration Design | `lid/label.py`, `lid/pattern.py`, `lid/decorate.py`, `lid/color_layers.py` |
| FR-025 | Material and Colour Model | `export/exporter.py` |
| FR-026 | Builder API Shape | `project.py`, `builders/*` |
| FR-027 | Print-Bed Reporting | `export/exporter.py` |
| FR-028 | *deferred, not in v1* | — |
| FR-029–FR-032 | Export Pipeline and Caching | `export/exporter.py`, `export/hausdorff.py`, `export/result.py` |
| FR-033, FR-034 | 3D Oblique Exploded PDF Guide Layout | `export/layout_pdf.py` |
| FR-035, FR-036 | Lid Decoration Design (per-mode overrides) | `lid/builder.py`, `compartments/labels.py` |
| FR-037 | Stackable Hexes Example (standalone) | `project.py` |
| FR-038, FR-039 | Stackable Hexes Example; Typed Options | `box/types/no_lid.py` |
| FR-040–FR-042 | 1835 Example (Hex Tiles) | `compartments/hex_grid.py` |
| FR-043, FR-044 | Finger Holes & Box Edge Smoothing | `box/shell.py`, `compartments/finger_hole.py` |
| FR-045 | Silhouette Fidelity | `compartments/element.py` |

| SC | Verified by |
|---|---|
| SC-001 | `quickstart.md` scenarios (T085) |
| SC-002, SC-008 | timed layout/auto-size tests in `test_compartments.py`, `test_packing.py` |
| SC-003 | `test_closures.py` — zero body/lid intersection for all 11 lidded types |
| SC-045 | `test_closures.py` — dovetail measures interior over half the wall width, grooves mirror, wall stays behind the groove, leading chamfer, stop end square |
| SC-046, SC-047 | `test_closures.py` — `HingeInsideTests` (a well is clipped clear of the hinge), `SlipoverFingerNotchTests` |
| SC-048 | `test_closures.py` — the stop wall is dovetailed like the sides and the lid seats in it; the closed lid slides all the way out with zero shared volume at every point, and jams within half a mm if lifted; clearance configurable |
| SC-050 | `test_closures.py` — corners rounded and both leading edges chamfered, each measured against the same lid with the feature off |
| SC-049 | `test_closures.py` — the bump and dimple sit at the outlet, follow the slide axis, straddle the lid's flank, and are absent unless asked for |
| SC-004, SC-007 | `test_compartments.py` validation cases |
| SC-005 | `test_packing.py`, `test_guillotine.py` |
| SC-006 | `test_carve.py`, render tests |
| SC-009, SC-010 | `test_packing.py` gap-threshold cases |
| SC-010a/b/c | `test_spacer_merge.py`, `test_emberleaf.py` |
| SC-011–SC-013 | `test_export.py`, `test_exporter.py`, render export tests |
| SC-014–SC-016 | `test_lid_label.py`, `test_lid_decorate.py` |
| SC-017–SC-019 | `test_export.py` PDF cases |
| SC-020 | `test_project.py` standalone path |
| SC-021, SC-022 | `test_all_box_types.py`, golden renders |
| SC-023 | `boxes/stackable_hexes` + `test_hex_grid.py` |

## Complexity Tracking

> No violations.
